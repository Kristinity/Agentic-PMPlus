# PMPlus – Docker-Workspace

Ein Container pro Step aus dem Agentic-PMPlus-Konzept. Jeder Step ist isoliert
(eigenes `Dockerfile`, eigene `requirements.txt`, eigenes `main.py`), teilt sich
aber ein gemeinsames Datenverzeichnis (`shared/`), damit z. B. die simulierten
ERP-CSVs aus Step 3 in Step 4/5 weiterverwendet werden können.

## Struktur

```
PMPlus/
├── docker-compose.yml
├── .env.example          # -> nach .env kopieren, ANTHROPIC_API_KEY eintragen
├── setup-branches.sh     # Prestep: legt Git-Branches pro Step an (auf dem Host, nicht im Container)
├── shared/
│   ├── data/             # z.B. simulierte ERP-CSVs (Step 3)
│   ├── context/          # RAG-Index / Context Engineering (Step 4)
│   └── models/           # trainierte PGP-Modelle (Step 5)
├── prestep/               # Setup-Check, keine fachliche Logik
├── step1-feasibility/     # Recherche-Agent (Feasibility)
├── step2-limits/          # Grenzen technisch/ökonomisch
├── step3-erp-simulation/  # ERP-Daten simulieren
├── step4-context-engineering/  # RAG aufsetzen
├── step5-pgp/             # Preference GP (μ, σ)
├── step6-calibration/     # τ/σ-Schwellenwerte (Risk-Coverage)
├── step7-active-learning/ # Active Learning Loop
└── step8-live-test/       # Live-Test / Integration
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

## Nächste Schritte

Aktuell enthält jedes `main.py` nur ein Platzhalter-Skript. Fachliche Logik pro
Step ergänzen (siehe README-Konzeptbeschreibung, Steps 1–8). Steps 4, 5 und 7
sind als "PRÄMISSE"/"KONZEPT" markiert – dort lohnt es sich, zuerst grob zu
prototypen, bevor die Docker-Struktur weiter verfeinert wird.
