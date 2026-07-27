"""
step7-active-learning/propagation.py - Agentic-PMPlus

TICKET-B08: propagiert eine validierte Experten-Entscheidung (POST /entscheidung) auf
aehnliche, noch offene (noch nicht entschiedene) Faelle - Design-Idee aus
Active-Learning-Loop-und-Frontend-Konzept.md Abschnitt 1.3 (analog #17/BAGEL: ein Urteil
wirkt ueber Aehnlichkeit auf mehrere Faelle statt nur auf den einen).

Sicherheitsgrenze (NICHT optional, siehe Architektur-Backend-Frontend-Schnittstelle.md
Abschnitt 2.5 und Systemgrenzen.md Teil D.1): keine der 17 recherchierten Quellen
validiert, dass Propagation aus folgenlosen Forschungskontexten sicher auf reale, teils
irreversible Produktionsentscheidungen uebertragbar ist. Deshalb eine harte, im Code
durchgesetzte Obergrenze N - Faelle darueber bleiben unveraendert eskaliert, werden NICHT
automatisch mitentschieden.

Aehnlichkeitsmass (Implementierungsentscheidung, siehe Architektur-Doc Abschnitt 5, offene
Frage 1: "das ist eine Implementierungsentscheidung fuer propagation.py, nicht Teil dieses
Architektur-Docs"): tau_vergleich.csv enthaelt keine rohen PGP-Feature-Vektoren (nur
rank/mu/sigma als Modell-Output, siehe step5-pgp/main.py) - eine echte
Embedding-Raum-Distanz wie bei #17/BAGEL ist hier deshalb nicht verfuegbar. Als Proxy
dient: gleiches product_id (strukturell aehnlicher Fertigungsweg) UND Naehe im PGP-mu
(das Modell selbst haelt beide Auftraege fuer aehnlich priorisiert). Explizit eine
Heuristik, keine aus der Literatur abgeleitete oder gegen echte Aehnlichkeit validierte
Methode.
"""

import os

PROPAGATION_LIMIT_N = int(os.environ.get("PROPAGATION_LIMIT_N", "5"))

REQUIRED_COLUMNS = {"order_id", "product_id", "mu"}


def find_similar_open_orders(order_id, orders_df, already_decided_ids):
    """orders_df: DataFrame aus tau_vergleich.csv. Liefert die zu order_id aehnlichsten,
    noch nicht entschiedenen offenen Auftraege, aufsteigend nach Aehnlichkeits-Abstand
    sortiert (siehe Modulkopf fuer das Aehnlichkeitsmass). Leere Liste, wenn order_id
    unbekannt ist oder die benoetigten Spalten (noch) fehlen."""
    if not REQUIRED_COLUMNS.issubset(orders_df.columns):
        return []
    if order_id not in orders_df["order_id"].values:
        return []

    source = orders_df[orders_df["order_id"] == order_id].iloc[0]
    candidates = orders_df[
        (orders_df["order_id"] != order_id)
        & (~orders_df["order_id"].isin(already_decided_ids))
        & (orders_df["product_id"] == source["product_id"])
    ].copy()
    if candidates.empty:
        return []

    candidates["mu_abstand"] = (candidates["mu"] - source["mu"]).abs()
    candidates = candidates.sort_values("mu_abstand")
    return candidates["order_id"].tolist()


def propagate(order_id, orders_df, already_decided_ids, limit_n=None):
    """Gibt (propagiert, uebersprungen) zurueck: propagiert = bis zu limit_n order_ids,
    die automatisch dieselbe Entscheidung uebernehmen sollen; uebersprungen = alle
    weiteren aehnlichen Faelle, die wegen der Obergrenze N unveraendert eskaliert bleiben
    (AC aus TICKET-B08-Propagation.md)."""
    limit_n = PROPAGATION_LIMIT_N if limit_n is None else limit_n
    similar = find_similar_open_orders(order_id, orders_df, already_decided_ids)
    return similar[:limit_n], similar[limit_n:]
