# TICKET-B05 – `POST /entscheidung`

**Status:** ✅ Erledigt (2026-07-27)
**Rolle:** backend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B01](TICKET-B01-Server-Grundgeruest.md), [B02](TICKET-B02-SQLite-Persistenz.md)
**MVP:** ✅

## User Story
#1, #5 (`step8-live-test/Userstories.md`); `step2-limits/Systemgrenzen.md` Teil D
(Provenienz).

## Beschreibung
Nimmt die menschliche Entscheidung entgegen und persistiert sie (siehe B02).

## Akzeptanzkriterien
- `entschieden_von` serverseitig fest auf `"mensch"`, vom Client nicht überschreibbar.
- Bei Abweichung von PGP **und** LLM: `begruendung` ist Pflichtfeld, Request ohne dieses
  Feld wird mit Fehler (4xx) abgelehnt.
- Response enthält `propagierte_faelle` (Platzhalter `[]`, bis
  [B08](TICKET-B08-Propagation.md) existiert).

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Testaufruf mit fehlender Begründung wird nachweislich abgelehnt. ✅ HTTP 422 bei
  `wahl=eigene_reihenfolge` ohne `begruendung`; kein DB-Eintrag erzeugt.
- Testaufruf mit `entschieden_von: "agent"` im Body wird nachweislich ignoriert/
  überschrieben. ✅ Sowohl Response als auch direkter DB-Query zeigen `"mensch"`.
- Zusätzlich verifiziert: `folgt_pgp`/`folgt_llm` ohne Begründung -> 200 (nicht
  fälschlich als Pflichtfeld behandelt), `eigene_reihenfolge` mit Begründung -> 200.

## Folgetickets
[B08](TICKET-B08-Propagation.md), [B09](TICKET-B09-Praeferenzpaar-Export.md),
[F03](TICKET-F03-Entscheidungserfassung.md)
