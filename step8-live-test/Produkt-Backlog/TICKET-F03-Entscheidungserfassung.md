# TICKET-F03 – Entscheidungserfassung mit erzwungener Provenienz

**Rolle:** frontend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B05](TICKET-B05-POST-Entscheidung.md), [F02](TICKET-F02-Eskalations-Review.md) (lose: [B08](TICKET-B08-Propagation.md))
**MVP:** ✅

## User Story
#1, #5 (`step8-live-test/Userstories.md`); `step2-limits/Systemgrenzen.md` Teil D

## Akzeptanzkriterien
- Drei Wahlmöglichkeiten: PGP folgen / LLM folgen / eigene Reihenfolge.
- Begründungsfeld im UI als Pflichtfeld markiert, blockiert Absenden bei Abweichung + leer.
- Falls `propagierte_faelle` nicht leer: vor dem finalen Bestätigen explizit anzeigen, wie
  viele/welche Fälle mitbetroffen sind.
- Kein Button, der wie eine irreversible Aktion aussieht, ohne separaten
  Bestätigungsschritt.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Testlauf ohne Backend-Propagation (B08 noch offen) zeigt korrekt "keine weiteren Fälle
  betroffen".
- Nach B08 zeigt derselbe Bildschirm die echte Liste.
