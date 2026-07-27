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
"""

import os

import pandas as pd
from fastapi import APIRouter

import rag_lookup

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
