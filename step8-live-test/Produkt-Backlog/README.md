# Product-Backlog – Live-Prototyp für Jens Pirinski

**Stand:** 2026-07-27
**Grundlage:** `step7-active-learning/Backend-Backlog.md`, `step7-active-learning/Frontend-Backlog.md`,
`step8-live-test/Userstories.md`, `step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md`,
`step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md`.

**Ziel:** die beiden Bereichs-Backlogs (Backend/Frontend) in einzelne,
abhängigkeitsgeordnete Tickets zerlegen, sodass daraus ein **Live-Prototyp** gebaut werden
kann, den die Persona Jens Pirinski (Produktionsplaner, Krasser Spass GmbH) tatsächlich
durchklicken kann: offene Aufträge sehen → PGP- und LLM-Einschätzung prüfen → entscheiden.

Jedes Ticket ist eine eigene Datei in diesem Ordner (`TICKET-<ID>-<Kurzname>.md`).

## Allgemeine Definition of Done (gilt zusätzlich zur ticket-spezifischen DoD)

- Code committed mit aussagekräftiger Commit-Message.
- Gegen echte Daten getestet (Docker-Build + Run gegen `output_2024`/`output_2025` bzw.
  echte API-Responses), nicht nur gegen erfundene Platzhalterdaten – Ausnahme nur, wenn im
  Ticket explizit ein Mock-Modus vorgesehen ist.
- Keine der nicht verhandelbaren Leitplanken verletzt (siehe Verweise je Ticket).
- Offene Annahmen/Schätzungen im Code dokumentiert (Kommentar/Docstring), nicht
  stillschweigend getroffen.
- Frontend-Tickets zusätzlich: gegen echte oder realistische Mock-API-Responses geprüft;
  keine Rohzahl ohne Einordnung (z. B. nie nur "τ=0.34" ohne die bildhafte Erklärung aus
  `Konzept-README.md`).

## Abhängigkeitsübersicht

```
B01 (Server-Grundgeruest)
 ├─> B02 (SQLite-Persistenz)
 │     ├─> B05 (POST /entscheidung) ─┬─> B08 (Propagation + Obergrenze N)
 │     │                              └─> B09 (Praeferenzpaar-Export)
 │     └─> B06 (GET /verlauf) ──────────> F05 (Audit-Trail)
 ├─> B03 (RAG-Metadaten-Aufloesung)
 │     └─> B04 (GET /eskalationen) ─┬─> F01 (Warteschlange)
 │                                   └─> F02 (Eskalations-Review) ──> F03 (Entscheidungserfassung)
 └─> B07 (tau0/sigma0-Kalibrierung, unabhaengig von B01-B06 bearbeitbar)
       └─> verbessert B04 (ampel_status) + F06 (Kalibrierungs-Gesundheit)

F03 haengt zusaetzlich lose von B08 ab (Propagations-Vorschau vor dem Bestaetigen)
F07 (Kosten-Transparenz) haengt lose von F02/F05 ab, kein Backend-Ticket noetig
```

## Ticket-Übersicht

| ID | Titel | Rolle | Priorität | Abhängigkeiten | MVP? | Status |
|---|---|---|---|---|---|---|
| [B01](TICKET-B01-Server-Grundgeruest.md) | FastAPI-Server-Grundgerüst | backend-dev | Hoch | – | ✅ | ✅ erledigt |
| [B02](TICKET-B02-SQLite-Persistenz.md) | SQLite-Persistenz für Entscheidungen | backend-dev | Hoch | B01 | ✅ | ✅ erledigt |
| [B03](TICKET-B03-RAG-Metadaten-Aufloesung.md) | RAG-Metadaten-Auflösung (Vertrauensstufe) | backend-dev | Mittel | B01 | ✅ | ✅ erledigt |
| [B04](TICKET-B04-GET-Eskalationen.md) | `GET /eskalationen` | backend-dev | Hoch | B01, B03 (weich: B07) | ✅ | ✅ erledigt |
| [B05](TICKET-B05-POST-Entscheidung.md) | `POST /entscheidung` | backend-dev | Hoch | B01, B02 | ✅ | ✅ erledigt |
| [B06](TICKET-B06-GET-Verlauf.md) | `GET /verlauf` | backend-dev | Mittel | B02 | – | ✅ erledigt |
| [B07](TICKET-B07-Kalibrierung.md) | τ₀/σ₀-Kalibrierung (Risk-Coverage) | backend-dev | Hoch (fachlich Blocker) | – | – | ✅ erledigt (Bootstrap-Variante, `step6-calibration/main.py`) |
| [B08](TICKET-B08-Propagation.md) | Propagation mit harter Obergrenze N | backend-dev | Hoch (sicherheitsrelevant) | B05 | – | offen |
| [B09](TICKET-B09-Praeferenzpaar-Export.md) | Präferenzpaar-Export für Step-5-Retraining | backend-dev | Mittel | B02, B05 | – | ✅ erledigt |
| [F01](TICKET-F01-Warteschlange.md) | Warteschlange mit Ampel-Status | frontend-dev | Hoch | B04 | ✅ | offen |
| [F02](TICKET-F02-Eskalations-Review.md) | Eskalations-Review (PGP/LLM getrennt) | frontend-dev | Hoch | B04, B03 | ✅ | offen |
| [F03](TICKET-F03-Entscheidungserfassung.md) | Entscheidungserfassung mit erzwungener Provenienz | frontend-dev | Hoch | B05, F02 (lose: B08) | ✅ | offen |
| [F05](TICKET-F05-Audit-Trail.md) | Audit-Trail | frontend-dev | Mittel | B06 | – | offen |
| [F06](TICKET-F06-Kalibrierungs-Gesundheit.md) | Kalibrierungs-Gesundheit (optional) | frontend-dev | Niedrig | B07 | – | offen |
| [F07](TICKET-F07-Kosten-Transparenz.md) | Kosten-Transparenz-Hinweis (optional) | frontend-dev | Niedrig | F02 oder F05 | – | offen |

**MVP für den ersten Live-Prototyp (Jens kann durchklicken):** B01, B02, B03, B05, B04,
F01, F02, F03. Diese acht Tickets ergeben einen vollständigen Durchlauf: Warteschlange
sehen → Fall prüfen → entscheiden. `ampel_status` läuft dabei bewusst als `"unbekannt"`
(B07 fehlt noch) – das ist erlaubt (siehe B04), solange es im UI als solches sichtbar
bleibt, nicht als 🟢 uminterpretiert wird.

**Vor einem echten Pilotbetrieb zwingend, für den Demo-Prototyp nicht blockierend:** B07
(ohne echte Kalibrierung ist die Ampel nicht belastbar – für eine Demo mit Jens aber
akzeptabel, für echten Einsatz nicht).

**Post-MVP:** B06, B08, B09, F05, F06, F07.

## Nicht in diesem Backlog (weiterhin bewusst offen)

Aus `Backend-Backlog.md`/`Architektur-Backend-Frontend-Schnittstelle.md` übernommen, hier
nicht neu entschieden: konkretes Ähnlichkeitsmaß für die Propagation, exakter Wert von N,
Authentifizierung/Autorisierung der API.
