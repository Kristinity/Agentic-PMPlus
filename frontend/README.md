# Frontend – Agentic-PMPlus

**Rolle:** frontend-dev. Umsetzung von `step8-live-test/Produkt-Backlog/TICKET-F01`,
`F02`, `F03`, `F05`, `F06`, `F07` (F04 existiert nicht, siehe Backlog).
**Grundlage:** `step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md`
Abschnitt 2, `Konzept-README.md`, `step7-active-learning/Frontend-Backlog.md`,
`.claude/agents/role/frontend-dev.md`.

## Stack-Entscheidung: Vanilla HTML/CSS/JS, kein Build-Schritt

Bewusst **kein** React/Vite/Bundler, obwohl Node/npm in der Umgebung verfügbar wären.
Begründung:

- Das restliche Projekt ist konsequent schlank (reine Python-Skripte, keine schweren
  Frameworks) – ein Node-Toolchain-Unterbau (package.json, node_modules, Build-Step) wäre
  ein Bruch mit dieser Linie für eine Handvoll Bildschirme mit überschaubarer Interaktion.
- Kein Build-Schritt heißt: `docker build` braucht keinen `npm install`-Schritt (der in
  dieser Sandbox ohnehin über einen Proxy laufen müsste) und der Production-Container
  bleibt minimal (`python:3.12-slim`, keine zusätzlichen Abhängigkeiten).
- Die UI-Logik ist Zustandsverwaltung pro Bildschirm + Fetch-Aufrufe – kein Fall, der ein
  Reactivity-Framework zwingend braucht.

ES-Module (`<script type="module">`) werden direkt im Browser geladen, kein Transpiling
nötig (Zielumgebung: interne Planer-Workstations mit aktuellem Browser).

## Warum ein eigener `server.py`-Proxy statt CORS im Backend

Frontend und Backend laufen als getrennte Docker-Services auf getrennten Ports (Backend
`step7-active-learning:8000`, Frontend hier `:8080`) – das hat schon
`Architektur-Backend-Frontend-Schnittstelle.md` Abschnitt 1 so vorgesehen ("ein künftiger
Frontend-Service braucht eine Port-Freigabe"). Der Browser blockiert plain `fetch()`-Calls
über Origin-Grenzen (Same-Origin-Policy) ohne CORS-Header.

Statt dafür `step7-active-learning/api.py` anzufassen (das wäre ein Eingriff in
backend-dev-Code, siehe Scope-Disziplin in `.claude/agents/role/frontend-dev.md`), macht
`server.py` (Python-Standardbibliothek: `http.server` + `urllib.request`, keine
Zusatz-Abhängigkeit) alle Browser-Aufrufe zu Same-Origin-Aufrufen: `/api/eskalationen`
wird intern 1:1 an `BACKEND_URL + /eskalationen` weitergereicht. Damit bleibt der
gesamte Backend-Code unangetastet – ein bewusster, dokumentierter Architektur-Entscheid,
kein Zufall.

## Bildschirmstruktur (folgt Frontend-Konzept Abschnitt 2.3)

| Route | Ticket | Bildschirm |
|---|---|---|
| `#/` | F01 | Auftrags-Warteschlange (Ampel-Status) |
| `#/order/:orderId` | F02 + F03 | Eskalations-Review (PGP/LLM getrennt) → Entscheidungserfassung |
| `#/verlauf` | F05 (+ F07-Hinweis) | Audit-Trail |
| `#/kalibrierung` | F06 | Kalibrierungs-Gesundheit (nur Footer-Link, nicht Hauptnav) |

**Bewusste Abweichung vom 1:1-Screen-Mapping:** F02 (Review) und F03 (Entscheidung) sind
als EIN Bildschirm mit zwei gestuft freigeschalteten Phasen gebaut, nicht als zwei
getrennte Routen. Begründung: die AC aus TICKET-F02 verlangt, dass "erst beide
Einschätzungen [PGP+LLM] betrachtet, dann erst der Wechsel zur Entscheidungserfassung
möglich" ist. Zwei getrennte Routen ließen sich durch einen direkten Link/Browser-Verlauf
umgehen; eine einzige Seite mit einer Phase-Sperre (Entscheidungsformular ist erst nach
Klick auf "Beide Einschätzungen geprüft" sichtbar) erzwingt die Reihenfolge robuster.
PGP- und LLM-Karte bleiben dabei zwei vollständig getrennte DOM-Elemente/Spalten – die
inhaltliche Trennung (nicht verhandelbare Leitplanke 1) ist davon unberührt.

## Bekannte Einschränkung: Propagationsvorschau vor dem finalen Bestätigen

TICKET-F03 verlangt, `propagierte_faelle` **vor** dem finalen Bestätigen anzuzeigen. Das
Backend hat aktuell aber **keinen side-effect-freien Vorschau-Endpunkt** – `POST
/entscheidung` schreibt sofort in die SQLite-DB und propagiert sofort (siehe `api.py`
TICKET-B05/B08). Es gibt keine Möglichkeit, die echte Propagationsliste zu kennen, ohne
den Schreibvorgang tatsächlich auszulösen; sie clientseitig nachzurechnen würde bedeuten,
`propagation.py`s Ähnlichkeitsheuristik (inkl. `product_id`, das `GET /eskalationen`
nicht einmal ausliefert) im Frontend zu duplizieren – explizit nicht Aufgabe von
frontend-dev (Scope-Disziplin: keine neue fachliche PGP-/Kalibrierungslogik).

Umgesetzte Lösung (zweistufiger Bestätigungsdialog, siehe `js/views/orderDetail.js`):

1. Formular ausfüllen → "Weiter zur Bestätigung" (noch kein Server-Call).
2. Bestätigungs-Karte zeigt die geplante Entscheidung, warnt explizit, dass Propagation
   passieren **kann**, und erklärt, dass die exakte Liste erst nach dem Absenden bekannt
   ist. Erst ein zusätzlicher, unübersehbar als "Jetzt verbindlich entscheiden" beschrifteter
   Button (rot, mit vorher zu setzender Bestätigungs-Checkbox) löst den echten `POST
   /entscheidung` aus.
3. Die Antwort (inkl. der echten `propagierte_faelle`-Liste) wird sofort auf derselben
   Seite angezeigt, bevor der Planer weiterklickt – kein verstecktes Nachwirken, aber
   technisch *nach* statt strikt *vor* der Ausführung, weil es keine Alternative ohne
   Backend-Änderung gibt.

**Empfehlung an backend-dev:** ein `dry_run`-Flag an `POST /entscheidung` (oder ein
eigener `GET /entscheidung/vorschau`-Endpunkt) würde eine echte Vor-Bestätigung ohne
Seiteneffekt ermöglichen. Bis dahin ist der oben beschriebene Zwei-Stufen-Dialog die
ehrlichste Annäherung ohne Backend-Code anzufassen oder Daten zu erfinden.

## Korrektur zur wörtlichen TICKET-F07-Formulierung

TICKET-F07 verlangt, sichtbar zu machen, dass "ein LLM-Ranking nur für Eskalationsfälle
angefordert wurde, nicht pauschal für jeden Auftrag". Ein Blick in
`step6-calibration/main.py` zeigt: das stimmt so nicht ganz – der LLM-Call liefert **eine
gemeinsame Rangfolge für alle aktuell offenen Aufträge in einem Planungslauf**, nicht nur
für die, die sich im Nachhinein als Eskalation herausstellen (das kann er auch nicht,
da τ erst aus dem Vergleich mit dem LLM-Rang berechnet wird – klassisches
Henne-Ei-Problem). Der tatsächlich zutreffende, kostenrelevante Fakt ist: **ein Batch-Call
pro Planungslauf für alle offenen Aufträge, kein Call pro Auftrag und kein zusätzlicher
Call pro Eskalation.** Genau das steht so im UI (Review-Bildschirm + Audit-Trail), nicht
die wörtliche, durch den Code nicht gedeckte Ticket-Formulierung – siehe
`step6-calibration/main.py` (`call_llm_ranking` wird einmal pro Lauf für das gesamte
Batch aufgerufen, nicht pro `order_id`).

## Lokal starten (ohne Docker)

```bash
BACKEND_URL=http://localhost:8000 PORT=8080 python3 server.py
```

Voraussetzung: das Backend (`step7-active-learning/main.py`) läuft bereits (z. B. auf
Port 8000, siehe `step7-active-learning/README`/Architektur-Doc).
