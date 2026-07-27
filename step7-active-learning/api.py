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

TICKET-B09 (step8-live-test/Produkt-Backlog/TICKET-B09-Praeferenzpaar-Export.md):
jede gespeicherte Entscheidung wird zusaetzlich, angereichert mit dem
PGP/LLM-Kontext aus tau_vergleich.csv zum Entscheidungszeitpunkt, an
shared_data/validated_preferences.csv angehaengt. Die step5-pgp/main.py-
seitige Nutzung dieser Datei fuer echtes Retraining ist AUSDRUECKLICH NICHT
Teil dieses Tickets (siehe Ticket-Datei) - hier wird nur exportiert.
"""

import csv
import os

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, model_validator
from typing import Literal, Optional

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
    return {
        "decision_id": decision_id,
        "zeitstempel": gespeichert["zeitstempel"],
        "entschieden_von": gespeichert["entschieden_von"],  # zur Verifikation: immer "mensch"
        # Platzhalter bis TICKET-B08 existiert (Propagation mit Obergrenze N).
        "propagierte_faelle": [],
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
