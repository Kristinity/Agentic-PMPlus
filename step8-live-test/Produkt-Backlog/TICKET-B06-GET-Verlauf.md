# TICKET-B06 – `GET /verlauf`

**Status:** ✅ Erledigt (2026-07-27)
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
- Mind. drei Testeinträge aus B02 werden korrekt und chronologisch zurückgegeben. ✅
  3 Einträge (2× O-A, 1× O-B) chronologisch nach Zeitstempel verifiziert; `order_id`-Filter
  liefert korrekt nur die 2 Einträge für O-A.

## Folgetickets
[F05](TICKET-F05-Audit-Trail.md)
