# TICKET-B09 – Präferenzpaar-Export für Step-5-Retraining

**Rolle:** backend-dev
**Priorität:** Mittel
**Abhängigkeiten:** [B02](TICKET-B02-SQLite-Persistenz.md), [B05](TICKET-B05-POST-Entscheidung.md)
**MVP:** nein (Post-MVP)

## Akzeptanzkriterien
- Validierte Entscheidungen landen in `shared_data/validated_preferences.csv`.
- **Ausdrücklich außerhalb dieses Tickets:** die `step5-pgp/main.py`-seitige Erweiterung,
  diese Datei einzulesen (siehe
  `step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md`, offene Frage 4).

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Nach einer Testentscheidung enthält die CSV einen neuen, korrekt formatierten Eintrag.
