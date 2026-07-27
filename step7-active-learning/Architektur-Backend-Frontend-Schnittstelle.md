# Step 7 – Architektur: Active Learning Loop (Backend + Frontend-Schnittstelle)

**Stand:** 2026-07-27
**Grundlage:** `Konzept-README.md`, `step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md`
(Abschnitt 1.3 Design-Idee, Abschnitt 2.5 offene technische Frage),
`step2-limits/Systemgrenzen.md` (Teil A.4, C.1, D.1), `.claude/agents/role/backend-dev.md`,
`.claude/agents/role/frontend-dev.md`.

Dieses Dokument beantwortet die in Abschnitt 2.5 des Frontend-Konzepts offen gelassene
Frage ("direkter Dateizugriff oder dünner API-Service?") und legt die Architektur fest,
**bevor** `step7-active-learning/main.py` gebaut wird.

---

## 1. Warum Step 7 kein Batch-Skript wie Step 3–6 sein kann

Step 3–6 folgen alle demselben Muster: `docker compose up stepX` → liest Input-CSVs aus
`shared_data` → schreibt Output-CSV → fertig. Das passt zur `depends_on`-Kette in
`docker-compose.yml`.

Step 7 ist strukturell anders: Ein Mensch (Produktionsplaner, siehe Persona Jens Pirinski
in `step8-live-test/Userstories.md`) muss **interaktiv, in Echtzeit** eskalierte Fälle
prüfen und entscheiden. Ein Batch-Skript kann das nicht abbilden – es braucht eine laufende
Schnittstelle. **Entscheidung: `step7-active-learning/main.py` startet einen leichten
API-Server (FastAPI + uvicorn), kein Einmal-Durchlauf-Skript.**

Konsequenz für `requirements.txt`: `fastapi`, `uvicorn` ergänzen. Konsequenz für
`docker-compose.yml`: Step 7 (und ein künftiger Frontend-Service) brauchen eine
`ports:`-Freigabe – bisher hat kein Service im Compose-File einen Port nach außen offen,
da alle bisherigen Steps reine Batch-Container ohne externe Ansprechbarkeit sind.

---

## 2. Backend-Architektur

### 2.1 Datenherkunft (read-only, bleibt dateibasiert)

Kein Grund, das bestehende CSV-Muster für die **Eingaben** von Step 7 zu ändern – die
kommen unverändert aus den bisherigen Steps:

- `pgp_priorisierung.csv` (Step 5): order_id, mu, sigma, rank, matched_rag_docs.
- `tau_vergleich.csv` (Step 6): order_id, tau, llm_rank, llm_begruendung.
- `rag_documents/*.md` (Step 4): für die Vertrauensstufe/Quelle hinter einer
  LLM-Begründung.

### 2.2 API-Endpunkte

| Endpunkt | Zweck | Request | Response (Kernfelder) |
|---|---|---|---|
| `GET /eskalationen` | Warteschlange + Review-Daten | – | Liste: `order_id`, `pgp: {rank, mu, sigma, begruendung}`, `llm: {rank, tau, begruendung, matched_rag_docs}`, `ampel_status` (🟢/🟡/🔴 nach der 2×2-Matrix) |
| `POST /entscheidung` | Menschliche Entscheidung erfassen | `order_id`, `wahl: "folgt_pgp"\|"folgt_llm"\|"eigene_reihenfolge"`, `eigene_reihenfolge?`, `begruendung` (**Pflicht** bei Abweichung von PGP und LLM), `entschieden_von: "mensch"` (fest, nicht vom Client überschreibbar) | `decision_id`, `zeitstempel`, `propagierte_faelle: [order_id, ...]` |
| `GET /verlauf` | Audit-Trail | optionale Filter (Zeitraum, order_id) | Liste aller Entscheidungen (automatisch + eskaliert), inkl. wer/was entschieden hat |
| `POST /rekalibrierung` (intern/getriggert, kein UI-Button) | Stößt Re-Kalibrierung von τ₀/σ₀ (Step 6) mit den neuen validierten Fällen an | – | Status/neue Schwellenwerte |

`entschieden_von` ist serverseitig fest auf `"mensch"` gesetzt für alles, was über
`POST /entscheidung` kommt – nie vom Client frei wählbar. Das ist die technische Umsetzung
der in Systemgrenzen Teil D geforderten Provenienz-Unterscheidung Mensch- vs. Agent-Feedback:
sie darf nicht durch einen Frontend-Bug oder eine manipulierte Anfrage aushebelbar sein.

### 2.3 Persistenz: SQLite statt CSV für Entscheidungen

CSV-Dateien sind für gleichzeitige Schreibzugriffe aus einer interaktiven Mehrbenutzer-UI
ungeeignet (Race Conditions bei parallelen `POST /entscheidung`-Aufrufen). Für die
Entscheidungs-/Audit-Historie braucht es erstmals in diesem Projekt eine echte, kleine
Persistenz – **SQLite** (Python-Standardbibliothek, kein neuer Infrastruktur-Dienst nötig,
Datei liegt in `shared/models/` oder einem neuen `shared/feedback/`). Die bisherigen
Batch-CSVs (Steps 3–6) bleiben unangetastet als Input.

### 2.4 Rückführung in den Loop

Pro validierter Entscheidung (aus `POST /entscheidung`):

1. **Als neues Präferenzpaar ablegen** für das nächste PGP-Retraining (Step 5). Landet in
   einer neuen Datei, z. B. `shared_data/validated_preferences.csv` – `step5-pgp/main.py`
   müsste in einem späteren Schritt erweitert werden, um diese Datei zusätzlich zur
   Bootstrap-Heuristik als Trainingssignal einzulesen (nicht Teil dieses Dokuments, aber
   als Abhängigkeit hier festgehalten).
2. **Propagation auf ähnliche, noch nicht entschiedene Fälle** – die in
   `Active-Learning-Loop-und-Frontend-Konzept.md` Abschnitt 1.3 hergeleitete Design-Idee
   (analog #17/BAGEL: ein Urteil wirkt über den GP auf mehrere ähnliche Fälle).
3. **Periodische Re-Kalibrierung** von τ₀/σ₀ (Step 6) mit wachsendem validierten Fallbestand.

### 2.5 Sicherheitsgrenze: Propagation muss gedrosselt sein

Systemgrenzen Teil D.1 hält fest: **keine der 17 Quellen validiert, dass Explorations-/
Propagationslogik aus folgenlosen Forschungskontexten sicher auf einen Kontext mit realen,
teils irreversiblen Konsequenzen übertragbar ist.** Deshalb hier eine harte, im Code
durchgesetzte Grenze statt unbegrenzter Propagation:

- Feste Obergrenze **N** an Fällen, die durch eine einzelne Freigabe automatisch
  mit-anpasst werden dürfen (Startwert vorschlagsweise klein, z. B. N=5 – konkreter Wert
  ist eine Projektentscheidung, nicht aus der Literatur ableitbar, siehe Teil D.1).
- Alles über dieser Grenze: **erneute Eskalation statt automatischer Übernahme.**
- `POST /entscheidung`-Response gibt `propagierte_faelle` **explizit zurück**, damit das
  Frontend dem Planer transparent zeigt, wie viele/welche Fälle von seiner Freigabe
  mit-beeinflusst wurden, *bevor* er bestätigt (siehe Frontend-Konzept 2.4, erster Punkt).

---

## 3. Frontend-Schnittstelle: Bildschirm-zu-Endpunkt-Mapping

| Bildschirm (Frontend-Konzept 2.3) | Endpunkt(e) |
|---|---|
| 1. Auftrags-Warteschlange | `GET /eskalationen` (Ampel-Status pro Auftrag) |
| 2. Eskalations-Review | `GET /eskalationen` (Detailfelder `pgp`/`llm` **getrennt** anzeigen) |
| 3. Entscheidungserfassung | `POST /entscheidung` |
| 4. Audit-Trail | `GET /verlauf` |
| 5. Kalibrierungs-Gesundheit (optional) | `GET /verlauf` aggregiert, oder eigener `GET /kalibrierung`-Endpunkt (nicht im MVP-Scope) |

**Nicht verhandelbar im Response-Format** (Frontend-Konzept 2.4, Leitplanke 1): `pgp` und
`llm` sind in `GET /eskalationen` **immer zwei getrennte Objekte**, nie zu einem
gemeinsamen Score verschmolzen – sonst kann das Frontend die geforderte Trennung gar nicht
umsetzen, unabhängig davon wie sorgfältig es gebaut wird. Das ist eine Anforderung an die
API selbst, nicht nur an die UI.

---

## 4. Vorgeschlagene Modulstruktur für `step7-active-learning/`

```
step7-active-learning/
├── main.py              # Startet den FastAPI-Server (uvicorn)
├── api.py                # Endpunkt-Definitionen (GET /eskalationen, POST /entscheidung, ...)
├── store.py              # SQLite-Persistenz fuer Entscheidungen/Verlauf
├── propagation.py        # Aehnlichkeits-/Propagationslogik inkl. der N-Obergrenze (2.5)
├── requirements.txt      # + fastapi, uvicorn
└── Dockerfile
```

---

## 5. Offene Fragen für die Umsetzung (bewusst nicht vorentschieden)

1. **Ähnlichkeitsmaß für die Propagation** (welche Fälle gelten als "ähnlich genug"?) –
   naheliegend wären dieselben Feature-Vektoren wie im PGP (Step 5), aber das ist eine
   Implementierungsentscheidung für `propagation.py`, nicht Teil dieses Architektur-Docs.
2. **Wert von N** (Propagations-Obergrenze) – Startwert vorschlagen, aber empirisch mit
   echten Nutzungsdaten überprüfen.
3. **Authentifizierung/Autorisierung der API** – wer darf `POST /entscheidung` aufrufen?
   Für den Prototyp evtl. auslassbar, für einen Pilotbetrieb (Systemgrenzen Teil B.1)
   nicht.
4. **`shared_data/validated_preferences.csv` → Step-5-Integration** – wie `step5-pgp/main.py`
   dieses neue Trainingssignal konkret aufnimmt, ist hier nur als Abhängigkeit benannt,
   nicht spezifiziert.
