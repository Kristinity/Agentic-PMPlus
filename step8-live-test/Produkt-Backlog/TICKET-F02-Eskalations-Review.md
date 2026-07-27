# TICKET-F02 – Eskalations-Review (PGP/LLM getrennt)

**Status:** ✅ Erledigt (2026-07-27)
**Rolle:** frontend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B04](TICKET-B04-GET-Eskalationen.md), [B03](TICKET-B03-RAG-Metadaten-Aufloesung.md)
**MVP:** ✅

## User Story
#3, #5 (`step8-live-test/Userstories.md`)

## Beschreibung
Umgesetzt als Erweiterung der bestehenden Auftragskarte aus F01
(`step7-active-learning/frontend/app.js`/`index.html`/`style.css`), nicht als
separater Bildschirm/eigene Route: der von F01 bereits gebaute "Details"-Toggle
zeigt pro Karte schon `pgp`/`llm` getrennt nebeneinander – das entspricht
inhaltlich bereits Screen 2 aus
`Active-Learning-Loop-und-Frontend-Konzept.md` Abschnitt 2.3.2. F02 ergänzt
darin `matched_rag_docs` (eigener dritter Abschnitt `renderRagDocs`, hängt an
keiner der beiden Boxen) und einen "Entscheidung erfassen"-Button, der erst
nach dem Öffnen der Details aktiviert wird (Vorarbeit für F03, das die
Provenienz-erzwungene Entscheidungserfassung baut).

## Akzeptanzkriterien
- `pgp.begruendung` und `llm.begruendung` in **getrennten UI-Elementen** – nicht
  verhandelbar (siehe `.claude/agents/role/frontend-dev.md`, Leitplanke 1). ✅
  Weiterhin zwei separate `renderAssessmentBox`-Aufrufe; `matched_rag_docs`
  bekam bewusst einen eigenen dritten `rag-box`-Block statt an eine der beiden
  Boxen angehängt zu werden.
- UI-Flow erzwingt: erst beide Einschätzungen sehen, dann erst Wechsel zur
  Entscheidungserfassung möglich. ✅ "Entscheidung erfassen" ist pro Auftrag
  deaktiviert (mit Begründungs-Tooltip), bis die Details (pgp+llm+RAG) für
  genau diesen Auftrag mindestens einmal geöffnet wurden
  (`markDetailsViewed`/`detailsViewedOrderIds`); F03 existiert noch nicht,
  daher führt der Klick bewusst nur auf eine Platzhalter-Aktion (Konsolen-Log
  + kurzer "kommt in Kürze"-Hinweis im UI), keine echte Aktion (Leitplanke 2).
- Vertrauensstufe pro RAG-Treffer sichtbar (aus B03). ✅ `renderRagDocs` zeigt
  `doc_id`/`title`/`vertrauensstufe`; fehlende/`null`-Vertrauensstufe wird als
  "⚠️ Vertrauensstufe unbekannt" markiert statt still leer zu bleiben
  (Systemgrenzen.md Teil C.1/C.2); eine leere `matched_rag_docs`-Liste wird
  explizit als "Keine RAG-Dokumente für diesen Auftrag hinterlegt"
  ausgeschrieben statt den Abschnitt wegzulassen.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt. ✅
- Manueller Klick-Test: PGP- und LLM-Begründung sind auch bei langem Text nie vermischt/
  zusammengefasst dargestellt. ✅ Kein echter Browser verfügbar (siehe
  `step7-active-learning/frontend/README.md`) – stattdessen echte
  `renderOrderCard`/`renderRagDocs`/`renderDecisionRow`-Funktionen in einer
  echten JS-Engine (JavaScriptCore via `osascript -l JavaScript`) gegen die
  echte `GET /eskalationen`-Antwort ausgeführt und das erzeugte HTML auf
  Struktur/Trennung/Reihenfolge geprüft (26/26 Checks bestanden). Visuelles
  Rendering/Klickverhalten im echten Browser nicht geprüft – offene Lücke vor
  einer Demo mit Jens, wie schon bei F01 dokumentiert.

## Folgetickets
[F03](TICKET-F03-Entscheidungserfassung.md)
