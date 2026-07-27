"""
step7-active-learning/api.py - Agentic-PMPlus

FastAPI-Endpunkte fuer Step 7 (Active Learning Loop). Architektur-Entscheidung + volles
Endpunkt-Schema: step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md.

TICKET-B04 (GET /eskalationen): liest die von Step 5/6 erzeugte tau_vergleich.csv. Die
enthaelt bereits alle pgp_priorisierung.csv-Spalten per Merge (siehe
step6-calibration/main.py:load_open_orders) - ein zusaetzliches separates Einlesen von
pgp_priorisierung.csv ist deshalb nicht noetig, es waere nur eine Duplizierung desselben
Merges. Response trennt pgp/llm strikt in zwei Objekte (nicht verhandelbar, s.
Architektur-Doc Abschnitt 3) und ergaenzt ampel_status.
"""

import math
import os

import pandas as pd
from fastapi import FastAPI

from rag_metadata import load_rag_metadata, resolve_matched_docs

TAU_VERGLEICH_PATH = os.environ.get(
    "TAU_VERGLEICH_PATH", os.path.join("shared_data", "tau_vergleich.csv")
)
RAG_DOCUMENTS_DIR = os.environ.get("RAG_DOCUMENTS_DIR", "rag_documents")

app = FastAPI(title="Agentic-PMPlus - step7-active-learning")


def _none_if_nan(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/eskalationen")
def get_eskalationen():
    df = pd.read_csv(TAU_VERGLEICH_PATH)
    metadata_by_id = load_rag_metadata(RAG_DOCUMENTS_DIR)
    # TICKET-B04: solange B07 (tau0/sigma0-Kalibrierung) nicht gelaufen ist, hat
    # tau_vergleich.csv noch keine ampel_status-Spalte -> "unbekannt" statt eines
    # geratenen Werts (AC aus TICKET-B04-GET-Eskalationen.md).
    has_ampel_status = "ampel_status" in df.columns

    eskalationen = []
    for r in df.to_dict(orient="records"):
        eskalationen.append({
            "order_id": r["order_id"],
            "pgp": {
                "rank": int(r["rank"]),
                "mu": _none_if_nan(r.get("mu")),
                "sigma": _none_if_nan(r.get("sigma")),
                "begruendung": _none_if_nan(r.get("pgp_begruendung")),
            },
            "llm": {
                "rank": int(r["llm_rank"]),
                "tau": _none_if_nan(r.get("tau")),
                "begruendung": _none_if_nan(r.get("llm_begruendung")),
                "matched_rag_docs": resolve_matched_docs(r.get("matched_rag_docs"), metadata_by_id),
            },
            "ampel_status": r["ampel_status"] if has_ampel_status else "unbekannt",
        })
    return eskalationen
