# step7-active-learning/frontend – Auftrags-Warteschlange + Eskalations-Review + Entscheidungserfassung (TICKET-F01/F02/F03)

Erster, zweiter und dritter Bildschirm des Live-Prototyps für Jens Pirinski
(Produktionsplaner, Krasser Spass GmbH, siehe `step8-live-test/Userstories.md`).
Zeigt `GET /eskalationen` sortiert nach PGP-Rang, mit Ampel-Status in der
Sprache aus `Konzept-README.md`. Jede Auftragskarte lässt sich aufklappen
("Details") und zeigt dann PGP-Einschätzung, LLM-Einschätzung und genutzte
RAG-Dokumente (inkl. Vertrauensstufe, TICKET-F02) jeweils in eigenen,
getrennten Abschnitten. TICKET-F03 ergänzt die echte Entscheidungserfassung
(PGP folgen / LLM folgen / eigene Reihenfolge, mit echtem Vorschau-Schritt vor
dem Bestätigen und Anzeige des echten Ergebnisses danach) – mit dem MVP-Backlog
(`step8-live-test/Produkt-Backlog/README.md`) ist damit der vollständige
Durchlauf Warteschlange → Review → Entscheidung fertig.

## Stack-Wahl (bewusst, siehe `.claude/agents/role/frontend-dev.md`)

**Plain HTML/CSS/vanilla JS, kein Build-Schritt, kein Framework.**

Begründung:
- Es existiert im Repo bisher **kein** Frontend-Code (kein `package.json`, keine
  `.tsx`/`.jsx`-Datei) – dieser Ticket ist der Anfang. Ein Build-Toolchain
  (npm/Vite/React) wäre für einen einzelnen, rein lesenden Bildschirm
  unverhältnismäßig viel Overhead (Node-Version-Pinning, `node_modules`,
  Lockfile-Pflege) gegenüber dem Nutzen.
- Das restliche Projekt ist konsequent Docker/CLI-first (siehe `README.md`,
  `Konzept-README.md`) ohne jede bestehende JS-Tooling-Konvention – ein
  minimaler Stack ohne neue Abhängigkeiten passt besser zur bestehenden
  Philosophie als ein neues Ökosystem einzuführen.
- Schnelle Iteration: Datei speichern, Browser neu laden – kein Kompilierschritt,
  keine zusätzliche Fehlerquelle zwischen Code und angezeigtem Ergebnis.
- Nachteil bewusst in Kauf genommen: kein Komponentenmodell, kein State-Management
  jenseits eines einzelnen Moduls. Für vier geplante Bildschirme (F01/F02/F03/F05,
  siehe `Frontend-Backlog.md`) ist das noch vertretbar; falls die Bildschirme
  später stärker verzahnt werden müssen (z. B. F03 braucht den in F02 geprüften
  Zustand), sollte das dann neu bewertet werden – kein Vorgriff hier.

## Ordner-Konvention

Liegt unter `step7-active-learning/frontend/`, nicht in einem eigenen
Top-Level-Ordner – passt zur bestehenden Konvention "ein Unterordner pro
Step-Bestandteil" (`step7-active-learning/` enthält bereits `api.py`, `main.py`,
`store.py`, `rag_lookup.py` als API-Backend für genau diesen Step; das Frontend
dafür gehört inhaltlich dazu, nicht in einen separaten Step).

## Dateien

- `index.html` – Grundgerüst, Filter-Toolbar, Statusbereich, Liste.
- `style.css` – Ampel-Farben (mit Dark-Mode via `prefers-color-scheme`), Layout.
  Farbe ist **nicht** das einzige Unterscheidungsmerkmal je Ampel-Zustand
  (zusätzlich Icon `✓ / ! / 🔎 / ?` und der Wortlaut selbst) – wichtig, weil Jens
  als Zielgruppe nicht unterstellt werden darf, Farben sicher unterscheiden zu
  können/müssen. TICKET-F02 ergänzt additiv: `.rag-box`/`.rag-doc-list`/
  `.rag-vertrauen(-unbekannt)` für die RAG-Treffer-Anzeige und
  `.decision-row`/`.decision-btn` für den gate-geschützten
  "Entscheidung erfassen"-Button. TICKET-F03 ergänzt additiv das gesamte
  Entscheidungsformular (`.decision-wizard`/`.decision-wahl-*`/
  `.decision-preview-*`) sowie die Ergebnis-Ansicht nach dem Speichern
  (`.decision-done*`).
- `app.js` – Fetch gegen `GET /eskalationen`, Sortierung, Rendering, Fail-safe-
  Fehlerbehandlung. Kein externes Paket, keine Build-Pipeline. TICKET-F02
  ergänzt `renderRagDocs` (RAG-Treffer + Vertrauensstufe je Auftrag) und die
  Sichtbarkeits-/Reihenfolge-Regel für "Entscheidung erfassen"
  (`renderDecisionRow`/`markDetailsViewed`/`detailsViewedOrderIds`). TICKET-F03
  ersetzt den bisherigen Platzhalter durch die echte Entscheidungserfassung:
  `validateDecisionForm`/`buildEntscheidungPayload` (Client-Validierung +
  Payload-Aufbau, ohne `entschieden_von`-Feld), `fetchAehnlicheFaelle`/
  `renderPreviewResult` (echter Vorschau-Schritt gegen den NEUEN,
  rein lesenden Endpunkt `GET /aehnliche-faelle`, s. `../api.py`, VOR dem
  Bestätigen), `postEntscheidung`/`renderDecisionDone`/`DecisionRejected`
  (die eigentliche, irreversible Aktion inkl. Fail-safe-Fehlerbehandlung für
  422/Netzwerkfehler) und `wireDecisionForm` (verdrahtet ein Formular:
  Radio-Wechsel, Vorschau-Klick, Zurück, finales Bestätigen).
- `kalibrierung.html`/`kalibrierung.js` (TICKET-F06) – **eigene, separate** Seite
  für die Kalibrierungs-Gesundheit (aktuelle τ₀/σ₀, Eskalationsrate, Anteil
  "Trügerische Ruhe" über die Historie der Kalibrierungsläufe aus
  `GET /kalibrierung`). Bewusst **nicht** von `index.html`/`verlauf.html` aus
  verlinkt (nur umgekehrt, ein Link zurück zur Warteschlange) – Zielgruppe ist die
  Person, die Step 6/7 betreut, siehe `Active-Learning-Loop-und-Frontend-
  Konzept.md` Abschnitt 2.3.5 ("Sinnvoll als separate Rolle/Ansicht statt im
  Hauptbildschirm, um die Kernzielgruppe nicht zu überladen"). Erreichbar über
  die direkte URL `kalibrierung.html`. `style.css` ergänzt additiv
  `.kalibrierung-aktuell`/`.kalibrierung-metric*`/`.kalibrierung-table*`.
  Backend-Gegenstück: `step6-calibration/main.py:append_kalibrierung_verlauf`
  hängt pro tatsächlich gelaufenem Kalibrierungslauf eine Zeile an
  `shared_data/kalibrierung_verlauf.csv` an (neu, sonst gäbe es keine echte
  "Eskalationsrate über Zeit", nur eine überschriebene Momentaufnahme); `../api.py`
  liefert das darüber unverändert als `GET /kalibrierung`.
- `verlauf.js` (TICKET-F07-Zusatz) – ergänzt additiv einen
  Kosten-Transparenz-Kasten (`renderKostenBox`/`renderKostenBoxError`/
  `fetchKalibrierung`/`loadKosten`) oberhalb der Verlaufsliste in `verlauf.html`,
  der `GET /kalibrierung` (TICKET-F06, kein neuer Endpunkt nötig) unabhängig vom
  eigentlichen Verlaufs-Fetch lädt und zeigt, dass keine Planer-Entscheidung je
  einen LLM-Call auslöst. Siehe Modulkopf von `verlauf.js` für die dokumentierte,
  bewusste Abweichung von der ursprünglichen Ticket-Formulierung ("nur für
  Eskalationsfälle angefragt") – trifft auf die aktuelle step6-Architektur nicht
  zu (ein einziger Batch-Call für alle offenen Aufträge, da der Eskalationsstatus
  erst aus diesem Ranking abgeleitet wird), daher die inhaltlich korrigierte,
  aber ebenso wirtschaftlich relevante Aussage.

## Wie starten

Das Frontend ist eine statische Seite und läuft unabhängig vom Backend-Prozess.
Voraussetzung: der Backend-Container läuft (siehe unten, Port 8007 laut
`docker-compose.yml`).

```bash
cd step7-active-learning/frontend
python3 -m http.server 5500
# dann im Browser: http://localhost:5500/
```

Da Frontend (Port 5500) und Backend (Port 8007) unterschiedliche Origins sind,
wurde `step7-active-learning/main.py` um `CORSMiddleware` (`allow_origins=["*"]`)
ergänzt – sonst blockiert der Browser das Lesen der Antwort clientseitig, obwohl
der Server sie korrekt liefert (siehe Kommentar im Modulkopf von `main.py`).
`allow_origins=["*"]` ist eine bewusste Prototyp-Vereinfachung ohne
Auth-Kontext; vor einem echten Pilotbetrieb auf die tatsächliche Frontend-Origin
einschränken.

Die API-Basis-URL ist standardmäßig `http://localhost:8007` (passend zum
docker-compose-Port-Mapping `8007:8000`) und ohne Code-Änderung überschreibbar,
z. B. `index.html?api=http://andere-adresse:8007`.

## `matched_rag_docs` – Scope-Entwicklung F01 → F02

**F01 (Warteschlange)** zeigte `matched_rag_docs` bewusst **nicht** – laut
`Frontend-Backlog.md` Abschnitt 2 explizit Akzeptanzkriterium von **F02**
(Eskalations-Review), wo die LLM-Begründung im Kontext der RAG-Treffer geprüft
wird. F01 dokumentierte hier zusätzlich einen beim Live-Test entdeckten Bug:
`rag_lookup.resolve_matched_docs` lieferte für Aufträge ohne echten RAG-Treffer
einen irreführenden Eintrag `{"doc_id": "nan", ...}` statt einer leeren Liste
(Ursache: `pandas` liest eine leere Zelle als `NaN`, `not NaN` ist in Python
`False`). **Stand F02:** dieser Bug ist im aktuellen `rag_lookup.py` bereits
behoben (expliziter `is_nan`-Check vor der Leer-Prüfung, siehe Kommentar dort)
– beim F02-Live-Test gegen frisch generierte Daten lieferten alle 4 Aufträge
ohne RAG-Treffer korrekt `[]`, kein `"nan"`-Fake-Eintrag mehr beobachtet.

**F02 (dieser Ticket-Stand) zeigt `matched_rag_docs` jetzt** – als eigener
dritter Abschnitt (`rag-box`) in derselben Detail-Ansicht jeder Auftragskarte,
die F01 bereits gebaut hat (siehe `app.js`-Modulkopf für die Begründung, warum
F02 keinen eigenen Bildschirm/keine eigene Route bekommen hat). Pro
RAG-Dokument werden `doc_id`, `title` und `vertrauensstufe` gezeigt; eine
fehlende/`null`-Vertrauensstufe (z. B. bei einer unbekannten Doc-ID, siehe
`rag_lookup.resolve_matched_docs`) wird als "⚠️ Vertrauensstufe unbekannt"
sichtbar markiert statt still leer zu bleiben (Systemgrenzen.md Teil C.1/C.2,
`frontend-dev.md` Leitplanke 4). Eine leere `matched_rag_docs`-Liste ist ein
legitimer Zustand und wird explizit als "Keine RAG-Dokumente für diesen
Auftrag hinterlegt" ausgeschrieben, nicht kommentarlos weggelassen
(Leitplanke 5, Fail-safe).

F02 hat außerdem, pro Auftragskarte, einen "Entscheidung erfassen"-Button
ergänzt, der erst aktiv wird, nachdem die Details (pgp+llm+RAG) für genau
diesen Auftrag mindestens einmal geöffnet wurden – Vorarbeit für **F03**
(Entscheidungserfassung, noch nicht gebaut); der Klick führt aktuell nur auf
eine Platzhalter-Aktion (Konsolen-Log + kurzer UI-Hinweis "kommt in Kürze"),
löst also bewusst keine echte Aktion aus (Leitplanke 2).

## Was getestet wurde (und was nicht)

**Kein Zugriff auf einen echten Browser in dieser oder den vorherigen Sessions**
– es gibt in dieser Umgebung kein Tool, das ein sichtbares/gerendertes
Browserfenster prüfen kann. Deshalb ausdrücklich: **nicht visuell in einem
Browser bestätigt**, weder für F01 noch für F02 noch für F03 noch für F06 noch
für F07.

### TICKET-F07 (Kosten-Transparenz-Hinweis)

**Wichtige, dokumentierte Abweichung von der Ticket-Formulierung:** s. Modulkopf
von `verlauf.js` und `TICKET-F07-Kosten-Transparenz.md` Abschnitt "Umsetzung" für
die ausführliche Begründung. Kurzfassung: die AC-Formulierung ("LLM-Ranking nur
für Eskalationsfälle angefragt") trifft auf die aktuelle Architektur nicht zu –
`step6-calibration/main.py` ruft das LLM einmal pro Lauf für ALLE offenen
Aufträge auf, weil der Eskalationsstatus erst aus diesem Ranking abgeleitet wird
(Henne-Ei-Problem). Der Kosten-Kasten zeigt stattdessen die tatsächlich
zutreffende Eigenschaft (keine Planer-Entscheidung löst je einen LLM-Call aus)
und benennt die Abweichung explizit im UI-Text, statt sie zu verschweigen.

1. **Kein neuer Backend-Endpunkt nötig** – `GET /kalibrierung` (TICKET-F06)
   existierte bereits. Ein echter Kalibrierungslauf (`MOCK_LLM_RESPONSE=1`) wurde
   gegen `shared/data` ausgeführt, der Backend-Container gestartet und
   `GET /kalibrierung` live per `curl` abgefragt (`n_auftraege: 20`, echter
   Zeitstempel) – diese echte Antwort war Grundlage aller folgenden Tests.
2. **JS-Syntaxprüfung des echten, geänderten `verlauf.js`** (JavaScriptCore via
   `osascript -l JavaScript`): `new Function(source)` parst fehlerfrei.
3. **Ausführung der echten, neuen `verlauf.js`-Funktionen** (Original-Modul,
   Browser-Stubs für `window`/`document`/`module`/`URLSearchParams`) gegen die
   echte `GET /kalibrierung`-Antwort – **8 automatisierte Checks, alle
   bestanden**:
   - `formatZeitpunktKurz` liefert einen lesbaren, nicht-leeren String für den
     echten Zeitstempel.
   - `renderKostenBox` gegen den echten `aktuell`-Wert zeigt den echten
     `n_auftraege`-Wert (20), die Formulierung "gebündelte(r) API-Call", den
     Satz "löst einen LLM-Aufruf aus" (keine Entscheidung löst einen Call aus)
     und die explizite Einschränkung "nicht nur die später als Eskalation
     markierten Fälle" (die dokumentierte Abweichung selbst).
   - `renderKostenBox(null)` (kein Lauf vorhanden) zeigt einen expliziten
     "Noch kein protokollierter Kalibrierungslauf"-Zustand statt stillschweigend
     Nullwerte/Fake-Zahlen anzuzeigen (Fail-safe, Leitplanke 5).
   - `renderKostenBoxError` zeigt den echten Fehlertext sichtbar mit
     `role="alert"`, statt den Fehler zu verschlucken.
4. **HTML-Wohlgeformtheit** von `verlauf.html` (Python `html.parser`) erneut
   geprüft, alle `getElementById`-Aufrufe in `verlauf.js` gegen `verlauf.html`
   abgeglichen (`retry-btn` fehlt dort weiterhin absichtlich, dynamisch erzeugt).
   `style.css`-Klammerbalance (134/134) geprüft.
5. **Regressionscheck:** `GET /verlauf` (leer, da keine Entscheidungen in dieser
   Test-DB) und der bestehende Audit-Trail-Ladepfad blieben unverändert
   funktionsfähig – der neue Kosten-Kasten lädt unabhängig und blockiert die
   Verlaufsanzeige nicht.

**Nicht geprüft** (weil ohne echten Browser nicht möglich, wie bei F01–F06):
tatsächliches CSS-Rendering/Layout des neuen Kosten-Kastens, Screenreader-
Verhalten des neuen `role="alert"`.

Erzeugte Test-Artefakte (`shared/data/kalibrierung_verlauf.csv`, der
Test-Container `pmplus-step7-test`) wurden nach dem Test wieder entfernt.

### TICKET-F06 (Kalibrierungs-Gesundheit)

1. **Docker-Images neu gebaut:** `pmplus-step6-calibration` (enthält den neuen
   `append_kalibrierung_verlauf`-Code) und `pmplus-step7-active-learning`
   (enthält den neuen `GET /kalibrierung`-Endpunkt).
2. **Zwei echte, unabhängige Kalibrierungsläufe** gegen `shared/data` ausgeführt
   (`docker run … pmplus-step6-calibration`, `MOCK_LLM_RESPONSE=1`, zweimal
   hintereinander) – `shared/data/kalibrierung_verlauf.csv` enthält danach
   nachweislich **zwei** echte, unterschiedliche Zeilen (τ₀ 0.665→0.600, σ₀
   konstant ≈0.0247, Eskalationsrate 30,0 %→25,0 %, Anteil "Trügerische Ruhe"
   beide Male 15,0 %) – bestätigt, dass angehängt statt überschrieben wird.
3. **Backend-Container gestartet** (`-p 8007:8000`, `shared/data` gemountet),
   `GET /kalibrierung` live per `curl` abgefragt – echte JSON-Antwort mit
   `verlauf` (beide Läufe) und `aktuell` (der zeitlich letzte Lauf, korrekt).
   **Fail-safe-Test:** `kalibrierung_verlauf.csv` temporär umbenannt →
   `GET /kalibrierung` liefert `{"verlauf": [], "aktuell": null, "hinweis": "…"}`
   statt eines Absturzes oder einer falschen leeren Erfolgsantwort; Datei danach
   zurückbenannt. **Regressionscheck:** `GET /eskalationen` währenddessen
   unverändert funktionsfähig (20 Einträge, wie zuvor).
4. **JS-Syntaxprüfung des echten `kalibrierung.js`** (JavaScriptCore via
   `osascript -l JavaScript`, kein Node.js verfügbar): `new Function(source)`
   parst fehlerfrei.
5. **Ausführung der echten `kalibrierung.js`-Funktionen** (Original-Modul,
   Browser-Stubs für `window`/`document`/`module`/`URLSearchParams`) gegen die
   echte, per `curl` eingefangene `GET /kalibrierung`-Antwort – **12
   automatisierte Checks, alle bestanden**: `formatPercent`/`formatNumber`
   korrekt (inkl. `null` → "–", kein Fake-Wert); `sortByZeitstempelAsc` stellt
   die echte chronologische Reihenfolge wieder her, auch wenn die Eingabe
   umgekehrt sortiert ist; `renderVerlaufRow` und `renderAktuell` zeigen die
   echten τ₀-Werte (0.665/0.600) und Eskalationsraten (30,0 %/25,0 %) aus der
   echten Antwort; `renderAktuell(null)` versteckt die Sektion statt
   Nullwerte/Fake-Zahlen anzuzeigen (Fail-safe, Leitplanke 5); `FetchFailure`/
   `BackendNotReady` korrekt als eigenständige `Error`-Subklassen.
6. **HTML-Wohlgeformtheit** von `kalibrierung.html` (Python `html.parser`)
   geprüft; alle `getElementById`-Aufrufe in `kalibrierung.js` gegen
   `kalibrierung.html` abgeglichen (`retry-btn` fehlt dort absichtlich – wird
   dynamisch in `renderError`/`renderHinweis` erzeugt, gleiches Muster wie
   `app.js`/`verlauf.js`). `style.css`-Klammerbalance (130/130) geprüft.

**Nicht geprüft** (weil ohne echten Browser nicht möglich, wie bei F01–F03):
tatsächliches CSS-Rendering/Layout der neuen Kennzahlen-Kacheln/Tabelle,
Verhalten bei sehr kleinen Bildschirmbreiten, Screenreader-Verhalten.

Erzeugte Test-Artefakte (`shared/data/kalibrierung_verlauf.csv`, der
Test-Container `pmplus-step7-test`) wurden nach dem Test wieder entfernt.

### TICKET-F03 (Entscheidungserfassung mit erzwungener Provenienz)

**Architektur-Konflikt und Lösung:** s. Modulkopf von `../api.py` und `app.js`
sowie `step8-live-test/Produkt-Backlog/TICKET-F03-Entscheidungserfassung.md`
Abschnitt "Umsetzung" für die ausführliche Begründung. Kurzfassung: `POST
/entscheidung` berechnete die Propagation bisher im selben Aufruf, in dem sie
auch persistiert wurde – kein "vorher sehen, ohne dass es passiert" möglich.
Gelöst über einen neuen, rein lesenden Endpunkt `GET /aehnliche-faelle`
(ruft `propagation.propagate()`, das bereits side-effect-frei war, aber
persistiert nichts) statt einer bloß als Schätzung gekennzeichneten
UI-Anzeige ohne echten Server-Call.

1. **Docker-Images neu gebaut:** `pmplus-step5-pgp`, `pmplus-step6-calibration`,
   `pmplus-step7-active-learning` (`docker build -t pmplus-step7-active-learning
   -f step7-active-learning/Dockerfile step7-active-learning/`).
2. **`pgp_priorisierung.csv`/`tau_vergleich.csv` frisch regeneriert**
   (`pmplus-step5-pgp` mit `AS_OF_DATE=2026-01-01`, `pmplus-step6-calibration`
   mit `MOCK_LLM_RESPONSE=1`, beide gegen `step3-erp-simulation/output_2025/`)
   – 20 offene Aufträge, u. a. mehrere `P-KK`/`P-DV`-Aufträge mit nahen
   Fälligkeitsdaten (Propagations-Kandidaten).
3. **Backend-Container gestartet** (`-p 8007:8000`, inkl.
   `./shared/feedback:/app/shared_feedback`), **echte** HTTP-Aufrufe per
   `curl` gegen den laufenden Container:
   - `GET /aehnliche-faelle?order_id=O-03791&wahl=eigene_reihenfolge` →
     `{"propagierte_faelle": [], "uebersprungene_faelle": []}` (Design:
     `eigene_reihenfolge` wird nie propagiert) UND `GET /verlauf` blieb dabei
     nachweislich leer (0 DB-Zeilen, per Pythons `sqlite3`-Modul direkt gegen
     `shared/feedback/entscheidungen.db` geprüft) – die Vorschau persistiert
     wirklich nichts.
   - `GET /aehnliche-faelle?order_id=O-03791&wahl=folgt_pgp` → 5 propagierte +
     8 übersprungene Fälle (13 ähnliche Kandidaten insgesamt, deckt sich mit
     dem in TICKET-B08 dokumentierten Live-Test für denselben Auftrag).
   - **Anschließend** `POST /entscheidung` mit identischem Payload
     (`{"order_id":"O-03791","wahl":"folgt_pgp",...}`) → `propagierte_faelle`
     in der Response war **exakt identisch** zur zuvor angezeigten Vorschau
     (`["O-03816","O-03837","O-03776","O-03775","O-03831"]`). Gleicher Test
     mit einem zweiten, unabhängigen Auftrag (`O-03927`/`folgt_llm`, 4
     propagierte Fälle) – wieder exakte Übereinstimmung Vorschau ↔ Ausführung.
   - `GET /verlauf` nach beiden Entscheidungen zeigt 1× `mensch` + je 5×/4×
     `agent` pro Ursprungsentscheidung, korrekt zeitlich sortiert.
   - **422 bei fehlender Begründung** (`wahl=eigene_reihenfolge` ohne
     `begruendung`) live gegen den echten Server ausgelöst und die reale
     FastAPI/Pydantic-Fehlerantwort eingefangen
     (`{"detail":[{"type":"value_error","msg":"Value error, begruendung ist
     Pflichtfeld…"}]}`) – anschließend **mit** Begründung erfolgreich
     gespeichert (`propagierte_faelle: []`, wie von `propagation.py` für
     `eigene_reihenfolge` dokumentiert).
   - Ungültige Query-Parameter an `GET /aehnliche-faelle` (unbekannter
     `wahl`-Wert, fehlendes `order_id`) liefern jeweils `422` – bestätigt,
     dass `fetchAehnlicheFaelle` in `app.js` solche Antworten als
     `FetchFailure` behandelt und den Bestätigen-Button NICHT freigibt.
4. **JS-Syntaxprüfung des echten, geänderten `app.js`** (JavaScriptCore via
   `osascript -l JavaScript`): `new Function(source)` parst fehlerfrei.
5. **Ausführung der echten, neuen `app.js`-Funktionen** (Original-Modul,
   Browser-Stubs für `window`/`document`/`module`/`fetch`/`URLSearchParams` –
   letzteres in dieser JavaScriptCore-Version nicht eingebaut, deshalb minimal
   nachgebaut) gegen **echte, zuvor per `curl` gegen den laufenden Container
   eingefangene** API-Antworten (`GET /eskalationen`, zwei
   `GET /aehnliche-faelle`-Antworten, eine echte `POST /entscheidung`-Erfolgs-
   und eine echte 422-Antwort) – **38 automatisierte Checks, alle bestanden**:
   - `WAHL_OPTIONS` exakt die drei Backend-erlaubten Strings.
   - `validateDecisionForm`: `folgt_pgp`/`folgt_llm` ohne Begründung OK
     (optional), `eigene_reihenfolge` ohne Freitext-Reihenfolge blockiert
     (zusätzliche Client-Anforderung, s. Kommentar in `app.js`),
     `eigene_reihenfolge` mit Text aber ohne Begründung blockiert (Pflichtfeld,
     Akzeptanzkriterium), mit beidem OK.
   - `buildEntscheidungPayload`: **kein** `entschieden_von`-Feld im Payload
     (Leitplanke 3/Aufgabenstellung Punkt 5), korrektes Trimmen, korrektes
     `null` für nicht zutreffende Felder.
   - `renderPreviewResult` gegen die echte `folgt_llm`-Antwort (4 propagiert):
     zeigt alle 4 echten IDs und die Anzahl; gegen die echte
     `eigene_reihenfolge`-Antwort: erklärender Text statt Liste; gegen einen
     synthetischen Fall mit `uebersprungene_faelle`: diese werden SEPARAT und
     sichtbar mit Eskalations-Hinweis gezeigt (Akzeptanzkriterium 3
     vollständig, nicht nur die propagierten Fälle).
   - `renderDecisionDone` gegen die echte `POST /entscheidung`-Erfolgsantwort:
     zeigt die echte `decision_id` und alle echten `propagierte_faelle`-IDs;
     HTML-Escaping von gefährlichen Zeichen in `eigene_reihenfolge` geprüft
     (kein `<script>` im Output).
   - `renderDecisionRow`/`renderOrderCard` end-to-end gegen einen echten
     Auftrag aus `GET /eskalationen`: Button `disabled` vor „Details öffnen“,
     nicht danach; Formular enthält alle drei Wahlmöglichkeiten, den
     Pflichtfeld-Hinweistext, einen separaten Vorschau- UND
     Bestätigen-Button (Bestätigen-Button anfangs `disabled`, erst nach
     Vorschau freigebbar – Leitplanke 2); **kein** `entschieden_von`-Feld im
     gerenderten Formular; bei bereits entschiedenem Auftrag kein
     Button/Formular mehr, nur das echte Ergebnis; `assessment-box pgp`/`llm`
     weiterhin getrennt (Leitplanke 1, Regressionscheck).
   - `fetchAehnlicheFaelle`/`postEntscheidung` (die echten, unveränderten
     Funktionen) gegen einen `fetch`-Stub, der auf die echten eingefangenen
     Antworten routet: liefern die echten Werte korrekt zurück;
     `postEntscheidung` wirft bei der echten 422-Antwort eine
     `DecisionRejected`-Exception mit dem echten Server-Fehlertext (Fail-safe
     – wird nicht verschluckt).
6. **HTML-Wohlgeformtheit**/`style.css`-Klammerbalance (117/117) erneut
   geprüft; alle `getElementById`-Aufrufe in `app.js` gegen `index.html`
   abgeglichen (weiterhin nur `retry-btn` dynamisch, wie seit F01).

**Nicht geprüft** (weil ohne echten Browser nicht möglich): tatsächliches
CSS-Rendering/Layout des neuen Entscheidungsformulars, echtes Klickverhalten
im DOM (insbesondere Radio-Wechsel → Freitextfeld ein-/ausblenden, das
Sperren der Felder nach erfolgreicher Vorschau, der komplette
Zwei-Klick-Ablauf im Browser), Verhalten bei sehr kleinen Bildschirmbreiten,
Screenreader-Verhalten der neuen `role="alert"`/`aria-*`-Attribute. Ebenfalls
nicht geprüft: eine echte Race Condition zwischen Vorschau und Bestätigen
(zwei gleichzeitige Planer) – dafür gibt es keinen Mehrbenutzer-Testaufbau in
dieser Umgebung; das Risiko ist im Code-Kommentar zu `GET /aehnliche-faelle`
in `api.py` dokumentiert. Sollte vor einer echten Demo mit Jens durch einen
kurzen manuellen Check in einem echten Browser geschlossen werden.

Erzeugte Test-CSVs (`pgp_priorisierung.csv`, `tau_vergleich.csv`,
`validated_preferences.csv` in `step3-erp-simulation/output_2025/`) sowie
`shared/feedback/entscheidungen.db` und der Test-Container wurden nach dem
Test wieder entfernt.

### TICKET-F02 (matched_rag_docs + "Entscheidung erfassen"-Gate)

Gleiches Muster wie F01 (docker build/run gegen echte Daten + Logik-Verifikation
ohne Browser über JavaScriptCore), erneut durchgeführt gegen frisch
regenerierte Daten:

1. **Docker-Image neu gebaut:**
   `docker build -t pmplus-step7-active-learning -f step7-active-learning/Dockerfile step7-active-learning/`
2. **`pgp_priorisierung.csv`/`tau_vergleich.csv` frisch regeneriert** (Images
   `pmplus-step5-pgp` mit `AS_OF_DATE=2026-01-01`, `pmplus-step6-calibration`
   mit `MOCK_LLM_RESPONSE=1`, beide gegen `step3-erp-simulation/output_2025/`
   als `shared_data`-Mount, `step5-pgp` zusätzlich mit
   `step4-context-engineering/rag_documents:/app/rag_documents:ro`) – 20
   offene Aufträge, 16 mit RAG-Treffer (`SLA-BECKS-001`,
   `vertrauensstufe: intern-verifiziert`), 4 ohne (`matched_rag_docs: []`,
   kein Fake-`"nan"`-Eintrag mehr, siehe oben). Ampel-Verteilung: 15 robust /
   2 trügerische Ruhe / 3 klarer Review-Fall.
3. **Backend-Container gestartet** (`-p 8007:8000`, gleiche Mounts plus
   `rag_documents:ro`), `GET /health` und `GET /eskalationen` live per `curl`
   abgefragt – echte JSON-Antwort erhalten und geprüft: `matched_rag_docs` ist
   ein Top-Level-Feld (nicht unter `llm`), `llm`-Objekt enthält nachweislich
   keinen `matched_rag_docs`-Key.
4. **JS-Syntaxprüfung des echten, geänderten `app.js`** (JavaScriptCore via
   `osascript -l JavaScript`, kein Node.js verfügbar): `new Function(source)`
   parst fehlerfrei.
5. **Ausführung der echten, neuen `app.js`-Funktionen** (nicht nachgebaut,
   Original-Modul mit Browser-Stubs für `window`/`document`/`module`/`fetch`)
   gegen die echte `GET /eskalationen`-Antwort, 26 automatisierte Checks, alle
   bestanden:
   - `istVertrauensstufeUnbekannt` korrekt für `null`/`undefined`/`""` (true)
     und einen echten Wert wie `"intern-verifiziert"` (false).
   - `renderRagDocs` zeigt für einen echten Auftrag mit RAG-Treffer Titel und
     Vertrauensstufe korrekt; für einen echten Auftrag ohne Treffer den
     expliziten "Keine RAG-Dokumente…"-Hinweis statt eines leeren Abschnitts;
     für einen synthetischen Fall mit `vertrauensstufe: null` (kommt in den
     aktuell kalibrierten Live-Daten nicht vor, da nur das bekannte
     SLA-Dokument referenziert wird) das Warnsymbol, den Text
     "Vertrauensstufe unbekannt" und die CSS-Klasse `rag-vertrauen-unbekannt`.
   - `renderOrderCard` enthält weiterhin `assessment-box pgp` und
     `assessment-box llm` als getrennte Blöcke (Leitplanke 1, Regressionscheck)
     UND den neuen `rag-box`-Abschnitt danach (Reihenfolge geprüft).
   - `renderOrderCard`/`renderDecisionRow`: der `decision-btn` trägt das
     `disabled`-Attribut, solange der Auftrag nicht als "betrachtet" markiert
     ist, und verliert es (samt Hinweistext), sobald `viewed=true` – geprüft
     für beide Zustände.
   - `pgp !== llm` weiterhin für alle 20 echten Aufträge (Leitplanke 1,
     Regressionscheck), `ampelMeta` weiterhin fail-safe für unbekannte Werte.
6. **HTML-Wohlgeformtheit** von `index.html` (Python `html.parser`) erneut
   geprüft, plus Abgleich aller in `app.js` per `getElementById` referenzierten
   IDs gegen `index.html` (`retry-btn` fehlt dort weiterhin absichtlich – wird
   dynamisch in `renderError`/`renderHinweis` erzeugt, unverändert seit F01).
   `style.css` auf ausgeglichene `{`/`}`-Klammern geprüft (65/65).

**Nicht geprüft** (weil ohne echten Browser nicht möglich, wie schon bei F01):
tatsächliches CSS-Rendering/Layout der neuen `rag-box`/`decision-row`-Bereiche,
Klickverhalten im echten DOM (insbesondere der Live-Übergang
disabled→enabled beim ersten Öffnen von "Details" sowie der Konsolen-Log/
UI-Hinweis beim Klick auf "Entscheidung erfassen"), Verhalten bei sehr kleinen
Bildschirmbreiten, Screenreader-Verhalten der neuen `aria-disabled`/
`aria-live`-Attribute. Sollte vor einer echten Demo mit Jens durch einen
kurzen manuellen Check in einem echten Browser geschlossen werden.

Erzeugte Test-CSVs (`pgp_priorisierung.csv`, `tau_vergleich.csv` in
`step3-erp-simulation/output_2025/`) und der Test-Container wurden nach dem
Test wieder entfernt – reine Laufzeit-Artefakte, nicht Teil des Repos. Es
wurde keine `POST /entscheidung` aufgerufen (F02 hat keine echte
Entscheidungserfassung), daher ist auch keine `shared/feedback`-Datenbank
entstanden.

### TICKET-F01 (historisch, unverändert gültig)

1. **Echter End-to-End-Datenfluss gegen den echten Backend-Container:**
   - `docker build -t pmplus-step7-active-learning -f step7-active-learning/Dockerfile step7-active-learning/`
   - `pgp_priorisierung.csv`/`tau_vergleich.csv` frisch regeneriert über die
     vorhandenen Images `pmplus-step5-pgp` und `pmplus-step6-calibration`
     (`MOCK_LLM_RESPONSE=1`), gegen die echten ERP-Daten aus
     `step3-erp-simulation/output_2025/` (als `shared_data`-Volume gemountet) –
     20 offene Aufträge, Ampel-Verteilung 14 robust / 3 trügerische Ruhe /
     3 klarer Review-Fall.
   - Backend-Container gestartet (`-p 8007:8000`), `GET /health` und
     `GET /eskalationen` live per `curl` abgefragt – echte JSON-Antwort erhalten
     und gegen die Response-Struktur aus dem Ticket geprüft.
2. **JS-Syntaxprüfung des echten `app.js`** in einer echten JS-Engine
   (JavaScriptCore, über `osascript -l JavaScript` auf macOS – kein Node.js in
   dieser Umgebung verfügbar): `new Function(source)` parst fehlerfrei.
3. **Ausführung der echten Kernlogik aus `app.js`** (nicht nachgebaut, sondern
   das echte Modul, minimal mit Browser-Stubs für `window`/`document`/`fetch`
   versehen) in derselben JS-Engine, gegen die **echte** `GET /eskalationen`-
   Antwort:
   - `sortByPgpRank` liefert eine streng aufsteigende Rangfolge (1..20).
   - `ampelMeta(status).label` erzeugt für alle drei in den echten Daten
     vorkommenden Zustände exakt den Wortlaut aus `Konzept-README.md`
     ("Robuste Übereinstimmung" / "Trügerische Ruhe" / "Klarer Fall für
     Experten-Review").
   - `ampelMeta("unbekannt")` und ein frei erfundener, unbekannter Status-String
     liefern beide `"Status unbekannt"` – nie `"Robuste Übereinstimmung"`
     (Fail-safe-Anforderung aus dem Ticket).
   - `filterAttention` blendet bei aktivem Filter zuverlässig alle
     `robuste_uebereinstimmung`-Fälle aus.
   - `pgp`/`llm` bleiben in den Eingabedaten und im Rendering zwei getrennte
     Objekte (Leitplanke 1) – geprüft an echten Daten.
4. **`renderOrderCard` end-to-end ausgeführt** (echte Funktion, echte Daten:
   ein realer `klarer_fall_fuer_review`-Auftrag aus der Live-Antwort sowie ein
   synthetischer `unbekannt`-Fall, da dieser Zustand in den aktuell kalibrierten
   Daten nicht vorkommt) – erzeugtes HTML manuell inspiziert und auf
   Struktur/Wortlaut geprüft (u. a.: PGP-Block und LLM-Block als getrennte
   `<div>`s, `ampel-badge` trägt exakt den erwarteten Text, `unbekannt`-Fall
   enthält nachweislich **nicht** den Text "Robuste Übereinstimmung").
5. **HTML-Wohlgeformtheit** von `index.html` per Python `html.parser` geprüft
   (alle Tags korrekt verschachtelt/geschlossen) und alle in `app.js` per
   `getElementById` referenzierten IDs gegen die tatsächlich in `index.html`
   vorhandenen IDs abgeglichen.

**Nicht geprüft** (weil ohne echten Browser nicht möglich): tatsächliches
CSS-Rendering/Layout, Klickverhalten im echten DOM, Verhalten bei sehr kleinen
Bildschirmbreiten, Screenreader-Verhalten. Diese Lücke sollte vor einer echten
Demo mit Jens durch einen kurzen manuellen Check in einem echten Browser
geschlossen werden.

Erzeugte Test-CSVs (`pgp_priorisierung.csv`, `tau_vergleich.csv` in
`step3-erp-simulation/output_2025/`) sowie `shared/feedback/entscheidungen.db`
wurden nach dem Test wieder entfernt – reine Laufzeit-Artefakte, nicht Teil des
Repos.
