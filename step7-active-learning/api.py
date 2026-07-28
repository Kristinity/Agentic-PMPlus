"""
step7-active-learning/api.py

TICKET-B04 (step8-live-test/Produkt-Backlog/TICKET-B04-GET-Eskalationen.md):
GET /eskalationen - liest tau_vergleich.csv (Step 6, enthaelt PGP+LLM+
Kalibrierung bereits gemergt) und liefert pro Auftrag pgp/llm als zwei
GETRENNTE Objekte (nicht verhandelbar, siehe
Architektur-Backend-Frontend-Schnittstelle.md Abschnitt 3) plus ampel_status
(TICKET-B07) und aufgeloeste RAG-Metadaten (TICKET-B03).

Abweichung vom urspruenglichen Architektur-Sketch: dort stand
matched_rag_docs unter llm - tatsaechlich stammen die Treffer aus der
PGP-Regelanwendung (step5-pgp/main.py, apply_rag_adjustments), nicht vom LLM.
Hier deshalb als eigenes, geteiltes Feld auf oberster Ebene statt faelschlich
dem LLM zugeschrieben.

TICKET-B05 (step8-live-test/Produkt-Backlog/TICKET-B05-POST-Entscheidung.md):
POST /entscheidung - nimmt die menschliche Entscheidung entgegen und
persistiert sie (store.py). entschieden_von ist im Request-Schema absichtlich
GAR NICHT vorhanden (Pydantic ignoriert unbekannte Felder), und store.py
verdrahtet 'mensch' ohnehin fest - der Client kann das serverseitig unter
keinen Umstaenden ueberschreiben. Bei wahl == 'eigene_reihenfolge' (der
einzige Fall, der von PGP UND LLM gleichzeitig abweicht) ist begruendung
Pflicht, sonst lehnt die Validierung mit 422 ab.

TICKET-B06 (step8-live-test/Produkt-Backlog/TICKET-B06-GET-Verlauf.md):
GET /verlauf - chronologischer Audit-Trail aus store.list_entscheidungen().

TICKET-F06 (step8-live-test/Produkt-Backlog/TICKET-F06-Kalibrierungs-Gesundheit.md):
GET /kalibrierung - liest die von step6-calibration/main.py (TICKET-B07,
append_kalibrierung_verlauf) gefuehrte KALIBRIERUNG_VERLAUF_PATH-CSV (ein echter
Kalibrierungslauf pro Zeile: tau0/sigma0/Eskalationsrate/Anteil "truegerische Ruhe")
und liefert Historie + letzten Lauf. Getrennter, technischerer Endpunkt fuer die
Person, die Step 6/7 betreut - NICHT fuer Jens (Produktionsplaner), siehe
Active-Learning-Loop-und-Frontend-Konzept.md Abschnitt 2.3.5.

TICKET-B09 (step8-live-test/Produkt-Backlog/TICKET-B09-Praeferenzpaar-Export.md):
jede gespeicherte Entscheidung wird zusaetzlich, angereichert mit dem
PGP/LLM-Kontext aus tau_vergleich.csv zum Entscheidungszeitpunkt, an
shared_data/validated_preferences.csv angehaengt. Die step5-pgp/main.py-
seitige Nutzung dieser Datei fuer echtes Retraining ist AUSDRUECKLICH NICHT
Teil dieses Tickets (siehe Ticket-Datei) - hier wird nur exportiert.

TICKET-B08 (step8-live-test/Produkt-Backlog/TICKET-B08-Propagation.md):
nach dem Speichern einer menschlichen Entscheidung wird propagation.propagate()
aufgerufen (Aehnlichkeitsmass + harte Obergrenze N, s. dortiger Modulkopf) und
liefert die tatsaechlich propagierten order_ids in propagierte_faelle statt des
bisherigen []-Platzhalters. Propagierte Faelle werden ueber
store.save_propagierte_entscheidung() mit entschieden_von="agent" persistiert
(Provenienz-Pflicht, Systemgrenzen.md Teil D) - NICHT ueber
export_validated_preference(), damit propagierte (agentengenerierte) Faelle nicht
faelschlich als menschliches Trainingssignal fuer Step 5 exportiert werden (s.
Systemgrenzen.md Teil D.1: sonst riskiert das System, sich an eigenen frueheren
Agent-Ausgaben zu "bestaetigen" statt an echtem Experten-Feedback zu lernen).

TICKET-F03 (step8-live-test/Produkt-Backlog/TICKET-F03-Entscheidungserfassung.md):
GET /aehnliche-faelle - NEUER, rein lesender Vorschau-Endpunkt. Architektur-
Konflikt, den dieses Ticket aufloest: POST /entscheidung berechnet die
Propagation UND fuehrt sie im selben Aufruf aus (persistiert sofort ueber
store.py) - es gab bisher keinen Weg, einem Menschen VOR dem verbindlichen
Klick zu zeigen, welche/wie viele Faelle mitbetroffen waeren
(Active-Learning-Loop-und-Frontend-Konzept.md 2.4, erster Punkt: "muss das
Frontend sichtbar machen, wie viele Faelle von einer einzelnen Freigabe
betroffen sind, bevor der Planer bestaetigt" - Leitplanke 2 aus
frontend-dev.md, "Vorschlag != Ausfuehrung"). Loesung: dieser Endpunkt ruft
GENAU dieselbe Funktion (propagation.propagate(), s. dortiger Modulkopf - rein
lesend/side-effect-frei, ruft an keiner Stelle store.save_* auf) mit denselben
Eingaben auf wie _propagate_decision() weiter unten, gibt das Ergebnis aber
NUR zurueck statt es zu persistieren. Das Frontend ruft diesen Endpunkt vor
dem finalen Bestaetigen auf und zeigt die ECHTE (nicht geratene) potenzielle
Liste; erst ein zweiter, separater Klick loest POST /entscheidung aus.
Bewusst NICHT Weg (b) aus der Aufgabenstellung (nur eine im UI als Schaetzung
gekennzeichnete Anzeige ohne echten Vorschau-Call) gewaehlt, weil (a) die vom
Ticket-Wortlaut geforderte "explizite Anzeige, wie viele/welche Faelle
mitbetroffen sind" wörtlicher erfuellt UND technisch genauso einfach ist
(propagation.propagate() existierte bereits side-effect-frei, es fehlte nur
der duenne Lese-Endpunkt).
Race-Bedingung (dokumentiert, nicht geloest): zwischen diesem Aufruf und dem
tatsaechlichen POST /entscheidung koennte theoretisch ein anderer Planer einen
der angezeigten Faelle bereits selbst entscheiden (already_decided_ids
aendert sich). Das macht die Vorschau zu einer Vorschau auf Basis des
aktuellen Standes, keiner Transaktionsgarantie - fuer einen Single-User-
Prototyp ohne Mehrbenutzerbetrieb (siehe Produkt-Backlog "Nicht in diesem
Backlog": Auth/Mehrbenutzer sind explizit offen) eine akzeptable, hier
dokumentierte Vereinfachung.
"""

import csv
import os

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, model_validator
from typing import Literal, Optional

import propagation
import rag_lookup
import store

router = APIRouter()

VALIDATED_PREFERENCES_PATH = os.environ.get(
    "VALIDATED_PREFERENCES_PATH", os.path.join("shared_data", "validated_preferences.csv")
)
PREFERENCE_FIELDS = [
    "order_id", "wahl", "eigene_reihenfolge", "begruendung", "entschieden_von",
    "zeitstempel", "pgp_rank", "pgp_mu", "pgp_sigma", "llm_rank", "llm_tau",
]

TAU_VERGLEICH_PATH = os.environ.get(
    "TAU_VERGLEICH_PATH", os.path.join("shared_data", "tau_vergleich.csv")
)

# TICKET-F06 (step8-live-test/Produkt-Backlog/TICKET-F06-Kalibrierungs-Gesundheit.md):
# von step6-calibration/main.py (TICKET-B07, append_kalibrierung_verlauf) gefuehrte
# Verlaufs-CSV - ein echter Kalibrierungslauf pro Zeile.
KALIBRIERUNG_VERLAUF_PATH = os.environ.get(
    "KALIBRIERUNG_VERLAUF_PATH", os.path.join("shared_data", "kalibrierung_verlauf.csv")
)


def _safe(value):
    """pandas/numpy-Skalare -> native Python-Typen fuer sauberes JSON."""
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


@router.get("/eskalationen")
def get_eskalationen():
    if not os.path.exists(TAU_VERGLEICH_PATH):
        return {
            "eskalationen": [],
            "hinweis": f"{TAU_VERGLEICH_PATH} nicht gefunden - Step 6 noch nicht gelaufen?",
        }

    df = pd.read_csv(TAU_VERGLEICH_PATH)
    metadata = rag_lookup.load_rag_metadata()

    eskalationen = []
    for r in df.itertuples(index=False):
        eskalationen.append({
            "order_id": r.order_id,
            "customer": r.customer,
            "product_id": r.product_id,
            "due_date": r.due_date,
            "pgp": {
                "rank": _safe(r.rank),
                "mu": _safe(r.mu),
                "sigma": _safe(r.sigma),
                "begruendung": _safe(r.pgp_begruendung),
            },
            "llm": {
                "rank": _safe(r.llm_rank),
                "tau": _safe(r.tau),
                "begruendung": _safe(r.llm_begruendung),
            },
            "matched_rag_docs": rag_lookup.resolve_matched_docs(r.matched_rag_docs, metadata),
            # Fallback "unbekannt" nur fuer den Fall einer aelteren tau_vergleich.csv
            # ohne ampel_status-Spalte (vor TICKET-B07) - nie geraten, s. Ticket.
            "ampel_status": _safe(r.ampel_status) if hasattr(r, "ampel_status") else "unbekannt",
        })

    eskalationen.sort(key=lambda e: e["pgp"]["rank"])
    return {"eskalationen": eskalationen}


@router.get("/kalibrierung")
def get_kalibrierung():
    """TICKET-F06: eigener, technischerer Endpunkt fuer die Person, die Step 6/7
    betreut (Active-Learning-Loop-und-Frontend-Konzept.md 2.3.5) - NICHT Teil von
    GET /eskalationen/GET /verlauf, die fuer Jens (Produktionsplaner) gedacht sind.
    Liest KALIBRIERUNG_VERLAUF_PATH (von step6-calibration/main.py gefuehrt, ein
    echter Lauf pro Zeile) und liefert die volle Historie plus "aktuell" (der
    zeitlich letzte Lauf) als bequemen Einzelwert, ohne eine neue Berechnung
    vorzunehmen - jede Zahl stammt 1:1 aus einem tatsaechlich gelaufenen
    Kalibrierungslauf. Fail-safe analog GET /eskalationen: fehlt die Datei (Step 6
    noch nie mit dem F06-Patch gelaufen), wird das als "hinweis" gemeldet, nicht
    als leere/fake Historie kaschiert."""
    if not os.path.exists(KALIBRIERUNG_VERLAUF_PATH):
        return {
            "verlauf": [],
            "aktuell": None,
            "hinweis": (
                f"{KALIBRIERUNG_VERLAUF_PATH} nicht gefunden - Step 6 noch nicht "
                "(mit TICKET-F06-Unterstuetzung) gelaufen?"
            ),
        }

    df = pd.read_csv(KALIBRIERUNG_VERLAUF_PATH)
    verlauf = [
        {col: _safe(getattr(r, col)) for col in df.columns}
        for r in df.itertuples(index=False)
    ]
    # zeitstempel ist ISO-8601 (datetime.now(timezone.utc).isoformat() in
    # step6-calibration/main.py) -> String-Sortierung reicht (lexikographisch
    # korrekt), gleiches Muster wie GET /verlauf (B06).
    verlauf.sort(key=lambda v: v["zeitstempel"])
    return {"verlauf": verlauf, "aktuell": verlauf[-1] if verlauf else None}


class EntscheidungRequest(BaseModel):
    order_id: str
    wahl: Literal["folgt_pgp", "folgt_llm", "eigene_reihenfolge"]
    eigene_reihenfolge: Optional[str] = None
    begruendung: Optional[str] = None
    # Bewusst KEIN entschieden_von-Feld - siehe Modulkopf. Ein evtl. trotzdem im
    # Request-Body mitgeschicktes entschieden_von wird von Pydantic (extra="ignore",
    # Standardverhalten) stillschweigend verworfen, nicht verarbeitet.

    @model_validator(mode="after")
    def begruendung_pflicht_bei_eigener_reihenfolge(self):
        if self.wahl == "eigene_reihenfolge" and not (self.begruendung and self.begruendung.strip()):
            raise ValueError(
                "begruendung ist Pflichtfeld bei wahl='eigene_reihenfolge' "
                "(Abweichung von PGP UND LLM gleichzeitig)"
            )
        return self


def _lookup_pgp_llm_context(order_id):
    """Bestmoegliche PGP/LLM-Werte fuer diesen Auftrag aus der aktuellen
    tau_vergleich.csv - kann fehlen (Auftrag nicht mehr offen, andere
    Laufserie), dann bleiben die Felder leer statt geraten."""
    if not os.path.exists(TAU_VERGLEICH_PATH):
        return {}
    df = pd.read_csv(TAU_VERGLEICH_PATH)
    match = df[df["order_id"] == order_id]
    if match.empty:
        return {}
    row = match.iloc[0]
    return {
        "pgp_rank": _safe(row.get("rank")), "pgp_mu": _safe(row.get("mu")),
        "pgp_sigma": _safe(row.get("sigma")), "llm_rank": _safe(row.get("llm_rank")),
        "llm_tau": _safe(row.get("tau")),
    }


def export_validated_preference(entscheidung):
    """TICKET-B09: haengt die validierte Entscheidung an
    shared_data/validated_preferences.csv an."""
    context = _lookup_pgp_llm_context(entscheidung["order_id"])
    row = {
        "order_id": entscheidung["order_id"],
        "wahl": entscheidung["wahl"],
        "eigene_reihenfolge": entscheidung["eigene_reihenfolge"],
        "begruendung": entscheidung["begruendung"],
        "entschieden_von": entscheidung["entschieden_von"],
        "zeitstempel": entscheidung["zeitstempel"],
        **context,
    }
    os.makedirs(os.path.dirname(VALIDATED_PREFERENCES_PATH) or ".", exist_ok=True)
    file_exists = os.path.exists(VALIDATED_PREFERENCES_PATH)
    with open(VALIDATED_PREFERENCES_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PREFERENCE_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def _compute_propagation_preview(order_id, wahl):
    """Gemeinsame, rein lesende Berechnung fuer GET /aehnliche-faelle (TICKET-F03) UND
    _propagate_decision() (TICKET-B08) - EINE Implementierung, damit Vorschau und
    tatsaechliche Ausfuehrung niemals durch zwei unabhaengig gepflegte Codepfade
    auseinanderlaufen koennen. Ruft ausschliesslich propagation.propagate() (side-effect-
    frei, s. dortiger Modulkopf) auf, schreibt nichts. Gibt (propagiert, uebersprungen)
    zurueck - beide leer, wenn TAU_VERGLEICH_PATH (noch) nicht existiert (B07/B04-
    Abhaengigkeit, kein Rateversuch, fail-safe)."""
    if not os.path.exists(TAU_VERGLEICH_PATH):
        return [], []
    orders_df = pd.read_csv(TAU_VERGLEICH_PATH)
    # bereits entschiedene Faelle duerfen nicht nochmal ueberschrieben werden.
    already_decided_ids = {e["order_id"] for e in store.list_entscheidungen()}
    return propagation.propagate(
        order_id=order_id,
        wahl=wahl,
        orders_df=orders_df,
        already_decided_ids=already_decided_ids,
    )


@router.get("/aehnliche-faelle")
def get_aehnliche_faelle(order_id: str, wahl: Literal["folgt_pgp", "folgt_llm", "eigene_reihenfolge"]):
    """TICKET-F03: rein lesende Vorschau, OHNE etwas zu persistieren - s. Modulkopf fuer
    die Begruendung, warum dieser Endpunkt neu ergaenzt wurde. Wird vom Frontend VOR dem
    finalen Bestaetigen aufgerufen; erst ein zweiter Aufruf (POST /entscheidung) fuehrt
    etwas aus. uebersprungene_faelle sind aehnliche Faelle, die wegen der Obergrenze N
    (propagation.PROPAGATION_LIMIT_N) NICHT automatisch mituebernommen wuerden und
    weiterhin eskaliert blieben - auch das zeigt das Frontend, damit "wie viele/welche
    Faelle mitbetroffen sind" vollstaendig beantwortet ist, nicht nur die Teilmenge, die
    tatsaechlich automatisch mitentschieden wuerde."""
    propagiert, uebersprungen = _compute_propagation_preview(order_id, wahl)
    return {
        "order_id": order_id,
        "wahl": wahl,
        "propagierte_faelle": propagiert,
        "uebersprungene_faelle": uebersprungen,
    }


def _propagate_decision(payload, decision_id):
    """TICKET-B08: findet aehnliche, noch offene/noch nicht entschiedene Faelle (auf
    Basis von TAU_VERGLEICH_PATH, s. propagation.py fuer das Aehnlichkeitsmass) und
    uebernimmt die Entscheidung automatisch fuer bis zu PROPAGATION_LIMIT_N davon. Faelle
    ueber der Obergrenze bleiben unangetastet eskaliert (Systemgrenzen.md Teil D.1, nicht
    optional). Gibt die Liste der tatsaechlich propagierten order_ids zurueck."""
    propagiert, _uebersprungen = _compute_propagation_preview(payload.order_id, payload.wahl)
    for propagierter_order_id in propagiert:
        store.save_propagierte_entscheidung(
            order_id=propagierter_order_id,
            wahl=payload.wahl,
            begruendung=(
                f"Automatisch propagiert (TICKET-B08) von Entscheidung #{decision_id} "
                f"fuer Auftrag {payload.order_id} - Aehnlichkeitsmass: gleiches "
                f"product_id + due_date innerhalb {propagation.PROPAGATION_WINDOW_DAYS} "
                f"Tagen, Obergrenze N={propagation.PROPAGATION_LIMIT_N} (s. propagation.py)."
            ),
        )
    return propagiert


@router.post("/entscheidung")
def post_entscheidung(payload: EntscheidungRequest):
    decision_id = store.save_entscheidung(
        order_id=payload.order_id,
        wahl=payload.wahl,
        begruendung=payload.begruendung,
        eigene_reihenfolge=payload.eigene_reihenfolge,
    )
    gespeichert = store.list_entscheidungen(order_id=payload.order_id)[-1]
    export_validated_preference(gespeichert)
    propagierte_faelle = _propagate_decision(payload, decision_id)
    return {
        "decision_id": decision_id,
        "zeitstempel": gespeichert["zeitstempel"],
        "entschieden_von": gespeichert["entschieden_von"],  # zur Verifikation: immer "mensch"
        # TICKET-B08: echte propagierte order_ids statt des bisherigen []-Platzhalters.
        "propagierte_faelle": propagierte_faelle,
    }


@router.get("/verlauf")
def get_verlauf(order_id: Optional[str] = None, von: Optional[str] = None, bis: Optional[str] = None):
    """TICKET-B06: chronologischer Audit-Trail (store.list_entscheidungen() liefert
    bereits ASC nach zeitstempel sortiert). von/bis sind ISO-8601-Zeitstempel-Praefixe
    (z. B. "2026-07-27") - String-Vergleich reicht, da ISO-8601 lexikographisch
    korrekt sortiert. entschieden_von ist in jedem Eintrag bereits enthalten
    (aktuell immer "mensch", s. store.py) - Mensch-/Agent-Provenienz damit pro
    Eintrag erkennbar, ohne zusaetzliche Logik hier."""
    entscheidungen = store.list_entscheidungen(order_id=order_id)
    if von:
        entscheidungen = [e for e in entscheidungen if e["zeitstempel"] >= von]
    if bis:
        entscheidungen = [e for e in entscheidungen if e["zeitstempel"] <= bis]
    return {"verlauf": entscheidungen}
