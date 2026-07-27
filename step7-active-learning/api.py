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
from typing import List, Literal, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag_metadata import load_rag_metadata, resolve_matched_docs
from store import insert_entscheidung

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


class EntscheidungRequest(BaseModel):
    order_id: str
    wahl: Literal["folgt_pgp", "folgt_llm", "eigene_reihenfolge"]
    eigene_reihenfolge: Optional[List[str]] = None
    begruendung: Optional[str] = None
    # Wird vom Handler unten IGNORIERT, egal was der Client schickt (TICKET-B05 AC) -
    # Feld existiert hier nur, damit ein Request, der es versehentlich mitschickt, nicht
    # an der Pydantic-Validierung scheitert.
    entschieden_von: Optional[str] = None


@app.post("/entscheidung")
def post_entscheidung(request: EntscheidungRequest):
    """TICKET-B05. entschieden_von ist serverseitig fest auf "mensch" gesetzt - nie vom
    Client ueberschreibbar (Systemgrenzen.md Teil D, Provenienz Mensch- vs. Agent-Feedback).
    Bei Abweichung von PGP UND LLM (wahl == "eigene_reihenfolge") ist begruendung Pflicht."""
    if request.wahl == "eigene_reihenfolge" and not request.begruendung:
        raise HTTPException(
            status_code=400,
            detail="begruendung ist Pflicht bei Abweichung von PGP und LLM (eigene_reihenfolge).",
        )

    eigene_reihenfolge_serialisiert = (
        ";".join(request.eigene_reihenfolge) if request.eigene_reihenfolge else None
    )
    decision_id, zeitstempel = insert_entscheidung(
        order_id=request.order_id,
        wahl=request.wahl,
        eigene_reihenfolge=eigene_reihenfolge_serialisiert,
        begruendung=request.begruendung,
        entschieden_von="mensch",
    )
    return {
        "decision_id": decision_id,
        "zeitstempel": zeitstempel,
        # Platzhalter bis TICKET-B08 (Propagation) existiert - Architektur-Doc Abschnitt 2.5.
        "propagierte_faelle": [],
    }
