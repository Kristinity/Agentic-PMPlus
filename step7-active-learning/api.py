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

import json
import math
import os
from typing import List, Literal, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from preference_export import append_validated_preferences
from propagation import propagate
from rag_metadata import load_rag_metadata, resolve_matched_docs
from store import insert_entscheidung, list_entscheidungen

TAU_VERGLEICH_PATH = os.environ.get(
    "TAU_VERGLEICH_PATH", os.path.join("shared_data", "tau_vergleich.csv")
)
RAG_DOCUMENTS_DIR = os.environ.get("RAG_DOCUMENTS_DIR", "rag_documents")
KALIBRIERUNG_SCHWELLENWERTE_PATH = os.environ.get(
    "KALIBRIERUNG_SCHWELLENWERTE_PATH",
    os.path.join("shared_data", "kalibrierung_schwellenwerte.json"),
)
KALIBRIERUNG_RISK_COVERAGE_PATH = os.environ.get(
    "KALIBRIERUNG_RISK_COVERAGE_PATH",
    os.path.join("shared_data", "kalibrierung_risk_coverage.csv"),
)

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

    orders_df = pd.read_csv(TAU_VERGLEICH_PATH)

    # TICKET-B09: nur die echte Mensch-Entscheidung selbst wird als Praeferenzpaar
    # exportiert - propagierte agent-Eintraege (unten) NICHT, sonst korreliert ein
    # einzelnes menschliches Urteil mehrfach im Retraining-Datensatz (siehe
    # preference_export.py Modulkopf).
    append_validated_preferences(
        decision_id=decision_id,
        order_id=request.order_id,
        wahl=request.wahl,
        eigene_reihenfolge=request.eigene_reihenfolge,
        begruendung=request.begruendung,
        zeitstempel=zeitstempel,
        orders_df=orders_df,
    )

    # TICKET-B08: auf aehnliche, noch nicht entschiedene Faelle propagieren - gedrosselt
    # durch eine harte Obergrenze N (Systemgrenzen.md Teil D.1, nicht optional). Faelle
    # ueber N bleiben bewusst unangetastet eskaliert statt automatisch uebernommen zu
    # werden.
    already_decided_ids = {e["order_id"] for e in list_entscheidungen()}
    propagierte_faelle, _uebersprungen = propagate(
        order_id=request.order_id,
        orders_df=orders_df,
        already_decided_ids=already_decided_ids,
    )
    for propagierter_order_id in propagierte_faelle:
        insert_entscheidung(
            order_id=propagierter_order_id,
            wahl=request.wahl,
            eigene_reihenfolge=None,
            begruendung=(
                f"Automatisch propagiert von Entscheidung {decision_id} "
                f"(Auftrag {request.order_id}) - Aehnlichkeitsheuristik: gleiches "
                "product_id + naechster PGP-mu, siehe propagation.py."
            ),
            entschieden_von="agent",
        )

    return {
        "decision_id": decision_id,
        "zeitstempel": zeitstempel,
        "propagierte_faelle": propagierte_faelle,
    }


@app.get("/verlauf")
def get_verlauf(
    order_id: Optional[str] = None,
    ab: Optional[str] = None,
    bis: Optional[str] = None,
):
    """TICKET-B06. Audit-Trail: chronologische Liste aller ueber POST /entscheidung
    erfassten Entscheidungen, optional gefiltert nach order_id und/oder Zeitraum (ab/bis
    als ISO-8601-Zeitstempel, siehe store.list_entscheidungen). entschieden_von macht die
    Mensch-/Agent-Provenienz pro Eintrag erkennbar (Systemgrenzen.md Teil B.6)."""
    return list_entscheidungen(order_id=order_id, ab=ab, bis=bis)


@app.get("/kalibrierung")
def get_kalibrierung():
    """TICKET-F06 (Kalibrierungs-Gesundheit, optional/Post-MVP): aktuelle tau0/sigma0-
    Schwellenwerte + diagnostische Risk-Coverage-Kurven aus
    step6-calibration/kalibrierung.py (TICKET-B07), plus die aktuelle Eskalationsrate und
    den Anteil "truegerische Ruhe" (Gelb) aus der laufenden tau_vergleich.csv.

    Liefert nur eine Momentaufnahme, KEINE "Eskalationsrate ueber Zeit" - dafuer muesste
    jeder Kalibrierungslauf historisiert werden, was kalibrierung.py aktuell nicht tut
    (es ueberschreibt dieselbe Datei). Diese Einschraenkung ist bewusst nicht verschwiegen,
    sondern hier dokumentiert, statt eine erfundene Zeitreihe auszugeben."""
    if not os.path.exists(KALIBRIERUNG_SCHWELLENWERTE_PATH):
        raise HTTPException(
            status_code=404,
            detail="Noch keine Kalibrierung gelaufen (step6-calibration/kalibrierung.py, TICKET-B07).",
        )

    with open(KALIBRIERUNG_SCHWELLENWERTE_PATH, encoding="utf-8") as f:
        schwellenwerte = json.load(f)

    risk_coverage = []
    if os.path.exists(KALIBRIERUNG_RISK_COVERAGE_PATH):
        risk_coverage = pd.read_csv(KALIBRIERUNG_RISK_COVERAGE_PATH).to_dict(orient="records")

    eskalationsrate = None
    truegerische_ruhe_anteil = None
    if os.path.exists(TAU_VERGLEICH_PATH):
        df = pd.read_csv(TAU_VERGLEICH_PATH)
        if "ampel_status" in df.columns and len(df) > 0:
            eskalationsrate = float(df["ampel_status"].isin(["\U0001F534", "\U0001F7E1"]).mean())
            truegerische_ruhe_anteil = float((df["ampel_status"] == "\U0001F7E1").mean())

    return {
        **schwellenwerte,
        "risk_coverage": risk_coverage,
        "eskalationsrate": eskalationsrate,
        "truegerische_ruhe_anteil": truegerische_ruhe_anteil,
    }
