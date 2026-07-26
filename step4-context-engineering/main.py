"""
step4-context-engineering - Agentic-PMPlus

Kombiniert die strukturierten ERP-Daten aus Step 3 (orders.csv, routings.csv)
mit den kuratierten RAG-Dokumenten aus rag_documents/ zu einem Kontext-Bundle
pro Auftrag. Begruendung des Ansatzes: gute-RAGs.md.

- KG-Seite (Metadaten-Filter): kunde/produkt/work_center aus dem Frontmatter
  jedes RAG-Dokuments grenzen die Treffermenge auf den jeweiligen Auftrag ein.
- Vector-Seite (Embedding-Aehnlichkeit): sentence-transformers/chromadb finden
  innerhalb der gefilterten Menge die inhaltlich passendsten Chunks.
- Vertrauensfilter: nur "intern-verifiziert" markierte Dokumente werden
  ungefiltert indexiert (siehe gute-RAGs.md Abschnitt 4 / Systemgrenze C.1,
  Prompt-Injection ueber RAG-Kontext). "extern-ungeprueft" wird separat
  gemeldet statt stillschweigend in den Kontext zu gelangen.
"""

import glob
import os
from datetime import date

import chromadb
import frontmatter
import pandas as pd
from chromadb.utils import embedding_functions

RAG_DOCUMENTS_DIR = os.environ.get(
    "RAG_DOCUMENTS_DIR", os.path.join(os.path.dirname(__file__), "rag_documents")
)
# Relativ zu WORKDIR /app im Container -> entspricht dem gemounteten
# ./shared/data:/app/shared_data aus docker-compose.yml (dort legt main.py
# aus step3-erp-simulation seine CSVs standardmaessig ab).
ERP_DATA_DIR = os.environ.get("ERP_DATA_DIR", "shared_data")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
TOP_K = int(os.environ.get("RAG_TOP_K", "3"))
SAMPLE_ORDERS = int(os.environ.get("SAMPLE_ORDERS", "3"))


def load_rag_documents(directory):
    """Laedt alle *.md ausser _template.md als (metadata, body)-Tupel."""
    docs = []
    for path in sorted(glob.glob(os.path.join(directory, "*.md"))):
        if os.path.basename(path).startswith("_"):
            continue
        post = frontmatter.load(path)
        docs.append((post.metadata, post.content.strip()))
    return docs


def is_valid(meta, as_of):
    gueltig_ab = meta.get("gueltig_ab")
    gueltig_bis = meta.get("gueltig_bis")
    if gueltig_ab and date.fromisoformat(str(gueltig_ab)) > as_of:
        return False
    if gueltig_bis and date.fromisoformat(str(gueltig_bis)) < as_of:
        return False
    return True


def build_index(docs, as_of):
    trusted, skipped = [], []
    for meta, body in docs:
        if not is_valid(meta, as_of):
            skipped.append((meta.get("doc_id", "?"), "abgelaufen/noch nicht gueltig"))
            continue
        if meta.get("vertrauensstufe") == "intern-verifiziert":
            trusted.append((meta, body))
        else:
            skipped.append((meta.get("doc_id", "?"), "vertrauensstufe != intern-verifiziert"))

    client = chromadb.EphemeralClient()
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    collection = client.get_or_create_collection("rag_documents", embedding_function=ef)
    if trusted:
        collection.add(
            ids=[m["doc_id"] for m, _ in trusted],
            documents=[f"{m['title']}\n\n{body}" for m, body in trusted],
            metadatas=[
                {
                    "doc_type": m.get("doc_type") or "",
                    "kunde": m.get("kunde") or "",
                    "produkt": m.get("produkt") or "",
                    "work_center": m.get("work_center") or "",
                }
                for m, _ in trusted
            ],
        )
    return collection, skipped


def retrieve(collection, query, kunde=None, produkt=None, work_center=None, k=TOP_K):
    """Holt breiter als k (Vector-Seite), filtert danach in Python auf
    passende/kundenuebergreifende Metadaten (KG-Seite) - vermeidet
    versionsabhaengige chromadb where-Filter-Syntax fuer diesen Prototyp."""
    n = min(max(k * 3, k), max(collection.count(), 1))
    if n == 0:
        return []
    result = collection.query(query_texts=[query], n_results=n)
    hits = []
    for doc, meta, dist in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        if kunde and meta["kunde"] and meta["kunde"] != kunde:
            continue
        if produkt and meta["produkt"] and meta["produkt"] != produkt:
            continue
        if work_center and meta["work_center"] and meta["work_center"] != work_center:
            continue
        hits.append({"text": doc, "metadata": meta, "distance": dist})
        if len(hits) >= k:
            break
    return hits


def assemble_context(order, work_centers, collection):
    query = (
        f"Auftrag fuer Kunde {order['customer']}, Produkt {order['product_id']}, "
        f"Prioritaet {order['priority']}, faellig {order['due_date']}"
    )
    hits = retrieve(
        collection,
        query,
        kunde=order["customer"],
        produkt=order["product_id"],
        work_center=work_centers[0] if work_centers else None,
    )
    return {"erp_facts": order, "work_centers": work_centers, "retrieved_context": hits}


def main():
    as_of = date.today()
    docs = load_rag_documents(RAG_DOCUMENTS_DIR)
    collection, skipped = build_index(docs, as_of)

    print("=== step4-context-engineering ===")
    print(f"{collection.count()} kuratierte RAG-Dokumente indexiert (Stand {as_of.isoformat()})")
    for doc_id, reason in skipped:
        print(f"  nicht indexiert: {doc_id} ({reason})")

    orders_path = os.path.join(ERP_DATA_DIR, "orders.csv")
    routings_path = os.path.join(ERP_DATA_DIR, "routings.csv")
    if not os.path.exists(orders_path):
        print(f"Keine ERP-Daten unter {ERP_DATA_DIR} gefunden - nur RAG-Index aufgebaut.")
        return

    orders = pd.read_csv(orders_path)
    routings = pd.read_csv(routings_path)

    for order in orders.head(SAMPLE_ORDERS).to_dict(orient="records"):
        work_centers = routings.loc[
            routings["product_id"] == order["product_id"], "work_center"
        ].tolist()
        context = assemble_context(order, work_centers, collection)

        print(f"\n--- Kontext-Bundle fuer {order['order_id']} ---")
        print(
            f"Kunde: {order['customer']}, Produkt: {order['product_id']}, "
            f"Faellig: {order['due_date']}, Prioritaet: {order['priority']}, "
            f"Work Center: {work_centers}"
        )
        if not context["retrieved_context"]:
            print("  keine passenden RAG-Treffer")
        for hit in context["retrieved_context"]:
            first_line = hit["text"].splitlines()[0]
            print(
                f"  RAG-Treffer [{hit['metadata']['doc_type']}] "
                f"(Distanz {hit['distance']:.3f}): {first_line}"
            )


if __name__ == "__main__":
    main()
