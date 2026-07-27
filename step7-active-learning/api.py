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
"""

import os

import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, model_validator
from typing import Literal, Optional

import rag_lookup
import store

router = APIRouter()

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


@router.post("/entscheidung")
def post_entscheidung(payload: EntscheidungRequest):
    decision_id = store.save_entscheidung(
        order_id=payload.order_id,
        wahl=payload.wahl,
        begruendung=payload.begruendung,
        eigene_reihenfolge=payload.eigene_reihenfolge,
    )
    gespeichert = store.list_entscheidungen(order_id=payload.order_id)[-1]
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
