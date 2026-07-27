"""
step7-active-learning/store.py - Agentic-PMPlus

TICKET-B02: SQLite-Persistenz fuer die menschliche Entscheidungshistorie. CSV ist fuer
gleichzeitige Schreibzugriffe aus einer interaktiven Mehrbenutzer-UI ungeeignet (Race
Conditions bei parallelen POST /entscheidung-Aufrufen) - siehe
Architektur-Backend-Frontend-Schnittstelle.md Abschnitt 2.3. Die Batch-CSVs der Steps 3-6
(orders.csv, pgp_priorisierung.csv, tau_vergleich.csv) bleiben davon unberuehrt reine
Inputs, hier entsteht erstmals in diesem Projekt eine echte kleine Schreib-Persistenz.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.environ.get(
    "ENTSCHEIDUNGEN_DB_PATH", os.path.join("shared_feedback", "entscheidungen.db")
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS entscheidungen (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    wahl TEXT NOT NULL,
    eigene_reihenfolge TEXT,
    begruendung TEXT,
    entschieden_von TEXT NOT NULL,
    zeitstempel TEXT NOT NULL
);
"""


def init_db(db_path=None):
    db_path = db_path or DB_PATH
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(SCHEMA)
    return db_path


@contextmanager
def get_connection(db_path=None):
    db_path = db_path or DB_PATH
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def insert_entscheidung(
    order_id, wahl, eigene_reihenfolge, begruendung, entschieden_von,
    db_path=None, zeitstempel=None,
):
    """entschieden_von wird vom Aufrufer (api.py, TICKET-B05) serverseitig fest auf
    "mensch" gesetzt, nie aus einem rohen Client-Request uebernommen - Systemgrenzen.md
    Teil D (Provenienz-Unterscheidung Mensch- vs. Agent-Feedback)."""
    zeitstempel = zeitstempel or datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO entscheidungen "
            "(order_id, wahl, eigene_reihenfolge, begruendung, entschieden_von, zeitstempel) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (order_id, wahl, eigene_reihenfolge, begruendung, entschieden_von, zeitstempel),
        )
        conn.commit()
        return cur.lastrowid, zeitstempel


def list_entscheidungen(order_id=None, ab=None, bis=None, db_path=None):
    """Chronologische Liste, optional gefiltert nach order_id und/oder Zeitraum (ISO-8601-
    Zeitstempel, lexikographisch sortierbar) - Grundlage fuer TICKET-B06 (GET /verlauf)."""
    query = "SELECT * FROM entscheidungen WHERE 1=1"
    params = []
    if order_id:
        query += " AND order_id = ?"
        params.append(order_id)
    if ab:
        query += " AND zeitstempel >= ?"
        params.append(ab)
    if bis:
        query += " AND zeitstempel <= ?"
        params.append(bis)
    query += " ORDER BY zeitstempel ASC"
    with get_connection(db_path) as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]
