"""
step7-active-learning/store.py

TICKET-B02 (step8-live-test/Produkt-Backlog/TICKET-B02-SQLite-Persistenz.md):
SQLite-Persistenz fuer die Entscheidungshistorie aus Step 7. CSV ist fuer
gleichzeitige Schreibzugriffe aus einer interaktiven UI ungeeignet (Race
Conditions), siehe
step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md
Abschnitt 2.3. Die CSVs der Steps 3-6 (orders.csv, pgp_priorisierung.csv,
tau_vergleich.csv, ...) bleiben unveraendert reine Inputs - diese Datenbank
ist ausschliesslich fuer die in Step 7 neu entstehenden Entscheidungen.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

# Gemountet als eigenes Shared-Verzeichnis (docker-compose.yml:
# ./shared/feedback:/app/shared_feedback), getrennt von shared_data (Steps 3-6
# Batch-Outputs), damit die Entscheidungs-DB Container-Neustarts uebersteht.
DB_PATH = os.environ.get("DB_PATH", os.path.join("shared_feedback", "entscheidungen.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS entscheidungen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    wahl TEXT NOT NULL CHECK (wahl IN ('folgt_pgp', 'folgt_llm', 'eigene_reihenfolge')),
    eigene_reihenfolge TEXT,
    begruendung TEXT,
    entschieden_von TEXT NOT NULL DEFAULT 'mensch',
    zeitstempel TEXT NOT NULL
);
"""


def init_db(db_path=DB_PATH):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(SCHEMA)
    return db_path


@contextmanager
def get_connection(db_path=DB_PATH):
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def save_entscheidung(order_id, wahl, begruendung=None, eigene_reihenfolge=None, db_path=DB_PATH):
    """entschieden_von ist HIER fest auf 'mensch' verdrahtet (nicht als Parameter
    entgegengenommen) - Provenienz-Erzwingung bereits auf Persistenz-Ebene, nicht
    erst im API-Layer von TICKET-B05. Konsistent mit Systemgrenzen.md Teil D."""
    zeitstempel = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO entscheidungen "
            "(order_id, wahl, eigene_reihenfolge, begruendung, entschieden_von, zeitstempel) "
            "VALUES (?, ?, ?, ?, 'mensch', ?)",
            (order_id, wahl, eigene_reihenfolge, begruendung, zeitstempel),
        )
        conn.commit()
        return cur.lastrowid


def list_entscheidungen(order_id=None, db_path=DB_PATH):
    query = "SELECT * FROM entscheidungen"
    params = ()
    if order_id:
        query += " WHERE order_id = ?"
        params = (order_id,)
    query += " ORDER BY zeitstempel ASC"
    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
