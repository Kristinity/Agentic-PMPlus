"""
step5-pgp - Agentic-PMPlus

Preference Gaussian Process (PGP), der offene/neue Auftraege priorisiert.
Rollenbeschreibung: Konzept-README.md (Repo-Root). Mathematische Grundlage:
step5-pgp/Preference-Gaussian-Process.md.

Der PGP hat laut Konzept-README.md "volle Einsicht auf ERP & Context
Engineering" und liefert pro Auftrag zwei Werte aus einem Modell: eine
Rang-Prognose **mu** und eine Selbstunsicherheit **sigma**. Priorisiert wird
anhand der dort genannten Faktoren:

  - prognostizierte Durchlaufzeit (DZ)          -> orders.csv + disruptions.csv
  - aktuelle Maschinenverfuegbarkeit             -> work_centers.csv + disruptions.csv
  - Materialverfuegbarkeit                       -> inventory.csv + disruptions.csv
  - Abhaengigkeiten zu laufenden Auftraegen      -> Work-Center-Konkurrenz in orders.csv
  - vertraglich festgelegter Bruttopreis         -> KEIN Preisfeld im Datenmodell;
                                                     quantity als grobe, klar markierte
                                                     Ersatzgroesse
  - Mitarbeiter-Coverage (Urlaub/Krankmeldungen) -> KEINE Datenquelle im Projekt -> nicht
                                                     modelliert (kein erfundener Wert)
  - Lieferantenbewertung                         -> KEINE Datenquelle im Projekt -> nicht
                                                     modelliert (kein erfundener Wert)

Context-Engineering-Zugriff (Step 4): der PGP laedt dieselben kuratierten
RAG-Dokumente wie step4-context-engineering/main.py (ueber das in
docker-compose.yml mount ./step4-context-engineering/rag_documents:/app/rag_documents)
und wendet die darin dokumentierten Geschaeftsregeln als Score-Anpassung an
(siehe apply_rag_adjustments) - z. B. die SLA-Eskalationsschwelle aus
sla-becksbrauerei.md oder den Praezedenzfall aus
stoerung-weissblech-engpass-2025.md.

Bootstrap-Hinweis: Es liegen noch keine echten menschlichen/LLM-Praeferenz-
urteile vor (die sammelt erst der Active Learning Loop, Step 7). Der GP wird
deshalb hier auf einer transparenten, im Code dokumentierten Heuristik-Utility
(compute_heuristic_utility) trainiert statt auf echten Praeferenzpaaren - ein
bewusster Uebergangszustand fuer den Prototyp, keine Endloesung. Sobald Step 7
echte Entscheidungen sammelt, ersetzt dieses Trainingssignal die Heuristik.
"""

import glob
import os
import random
from datetime import date

import gpytorch
import numpy as np
import pandas as pd
import torch
import yaml

ERP_DATA_DIR = os.environ.get("ERP_DATA_DIR", "shared_data")
RAG_DOCUMENTS_DIR = os.environ.get("RAG_DOCUMENTS_DIR", "rag_documents")
AS_OF_DATE = os.environ.get("AS_OF_DATE")  # ISO-Datum; Default: Median der order_date
TRAIN_SAMPLE_SIZE = int(os.environ.get("TRAIN_SAMPLE_SIZE", "300"))
MAX_NEW_ORDERS = int(os.environ.get("MAX_NEW_ORDERS", "20"))
GP_TRAIN_ITERS = int(os.environ.get("GP_TRAIN_ITERS", "80"))
SEED = int(os.environ.get("SEED", "42"))

FEATURE_NAMES = [
    "urgency", "machine_scarcity", "material_risk", "contention",
    "quantity_proxy", "sla_breach", "material_precedent",
]


# --- Laden -------------------------------------------------------------

def load_erp_data(data_dir):
    def read(name, date_cols=None):
        return pd.read_csv(os.path.join(data_dir, name), parse_dates=date_cols)

    disruptions = read("disruptions.csv")
    # "impact" mischt Zahlen (machine_breakdown/material_shortage) und Text
    # ("hoch"/"normal" bei priority_change) -> Spalte wird als object/string
    # gelesen. Fuer die numerische Nutzung separat coercen statt zu casten.
    disruptions["impact_numeric"] = pd.to_numeric(disruptions["impact"], errors="coerce")

    return {
        "orders": read("orders.csv", ["order_date", "due_date"]),
        "bom": read("bom.csv"),
        "routings": read("routings.csv"),
        "work_centers": read("work_centers.csv"),
        "calendar": read("calendar.csv", ["date"]),
        "inventory": read("inventory.csv"),
        "disruptions": disruptions,
    }


def load_rag_documents(directory):
    """Manuelles Frontmatter-Parsing (kein python-frontmatter-Paket noetig,
    gleiches Format wie in step4-context-engineering/rag_documents/*.md)."""
    docs = []
    for path in sorted(glob.glob(os.path.join(directory, "*.md"))):
        if os.path.basename(path).startswith("_"):
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        meta = yaml.safe_load(parts[1]) or {}
        docs.append((meta, parts[2].strip()))
    return docs


def is_valid(meta, as_of):
    gueltig_ab = meta.get("gueltig_ab")
    gueltig_bis = meta.get("gueltig_bis")
    if gueltig_ab and date.fromisoformat(str(gueltig_ab)) > as_of:
        return False
    if gueltig_bis and date.fromisoformat(str(gueltig_bis)) < as_of:
        return False
    return True


def trusted_documents(docs, as_of):
    return [
        (m, b) for m, b in docs
        if is_valid(m, as_of) and m.get("vertrauensstufe") == "intern-verifiziert"
    ]


# --- Feature-Engineering -------------------------------------------------

def week_index(d, start_date):
    return (d.date() - start_date).days // 7


def build_lookup_tables(erp):
    start_date = erp["calendar"]["date"].min().date()
    routing_by_product = {
        pid: grp["work_center"].tolist()
        for pid, grp in erp["routings"].groupby("product_id")
    }
    wc_info = erp["work_centers"].set_index("work_center_id").to_dict(orient="index")
    bom_by_product = {
        pid: grp[["component", "quantity"]].to_dict(orient="records")
        for pid, grp in erp["bom"].groupby("product_id")
    }
    breakdowns = erp["disruptions"][erp["disruptions"]["type"] == "machine_breakdown"]
    shortages = erp["disruptions"][erp["disruptions"]["type"] == "material_shortage"]
    return start_date, routing_by_product, wc_info, bom_by_product, breakdowns, shortages


def machine_scarcity_for_order(order, start_date, routing_by_product, wc_info, breakdowns):
    work_centers = routing_by_product.get(order["product_id"], [])
    if not work_centers:
        return 0.5
    w_order = week_index(order["order_date"], start_date)
    w_due = week_index(order["due_date"], start_date)
    worst = 0.0
    for wc in work_centers:
        info = wc_info.get(wc, {})
        avail = info.get("availability_pct", 1.0)
        cap_per_week = info.get("capacity_hours_per_shift", 8) * info.get("shifts_per_day", 1) * 5
        hits = breakdowns[
            (breakdowns["target"] == wc)
            & (breakdowns["week"] >= w_order) & (breakdowns["week"] <= w_due)
        ]
        downtime_penalty = hits["impact_numeric"].sum() / cap_per_week if not hits.empty else 0.0
        scarcity = (1 - avail) + downtime_penalty
        worst = max(worst, scarcity)
    return min(worst, 1.0)


def material_risk_for_order(order, start_date, bom_by_product, shortages):
    w_order = week_index(order["order_date"], start_date)
    w_due = week_index(order["due_date"], start_date)
    components = [c["component"] for c in bom_by_product.get(order["product_id"], [])]
    hits = shortages[
        shortages["target"].isin(components)
        & (shortages["week"] >= w_order) & (shortages["week"] <= w_due)
    ]
    if hits.empty:
        return 0.0
    # delay_days im Profil max. 10 (siehe company_profile.example.yaml) -> normieren
    return min(hits["impact_numeric"].max() / 10.0, 1.0)


def contention_for_orders(target_orders, all_orders, window_days=7):
    """Wie viele andere offene Auftraege desselben Produkts (=gleicher
    Arbeitsplan/gleiche Work Center) haben einen Liefertermin im Fenster
    +-window_days -> Proxy fuer 'Abhaengigkeiten zu laufenden Auftraegen'."""
    counts = []
    for _, row in target_orders.iterrows():
        same_product = all_orders[all_orders["product_id"] == row["product_id"]]
        delta = (same_product["due_date"] - row["due_date"]).dt.days.abs()
        counts.append(int(((delta <= window_days) & (same_product["order_id"] != row["order_id"])).sum()))
    return counts


def apply_rag_adjustments(order, buffer_days, trusted_docs, shortages, start_date):
    """Wendet die in den kuratierten RAG-Dokumenten dokumentierten
    Geschaeftsregeln an - nur wenn ein passendes, gueltiges,
    intern-verifiziertes Dokument tatsaechlich gefunden wird (kein
    hartkodiertes Business-Regelwerk unabhaengig vom Context-Engineering)."""
    sla_breach = 0.0
    material_precedent = 0.0
    matched_docs = []

    for meta, _ in trusted_docs:
        doc_type = meta.get("doc_type")
        kunde = meta.get("kunde")

        # sla-becksbrauerei.md: "< 3 Arbeitstage Puffer -> hoch"
        if doc_type == "sla" and kunde == order["customer"] and buffer_days < 3:
            sla_breach = 1.0
            matched_docs.append(meta.get("doc_id"))

        # stoerung-weissblech-engpass-2025.md: bei aktivem Weissblech-Engpass
        # wurde Becks historisch vor dem Sammelposten bedient (Praezedenzfall)
        if doc_type == "stoerungsbericht" and "material_shortage" in (meta.get("tags") or []):
            w_order = week_index(order["order_date"], start_date)
            w_due = week_index(order["due_date"], start_date)
            active = shortages[
                (shortages["target"] == "Weissblech-Coil")
                & (shortages["week"] >= w_order) & (shortages["week"] <= w_due)
            ]
            if not active.empty and order["customer"] == "Becksbrauerei":
                material_precedent = 1.0
                matched_docs.append(meta.get("doc_id"))

    return sla_breach, material_precedent, matched_docs


def generate_begruendung(urgency, scarcity, material_risk, contention_norm, sla_breach,
                          material_precedent, buffer_days):
    """Menschenlesbare Kurzbegruendung aus den tatsaechlich berechneten Faktoren -
    fuer die Eskalations-Review-Anzeige im Frontend (siehe
    step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md, GET
    /eskalationen braucht pgp.begruendung analog zu llm.begruendung). Schwellenwerte
    sind eine dokumentierte Heuristik, keine gelernte/validierte Groesse."""
    reasons = []
    if sla_breach:
        reasons.append(f"SLA-Eskalation (Puffer {buffer_days}d < 3 Arbeitstage)")
    if material_precedent:
        reasons.append("Materialengpass-Praezedenzfall (Becks bevorzugt)")
    if urgency > 0.7:
        reasons.append(f"hohe zeitliche Dringlichkeit (Puffer {buffer_days}d)")
    if scarcity > 0.5:
        reasons.append("knappe Maschinenverfuegbarkeit auf dem Fertigungsweg")
    if material_risk > 0.3:
        reasons.append("Materialverfuegbarkeitsrisiko bei Stuecklisten-Komponente")
    if contention_norm > 0.5:
        reasons.append("hohe Konkurrenz um dieselben Arbeitsplaetze")
    if not reasons:
        reasons.append("keine dominanten Risikofaktoren, Einstufung ueber Basis-Faktoren")
    return "; ".join(reasons)


def build_features(orders_subset, all_orders, erp, trusted_docs, as_of):
    start_date, routing_by_product, wc_info, bom_by_product, breakdowns, shortages = build_lookup_tables(erp)
    contentions = contention_for_orders(orders_subset, all_orders)

    rows, meta_rows = [], []
    for (_, order), contention in zip(orders_subset.iterrows(), contentions):
        buffer_days = (order["due_date"] - pd.Timestamp(as_of)).days
        urgency = float(np.clip(1 - buffer_days / 21.0, 0.0, 1.0))  # 21 = max due_date_distribution
        scarcity = machine_scarcity_for_order(order, start_date, routing_by_product, wc_info, breakdowns)
        material_risk = material_risk_for_order(order, start_date, bom_by_product, shortages)
        contention_norm = min(contention / 10.0, 1.0)
        quantity_proxy = min(order["quantity"] / 20.0, 1.0)  # 20 = max quantity im Profil
        sla_breach, material_precedent, matched_docs = apply_rag_adjustments(
            order, buffer_days, trusted_docs, shortages, start_date
        )
        begruendung = generate_begruendung(
            urgency, scarcity, material_risk, contention_norm, sla_breach,
            material_precedent, buffer_days,
        )

        rows.append([urgency, scarcity, material_risk, contention_norm, quantity_proxy, sla_breach, material_precedent])
        meta_rows.append({
            "order_id": order["order_id"], "customer": order["customer"],
            "product_id": order["product_id"], "due_date": order["due_date"].date().isoformat(),
            "buffer_days": buffer_days, "matched_rag_docs": matched_docs,
            "begruendung": begruendung,
        })
    return np.array(rows, dtype=np.float32), meta_rows


WEIGHTS = np.array([2.5, 1.0, 1.2, 0.5, 0.3, 2.0, 1.5], dtype=np.float32)


def compute_heuristic_utility(features):
    """Transparente Bootstrap-Utility (siehe Modulkopf) - gewichtete Summe der
    Faktoren aus Konzept-README.md, so weit sie sich aus den Daten ableiten
    lassen. Gewichte sind eine dokumentierte Startannahme, keine gelernte/
    validierte Groesse (das ist Aufgabe von Step 6/7)."""
    return features @ WEIGHTS


# --- Gaussian Process ------------------------------------------------------

class ExactGPModel(gpytorch.models.ExactGP):
    def __init__(self, train_x, train_y, likelihood):
        super().__init__(train_x, train_y, likelihood)
        self.mean_module = gpytorch.means.ConstantMean()
        self.covar_module = gpytorch.kernels.ScaleKernel(gpytorch.kernels.RBFKernel())

    def forward(self, x):
        return gpytorch.distributions.MultivariateNormal(
            self.mean_module(x), self.covar_module(x)
        )


def train_gp(x_train, y_train, iters):
    x_t = torch.tensor(x_train)
    y_t = torch.tensor(y_train)
    likelihood = gpytorch.likelihoods.GaussianLikelihood()
    model = ExactGPModel(x_t, y_t, likelihood)

    model.train()
    likelihood.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.1)
    mll = gpytorch.mlls.ExactMarginalLogLikelihood(likelihood, model)
    for _ in range(iters):
        optimizer.zero_grad()
        loss = -mll(model(x_t), y_t)
        loss.backward()
        optimizer.step()

    model.eval()
    likelihood.eval()
    return model, likelihood


def predict(model, likelihood, x_new):
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
        pred = likelihood(model(torch.tensor(x_new)))
    return pred.mean.numpy(), pred.stddev.numpy()


# --- Main --------------------------------------------------------------

def main():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)

    erp = load_erp_data(ERP_DATA_DIR)
    orders = erp["orders"]

    as_of = (
        date.fromisoformat(AS_OF_DATE) if AS_OF_DATE
        else orders["order_date"].median().date()
    )

    rag_docs = load_rag_documents(RAG_DOCUMENTS_DIR)
    trusted_docs = trusted_documents(rag_docs, as_of)

    print("=== step5-pgp ===")
    print(f"Stichtag (as_of): {as_of.isoformat()}")
    print(f"{len(trusted_docs)}/{len(rag_docs)} RAG-Dokumente gueltig+intern-verifiziert "
          f"(Context-Engineering-Zugriff: {RAG_DOCUMENTS_DIR})")
    print("Nicht modelliert (keine Datenquelle im Projekt): Mitarbeiter-Coverage, Lieferantenbewertung")

    history = orders[orders["order_date"].dt.date < as_of]
    open_orders = orders[orders["due_date"].dt.date >= as_of]

    if history.empty or open_orders.empty:
        print("Zu wenig Historie/offene Auftraege fuer den gewaehlten Stichtag - main.py beenden.")
        return

    train_sample = history.sample(min(TRAIN_SAMPLE_SIZE, len(history)), random_state=SEED)
    new_sample = open_orders.sort_values("due_date").head(MAX_NEW_ORDERS)

    x_train, _ = build_features(train_sample, orders, erp, trusted_docs, as_of)
    y_train = compute_heuristic_utility(x_train)

    x_new, meta_new = build_features(new_sample, orders, erp, trusted_docs, as_of)

    print(f"\nGP trainiert auf {len(x_train)} historischen Auftraegen "
          f"(Bootstrap-Utility, s. Modulkopf) -> priorisiere {len(x_new)} offene Auftraege.")

    model, likelihood = train_gp(x_train, y_train, GP_TRAIN_ITERS)
    mu, sigma = predict(model, likelihood, x_new)

    ranking = sorted(zip(mu, sigma, meta_new), key=lambda t: t[0], reverse=True)

    os.makedirs(ERP_DATA_DIR, exist_ok=True)
    out_path = os.path.join(ERP_DATA_DIR, "pgp_priorisierung.csv")
    pd.DataFrame([
        {
            "rank": i + 1, "order_id": m["order_id"], "customer": m["customer"],
            "product_id": m["product_id"], "due_date": m["due_date"],
            "buffer_days": m["buffer_days"], "mu": float(mu_i), "sigma": float(sigma_i),
            "matched_rag_docs": ";".join(m["matched_rag_docs"]),
            "pgp_begruendung": m["begruendung"],
        }
        for i, (mu_i, sigma_i, m) in enumerate(ranking)
    ]).to_csv(out_path, index=False)

    print(f"\n--- Priorisierte Auftragsreihenfolge (mu absteigend) -> {out_path} ---")
    for i, (mu_i, sigma_i, m) in enumerate(ranking, start=1):
        docs = f", RAG: {m['matched_rag_docs']}" if m["matched_rag_docs"] else ""
        print(
            f"{i:2d}. {m['order_id']} ({m['customer']}, {m['product_id']}, "
            f"faellig {m['due_date']}, Puffer {m['buffer_days']}d) "
            f"mu={mu_i:.3f} sigma={sigma_i:.3f}{docs}"
        )
        print(f"     Begruendung: {m['begruendung']}")


if __name__ == "__main__":
    main()
