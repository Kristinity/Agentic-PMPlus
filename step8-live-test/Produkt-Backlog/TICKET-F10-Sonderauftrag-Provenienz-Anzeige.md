# TICKET-F10 – Anzeige des Sonderauftrags-Provenienz-Logs

**Status:** Offen
**Rolle:** frontend-dev
**Priorität:** Mittel
**Abhängigkeiten:** [B12](TICKET-B12-Sonderauftrag-Provenienz-Log.md)
**MVP:** nein (Post-MVP)

## User Story
#17 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28)

## Beschreibung
Eigener, kleiner Anzeige-Abschnitt in `step9-upload-interface/app.py` (z. B.
`st.expander("Bisherige Sonderauftrags-Eingaben (Audit)")`), der das Log aus B12
liest und anzeigt. **Bewusst nicht** der bestehende Audit-Trail-Bildschirm aus
TICKET-F05 (`step7-active-learning/frontend/verlauf.html`) – der bezieht sich auf
Planer-**Entscheidungen** (PGP folgen/LLM folgen/eigene Reihenfolge), nicht auf
Auftrags-**Erfassungsdaten**. Eine Vereinheitlichung beider Audit-Ansichten in einen
gemeinsamen Bildschirm wäre ein separates, hier bewusst nicht mit übernommenes
Ticket.

## Akzeptanzkriterien
- Tabelle mit Zeitstempel, `order_id`, `is_sonderauftrag`, `sonderwert_eur`,
  "eintragende Person" (inkl. sichtbarem Platzhalterhinweis bei fehlender
  Authentifizierung, s. B12).
- Leerer Log (noch keine Sonderaufträge erfasst) wird explizit als "Noch keine
  Sonderaufträge erfasst" ausgeschrieben statt eine leere Tabelle kommentarlos zu
  zeigen (Analogie zu TICKET-F02s Umgang mit leerer `matched_rag_docs`-Liste).

## Bezug zu Leitplanken
`step2-limits/Systemgrenzen.md` Teil D – Sichtbarkeit der Provenienz, nicht nur
Erfassung.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners.
- Nach mindestens zwei Log-Einträgen (aus B12-Testdaten) werden beide korrekt
  dargestellt.

## Folgetickets
–
