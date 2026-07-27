# TICKET-B04 – `GET /eskalationen`

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
  `llm: {rank, tau, begruendung, matched_rag_docs}`, `ampel_status`.
- Solange B07 nicht fertig: `ampel_status: "unbekannt"`, kein geratener Wert.
- `matched_rag_docs` enthält Vertrauensstufe (aus B03).

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Response gegen echte `output_2025`-Daten geprüft.
- `pgp`/`llm` sind im JSON nachweislich getrennte Objekte (kein gemeinsamer Score).

## Folgetickets
[F01](TICKET-F01-Warteschlange.md), [F02](TICKET-F02-Eskalations-Review.md)
