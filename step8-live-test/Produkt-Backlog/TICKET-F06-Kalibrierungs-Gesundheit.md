# TICKET-F06 – Kalibrierungs-Gesundheit (optional)

**Status:** ✅ Erledigt (2026-07-28)
**Rolle:** frontend-dev (mit backend-dev abstimmen)
**Priorität:** Niedrig
**Abhängigkeiten:** [B07](TICKET-B07-Kalibrierung.md)
**MVP:** nein – explizit nicht MVP-Scope

## Beschreibung
Technischer Überblick für die Person, die Step 6/7 betreut – nicht für Jens/Tagesplaner
(siehe `step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md` Abschnitt
2.3.5: Zielgruppe nicht überladen).

## Akzeptanzkriterien
- Aktuelle τ₀/σ₀, Eskalationsrate über Zeit, Anteil "trügerische Ruhe"-Fälle. ✅
- Separate Ansicht/Rolle, nicht im Hauptbildschirm für Jens. ✅

## Umsetzung (Kurzfassung)
- **Backend-Voraussetzung geschaffen (mit backend-dev-Rolle abgestimmt):**
  `tau0`/`sigma0` wurden bisher nur auf stdout ausgegeben, nie persistiert – ohne
  Historie gäbe es keine echte "Eskalationsrate über Zeit", nur eine Momentaufnahme
  aus der jeweils überschriebenen `tau_vergleich.csv`. `step6-calibration/main.py`
  hängt deshalb neu (`append_kalibrierung_verlauf`) **eine Zeile pro tatsächlich
  gelaufenem Kalibrierungslauf** an `shared_data/kalibrierung_verlauf.csv` an
  (Header nur beim ersten Lauf) – jede Zahl darin ist ein echter Lauf, keine
  synthetische/interpolierte Zeitreihe.
- **Neuer Endpunkt `GET /kalibrierung`** (`step7-active-learning/api.py`) liest diese
  Verlaufs-CSV und liefert `verlauf` (volle Historie) + `aktuell` (letzter Lauf) –
  fail-safe analog `GET /eskalationen`: fehlt die Datei, wird das als `hinweis`
  gemeldet statt als leere/fake Historie kaschiert.
- **Eigene, separate Seite** `step7-active-learning/frontend/kalibrierung.html` +
  `kalibrierung.js` (nicht `index.html`/`app.js`) – bewusst **nicht** von der
  Auftrags-Warteschlange oder dem Verlauf aus verlinkt, nur umgekehrt (Link zurück).
  Zeigt aktuelle τ₀/σ₀, Eskalationsrate und Anteil "Trügerische Ruhe" als
  Kennzahlen-Kacheln sowie die volle Lauf-Historie als Tabelle. Footer erinnert
  explizit an den Bootstrap-Platzhalter-Charakter (s. `step6-calibration/main.py`
  Modulkopf) und `Systemgrenzen.md` Teil A.3.

## Bezug zu Leitplanken
`step2-limits/Systemgrenzen.md` Teil A.3: die Übertragung von Risk-Coverage-Prinzipien
von LLM- auf GP-Unsicherheit ist unbelegt – im Footer der neuen Seite explizit
gegengezeichnet, damit die Kennzahlen nicht als belastbare Kalibrierung
missverstanden werden.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt. ✅ Docker-Images
  (`pmplus-step6-calibration`, `pmplus-step7-active-learning`) neu gebaut; zwei echte
  Kalibrierungsläufe (`MOCK_LLM_RESPONSE=1`) gegen `shared/data` ausgeführt –
  `kalibrierung_verlauf.csv` enthält nachweislich zwei echte, unterschiedliche
  Zeilen (τ₀ 0.665→0.600, Eskalationsrate 30,0 %→25,0 %). `GET /kalibrierung` gegen
  den laufenden Container per `curl` geprüft: liefert exakt diese zwei Zeilen plus
  den korrekten letzten Lauf als `aktuell`. Fail-safe-Fall (Datei umbenannt) liefert
  `verlauf: [], aktuell: null` + `hinweis`, kein Absturz. `GET /eskalationen` als
  Regressionscheck weiterhin unverändert funktionsfähig (20 Einträge).
- **JS-Syntaxprüfung** von `kalibrierung.js` (JavaScriptCore via
  `osascript -l JavaScript`, kein Node.js verfügbar): `new Function(source)` parst
  fehlerfrei.
- **12 automatisierte Checks, alle bestanden** – echte `kalibrierung.js`-Funktionen
  gegen die echte, per `curl` eingefangene `GET /kalibrierung`-Antwort ausgeführt
  (Browser-Stubs für `window`/`document`/`module`/`URLSearchParams`):
  `formatPercent`/`formatNumber` korrekt inkl. Fail-safe-Fall (`null` → "–"),
  `sortByZeitstempelAsc` stellt echte chronologische Reihenfolge wieder her,
  `renderVerlaufRow`/`renderAktuell` zeigen die echten τ₀/Eskalationsraten-Werte,
  `renderAktuell(null)` versteckt die Sektion (kein Fake-Nullwert-Rendering),
  `FetchFailure`/`BackendNotReady` korrekt als Error-Subklassen.
- **HTML-Wohlgeformtheit** von `kalibrierung.html` (Python `html.parser`) geprüft,
  alle `getElementById`-Aufrufe in `kalibrierung.js` gegen `kalibrierung.html`
  abgeglichen (`retry-btn` fehlt dort absichtlich – wird dynamisch erzeugt, gleiches
  Muster wie `app.js`/`verlauf.js`). `style.css`-Klammerbalance (130/130) geprüft.
- Test-Container/Test-Artefakte (`kalibrierung_verlauf.csv`, Docker-Testcontainer)
  nach dem Test wieder entfernt.
