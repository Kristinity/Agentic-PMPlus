"""
step7-active-learning - Agentic-PMPlus

TICKET-B01 (step8-live-test/Produkt-Backlog/TICKET-B01-Server-Grundgeruest.md):
FastAPI-Server-Grundgeruest. Step 7 ist im Gegensatz zu Steps 3-6 kein
Batch-Skript, sondern ein laufender Server - ein Mensch (Produktionsplaner)
muss eskalierte Faelle interaktiv pruefen und entscheiden koennen, siehe
step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md Abschnitt 1.

Aktueller Umfang (nur B01): Server-Grundgeruest + Health-Check. Die
eigentlichen Endpunkte (GET /eskalationen, POST /entscheidung, GET /verlauf)
folgen in separaten Tickets (B04, B05, B06), siehe
step8-live-test/Produkt-Backlog/.
"""

import os

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Agentic-PMPlus - step7-active-learning")


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "service": "step7-active-learning"}


def main():
    port = int(os.environ.get("PORT", "8000"))
    print("=== step7-active-learning ===")
    print(f"FastAPI-Server startet auf Port {port} (TICKET-B01 - nur Health-Check, "
          f"weitere Endpunkte folgen in B04/B05/B06)")
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
