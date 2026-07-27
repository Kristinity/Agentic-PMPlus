# RUNBOOK – Live-Prototyp starten

Diese Anleitung ist die einzige, die noetig ist, um den Prototyp fuer Jens
Pirinski (Produktionsplaner, Krasser Spass GmbH) tatsaechlich zu bedienen –
vom leeren Checkout bis zum Klick durch die Auftrags-Warteschlange im
Browser. Sie ersetzt kein einzelnes README (`step7-active-learning/frontend/README.md`
z. B. dokumentiert die Frontend-Architektur/Testmethodik im Detail), sondern
buendelt den Gesamtablauf, der bisher nur ueber einzelne manuelle
`docker run`-Befehle in der Entwicklung existierte.

## 1. Voraussetzungen

- Docker Desktop (getestet mit Docker 29 / Compose v5)
- Ein Anthropic-API-Key **nur**, wenn Step 6 eine echte (nicht simulierte)
  unabhaengige LLM-Einschaetzung liefern soll – siehe Abschnitt 4.

## 2. Einmaliges Setup

```bash
cp .env.example .env
```

`.env` funktioniert unveraendert (Mock-Modus, siehe unten). Fuer eine echte
LLM-Kalibrierung `ANTHROPIC_API_KEY` eintragen und `MOCK_LLM_RESPONSE=0`
setzen – Details und Fallstricke in Abschnitt 4.

## 3. Starten

```bash
docker compose up --build
```

Das laeuft die gesamte Kette in der richtigen Reihenfolge durch (jeder
Batch-Schritt wartet jetzt per `condition: service_completed_successfully`
auf den vorherigen – vorher lief das nicht zuverlaessig):

1. `prestep` → `step1-feasibility` → `step2-limits` (Recherche/Grenzen,
   liefern Markdown-Ergebnisse, keine Daten fuer die Pipeline)
2. `step3-erp-simulation` – generiert die ERP-CSVs nach `shared/data/`. Feste
   `START_DATE=2025-01-01`/`WEEKS=53` reproduzieren exakt das Datenset, gegen
   das der gesamte Prototyp bisher getestet wurde (entspricht dem
   committeten `step3-erp-simulation/output_2025/`); `company_profile.example.yaml`
   setzt `random_seed: 42`, der Lauf ist also deterministisch.
3. `step4-context-engineering` – baut den RAG-Kontext.
4. `step5-pgp` – trainiert den PGP, schreibt `pgp_priorisierung.csv`
   (fester `AS_OF_DATE=2026-01-01`, sonst waere "heute" nach jedem Neustart
   in der Zukunft der simulierten Auftraege).
5. `step6-calibration` – holt die unabhaengige LLM-Rangfolge, berechnet tau,
   schreibt `tau_vergleich.csv`.
6. `step7-active-learning` – startet den FastAPI-Server auf Port **8007**
   und bleibt laufen (kein Batch-Schritt).
7. `frontend` – liefert `step7-active-learning/frontend/` per nginx auf Port
   **8080** aus (vorher nur manuell per `python3 -m http.server` moeglich,
   fehlte komplett in `docker-compose.yml`).
8. `step8-live-test` ist ein bewusster Platzhalter ohne Fachlogik, laeuft mit,
   liefert aber keinen fuer die Bedienung relevanten Output.

## 4. Bedienen

Browser oeffnen: **http://localhost:8080**

- Warteschlange mit Ampel-Status (F01), pro Auftrag Details mit PGP- und
  LLM-Begruendung + RAG-Belegen (F02), Entscheidung erfassen inkl.
  Vorschau der propagierten Faelle (F03).
- Verlaufsseite: **http://localhost:8080/verlauf.html** (F05) – Herkunft
  jeder Entscheidung (Mensch vs. Agent-Propagation) nachvollziehbar.
- API direkt: **http://localhost:8007/health**, **http://localhost:8007/eskalationen**.
- Neue Aufträge hochladen und priorisieren lassen (ohne Kommandozeile/Docker
  direkt zu bedienen): **http://localhost:8501** (Streamlit,
  `step9-upload-interface/`). Die ERP-Stammdaten (Auftragshistorie,
  Maschinen, Lager, Störungen) sind fixer Teil des Context Engineering
  (`step3-erp-simulation/output_2026/`, read-only gemountet) und werden
  NICHT hochgeladen – hochgeladen werden ausschließlich neue Aufträge nach
  einem herunterladbaren Auftragstemplate; sie werden der bestehenden
  Auftragslage hinzugefügt und im Kontext aller offenen Aufträge priorisiert
  (mit 🆕-Markierung im Ergebnis). Erzeugt nur ein Ergebnis (Tabelle +
  CSV-Download) – ändert NICHT die laufende Warteschlange von Step 7; für
  Review/Entscheidung weiterhin Port 8080 verwenden.

Entscheidungen landen in `shared/feedback/entscheidungen.db` (SQLite, per
Volume ausserhalb des Containers – ueberlebt `docker compose down` und
Neustarts; erst `docker compose down -v` oder manuelles Loeschen der Datei
setzt den Verlauf zurueck).

## 5. Mock- vs. Echt-Modus fuer Step 6 (LLM-Ranking)

Standardmaessig laeuft `docker compose up` **ohne** ANTHROPIC_API_KEY (Mock-
Modus, `MOCK_LLM_RESPONSE=1` in `.env.example`/`.env`) – bewusst so
voreingestellt, damit der Prototyp ohne Bezahlkonto sofort startet. Im
Mock-Modus ist `tau` **nicht** aussagekraeftig (die "LLM-Rangfolge" ist eine
simulierte Platzhalter-Antwort, siehe Kommentar in `step6-calibration/main.py`).

Fuer eine echte, unabhaengige LLM-Einschaetzung:

1. In `.env`: `MOCK_LLM_RESPONSE=0` und `ANTHROPIC_API_KEY=sk-ant-...` (den
   **vollstaendigen** Key, nicht einen in einer UI abgeschnittenen/maskierten
   Ausschnitt – ein maskierter Key sieht aus wie `sk-ant-api03-hs5...EgAA`
   und ist **nicht** der echte Wert).
2. Sicherstellen, dass es der richtige Key ist: **Guthaben auf
   `claude.ai/settings/usage` (Consumer-Abo) ist etwas komplett anderes als
   Guthaben auf `platform.claude.com/dashboard`** (Developer-Platform-API,
   das ist der Pool, aus dem `step6-calibration` tatsaechlich abrechnet). Ein
   Consumer-Abo-Guthaben von x€ bedeutet nicht automatisch nutzbares
   API-Guthaben.
3. `docker compose up --build step6-calibration` (bzw. den ganzen Stack neu
   starten) – ein 404 auf das Modell bedeutet meist ein veraltetes/falsches
   Modellkuerzel, kein Kontingent-Problem.

## 6. Neu generieren / zuruecksetzen

`docker compose up` ist bei jedem Durchlauf idempotent (fester Seed/fixe
Stichtage) – erneutes Ausfuehren erzeugt dieselben `shared/data/*.csv` neu.
Um wirklich bei null anzufangen (inkl. Entscheidungsverlauf):

```bash
docker compose down
rm -rf shared/data/* shared/feedback/*
docker compose up --build
```

## 7. Bekannte Grenzen (bewusst nicht Teil dieses Runbooks geloest)

- **Bootstrap-Kalibrierung**: `tau0`/`sigma0` in Step 6 basieren auf derselben
  Heuristik, mit der der PGP selbst trainiert wurde – zirkulaer, kein
  echter Validierungsdatensatz. Siehe Modulkopf `step6-calibration/main.py`
  und `TICKET-B07`.
- **F06 (Kalibrierungs-Gesundheit)** und **F07 (Kosten-Transparenz)** sind
  nicht gebaut (Post-MVP, siehe `step8-live-test/Produkt-Backlog/README.md`).
- **Kein Auth/keine Nutzertrennung** – bewusste Prototyp-Vereinfachung
  (`allow_origins="*"` in `step7-active-learning/main.py`), vor einem echten
  Pilotbetrieb zu schliessen.
- **Frontend-Visualtest**: Klick-Verhalten und CSS-Rendering wurden bisher
  nur per Logik-Test (JavaScriptCore) geprueft, nicht in einem echten
  Browser durch einen Menschen – vor einer Demo einmal manuell durchklicken.
