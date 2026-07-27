# Backend-Backlog – Agentic-PMPlus (Step 7)

**Stand:** 2026-07-27
**Grundlage:** `step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md`,
`step7-active-learning/Architektur-Backend-Frontend-Schnittstelle.md`,
`step8-live-test/Userstories.md`, `.claude/agents/role/backend-dev.md`.
**Vorab-Review:** Steps 1–6 wurden gegen die drei Grundlagendokumente geprüft (siehe
"Review-Ergebnis" unten). Ein konkreter Gap wurde bereits behoben, bevor dieses Backlog
geschrieben wurde – siehe Punkt 0.

---

## 0. Bereits erledigt (aus dem Review, nicht mehr im Backlog)

**Gap:** `pgp_priorisierung.csv` (Step 5) hatte keine menschenlesbare Begründung pro
Auftrag – nur numerische Faktoren (`mu`, `sigma`) und `matched_rag_docs` (Doc-IDs ohne
Text). Die Architektur (`GET /eskalationen`) braucht aber `pgp.begruendung` analog zu
`llm.begruendung`.

**Fix:** `step5-pgp/main.py` erzeugt jetzt pro Auftrag eine `pgp_begruendung`-Spalte
(`generate_begruendung()`, transparente Regel-Heuristik aus den bereits berechneten
Faktoren: SLA-Eskalation, Materialengpass-Präzedenzfall, zeitliche Dringlichkeit,
Maschinen-Engpass, Materialrisiko, Work-Center-Konkurrenz). Fließt ohne Änderung an
`step6-calibration/main.py` automatisch in `tau_vergleich.csv` durch (verifiziert per
Docker-Testlauf gegen `output_2025`-Daten und im Mock-Modus).

---

## Review-Ergebnis: Steps 1–6 gegen die Architektur geprüft

| Step | Ergebnis |
|---|---|
| 1–2 | Kein main.py-Bezug – Ergebnis ist Markdown (`Benchmark-Analyse.md`, `Systemgrenzen.md`), von der API nicht konsumiert. Kein Anpassungsbedarf. |
| 3 (ERP-Simulation) | Wird nur indirekt über Step 5/6 konsumiert, keine direkte API-Abhängigkeit. Kein Anpassungsbedarf. |
| 4 (Context Engineering) | `rag_documents/*.md` liegen bereits im von Step 5/6 genutzten Format vor; die API kann sie direkt lesen (siehe Punkt 3 unten) – kein Export-Mechanismus in Step 4 selbst nötig. |
| 5 (PGP) | Gap gefunden und behoben, siehe Punkt 0. |
| 6 (Kalibrierung) | `tau_vergleich.csv` liefert bereits `tau`, `llm_begruendung`, jetzt auch `pgp_begruendung`. **Fehlt:** τ₀/σ₀-Schwellenwerte selbst – die eigentliche Kalibrierung (Risk-Coverage/Conformal Risk Control) war im ursprünglichen Scope von Step 6 bewusst ausgeklammert. Ohne sie kann `ampel_status` (🟢/🟡/🔴) nicht berechnet werden. Siehe Punkt 2 unten – **das ist der wichtigste Blocker im ganzen Backlog.** |

---

## Backlog-Items

### 1. API-Grundgerüst

**Titel:** FastAPI-Server statt Batch-Skript für Step 7
**User Story:** *Als Produktionsplaner möchte ich eskalierte Fälle in Echtzeit einsehen
können* (Userstories #1, #2, #3), was ein Batch-Skript strukturell nicht leisten kann.
**Akzeptanzkriterien:**
- `step7-active-learning/main.py` startet einen uvicorn/FastAPI-Server statt einmalig
  durchzulaufen.
- `requirements.txt` um `fastapi`, `uvicorn` ergänzt.
- `docker-compose.yml`: Step 7 bekommt eine `ports:`-Freigabe (bisher hat kein Service
  einen Port nach außen offen).
**Rolle(n):** backend-dev.
**Priorität:** Hoch – Voraussetzung für alle weiteren Items.

**Titel:** `GET /eskalationen`
**User Story:** Userstories #1 (Priorisierung sehen), #2 (Unsicherheit erkennen), #3
(Begründung nachvollziehen), #5 (PGP/LLM getrennt sehen).
**Akzeptanzkriterien:**
- Liest `pgp_priorisierung.csv` + `tau_vergleich.csv`, filtert auf τ>τ₀ ODER σ>σ₀ (siehe
  Blocker Punkt 2 – bis dahin: alle offenen Fälle liefern, `ampel_status` als `"unbekannt"`
  kennzeichnen statt zu raten).
- Response: `pgp` und `llm` **immer als zwei getrennte Objekte** (Architektur-Doc
  Abschnitt 3, nicht verhandelbar) – nie zu einem Score verschmolzen.
- Jeder Eintrag enthält `matched_rag_docs` inkl. Vertrauensstufe (siehe Punkt 3).
**Rolle(n):** backend-dev.
**Priorität:** Hoch.

**Titel:** `POST /entscheidung`
**User Story:** Userstories #1, #5 (Entscheidungsgrundlage), sowie implizit die
Provenienz-Anforderung aus Systemgrenzen Teil D.
**Akzeptanzkriterien:**
- `entschieden_von` serverseitig **fest auf `"mensch"`** gesetzt, vom Client nicht
  überschreibbar.
- Bei Abweichung von PGP **und** LLM: `begruendung`-Feld ist Pflicht (Request ohne dieses
  Feld wird mit Fehler abgelehnt, nicht stillschweigend akzeptiert).
- Response enthält `propagierte_faelle` (siehe Punkt 4).
**Rolle(n):** backend-dev.
**Priorität:** Hoch.

**Titel:** `GET /verlauf`
**User Story:** Userstories #7 (Vertrauen durch Historie), #9 (Nachvollziehbarkeit von
Planänderungen).
**Akzeptanzkriterien:** Liste aller Entscheidungen (automatisch + eskaliert) inkl.
wer/was entschieden hat, chronologisch, filterbar nach Zeitraum/order_id.
**Rolle(n):** backend-dev.
**Priorität:** Mittel – nicht blockierend für den Kernfluss, aber Voraussetzung für
Systemgrenzen-Teil-B.6-Konformität (Governance/Verantwortlichkeit).

### 2. τ₀/σ₀-Kalibrierung (Blocker – ohne dieses Item bleibt `ampel_status` unbelegt)

**Titel:** Risk-Coverage-Kalibrierung für τ₀/σ₀
**User Story:** Userstories #2, #6 (nur bei echter Unsicherheit eskalieren, sonst
automatisch weiter).
**Akzeptanzkriterien:**
- Getrennte Schwellenwerte τ₀ und σ₀ (nicht addiert/gleich gewichtet, `Konzept-README.md`
  Step 6).
- Validierungsdatensatz mit demselben Bootstrap-Hinweis wie in `step5-pgp/main.py`
  dokumentiert (kein Vortäuschen echter Kalibrierungsdaten, solange keine realen
  Präferenzurteile vorliegen).
- `Systemgrenzen.md` Teil A.3 explizit referenzieren: Übertragung von
  Risk-Coverage-Prinzipien von LLM-Unsicherheit auf GP-Unsicherheit ist **unbelegt**, nicht
  aus der Literatur ableitbar – im Code/Docstring kennzeichnen, nicht verschweigen.
**Rolle(n):** backend-dev (Berührungspunkt mit Step 6, technisch aber Teil des Step-7-Datenflusses, da `GET /eskalationen` davon abhängt).
**Priorität:** **Höchste Priorität** – ohne dieses Item kann `ampel_status` nicht korrekt
berechnet werden, und die gesamte Eskalationslogik (Kernversprechen des Konzepts) bleibt
unvollständig.

### 3. RAG-Metadaten-Zugriff für die API

**Titel:** Vertrauensstufe pro `matched_rag_docs`-Eintrag auflösen
**User Story:** Frontend-Konzept 2.4 ("Vertrauensstufe sichtbar machen"), Systemgrenzen
Teil C.1/C.2.
**Akzeptanzkriterien:** API liest `rag_documents/*.md` direkt (analog zu
`step5-pgp/main.py`/`step6-calibration/main.py`, kein neuer Export-Mechanismus in Step 4
nötig), löst `matched_rag_docs`-IDs zu `{doc_id, title, vertrauensstufe}` auf.
**Rolle(n):** backend-dev.
**Priorität:** Mittel.

### 4. Rückführung in den Loop

**Titel:** SQLite-Persistenz für Entscheidungen/Verlauf
**Akzeptanzkriterien:** Neue Datei (z. B. `shared/feedback/entscheidungen.db`), CSVs der
Steps 3–6 bleiben unangetastet als reine Inputs.
**Rolle(n):** backend-dev.
**Priorität:** Hoch (Voraussetzung für `POST /entscheidung`/`GET /verlauf`).

**Titel:** Präferenzpaar-Export für Step-5-Retraining
**Akzeptanzkriterien:** Validierte Entscheidungen landen in
`shared_data/validated_preferences.csv`; **Hinweis:** `step5-pgp/main.py`-Erweiterung, um
diese Datei einzulesen, ist **nicht** Teil dieses Backlogs (siehe Architektur-Doc, offene
Frage 4) – hier nur der Export, nicht die Step-5-seitige Konsumierung.
**Rolle(n):** backend-dev.
**Priorität:** Mittel.

**Titel:** Propagation auf ähnliche Fälle mit harter Obergrenze N
**Akzeptanzkriterien:** Feste, konfigurierbare Obergrenze N (Startwert vorschlagsweise 5,
siehe Architektur-Doc 2.5); Fälle über N: erneute Eskalation statt automatischer
Übernahme; `propagierte_faelle` wird in der `POST /entscheidung`-Response transparent
zurückgegeben.
**Bezug zu Leitplanken:** Systemgrenzen Teil D.1 (keine Quelle validiert sichere
Propagation bei realen Konsequenzen) – die Obergrenze ist die im Architektur-Doc
geforderte Sicherheitsgrenze, nicht optional.
**Rolle(n):** backend-dev.
**Priorität:** Hoch – direkt sicherheitsrelevant, nicht nur funktional.

---

## Nicht in diesem Backlog (bewusst offen, siehe Architektur-Doc Abschnitt 5)

- Konkretes Ähnlichkeitsmaß für die Propagation.
- Exakter Wert von N.
- Authentifizierung/Autorisierung der API.
