# TICKET-B09 – Präferenzpaar-Export für Step-5-Retraining

**Status:** ✅ Erledigt (2026-07-27)
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
- Nach einer Testentscheidung enthält die CSV einen neuen, korrekt formatierten Eintrag. ✅
  Getestet gegen echte `output_2025`-Daten: Eintrag enthält den vollen PGP/LLM-Kontext
  (pgp_rank/mu/sigma, llm_rank/tau) aus `tau_vergleich.csv` zum Entscheidungszeitpunkt.
  Randfall geprüft: Entscheidung zu einem in `tau_vergleich.csv` nicht vorhandenen Auftrag
  erzeugt trotzdem einen Eintrag, mit leeren statt geratenen PGP/LLM-Feldern.
