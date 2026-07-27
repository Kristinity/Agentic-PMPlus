# TICKET-F05 – Audit-Trail

**Status:** ✅ Erledigt (2026-07-27)
**Rolle:** frontend-dev
**Priorität:** Mittel
**Abhängigkeiten:** [B06](TICKET-B06-GET-Verlauf.md)
**MVP:** nein (Post-MVP)

## User Story
#7, #9 (`step8-live-test/Userstories.md`)

## Akzeptanzkriterien
- Chronologische Liste aus `GET /verlauf`. ✅
- Mensch-/Agent-Provenienz optisch klar unterscheidbar (nicht nur Textfeld irgendwo). ✅

## Umsetzung
Neue, eigenständige Seite `step7-active-learning/frontend/verlauf.html` +
`verlauf.js` (plain HTML/CSS/vanilla JS, kein Build-Schritt – gleicher Stack wie
F01) statt `index.html`/`app.js` umzubauen, damit der parallel an TICKET-F02
arbeitende Sibling-Agent (erweitert `index.html`/`app.js`) keine Merge-Konflikte
bekommt. `style.css` nur additiv ergänzt (neue Klassen `.provenienz-*`,
`.verlauf-*`, `.app-nav` angehängt, bestehende Klassen unverändert). Minimale
gegenseitige Verlinkung: `index.html` bekommt einen Link "Zum Verlauf →" im
Header, `verlauf.html` einen Link "← Zur Auftrags-Warteschlange" zurück.

**Provenienz-Darstellung (Kernanforderung):** jeder Eintrag trägt ein eigenes
Badge (`renderProvenienzBadge`), das sich in Icon (👤 vs. 🤖), Farbe/Rahmen
(wiederverwendet die robust/trügerisch-Farbpaletten aus F01) UND Wortlaut
unterscheidet – nie nur Text. Zusätzlich pro Eintrag ein Erklärsatz, was
`entschieden_von: "agent"` konkret bedeutet ("kein Mensch hat DIESEN Auftrag
einzeln geprüft – ein Mensch hat für einen ähnlichen Auftrag entschieden,
TICKET-B08-Propagation hat das automatisch übernommen"), damit es für Jens
nicht wie eine geheimnisvolle Blackbox-Entscheidung wirkt (Aufgabenstellung).
Ein unbekannter/fehlender `entschieden_von`-Wert fällt fail-safe auf einen
dritten, eigenen "Herkunft unbekannt"-Zustand zurück – wird NIE stillschweigend
als "mensch" interpretiert (das wäre die sicherheitskritischere Fehlrichtung).

**wahl in verständlicher Sprache:** `folgt_pgp` → "folgt PGP-Empfehlung",
`folgt_llm` → "folgt LLM-Empfehlung", `eigene_reihenfolge` → "eigene Reihenfolge
des Planers" (Rohwert nie unübersetzt gezeigt, unbekannte Rohwerte fallen
fail-safe auf einen Text zurück, der den Rohwert sichtbar mitführt statt ihn zu
verschlucken).

**Abweichung von `Frontend-Backlog.md` Abschnitt 4 / Konzept-Doc 2.3 Punkt 4
dokumentiert:** dort ist als Akzeptanzkriterium "μ/σ/τ" pro Eintrag genannt. Die
tatsächliche, bereits fertige `GET /verlauf`-Response (B06, `api.py`/`store.py`)
liefert diese Felder NICHT (nur `id`, `order_id`, `wahl`,
`eigene_reihenfolge`, `begruendung`, `entschieden_von`, `zeitstempel` – die
Entscheidungs-Tabelle in `store.py` hat kein μ/σ/τ-Feld; diese Werte werden nur
bei B09-Export zum Entscheidungszeitpunkt separat nach
`validated_preferences.csv` geschrieben, nicht ins Audit-Trail zurückgespielt).
Dieser Bildschirm zeigt deshalb bewusst nur, was der reale Endpunkt tatsächlich
liefert, statt Werte zu erfinden oder zu verschweigen, dass sie fehlen – keine
stillschweigende Annahme. Eine Erweiterung von `GET /verlauf` um den
PGP/LLM-Kontext zum Entscheidungszeitpunkt (analog zu `_lookup_pgp_llm_context`
in `api.py`) wäre ein separates Backend-Ticket.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Mind. drei Einträge (aus B06-Testdaten) korrekt dargestellt inkl.
  Provenienz-Kennzeichnung. ✅ Backend-Container frisch gebaut
  (`pmplus-step7-active-learning`), `pgp_priorisierung.csv`/`tau_vergleich.csv`
  über `pmplus-step5-pgp`/`pmplus-step6-calibration` (`MOCK_LLM_RESPONSE=1`)
  gegen die echten `output_2025`-Daten regeneriert, 3 echte `POST /entscheidung`
  gegen den laufenden Container ausgelöst (`folgt_pgp`, `folgt_llm`,
  `eigene_reihenfolge`) – TICKET-B08-Propagation griff automatisch (gleiches
  `product_id` + nahes `due_date`) und erzeugte zusätzlich 10 `entschieden_von:
  "agent"`-Einträge. `GET /verlauf` lieferte 13 echte Einträge (3 mensch, 10
  agent), per `curl` verifiziert.
  **Kein echter Browser in dieser Session verfügbar** – stattdessen `verlauf.js`
  in einer echten JS-Engine (JavaScriptCore via `osascript -l JavaScript`, mit
  korrektem UTF-8-Read über den ObjC-Bridge, da JXAs `read`-Befehl Umlaute
  sonst falsch dekodiert) gegen die echte 13-Eintrag-Antwort ausgeführt: 19
  Prüfungen (Provenienz-Unterscheidung, Fail-safe bei unbekanntem
  `entschieden_von`, `wahl`-Übersetzung, chronologische Sortierung,
  Zeitstempel-Formatierung) – alle bestanden. `index.html`/`verlauf.html`
  zusätzlich per `python3 -m http.server` bedient und mit `curl` auf HTTP 200
  geprüft, HTML-Wohlgeformtheit per `html.parser` verifiziert, alle
  `getElementById`-Aufrufe in `verlauf.js` gegen tatsächlich vorhandene IDs in
  `verlauf.html` abgeglichen. **Nicht geprüft** (ohne echten Browser nicht
  möglich): tatsächliches CSS-Rendering/Layout, Klickverhalten im echten DOM,
  Screenreader-Verhalten.
- Test-Artefakte aufgeräumt: alle Test-CSVs in `shared/data/` (kopierte
  ERP-Rohdaten + generierte `pgp_priorisierung.csv`/`tau_vergleich.csv`/
  `validated_preferences.csv`) sowie `shared/feedback/` (Entscheidungs-DB)
  nach dem Test wieder entfernt, Test-Container gestoppt/entfernt.
