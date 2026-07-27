# TICKET-F01 – Warteschlange mit Ampel-Status

**Status:** ✅ Erledigt (2026-07-27)
**Rolle:** frontend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B04](TICKET-B04-GET-Eskalationen.md)
**MVP:** ✅

## User Story
#1, #4, #6 (`step8-live-test/Userstories.md`)

## Akzeptanzkriterien
- Liste aus `GET /eskalationen`, sortiert nach PGP-Rang. ✅
- Ampel-Sprache exakt aus `Konzept-README.md` übernommen ("Robuste Übereinstimmung",
  "Trügerische Ruhe", "Klarer Fall für Experten-Review"). ✅
- `ampel_status: "unbekannt"` als eigener, sichtbarer Zustand – nicht als 🟢 dargestellt. ✅
  (Grauer/neutraler Zustand "Status unbekannt"; auch jeder unbekannte/zukünftige
  ampel_status-Wert fällt fail-safe auf diesen Zustand zurück, nie auf grün.)

## Umsetzung
Neuer Ordner `step7-active-learning/frontend/` (plain HTML/CSS/vanilla JS, kein
Build-Schritt – Begründung in `frontend/README.md`). `step7-active-learning/main.py`
zusätzlich um `CORSMiddleware` ergänzt, sonst kann der Browser die API von einer
separaten Frontend-Origin aus nicht lesen (siehe Kommentar dort).

**Scope-Entscheidung:** `matched_rag_docs`/Vertrauensstufe wird auf diesem
Bildschirm bewusst nicht angezeigt – das ist Akzeptanzkriterium von F02, nicht F01
(siehe `Frontend-Backlog.md`). Beim Live-Test zusätzlich ein bestehendes
Backend-Datenqualitätsproblem entdeckt (leere `matched_rag_docs`-Zelle wird über
pandas zu `NaN` und dann fälschlich als Dokument-ID `"nan"` durchgereicht,
`rag_lookup.resolve_matched_docs`) – dokumentiert in `frontend/README.md`, bewusst
nicht mitgefixt (außerhalb des F01-Scopes), aber relevant für F02.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Gegen echte `GET /eskalationen`-Response (aus B04) getestet. ✅ Backend-Container
  frisch gebaut und gestartet, `pgp_priorisierung.csv`/`tau_vergleich.csv` über
  `pmplus-step5-pgp`/`pmplus-step6-calibration` (`MOCK_LLM_RESPONSE=1`) gegen die
  echten `output_2025`-Daten regeneriert, `GET /eskalationen` per `curl` live
  abgefragt (20 Aufträge, 14 robust / 3 trügerische Ruhe / 3 klarer Review-Fall).
  **Kein echter Browser in dieser Session verfügbar** – stattdessen `app.js`
  syntaktisch und in seiner Kernlogik (Sortierung, Ampel-Mapping, Filter,
  `renderOrderCard`) in einer echten JS-Engine (JavaScriptCore via
  `osascript -l JavaScript`) gegen die echte API-Antwort ausgeführt und verifiziert
  – Details und explizit NICHT geprüfte Aspekte (echtes CSS-Rendering, Klicks im
  echten DOM) in `frontend/README.md` Abschnitt "Was getestet wurde".
- Alle drei Ampel-Zustände + "unbekannt" sind visuell unterscheidbar. ✅ Farbe +
  Icon + Wortlaut je Zustand (nicht nur Farbe, siehe `style.css`); "unbekannt"
  an einem synthetischen Testfall verifiziert (kommt in der aktuell kalibrierten
  `tau_vergleich.csv` nicht vor, da B07 bereits läuft).
- Test-Artefakte aufgeräumt: `pgp_priorisierung.csv`/`tau_vergleich.csv` aus
  `step3-erp-simulation/output_2025/` sowie `shared/feedback/entscheidungen.db`
  nach dem Test wieder entfernt.
