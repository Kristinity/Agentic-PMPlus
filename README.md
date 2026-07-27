# PMPlus – Docker-Workspace

Ein Container pro Step aus dem Agentic-PMPlus-Konzept. Jeder Step ist isoliert
(eigenes `Dockerfile`, eigene `requirements.txt`, eigenes `main.py`), teilt sich
aber ein gemeinsames Datenverzeichnis (`shared/`), damit z. B. die simulierten
ERP-CSVs aus Step 3 in Step 4/5 weiterverwendet werden können.

## Struktur

```
PMPlus/
├── docker-compose.yml
├── RUNBOOK.md             # -> kompletter Ablauf, um den Live-Prototyp zu bedienen
├── .env.example           # -> nach .env kopieren, ANTHROPIC_API_KEY eintragen
├── setup-branches.sh      # Prestep: legt Git-Branches pro Step an (auf dem Host, nicht im Container)
├── shared/
│   ├── data/             # z.B. simulierte ERP-CSVs (Step 3), pgp_priorisierung.csv (5), tau_vergleich.csv (6)
│   ├── feedback/         # Entscheidungshistorie (SQLite, Step 7)
│   ├── context/          # RAG-Index / Context Engineering (Step 4)
│   └── models/           # trainierte PGP-Modelle (Step 5)
├── prestep/               # Setup-Check, keine fachliche Logik
├── step1-feasibility/     # Recherche-Agent (Feasibility)
├── step2-limits/          # Grenzen technisch/ökonomisch
├── step3-erp-simulation/  # ERP-Daten simulieren
├── step4-context-engineering/  # RAG aufsetzen
├── step5-pgp/             # Preference GP (μ, σ)
├── step6-calibration/     # unabhängiges LLM-Ranking + τ/σ-Schwellenwerte (Bootstrap-Kalibrierung)
├── step7-active-learning/ # Active Learning Loop: FastAPI-Server + Frontend (frontend/)
└── step8-live-test/       # Userstories + Produkt-Backlog; main.py bleibt Platzhalter
```

## Setup

1. **Branches anlegen** (einmalig, auf dem Host-Git-Repo):
   ```bash
   ./setup-branches.sh
   ```
   Damit du pro Step in einem eigenen Branch arbeiten kannst.

2. **API-Key hinterlegen:**
   ```bash
   cp .env.example .env
   # ANTHROPIC_API_KEY=... eintragen
   ```

3. **Alle Container bauen:**
   ```bash
   docker compose build
   ```

## Nutzung

**Einen einzelnen Step laufen lassen** (z. B. Step 3):
```bash
docker compose up step3-erp-simulation
```

**Alle Steps der Reihe nach laufen lassen** (respektiert die `depends_on`-Kette):
```bash
docker compose up
```

**Interaktiv in einem Step arbeiten** (z. B. um Step 5 zu entwickeln):
```bash
docker compose run --rm step5-pgp bash
```

**In VS Code direkt in einem Step-Container öffnen:**
Die `.devcontainer/<step>/devcontainer.json`-Dateien sind bereits vorbereitet.
`Dev Containers: Reopen in Container` → passenden Step auswählen.

## Live-Prototyp bedienen

Kompletter Ablauf (Setup → `docker compose up` → Browser öffnen → Mock- vs.
Echt-Modus für Step 6 → bekannte Grenzen): **[RUNBOOK.md](RUNBOOK.md)**.

## Stand der Umsetzung

- **Implementiert & Docker-getestet:** Step 3 (ERP-CSV-Generator), Step 4
  (RAG-Kontext-Assemblierung), Step 5 (PGP mit μ/σ-Ausgabe), Step 6
  (unabhängiges LLM-Ranking + τ + Bootstrap-Kalibrierung) und Step 7
  (FastAPI-Server + Active-Learning-Endpunkte + Frontend unter
  `step7-active-learning/frontend/`) haben funktionsfähige `main.py`/Server.
  MVP-Ticketstand: `step8-live-test/Produkt-Backlog/README.md`.
- **Recherche/Analyse statt Code:** Step 1 (`Benchmark-Analyse.md`, `Instructions.md`)
  und Step 2 (`Systemgrenzen.md`) haben ihr eigentliches Ergebnis als Markdown-Dokument,
  `main.py` bleibt dort bewusst Platzhalter.
- **Noch offen (Post-MVP):** F06 (Kalibrierungs-Gesundheit), F07
  (Kosten-Transparenz) – siehe `step8-live-test/Produkt-Backlog/README.md`.
  Step 8 (`step8-live-test/main.py`) bleibt bewusst Platzhalter; sein
  eigentlicher Inhalt sind die Userstories/das Produkt-Backlog in
  `step8-live-test/`.
