# TICKET-B06 – `GET /verlauf`

**Rolle:** backend-dev
**Priorität:** Mittel
**Abhängigkeiten:** [B02](TICKET-B02-SQLite-Persistenz.md)
**MVP:** nein (Post-MVP)

## User Story
#7, #9 (`step8-live-test/Userstories.md`)

## Beschreibung
Liefert die chronologische Entscheidungshistorie für den Audit-Trail. Nicht blockierend
für den Kernfluss, aber Voraussetzung für Systemgrenzen-Teil-B.6-Konformität (Governance/
Verantwortlichkeit).

## Akzeptanzkriterien
- Chronologische Liste aller Entscheidungen, filterbar nach Zeitraum/`order_id`.
- Mensch-/Agent-Provenienz pro Eintrag erkennbar.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Mind. drei Testeinträge aus B02 werden korrekt und chronologisch zurückgegeben.

## Folgetickets
[F05](TICKET-F05-Audit-Trail.md)
