# TICKET-B04 – `GET /eskalationen`

**Status:** ✅ Erledigt (2026-07-27)
**Rolle:** backend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B01](TICKET-B01-Server-Grundgeruest.md), [B03](TICKET-B03-RAG-Metadaten-Aufloesung.md) (weich: [B07](TICKET-B07-Kalibrierung.md))
**MVP:** ✅

## User Story
#1, #2, #3, #5 (`step8-live-test/Userstories.md`)

## Beschreibung
Liest `pgp_priorisierung.csv` + `tau_vergleich.csv`, liefert pro Auftrag `pgp`/`llm` **als
zwei getrennte Objekte** (nicht verhandelbar, siehe
`step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md` Abschnitt 3).

## Akzeptanzkriterien
- Response-Felder: `order_id`, `pgp: {rank, mu, sigma, begruendung}`,
  `llm: {rank, tau, begruendung}`, `matched_rag_docs`, `ampel_status`.
  **Korrektur bei Umsetzung:** `matched_rag_docs` stammt tatsächlich aus der
  PGP-Regelanwendung (`step5-pgp/main.py`, `apply_rag_adjustments`), nicht vom LLM -
  daher als eigenes, geteiltes Feld auf oberster Ebene statt fälschlich unter `llm`.
- B07 ist inzwischen fertig, `ampel_status` liefert echte Werte (nicht mehr nur
  `"unbekannt"`); der `"unbekannt"`-Fallback bleibt für ältere `tau_vergleich.csv`
  ohne diese Spalte erhalten.
- `matched_rag_docs` enthält Vertrauensstufe (aus B03). ✅

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Response gegen echte `output_2025`-Daten geprüft. ✅ 20 Aufträge, Ampel-Verteilung
  passend zur Kalibrierung (16 robust / 2 klarer Review-Fall / 2 trügerische Ruhe).
- `pgp`/`llm` sind im JSON nachweislich getrennte Objekte (kein gemeinsamer Score). ✅
  Verifiziert (`e['pgp'] is not e['llm']` sowie getrennte Key-Sets).

## Folgetickets
[F01](TICKET-F01-Warteschlange.md), [F02](TICKET-F02-Eskalations-Review.md)
