"""
generate_produktionsauftraege.py - step3-erp-simulation

Bildet die von main.py generierten orders.csv/bom.csv/routings.csv/calendar.csv/
disruptions.csv auf das Spaltenschema eines echten ERP-Produktionsauftrags-
Exports ab (produktionsauftrag_id, durchlaufzeit_bkt, kundenstatus, ... - siehe
FIELDNAMES), damit die K.S.-Simulationsdaten im selben Format wie ein reales
Referenzbeispiel vorliegen.

Mehrere Zielspalten beschreiben in der Referenz grosse, individuell gefertigte
Werkstuecke (z. B. laenge_mm/traglast_kg/anzahl_werkstuecktraeger fuer
Werkstuecktraeger-Handling). K.S. stellt dagegen kleine gestanzte Verschluesse
in Serie her - dafuer gibt es kein echtes 1:1-Gegenstueck. Solche Spalten sind
unten mit "Proxy:"/"Schaetzung:" kommentiert statt unbegruendete Zufallswerte
als Messwerte auszugeben.
"""

import argparse
import os
import random
import re

import pandas as pd
import yaml

FIELDNAMES = [
    "produktionsauftrag_id", "erstellungsdatum", "auftragsart", "durchlaufzeit_bkt",
    "kundenstatus", "kundenbranche", "anwendungstyp", "anzahl_werkstuecktraeger",
    "material", "oberflaechenbehandlung", "laenge_mm", "breite_mm", "hoehe_mm",
    "traglast_kg", "anzahl_aufnahmepunkte", "anzahl_einzelteile", "anzahl_zukaufteile",
    "anteil_lagerhaltiger_einzelteile", "anzahl_arbeitsgaenge",
    "vorgabezeit_saegen_min", "vorgabezeit_drehen_min", "vorgabezeit_fraesen_min",
    "vorgabezeit_montage_min",
]

# Schaetzung: Hoehe/Stueckgewicht pro Verschlusstyp, nicht im Profil enthalten
# (Kronkorken flach & leicht, Twist-off hoeher & etwas schwerer).
CAP_HEIGHT_MM = {"P-KK": 7, "P-DV": 15}
CAP_WEIGHT_KG = {"P-KK": 0.002, "P-DV": 0.003}

# K.S.s Kunden sind durchweg Brauereien -> keine der 6 realen Branchen passt
# inhaltlich wirklich. Statt jede Zeile auf "Sonstige" zu setzen, wird die
# Kategorie mit den tatsaechlichen Haeufigkeiten aus der Referenzdatei
# (2026_SoSe_ProdMan_Uebung_ML_01_Rohdaten.csv) gezogen, damit die Spalte die
# gleiche Verteilung wie das reale Vorbild hat.
KUNDENBRANCHE_WEIGHTS = {
    "Maschinenbau": 341,
    "Automobilindustrie": 335,
    "Sonstige": 203,
    "Logistiktechnik": 203,
    "Haushaltsgeräte": 138,
    "Medizintechnik": 137,
}


def parse_diameter_mm(product_name):
    m = re.search(r"(\d+)\s*mm", product_name)
    return int(m.group(1)) if m else 26


def load_calendar_lookup(calendar_df):
    calendar_map = dict(zip(calendar_df["date"].dt.date, calendar_df["is_working_day"]))

    def is_working(d):
        if d in calendar_map:
            return bool(calendar_map[d])
        # Fallback ausserhalb des generierten Kalenderbereichs (z. B. Liefer-
        # termine kurz nach Jahresende): Mo-Fr als Arbeitstag annehmen.
        return d.weekday() < 5

    return is_working


def business_days_between(start_date, end_date, is_working):
    d = start_date
    count = 0
    while d < end_date:
        d += pd.Timedelta(days=1)
        if is_working(d):
            count += 1
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--data-dir", required=True, help="Ordner mit orders.csv, bom.csv, routings.csv, calendar.csv, disruptions.csv")
    ap.add_argument("--out", default=None, help="Zieldatei (Default: <data-dir>/produktionsauftraege.csv)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    with open(args.profile, "r", encoding="utf-8") as f:
        profile = yaml.safe_load(f)

    products = {p["id"]: p for p in profile["products"]}
    diameters = {pid: parse_diameter_mm(p["name"]) for pid, p in products.items()}

    orders = pd.read_csv(os.path.join(args.data_dir, "orders.csv"), parse_dates=["order_date", "due_date"])
    bom = pd.read_csv(os.path.join(args.data_dir, "bom.csv"))
    routings = pd.read_csv(os.path.join(args.data_dir, "routings.csv"))
    calendar = pd.read_csv(os.path.join(args.data_dir, "calendar.csv"), parse_dates=["date"])
    disruptions = pd.read_csv(os.path.join(args.data_dir, "disruptions.csv"))

    is_working = load_calendar_lookup(calendar)
    changed_order_ids = set(disruptions.loc[disruptions["type"] == "priority_change", "target"])

    bom_count = bom.groupby("product_id").size().to_dict()
    routing_by_product = {pid: routings[routings["product_id"] == pid] for pid in products}

    rng = random.Random(args.seed)

    rows = []
    for i, order in enumerate(orders.itertuples(index=False), start=1):
        pid = order.product_id
        p_routing = routing_by_product[pid]
        qty = int(order.quantity)

        op_minutes = {}
        for r in p_routing.itertuples(index=False):
            # "Formen"/"Gewindeformen" sind produktspezifische Namen fuer den
            # gleichen Form-/Praegeschritt -> zusammen zaehlen.
            key = "Formen" if r.operation in ("Formen", "Gewindeformen") else r.operation
            op_minutes[key] = op_minutes.get(key, 0) + r.duration_minutes

        # K.S. hat keinen spanenden Saege-/Drehprozess (Stanzen/Praegen statt
        # Zerspanung) -> 0. Stanzen+Formen+Bedrucken als naeherungsweise
        # "fraesen"-Sammelkategorie (Form-/Oberflaechenschritte); die
        # Dichtungseinlage ist die einzige echte Montagetaetigkeit.
        vz_fraesen = (
            op_minutes.get("Stanzen", 0) + op_minutes.get("Formen", 0) + op_minutes.get("Bedrucken", 0)
        ) * qty
        vz_montage = op_minutes.get("Dichtungseinlage einbringen", 0) * qty

        diameter = diameters.get(pid, 26)
        n_bom = bom_count.get(pid, 0)
        n_routing = len(p_routing)

        is_bestandskunde = order.customer == "Becksbrauerei" or rng.random() < 0.8
        kundenbranche = rng.choices(
            list(KUNDENBRANCHE_WEIGHTS.keys()), weights=list(KUNDENBRANCHE_WEIGHTS.values()), k=1
        )[0]

        rows.append({
            "produktionsauftrag_id": f"PA{order.order_date.year}-{i:04d}",
            "erstellungsdatum": order.order_date.date().isoformat(),
            # "Aenderung": Auftrag wurde laut disruptions.csv nachtraeglich
            # umpriorisiert -> naechstliegende reale Kategorie fuer einen
            # veraenderten Auftrag. "Intern" hat in K.S.s Auftragsmodell kein
            # Gegenstueck (jeder Auftrag hat einen externen Kunden) -> entfaellt.
            "auftragsart": "Änderung" if order.order_id in changed_order_ids else "Standard",
            "durchlaufzeit_bkt": business_days_between(order.order_date, order.due_date, is_working),
            "kundenstatus": "Bestandskunde" if is_bestandskunde else "Neukunde",
            # Alle K.S.-Kunden sind Brauereien -> keine reale Kategorie passt
            # inhaltlich; Ziehung nach KUNDENBRANCHE_WEIGHTS s. Modulkopf.
            "kundenbranche": kundenbranche,
            # Alle K.S.-Routings sind Form-/Bearbeitungsschritte (Stanzen,
            # Praegen, Bedrucken) -> "Bearbeitung".
            "anwendungstyp": "Bearbeitung",
            # Proxy: keine Werkstuecktraeger im K.S.-Prozess (Kleinteile im
            # Schuettgut/Karton) -> Bestellmenge als Groessenordnungs-Analogon.
            "anzahl_werkstuecktraeger": qty,
            "material": "Stahl",  # Weissblech-Coil = verzinntes Feinblech (Stahlbasis)
            # Bedrucken/Lackieren (Druckfarbe/Lack-Komponente) am ehesten mit
            # "pulverbeschichtet" vergleichbar (nicht mit Verzinken/Eloxieren).
            "oberflaechenbehandlung": "pulverbeschichtet",
            "laenge_mm": diameter,
            "breite_mm": diameter,  # runder Verschluss: Laenge = Breite = Durchmesser
            "hoehe_mm": CAP_HEIGHT_MM.get(pid, 10),  # Schaetzung, s. Modulkopf
            "traglast_kg": round(qty * CAP_WEIGHT_KG.get(pid, 0.0025), 4),  # Schaetzung, s. Modulkopf
            "anzahl_aufnahmepunkte": n_routing,  # Proxy: Anzahl Arbeitsstationen im Routing
            "anzahl_einzelteile": qty * n_bom,
            "anzahl_zukaufteile": qty * n_bom,  # alle BOM-Komponenten sind zugekauftes Rohmaterial
            "anteil_lagerhaltiger_einzelteile": 1.0,  # alle Komponenten sind in inventory.csv gefuehrt
            "anzahl_arbeitsgaenge": n_routing,
            "vorgabezeit_saegen_min": 0,
            "vorgabezeit_drehen_min": 0,
            "vorgabezeit_fraesen_min": vz_fraesen,
            "vorgabezeit_montage_min": vz_montage,
        })

    df = pd.DataFrame(rows, columns=FIELDNAMES)
    # Nur echte Nachkommawert-Spalten bekommen ein Dezimalkomma (wie im
    # Referenzformat); reine Zaehl-/Zeit-Spalten bleiben ganzzahlig.
    int_cols = [c for c in FIELDNAMES if c not in ("traglast_kg", "anteil_lagerhaltiger_einzelteile")]
    for c in int_cols:
        if c not in ("produktionsauftrag_id", "erstellungsdatum", "auftragsart", "kundenstatus", "kundenbranche", "anwendungstyp", "material", "oberflaechenbehandlung"):
            df[c] = df[c].astype(int)

    out_path = args.out or os.path.join(args.data_dir, "produktionsauftraege.csv")
    df.to_csv(out_path, sep=";", index=False, decimal=",")
    print(f"{len(df)} Produktionsauftraege -> {out_path}")


if __name__ == "__main__":
    main()
