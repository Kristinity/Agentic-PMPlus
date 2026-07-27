# TICKET-F02 – Eskalations-Review (PGP/LLM getrennt)

**Rolle:** frontend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B04](TICKET-B04-GET-Eskalationen.md), [B03](TICKET-B03-RAG-Metadaten-Aufloesung.md)
**MVP:** ✅

## User Story
#3, #5 (`step8-live-test/Userstories.md`)

## Akzeptanzkriterien
- `pgp.begruendung` und `llm.begruendung` in **getrennten UI-Elementen** – nicht
  verhandelbar (siehe `.claude/agents/role/frontend-dev.md`, Leitplanke 1).
- UI-Flow erzwingt: erst beide Einschätzungen sehen, dann erst Wechsel zur
  Entscheidungserfassung möglich.
- Vertrauensstufe pro RAG-Treffer sichtbar (aus B03).

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Manueller Klick-Test: PGP- und LLM-Begründung sind auch bei langem Text nie vermischt/
  zusammengefasst dargestellt.

## Folgetickets
[F03](TICKET-F03-Entscheidungserfassung.md)
