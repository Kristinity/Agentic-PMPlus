# TICKET-B02 – SQLite-Persistenz für Entscheidungen

**Rolle:** backend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B01](TICKET-B01-Server-Grundgeruest.md)
**MVP:** ✅

## Beschreibung
Neue, kleine Persistenzschicht für die Entscheidungshistorie. CSV ist für gleichzeitige
Schreibzugriffe aus einer interaktiven UI ungeeignet (siehe
`step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md` Abschnitt 2.3).

## Akzeptanzkriterien
- SQLite-Datei in `shared/feedback/entscheidungen.db` (neuer Ordner).
- Schema mind.: `order_id, wahl, eigene_reihenfolge, begruendung, entschieden_von,
  zeitstempel`.
- CSVs der Steps 3–6 bleiben unangetastet als reine Inputs.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Schreiben + Lesen eines Testeintrags per Skript verifiziert.
- Datei persistiert über Container-Neustart (Volume-Mount geprüft).

## Folgetickets
[B05](TICKET-B05-POST-Entscheidung.md), [B06](TICKET-B06-GET-Verlauf.md),
[B09](TICKET-B09-Praeferenzpaar-Export.md)
