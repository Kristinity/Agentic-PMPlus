# step7-active-learning/frontend – Auftrags-Warteschlange + Eskalations-Review (TICKET-F01/F02)

Erster und zweiter Bildschirm des Live-Prototyps für Jens Pirinski
(Produktionsplaner, Krasser Spass GmbH, siehe `step8-live-test/Userstories.md`).
Zeigt `GET /eskalationen` sortiert nach PGP-Rang, mit Ampel-Status in der
Sprache aus `Konzept-README.md`. Jede Auftragskarte lässt sich aufklappen
("Details") und zeigt dann PGP-Einschätzung, LLM-Einschätzung und genutzte
RAG-Dokumente (inkl. Vertrauensstufe, TICKET-F02) jeweils in eigenen,
getrennten Abschnitten.

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
  "Entscheidung erfassen"-Button.
- `app.js` – Fetch gegen `GET /eskalationen`, Sortierung, Rendering, Fail-safe-
  Fehlerbehandlung. Kein externes Paket, keine Build-Pipeline. TICKET-F02
  ergänzt `renderRagDocs` (RAG-Treffer + Vertrauensstufe je Auftrag) und die
  Sichtbarkeits-/Reihenfolge-Regel für "Entscheidung erfassen"
  (`renderDecisionRow`/`markDetailsViewed`/`detailsViewedOrderIds`).

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

**Kein Zugriff auf einen echten Browser in dieser oder der vorherigen Session**
– es gibt in dieser Umgebung kein Tool, das ein sichtbares/gerendertes
Browserfenster prüfen kann. Deshalb ausdrücklich: **nicht visuell in einem
Browser bestätigt**, weder für F01 noch für F02.

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
