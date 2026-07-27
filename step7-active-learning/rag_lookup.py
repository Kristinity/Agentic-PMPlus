"""
step7-active-learning/rag_lookup.py

TICKET-B03 (step8-live-test/Produkt-Backlog/TICKET-B03-RAG-Metadaten-Aufloesung.md):
loest matched_rag_docs-IDs (aus pgp_priorisierung.csv/tau_vergleich.csv,
semikolon-getrennt, z. B. "SLA-BECKS-001") zu {doc_id, title, vertrauensstufe}
auf, damit die API/das Frontend die Vertrauensstufe zeigen kann (siehe
step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md 2.4,
step2-limits/Systemgrenzen.md Teil C.1/C.2).

Liest rag_documents/*.md direkt - gleiches Frontmatter-Parsing wie
step5-pgp/main.py und step6-calibration/main.py, kein neuer Export-
Mechanismus in Step 4 noetig (siehe Backend-Backlog.md Abschnitt 3).
"""

import glob
import os

import yaml

RAG_DOCUMENTS_DIR = os.environ.get("RAG_DOCUMENTS_DIR", "rag_documents")


def load_rag_metadata(directory=RAG_DOCUMENTS_DIR):
    """doc_id -> {doc_id, title, vertrauensstufe}."""
    metadata = {}
    for path in sorted(glob.glob(os.path.join(directory, "*.md"))):
        if os.path.basename(path).startswith("_"):
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        meta = yaml.safe_load(parts[1]) or {}
        doc_id = meta.get("doc_id")
        if doc_id:
            metadata[doc_id] = {
                "doc_id": doc_id,
                "title": meta.get("title"),
                "vertrauensstufe": meta.get("vertrauensstufe"),
            }
    return metadata


def resolve_matched_docs(matched_rag_docs, metadata=None):
    """"SLA-BECKS-001;INC-2025-014" -> [{doc_id, title, vertrauensstufe}, ...].
    Leere/None-Eingabe -> leere Liste. Unbekannte IDs werden mit
    vertrauensstufe=None durchgereicht statt stillschweigend zu verschwinden -
    eine fehlende Vertrauensstufe soll im Frontend auffallen, nicht verborgen
    werden (Fail-safe statt Fail-open, s. o. genannte Dokumente)."""
    if metadata is None:
        metadata = load_rag_metadata()
    if not matched_rag_docs:
        return []
    ids = [d for d in str(matched_rag_docs).split(";") if d]
    return [
        metadata.get(doc_id, {"doc_id": doc_id, "title": None, "vertrauensstufe": None})
        for doc_id in ids
    ]
