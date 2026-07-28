# TICKET-B14 – `GET /eskalationen` um Sonderauftrags-Feld erweitern

**Status:** Offen
**Rolle:** backend-dev
**Priorität:** Mittel
**Abhängigkeiten:** [B11](TICKET-B11-Sonderwert-PGP-Feature.md) (lose: [B04](TICKET-B04-GET-Eskalationen.md), bereits erledigt)
**MVP:** nein (Post-MVP)

## User Story
#16 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28)

## Beschreibung
`step5-pgp/main.py` schreibt `is_sonderauftrag`/`sonderwert_eur` bereits in
`pgp_priorisierung.csv` (B11). Über den bestehenden Merge in
`step6-calibration/main.py:load_open_orders` (`pgp.merge(orders[["order_id",
"order_date", "quantity"]], on="order_id", how="left")`, Zeile 147/148) werden nur
`order_date`/`quantity` zusätzlich aus `orders.csv` geholt – alle
`pgp_priorisierung.csv`-Spalten (inkl. der neuen aus B11) bleiben aber ohnehin in
`open_orders`/`result` erhalten und landen unverändert in `tau_vergleich.csv`. Es
fehlt nur die explizite Aufnahme in das von `api.py` (`GET /eskalationen`,
TICKET-B04) manuell zusammengestellte Response-Schema (`order_id`, `pgp{...}`,
`llm{...}`, `matched_rag_docs`, `ampel_status`).

## Akzeptanzkriterien
- `GET /eskalationen`-Response bekommt ein neues, oberstes Feld (z. B.
  `sonderauftrag: {ist_sonderauftrag: bool, wert_eur: float|null}`), analog zur
  bestehenden Struktur (`pgp`/`llm` als eigene Objekte).
- Fehlt die Spalte in einer älteren `tau_vergleich.csv` (vor B11 erzeugt), fällt
  der Wert fail-safe auf `{ist_sonderauftrag: false, wert_eur: null}` zurück,
  nicht auf einen geratenen Wert (analog zum bestehenden
  `ampel_status: "unbekannt"`-Fallback-Muster aus B04/F01).

## Bezug zu Leitplanken
Fail-safe-Prinzip (`.claude/agents/role/frontend-dev.md`, Leitplanke 5 /
Systemgrenzen Teil D.2) – hier auf ein Backend-Response-Feld übertragen.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners.
- Response gegen echte, mit B11 regenerierte `tau_vergleich.csv` geprüft; Fallback
  gegen eine ältere `tau_vergleich.csv` ohne die neue Spalte separat geprüft.

## Folgetickets
[F12](TICKET-F12-Warteschlange-Sonderauftrag-Badge.md)
