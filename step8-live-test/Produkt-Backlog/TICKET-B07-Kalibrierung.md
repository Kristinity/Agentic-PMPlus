# TICKET-B07 – τ₀/σ₀-Kalibrierung (Risk-Coverage)

**Rolle:** backend-dev
**Priorität:** Hoch (fachlich Blocker, MVP-Demo nicht blockierend)
**Abhängigkeiten:** keine (nutzt bestehende `tau_vergleich.csv`), unabhängig von
B01–B06 bearbeitbar
**MVP:** nein – für den Demo-Prototyp nicht blockierend, für einen echten Pilotbetrieb
zwingend

## User Story
#2, #6 (`step8-live-test/Userstories.md`)

## Beschreibung
Die eigentliche Kalibrierung, im ursprünglichen Step-6-Scope bewusst ausgeklammert (siehe
`step7-active-learning/Backend-Backlog.md` Abschnitt 2). Ohne dieses Ticket bleibt
`ampel_status` in [B04](TICKET-B04-GET-Eskalationen.md) auf `"unbekannt"`.

## Akzeptanzkriterien
- Getrennte Schwellenwerte τ₀, σ₀ (nicht addiert/gleich gewichtet,
  `Konzept-README.md` Step 6).
- Bootstrap-Hinweis analog `step5-pgp/main.py` dokumentiert (keine vorgetäuschten echten
  Kalibrierungsdaten, solange keine realen Präferenzurteile vorliegen).
- `step2-limits/Systemgrenzen.md` Teil A.3 im Code/Docstring referenziert: Übertragung von
  Risk-Coverage-Prinzipien von LLM- auf GP-Unsicherheit ist **unbelegt**, nicht aus der
  Literatur ableitbar.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- τ₀/σ₀ werden aus einem (Bootstrap-)Validierungsdatensatz berechnet und ausgegeben.
- B04 kann `ampel_status` danach korrekt statt `"unbekannt"` liefern.

## Folgetickets
[B04](TICKET-B04-GET-Eskalationen.md) (Verbesserung), [F06](TICKET-F06-Kalibrierungs-Gesundheit.md)
