"""
step7-active-learning/preference_export.py - Agentic-PMPlus

TICKET-B09: schreibt aus einer validierten menschlichen Entscheidung (POST /entscheidung,
entschieden_von == "mensch") ein oder mehrere Praeferenzpaare (A ueber B bevorzugt, siehe
step5-pgp/Preference-Gaussian-Process.md Abschnitt 1.2/4: "Praeferenzpaare (A > B)") nach
shared_data/validated_preferences.csv.

Ausdruecklich AUSSERHALB dieses Tickets (siehe
step8-live-test/Produkt-Backlog/TICKET-B09-Praeferenzpaar-Export.md): step5-pgp/main.py
liest diese Datei noch NICHT als zusaetzliches Trainingssignal ein - das ist offene Frage 4
in Architektur-Backend-Frontend-Schnittstelle.md, nicht Teil dieses Moduls.

Nur echte Mensch-Entscheidungen erzeugen Praeferenzpaare, keine automatisch propagierten
(agent-)Eintraege (TICKET-B08) - sonst wuerde ein einzelnes menschliches Urteil ueber die
Propagation mehrfach korreliert als vermeintlich unabhaengiges Trainingssignal in den
Retraining-Satz einfliessen.

Paarableitung pro wahl (Implementierungsentscheidung, keine aus der Literatur
spezifizierte Paar-Elizitierung):
- "eigene_reihenfolge": jedes benachbarte Paar in der vom Planer angegebenen Reihenfolge
  ist ein eindeutiges Praeferenzpaar (orders[i] > orders[i+1]).
- "folgt_pgp"/"folgt_llm": der Planer bestaetigt die jeweilige Rangfolge (rank bzw.
  llm_rank) fuer genau diesen Auftrag - als Paar wird er dem naechst-niedriger
  priorisierten Auftrag derselben Rangfolge gegenuebergestellt (rank+1, sonst rank-1 mit
  vertauschten Rollen). Ohne Nachbarn (z. B. nur ein offener Auftrag im Datensatz) wird
  kein Paar erzeugt.
"""

import csv
import os

VALIDATED_PREFERENCES_PATH = os.environ.get(
    "VALIDATED_PREFERENCES_PATH", os.path.join("shared_data", "validated_preferences.csv")
)

FIELDNAMES = [
    "decision_id", "bevorzugt_order_id", "alternative_order_id",
    "quelle", "entschieden_von", "zeitstempel", "begruendung",
]


def _rank_neighbor_pair(order_id, rank_column, orders_df):
    if rank_column not in orders_df.columns:
        return None
    row = orders_df[orders_df["order_id"] == order_id]
    if row.empty:
        return None
    rank = row.iloc[0][rank_column]

    naechster = orders_df[orders_df[rank_column] == rank + 1]
    if not naechster.empty:
        return order_id, naechster.iloc[0]["order_id"]

    vorheriger = orders_df[orders_df[rank_column] == rank - 1]
    if not vorheriger.empty:
        return vorheriger.iloc[0]["order_id"], order_id

    return None


def derive_pairs(order_id, wahl, eigene_reihenfolge, orders_df):
    """Liefert Liste von (bevorzugt_order_id, alternative_order_id)-Tupeln, siehe
    Modulkopf fuer die Ableitungsregel je wahl."""
    if wahl == "eigene_reihenfolge":
        sequenz = eigene_reihenfolge or []
        return [(sequenz[i], sequenz[i + 1]) for i in range(len(sequenz) - 1)]

    rank_column = "rank" if wahl == "folgt_pgp" else "llm_rank"
    paar = _rank_neighbor_pair(order_id, rank_column, orders_df)
    return [paar] if paar else []


def append_validated_preferences(
    decision_id, order_id, wahl, eigene_reihenfolge, begruendung, zeitstempel,
    orders_df, path=None,
):
    """Haengt ein oder mehrere Praeferenzpaare an - nur fuer echte Mensch-Entscheidungen
    aufrufen (siehe Modulkopf). Gibt die erzeugten Paare zurueck (leer, wenn keine
    ableitbar waren, z. B. mangels Rang-Nachbar)."""
    pairs = derive_pairs(order_id, wahl, eigene_reihenfolge, orders_df)
    if not pairs:
        return []

    path = path or VALIDATED_PREFERENCES_PATH
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        for bevorzugt, alternative in pairs:
            writer.writerow({
                "decision_id": decision_id,
                "bevorzugt_order_id": bevorzugt,
                "alternative_order_id": alternative,
                "quelle": wahl,
                "entschieden_von": "mensch",
                "zeitstempel": zeitstempel,
                "begruendung": begruendung,
            })
    return pairs
