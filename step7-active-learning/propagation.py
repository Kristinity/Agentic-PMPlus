"""
step7-active-learning/propagation.py

TICKET-B08 (step8-live-test/Produkt-Backlog/TICKET-B08-Propagation.md):
propagiert eine validierte MENSCHLICHE Entscheidung aus POST /entscheidung automatisch
auf aehnliche, noch offene und noch nicht entschiedene Faelle - die in
Active-Learning-Loop-und-Frontend-Konzept.md Abschnitt 1.3 hergeleitete Design-Idee
(analog #17/BAGEL: ein validiertes Urteil wirkt ueber ein Aehnlichkeitsmass auf mehrere
Faelle, nicht nur auf den einen). Modulstruktur wie in
Architektur-Backend-Frontend-Schnittstelle.md Abschnitt 4 vorgeschlagen.

--- Aehnlichkeitsmass: bewusste Implementierungsentscheidung, KEINE bewiesene Methode ---
Architektur-Doc Abschnitt 5 laesst das Aehnlichkeitsmass ausdruecklich offen ("das ist
eine Implementierungsentscheidung fuer propagation.py, nicht Teil dieses
Architektur-Docs"). tau_vergleich.csv/pgp_priorisierung.csv enthalten keine rohen
PGP-Feature-Vektoren (nur order_id/customer/product_id/due_date/buffer_days plus
mu/sigma als Modell-OUTPUT, siehe step5-pgp/main.py build_features) - eine echte
Embedding-Raum-Distanz wie bei #17/BAGEL ist damit hier nicht verfuegbar.

Als Proxy wird deshalb dasselbe Muster wiederverwendet, das step5-pgp/main.py bereits
fuer "Auftraege, die sich gegenseitig beeinflussen" etabliert hat
(contention_for_orders): GLEICHES product_id (= gleicher Fertigungsweg/dieselben
Arbeitsplaetze laut routing_by_product) UND due_date innerhalb eines Zeitfensters von
PROPAGATION_WINDOW_DAYS Tagen (Default 7, identisch zum window_days-Default dort). Das
ist eine dokumentierte Heuristik ("strukturell verwandter Auftrag"), keine gelernte oder
gegen echte Aehnlichkeit validierte Distanz - austauschbar, sobald echte Nutzungsdaten
vorliegen (siehe Systemgrenzen.md Teil A.1: das Gesamtsystem ist eine unvalidierte
Neukombination, jede Schnittstelle eine Design-Annahme des Projekts).

Kandidaten werden nach zeitlicher Naehe zum due_date des Quellauftrags sortiert (naeher
zuerst) - bei mehr als N aehnlichen Faellen (s.u.) werden so die zeitlich naechstliegenden
zuerst automatisch mit-entschieden, der Rest bleibt eskaliert.

--- Sicherheitsgrenze: harte Obergrenze N (NICHT optional) ---
Systemgrenzen.md Teil D.1 / Architektur-Doc Abschnitt 2.5: keine der 17
Benchmark-Quellen validiert, dass Propagations-/Explorationslogik aus folgenlosen
Forschungskontexten sicher auf einen Kontext mit realen, teils irreversiblen
Produktionsentscheidungen uebertragbar ist. Deshalb hier eine feste, im Code
durchgesetzte Obergrenze N (Env-Var PROPAGATION_LIMIT_N, Standardwert 5) - alles
darueber hinaus bleibt UNVERAENDERT eskaliert, wird nicht automatisch uebernommen.

--- Was NICHT propagiert wird (zusaetzliche, bewusste Einschraenkung) ---
Nur wahl in {"folgt_pgp", "folgt_llm"} wird propagiert. "eigene_reihenfolge" enthaelt
eine freitextliche, fallspezifische Reihenfolge des Planers fuer GENAU diesen einen
Auftrag - eine automatische Uebertragung dieses Freitexts auf einen anderen Auftrag waere
keine Anwendung derselben Entscheidungslogik, sondern eine geratene Uebertragung von
Inhalt, der nie fuer den Zielauftrag formuliert wurde. Diese Faelle bleiben deshalb immer
eskaliert (siehe Aufruf in api.py).
"""

import os

import pandas as pd

# Obergrenze N: Sicherheitsgrenze aus Systemgrenzen.md Teil D.1, siehe Modulkopf.
# Startwert 5 ist eine Projektentscheidung (Architektur-Doc Abschnitt 5, offene Frage 2),
# nicht aus der Literatur ableitbar - deshalb per Env-Var ueberschreibbar, aber mit
# sicherem, kleinem Default.
PROPAGATION_LIMIT_N = int(os.environ.get("PROPAGATION_LIMIT_N", "5"))

# Zeitfenster fuer das Aehnlichkeitsmass, identisch zum Default in
# step5-pgp/main.py:contention_for_orders (window_days=7).
PROPAGATION_WINDOW_DAYS = int(os.environ.get("PROPAGATION_WINDOW_DAYS", "7"))

# wahl-Werte, die ueberhaupt propagiert werden duerfen, s. Modulkopf.
PROPAGIERBARE_WAHL = {"folgt_pgp", "folgt_llm"}

REQUIRED_COLUMNS = {"order_id", "product_id", "due_date"}


def find_similar_open_orders(order_id, orders_df, already_decided_ids, window_days=None):
    """orders_df: DataFrame mit mindestens order_id/product_id/due_date (z. B. direkt
    aus tau_vergleich.csv oder pgp_priorisierung.csv gelesen). Liefert die zum
    Referenzauftrag aehnlichen, noch offenen (nicht in already_decided_ids enthaltenen)
    Auftraege - aufsteigend nach zeitlichem Abstand des due_date sortiert (s. Modulkopf).
    Leere Liste bei unbekannter order_id oder fehlenden Spalten (kein Rateversuch, kein
    Fehler - fail-safe statt fail-open, konsistent mit rag_lookup.resolve_matched_docs)."""
    window_days = PROPAGATION_WINDOW_DAYS if window_days is None else window_days
    if not REQUIRED_COLUMNS.issubset(orders_df.columns):
        return []
    if order_id not in orders_df["order_id"].values:
        return []

    df = orders_df.copy()
    df["due_date"] = pd.to_datetime(df["due_date"])
    source = df[df["order_id"] == order_id].iloc[0]

    candidates = df[
        (df["order_id"] != order_id)
        & (~df["order_id"].isin(already_decided_ids))
        & (df["product_id"] == source["product_id"])
    ].copy()
    if candidates.empty:
        return []

    candidates["tage_abstand"] = (candidates["due_date"] - source["due_date"]).dt.days.abs()
    candidates = candidates[candidates["tage_abstand"] <= window_days]
    if candidates.empty:
        return []

    candidates = candidates.sort_values("tage_abstand", kind="stable")
    return candidates["order_id"].tolist()


def propagate(order_id, wahl, orders_df, already_decided_ids, limit_n=None, window_days=None):
    """Gibt (propagiert, uebersprungen) zurueck.

    propagiert: bis zu limit_n order_ids (Sicherheitsgrenze N, s. Modulkopf), die
    automatisch dieselbe Entscheidung (wahl) uebernehmen sollen.
    uebersprungen: alle weiteren aehnlichen, noch offenen Faelle, die wegen der
    Obergrenze N unveraendert eskaliert bleiben (Akzeptanzkriterium aus TICKET-B08).

    Bei wahl == "eigene_reihenfolge" wird grundsaetzlich NICHT propagiert (s.
    Modulkopf) - beide Rueckgabelisten sind dann leer, unabhaengig davon, wie viele
    aehnliche Faelle existieren wuerden (die bleiben schlicht wie jeder andere noch
    nicht entschiedene Fall regulaer eskaliert, ohne hier extra aufgefuehrt zu werden)."""
    if wahl not in PROPAGIERBARE_WAHL:
        return [], []

    limit_n = PROPAGATION_LIMIT_N if limit_n is None else limit_n
    similar = find_similar_open_orders(order_id, orders_df, already_decided_ids, window_days)
    return similar[:limit_n], similar[limit_n:]
