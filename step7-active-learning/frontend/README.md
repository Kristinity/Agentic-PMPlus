# step7-active-learning/frontend – Auftrags-Warteschlange (TICKET-F01)

Erster Bildschirm des Live-Prototyps für Jens Pirinski (Produktionsplaner, Krasser
Spass GmbH, siehe `step8-live-test/Userstories.md`). Zeigt `GET /eskalationen`
sortiert nach PGP-Rang, mit Ampel-Status in der Sprache aus `Konzept-README.md`.

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
  können/müssen.
- `app.js` – Fetch gegen `GET /eskalationen`, Sortierung, Rendering, Fail-safe-
  Fehlerbehandlung. Kein externes Paket, keine Build-Pipeline.

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

## Scope-Entscheidung: `matched_rag_docs` NICHT auf diesem Bildschirm

`GET /eskalationen` liefert `matched_rag_docs` inkl. Vertrauensstufe, aber F01
(Warteschlange) zeigt sie bewusst **nicht** – das ist laut `Frontend-Backlog.md`
Abschnitt 2 explizit Akzeptanzkriterium von **F02** (Eskalations-Review), wo die
LLM-Begründung im Kontext der RAG-Treffer geprüft wird. Zusätzlicher, während des
Live-Tests entdeckter Grund: für Aufträge ohne echten RAG-Treffer liefert die
aktuelle `rag_lookup.py`/`api.py`-Kombination (`TICKET-B03`/`B04`) einen
irreführenden Eintrag `{"doc_id": "nan", "title": null, "vertrauensstufe": null}`
statt einer leeren Liste – Ursache: `pandas` liest eine leere
`matched_rag_docs`-Zelle als `NaN` (float), und `not matched_rag_docs` in
`rag_lookup.resolve_matched_docs` ist für `NaN` `False` (NaN ist in Python
"truthy"), wodurch `str(nan)` → `"nan"` als vermeintliche Dokument-ID
durchgereicht wird. Beobachtet beim Live-Test gegen die echte, frisch generierte
`tau_vergleich.csv` (siehe unten) – kein erfundener Fall. Das ist ein
**Backend-Datenqualitätsproblem** (`step7-active-learning/rag_lookup.py`,
außerhalb des Scopes von F01/frontend-dev), hier bewusst nicht mitgefixt, aber
dokumentiert, damit es beim Bau von F02 (das dieses Feld tatsächlich anzeigen
muss) nicht unbemerkt in die UI durchsickert.

## Was getestet wurde (und was nicht)

**Kein Zugriff auf einen echten Browser in dieser Session** – es gibt in dieser
Umgebung kein Tool, das ein sichtbares/gerendertes Browserfenster prüfen kann.
Deshalb ausdrücklich: **nicht visuell in einem Browser bestätigt.** Stattdessen
wurde Folgendes tatsächlich ausgeführt und verifiziert:

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
