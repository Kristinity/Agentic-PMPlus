# TICKET-B01 – FastAPI-Server-Grundgerüst

**Status:** ✅ Erledigt (2026-07-27)
**Rolle:** backend-dev
**Priorität:** Hoch
**Abhängigkeiten:** keine
**MVP:** ✅

## User Story
#1, #2, #3 (`step8-live-test/Userstories.md`) – Echtzeit-Einsicht statt Batch-Ergebnis.

## Beschreibung
`step7-active-learning/main.py` startet einen uvicorn/FastAPI-Server statt einmalig
durchzulaufen. Begründung (siehe
`step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md` Abschnitt 1): Step 7
ist inhärent interaktiv, kein Batch-Job wie Steps 3–6.

## Akzeptanzkriterien
- `requirements.txt` um `fastapi`, `uvicorn` ergänzt.
- `docker-compose.yml`: Step 7 bekommt eine `ports:`-Freigabe (bisher hat kein Service
  einen Port nach außen offen).
- Server startet in Docker und antwortet auf einen einfachen Health-Check.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Container startet via `docker run`, `GET /` (oder `/health`) liefert 200 – verifiziert
  per Docker-Testlauf. ✅ Beide Endpunkte liefern 200 (getestet gegen
  `pmplus-step7-active-learning`, Port 8007).

## Folgetickets
[B02](TICKET-B02-SQLite-Persistenz.md), [B03](TICKET-B03-RAG-Metadaten-Aufloesung.md),
[B04](TICKET-B04-GET-Eskalationen.md), [B05](TICKET-B05-POST-Entscheidung.md)
