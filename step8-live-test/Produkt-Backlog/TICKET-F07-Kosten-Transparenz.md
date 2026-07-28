# TICKET-F07 – Kosten-Transparenz-Hinweis (optional)

**Status:** ✅ Erledigt (2026-07-28)
**Rolle:** frontend-dev
**Priorität:** Niedrig
**Abhängigkeiten:** [F02](TICKET-F02-Eskalations-Review.md) oder [F05](TICKET-F05-Audit-Trail.md)
**MVP:** nein – explizit nicht MVP-Scope

## User Story
#12 (`step8-live-test/Userstories.md`, als Annahme gekennzeichnet)

## Akzeptanzkriterien
- Erkennbar, dass ein LLM-Ranking nur für Eskalationsfälle angefragt wurde, nicht
  pauschal für jeden Auftrag. ⚠️ **Umgesetzt mit dokumentierter, bewusster
  Abweichung** – s. "Umsetzung" unten: diese Formulierung trifft auf die
  aktuelle Architektur nicht zu, und eine UI, die sie trotzdem wörtlich
  behauptet hätte, wäre eine falsche Aussage gewesen.

## Umsetzung (Kurzfassung)
**Bewusste, dokumentierte Abweichung von der AC-Formulierung:** `step6-calibration/
main.py` ruft das LLM genau **einmal pro Kalibrierungslauf für ALLE offenen
Aufträge gemeinsam** auf (ein einziger Anthropic-Tool-Use-Call) – nicht gefiltert
auf Eskalationsfälle. Das ist kein Bug, sondern strukturell zwingend: der
Eskalationsstatus (`ampel_status`) wird erst **aus** diesem LLM-Ranking abgeleitet
(`tau` = Rangdifferenz PGP vs. LLM) – eine Vorfilterung auf "nur Eskalationsfälle"
ist ein Henne-Ei-Problem, bevor das Ranking existiert, ist unbekannt, welche
Fälle überhaupt eskalieren würden. Statt diese (falsche) Behauptung im UI
anzuzeigen, zeigt der neue Kosten-Transparenz-Kasten die tatsächlich zutreffende,
für User Story #12 ebenso relevante Eigenschaft: **keine Planer-Entscheidung
(`POST /entscheidung`) löst jemals einen LLM-Call aus** – die gesamte LLM-Nutzung
im Prototyp ist der eine gebündelte Kalibrierungslauf. Die Abweichung selbst wird
zusätzlich explizit im UI-Text benannt ("dieser eine Call deckt aktuell ALLE
offenen Aufträge ab, nicht nur die später als Eskalation markierten Fälle").

**Umsetzung, ohne neuen Backend-Endpunkt:** `GET /kalibrierung` (TICKET-F06)
existiert bereits und liefert Zeitstempel + Auftragsanzahl des letzten
Kalibrierungslaufs – `verlauf.js` lädt diesen Endpunkt zusätzlich, unabhängig vom
eigentlichen `GET /verlauf`-Fetch (ein Fehler hier blockiert den Audit-Trail
selbst nicht), und zeigt einen neuen Kosten-Box-Abschnitt
(`renderKostenBox`/`renderKostenBoxError`) oberhalb der Verlaufsliste in
`verlauf.html`. Bewusst auf F05 (Audit-Trail) statt F02 (Eskalations-Review)
gesetzt – ein einmaliger Summary-Kasten passt besser als eine Wiederholung pro
Auftragskarte.

## Bezug zu Leitplanken
Keine stillschweigend "passend gemachte" Behauptung (Leitplanke 5, Fail-safe/
Ehrlichkeit): die Diskrepanz zwischen Ticket-Wortlaut und tatsächlicher
Architektur wird im Code-Kommentar (`verlauf.js`-Modulkopf), im UI-Text selbst
und hier dokumentiert, nicht verschwiegen.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt. ✅ Echter Kalibrierungslauf
  (`MOCK_LLM_RESPONSE=1`) gegen `shared/data` ausgeführt, Backend-Container
  gestartet, `GET /kalibrierung` per `curl` live abgefragt und die echte Antwort
  als Grundlage für die Tests verwendet.
- **JS-Syntaxprüfung** von `verlauf.js` (JavaScriptCore via
  `osascript -l JavaScript`): `new Function(source)` parst fehlerfrei.
- **8 automatisierte Checks, alle bestanden** – echte `verlauf.js`-Funktionen
  gegen die echte `GET /kalibrierung`-Antwort ausgeführt: `renderKostenBox` zeigt
  den echten `n_auftraege`-Wert (20) und die erwarteten Kernaussagen
  ("gebündelte(r) API-Call", "löst einen LLM-Aufruf aus", die Einschränkung
  "nicht nur die später als Eskalation markierten Fälle"); `renderKostenBox(null)`
  zeigt einen expliziten "kein Lauf"-Zustand statt Fake-Zahlen;
  `renderKostenBoxError` zeigt den echten Fehlertext sichtbar mit `role="alert"`.
- **HTML-Wohlgeformtheit** von `verlauf.html` (Python `html.parser`) geprüft, alle
  `getElementById`-Aufrufe in `verlauf.js` gegen `verlauf.html` abgeglichen
  (`retry-btn` fehlt dort absichtlich – dynamisch erzeugt, gleiches Muster wie
  `app.js`/`kalibrierung.js`). `style.css`-Klammerbalance (134/134) geprüft.
- Test-Container/Test-Artefakte (`kalibrierung_verlauf.csv`, Docker-Testcontainer)
  nach dem Test wieder entfernt.
