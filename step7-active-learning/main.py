"""
step7-active-learning/main.py - Agentic-PMPlus

TICKET-B01: startet einen FastAPI/uvicorn-Server statt eines Einmal-Batch-Laufs wie Steps
3-6 (Begruendung: Architektur-Backend-Frontend-Schnittstelle.md Abschnitt 1 - Step 7 ist
inhaerent interaktiv, ein Mensch muss eskalierte Faelle in Echtzeit pruefen koennen).
Endpunkt-Definitionen liegen in api.py (Modulstruktur siehe Architektur-Doc Abschnitt 4).
"""

import os

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print("=== step7-active-learning ===")
    print(f"Starte API-Server auf 0.0.0.0:{port} (Endpunkte: siehe api.py)")
    uvicorn.run("api:app", host="0.0.0.0", port=port)
