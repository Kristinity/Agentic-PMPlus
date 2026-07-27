"""
step7-active-learning - Agentic-PMPlus

TICKET-B01 (step8-live-test/Produkt-Backlog/TICKET-B01-Server-Grundgeruest.md):
FastAPI-Server-Grundgeruest. Step 7 ist im Gegensatz zu Steps 3-6 kein
Batch-Skript, sondern ein laufender Server - ein Mensch (Produktionsplaner)
muss eskalierte Faelle interaktiv pruefen und entscheiden koennen, siehe
step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md Abschnitt 1.

TICKET-B02: SQLite-Persistenz fuer die Entscheidungshistorie (siehe store.py),
beim Serverstart initialisiert.

TICKET-B04: GET /eskalationen (siehe api.py).

TICKET-F01 (step8-live-test/Produkt-Backlog/TICKET-F01-Warteschlange.md):
CORSMiddleware ergaenzt, damit step7-active-learning/frontend/ (statisches
HTML/JS, ueber einen eigenen einfachen Webserver auf einem anderen Port
ausgeliefert, siehe frontend/README.md) im Browser tatsaechlich gegen diese
API fetchen kann - ohne CORS-Header blockiert der Browser die Antwort
serverseitig unveraendert, nur das Lesen im JS schlaegt fehl. allow_origins="*"
ist eine bewusste Prototyp-Vereinfachung (keine Auth/keine sensiblen
Cookies im Spiel, siehe Produkt-Backlog "Nicht in diesem Backlog": Auth ist
explizit offen) - vor einem echten Pilotbetrieb auf die tatsaechliche
Frontend-Origin einschraenken.

Aktueller Umfang (B01+B02+B04): Server-Grundgeruest + Health-Check +
Persistenz-Initialisierung + Eskalations-Liste. POST /entscheidung und
GET /verlauf folgen in B05/B06, siehe step8-live-test/Produkt-Backlog/.
"""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api
import store

app = FastAPI(title="Agentic-PMPlus - step7-active-learning")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api.router)


@app.on_event("startup")
def on_startup():
    db_path = store.init_db()
    print(f"Entscheidungs-DB initialisiert: {db_path}")


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok", "service": "step7-active-learning"}


def main():
    port = int(os.environ.get("PORT", "8000"))
    print("=== step7-active-learning ===")
    print(f"FastAPI-Server startet auf Port {port} (TICKET-B01/B02 - Health-Check + "
          f"Persistenz, weitere Endpunkte folgen in B04/B05/B06)")
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
