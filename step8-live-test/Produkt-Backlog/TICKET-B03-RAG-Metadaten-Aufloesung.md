# TICKET-B03 – RAG-Metadaten-Auflösung (Vertrauensstufe)

**Rolle:** backend-dev
**Priorität:** Mittel
**Abhängigkeiten:** [B01](TICKET-B01-Server-Grundgeruest.md)
**MVP:** ✅

## User Story
`step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md` Abschnitt 2.4
("Vertrauensstufe sichtbar machen"), `step2-limits/Systemgrenzen.md` Teil C.1/C.2.

## Beschreibung
API liest `rag_documents/*.md` direkt (analog zu `step5-pgp/main.py`/
`step6-calibration/main.py`, kein neuer Export-Mechanismus in Step 4 nötig), löst
`matched_rag_docs`-IDs zu `{doc_id, title, vertrauensstufe}` auf.

## Akzeptanzkriterien
- Für alle drei bestehenden RAG-Dokumente (SLA, Prozessanweisung, Störungsbericht)
  korrekt aufgelöst inkl. `vertrauensstufe: intern-verifiziert`.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Unit-Test oder manueller Testlauf mit den drei echten Dokumenten aus
  `step4-context-engineering/rag_documents/`.

## Folgetickets
[B04](TICKET-B04-GET-Eskalationen.md), [F02](TICKET-F02-Eskalations-Review.md)
