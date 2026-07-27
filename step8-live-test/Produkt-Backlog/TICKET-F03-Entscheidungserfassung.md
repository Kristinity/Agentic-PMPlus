# TICKET-F03 – Entscheidungserfassung mit erzwungener Provenienz

**Rolle:** frontend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B05](TICKET-B05-POST-Entscheidung.md), [F02](TICKET-F02-Eskalations-Review.md) (lose: [B08](TICKET-B08-Propagation.md))
**MVP:** ✅
**Status:** ✅ erledigt

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

## Umsetzung (Stand: erledigt)

**Architektur-Konflikt gelöst (Weg a, s. Aufgabenstellung):** `POST /entscheidung`
berechnete die Propagation bisher im selben Aufruf, in dem sie auch persistiert wurde – es
gab keinen Weg, dem Planer VOR dem verbindlichen Klick zu zeigen, welche/wie viele Fälle
mitbetroffen wären. Gelöst über einen neuen, rein lesenden Endpunkt
`GET /aehnliche-faelle?order_id=…&wahl=…` (`step7-active-learning/api.py`), der
`propagation.propagate()` (bereits side-effect-frei) aufruft, aber nichts persistiert.
`_propagate_decision()` (aufgerufen von `POST /entscheidung`) und der neue Endpunkt teilen
sich jetzt dieselbe Hilfsfunktion `_compute_propagation_preview()` – Vorschau und
tatsächliche Ausführung können dadurch nie auseinanderlaufen. Live gegen den echten
Container verifiziert: die Vorschau für `O-03791`/`folgt_pgp` lieferte exakt dieselben 5
`propagierte_faelle`, die der anschließende `POST /entscheidung` tatsächlich gespeichert
hat (gleiches Ergebnis für `O-03927`/`folgt_llm`, 4 propagiert).

**Frontend (`step7-active-learning/frontend/app.js`):** ersetzt `handleDecisionPlaceholder`
durch ein echtes zweistufiges Formular pro Auftragskarte (drei Radio-Optionen, Freitextfeld
bei „eigene Reihenfolge“, Begründungsfeld optional/Pflicht je nach Wahl mit
Client-Validierung `validateDecisionForm`) – Schritt 1 „Weiter: Auswirkung prüfen“ ruft
`GET /aehnliche-faelle` auf und zeigt die echte Liste (inkl. wegen der Sicherheitsgrenze N
übersprungener Fälle), sperrt danach die Eingabefelder und gibt erst dann den zweiten,
separat beschrifteten Button „Entscheidung jetzt endgültig speichern“ frei
(`POST /entscheidung`). Nach Erfolg wird das echte Ergebnis (inkl. echter
`propagierte_faelle`) angezeigt und die Karte als entschieden markiert (kein erneuter
Entscheidungs-Button). 422 (fehlende Begründung trotz Client-Validierung) und
Netzwerkfehler werden sichtbar gemeldet, nicht verschluckt. `entschieden_von` wird nirgends
als Feld angeboten. Details: Kommentare im Modulkopf von `app.js` und in `api.py`.

Getestet gegen den echten Backend-Container (Docker build/run,
`pgp_priorisierung.csv`/`tau_vergleich.csv` frisch aus echten `output_2025`-Daten
regeneriert) sowie per JavaScriptCore-Ausführung des echten, unveränderten `app.js` gegen
zuvor per `curl` eingefangene echte API-Antworten (38/38 Checks bestanden). Nicht in einem
echten Browser visuell verifiziert (kein Browser-Tool in dieser Umgebung verfügbar) – siehe
`step7-active-learning/frontend/README.md` für den vollständigen Testbericht und die Liste
dessen, was vor einer echten Demo mit Jens noch in einem echten Browser geprüft werden
sollte.
