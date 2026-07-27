"""
step7-active-learning/rag_metadata.py - Agentic-PMPlus

TICKET-B03 (step8-live-test/Produkt-Backlog/TICKET-B03-RAG-Metadaten-Aufloesung.md):
loest doc_ids aus matched_rag_docs (siehe step5-pgp/main.py, apply_rag_adjustments) zu
{doc_id, title, vertrauensstufe} auf. Liest step4-context-engineering/rag_documents/*.md
direkt (analog step5-pgp/main.py/step6-calibration/main.py: kein neuer Export-Mechanismus
in Step 4 noetig).
"""

import glob
import os

import yaml

RAG_DOCUMENTS_DIR = os.environ.get("RAG_DOCUMENTS_DIR", "rag_documents")


def load_rag_metadata(directory=None):
    """{doc_id: {doc_id, title, vertrauensstufe}} fuer alle *.md ausser _template.md."""
    directory = directory or RAG_DOCUMENTS_DIR
    metadata_by_id = {}
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
        if not doc_id:
            continue
        metadata_by_id[doc_id] = {
            "doc_id": doc_id,
            "title": meta.get("title"),
            "vertrauensstufe": meta.get("vertrauensstufe"),
        }
    return metadata_by_id


def resolve_matched_docs(matched_rag_docs_field, metadata_by_id):
    """matched_rag_docs_field: Semikolon-getrennter String aus pgp_priorisierung.csv/
    tau_vergleich.csv (siehe step5-pgp/main.py: ';'.join(matched_docs)). Leerer String/NaN
    -> leere Liste (kein RAG-Treffer fuer diesen Auftrag). Unbekannte doc_ids (Dokument
    seither entfernt/umbenannt) werden mit title/vertrauensstufe=None statt eines Fehlers
    zurueckgegeben - fehlende Metadaten sind kein Grund, den ganzen Auftrag zu verwerfen."""
    if not matched_rag_docs_field or not isinstance(matched_rag_docs_field, str):
        return []
    resolved = []
    for doc_id in matched_rag_docs_field.split(";"):
        doc_id = doc_id.strip()
        if not doc_id:
            continue
        resolved.append(metadata_by_id.get(doc_id, {
            "doc_id": doc_id, "title": None, "vertrauensstufe": None,
        }))
    return resolved
