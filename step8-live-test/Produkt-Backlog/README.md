# Product-Backlog – Live-Prototyp für Jens Pirinski

**Stand:** 2026-07-27 (Erweiterung 2026-07-28, s. Abschnitt "Erweiterung" unten)
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

F03 haengt zusaetzlich lose von B08 ab (Propagations-Vorschau vor dem Bestaetigen) - geloest
durch einen NEUEN, rein lesenden Endpunkt GET /aehnliche-faelle (F03 selbst ergaenzt, s.
TICKET-F03-Entscheidungserfassung.md "Umsetzung"), da B08s POST /entscheidung Propagation
berechnet UND sofort persistiert, statt sie vorher nur anzuzeigen.
F07 (Kosten-Transparenz) haengt lose von F02/F05 ab, kein Backend-Ticket noetig
```

Siehe auch den Abschnitt "Erweiterung (2026-07-28)" unten für eine eigene
Abhängigkeitsübersicht der Sonderauftrags-Tickets (B10–B14/F08–F12).

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
| [B08](TICKET-B08-Propagation.md) | Propagation mit harter Obergrenze N | backend-dev | Hoch (sicherheitsrelevant) | B05 | – | ✅ erledigt |
| [B09](TICKET-B09-Praeferenzpaar-Export.md) | Präferenzpaar-Export für Step-5-Retraining | backend-dev | Mittel | B02, B05 | – | ✅ erledigt |
| [F01](TICKET-F01-Warteschlange.md) | Warteschlange mit Ampel-Status | frontend-dev | Hoch | B04 | ✅ | ✅ erledigt |
| [F02](TICKET-F02-Eskalations-Review.md) | Eskalations-Review (PGP/LLM getrennt) | frontend-dev | Hoch | B04, B03 | ✅ | ✅ erledigt |
| [F03](TICKET-F03-Entscheidungserfassung.md) | Entscheidungserfassung mit erzwungener Provenienz | frontend-dev | Hoch | B05, F02 (lose: B08) | ✅ | ✅ erledigt |
| [F05](TICKET-F05-Audit-Trail.md) | Audit-Trail | frontend-dev | Mittel | B06 | – | ✅ erledigt |
| [F06](TICKET-F06-Kalibrierungs-Gesundheit.md) | Kalibrierungs-Gesundheit (optional) | frontend-dev | Niedrig | B07 | – | ✅ erledigt |
| [F07](TICKET-F07-Kosten-Transparenz.md) | Kosten-Transparenz-Hinweis (optional) | frontend-dev | Niedrig | F02 oder F05 | – | ✅ erledigt |
| [B10](TICKET-B10-Sonderauftrag-Kennzeichnung-Schema.md) | Sonderauftrags-Kennzeichnung (Datenschema) | backend-dev | Hoch | – | ✅ | ✅ erledigt |
| [F08](TICKET-F08-Sonderauftrag-Erfassung.md) | Sonderauftrag-Erfassung in der Auftragstabelle | frontend-dev | Hoch | B10 | ✅ | ✅ erledigt |
| [B11](TICKET-B11-Sonderwert-PGP-Feature.md) | Sondervergütungswert als PGP-Feature | backend-dev | Hoch | B10 | ✅ | offen |
| [F09](TICKET-F09-Sonderwert-Erfassung-Anzeige.md) | Sondervergütungswert erfassen und anzeigen | frontend-dev | Hoch | B11, F08 | ✅ | offen |
| [B12](TICKET-B12-Sonderauftrag-Provenienz-Log.md) | Provenienz-Log für Sonderauftrags-/Wertangaben | backend-dev | Mittel-Hoch | B10 (lose: B11) | – | offen |
| [F10](TICKET-F10-Sonderauftrag-Provenienz-Anzeige.md) | Anzeige des Sonderauftrags-Provenienz-Logs | frontend-dev | Mittel | B12 | – | offen |
| [B14](TICKET-B14-Eskalationen-Sonderauftrag-Feld.md) | `GET /eskalationen` um Sonderauftrags-Feld erweitern | backend-dev | Mittel | B11 (lose: B04) | – | offen |
| [F12](TICKET-F12-Warteschlange-Sonderauftrag-Badge.md) | Sonderauftrag-Badge in der Warteschlange | frontend-dev | Mittel | B14 (lose: F08) | – | offen |
| [B13](TICKET-B13-Sonderanfertigung-Produkttyp-Stammdaten.md) | Neuer Produkttyp "Sonderanfertigung" – Stammdaten | backend-dev | Niedrig | – | – | offen |
| [F11](TICKET-F11-Sonderanfertigung-Auswahl-Spezifikation.md) | Sonderanfertigung auswählbar + Spezifikationsfeld | frontend-dev | Niedrig | B13 | – | offen |

**MVP für den ersten Live-Prototyp (Jens kann durchklicken):** B01, B02, B03, B05, B04,
F01, F02, F03. Diese acht Tickets ergeben einen vollständigen Durchlauf: Warteschlange
sehen → Fall prüfen → entscheiden. `ampel_status` läuft dabei bewusst als `"unbekannt"`
(B07 fehlt noch) – das ist erlaubt (siehe B04), solange es im UI als solches sichtbar
bleibt, nicht als 🟢 uminterpretiert wird.

**Vor einem echten Pilotbetrieb zwingend, für den Demo-Prototyp nicht blockierend:** B07
(ohne echte Kalibrierung ist die Ampel nicht belastbar – für eine Demo mit Jens aber
akzeptabel, für echten Einsatz nicht).

**Post-MVP:** B06, B08, B09, F05, F06, F07.

**Sonderauftrags-Erweiterung (2026-07-28):** B10, F08, B11, F09, B12, F10, B13, F11, B14,
F12 – Details, Priorisierung und eigene Abhängigkeitsübersicht siehe Abschnitt
"Erweiterung" unten.

## Nicht in diesem Backlog (weiterhin bewusst offen)

Aus `Backend-Backlog.md`/`Architektur-Backend-Frontend-Schnittstelle.md` übernommen, hier
nicht neu entschieden: Authentifizierung/Autorisierung der API. (Konkretes Ähnlichkeitsmaß
für die Propagation und der Wert von N sind inzwischen in B08 als dokumentierte
Implementierungsentscheidung getroffen, s. `TICKET-B08-Propagation.md` – weiterhin
empirisch mit echten Nutzungsdaten zu überprüfen, keine bewiesene Methode.)

---

## Erweiterung (2026-07-28): Sonderaufträge mit besonderer Vergütung

**Auslöser:** Nutzeranfrage vom 2026-07-28 (Produktionsplaner-Perspektive, K.S. GmbH):
"Spezialaufträge erfassen können, die besonders teuer vergütet werden, weil es
Sonderanfertigungen sind, z. B. Drehverschluss mit 20cm Durchmesser für Events."
Aufgearbeitet vom Produktanalyst-Agenten, verifiziert gegen `step5-pgp/main.py`,
`step9-upload-interface/pipeline.py`/`app.py`, `step3-erp-simulation/main.py`/
`company_profile.example.yaml`, `step6-calibration/main.py`. Korrespondierende
User Stories: `step8-live-test/Userstories.md` #13–#17 (Abschnitt "Ergänzung").

**Scope-Entscheidungen (vom Nutzer am 2026-07-28 getroffen, nicht vom Agenten):**
1. Sowohl ein reines Erfassungs-/Gewichtungsfeld für den Sondervergütungswert (Story #14,
   Tickets B11/F09) **als auch** ein strukturell neuer Produkttyp mit eigener BOM/Routing
   für abweichende Durchmesser/Sonderanfertigungen (Story #15, Tickets B13/F11) sind Teil
   des Backlogs – Letzteres war zunächst als "vermutlich zu großer Scope" zur Rückfrage
   gestellt, wurde vom Nutzer aber ausdrücklich bestätigt.
2. Generisches "Sonderauftrag"-Flag statt Hardcoding auf den Durchmesser-Beispielfall
   (Story #13, Tickets B10/F08).
3. Neues, separates Datenfeld statt Wiederverwendung des bestehenden, laut
   `step5-pgp/main.py` nirgends gelesenen `priority`-Felds ("normal"/"hoch") – Verwechslung
   von zeitlicher Dringlichkeit und wirtschaftlicher Sonderstellung vermeiden.

**Wichtiger, an mehreren Stellen relevanter Befund aus der Verifikation:**
`step6-calibration/main.py:load_open_orders` merged aus `orders.csv` explizit **nur**
`order_date`/`quantity` dazu (Zeile 147: `orders = pd.read_csv(orders_path)[["order_id",
"order_date", "quantity"]]`) – alle in `step5-pgp/main.py` erzeugten
`pgp_priorisierung.csv`-Spalten (inkl. neuer Spalten aus B11) laufen dagegen unverändert
durch den anschließenden Merge in `tau_vergleich.csv` durch. Ein neues PGP-Feature (B11)
erreicht also automatisch `tau_vergleich.csv`, aber **nicht** automatisch den
LLM-Kontext – das ist beabsichtigt (PGP hat "volle Einsicht", LLM "eingeschränkte
Einsicht", `Konzept-README.md`) und in B11 als Akzeptanzkriterium festgehalten, nicht nur
als Nebeneffekt.

### Abhängigkeitsübersicht (Erweiterung)

```
B10 (Sonderauftrags-Kennzeichnung, Schema)
 ├─> F08 (Erfassungs-UI in step9-upload-interface)
 ├─> B11 (Sonderwert als PGP-Feature, step5-pgp/main.py)
 │     ├─> F09 (Erfassung + Anzeige des Werts in step9-upload-interface)
 │     └─> B14 (GET /eskalationen um Sonderauftrags-Feld erweitern)
 │           └─> F12 (Badge in der Warteschlange, step7-active-learning/frontend)
 └─> B12 (Provenienz-Log für Sonderauftrags-/Wertangaben, lose: B11)
       └─> F10 (Anzeige des Provenienz-Logs in step9-upload-interface)

B13 (Neuer Produkttyp "Sonderanfertigung", Stammdaten – unabhängiger Strang)
 └─> F11 (Auswahl + Freitext-Spezifikationsfeld in step9-upload-interface)
```

**MVP der Sonderauftrags-Erweiterung** (deckt den Kern der Nutzeranforderung –
"erfassen" + "in der Priorisierung berücksichtigt"): B10, F08, B11, F09.

**Post-MVP, vor einem echten Pilotbetrieb aber governance-relevant:** B12, F10
(Provenienz der Wertangaben – Systemgrenzen Teil D, hier erstmals auf Dateneingabe statt
nur auf Entscheidungen angewendet), B14, F12 (Sichtbarkeit in der Warteschlange – bewusst
niedriger priorisiert als B12/F10, da eine kosmetische Sichtbarkeitsverbesserung einer
Governance-Leitplanke nachgeordnet wird).

**Niedrigste Priorität, größter Scope, ausdrücklich als Annahme gekennzeichnet:** B13, F11
(neuer Produkttyp für strukturell abweichende Sonderanfertigungen). TICKET-B13 hält
ausdrücklich fest, dass die Frage, ob dafür eine neue Maschine/Presse nötig ist oder
bestehende Werkzeuge mit zusätzlicher Rüstzeit ausreichen, eine reale, von K.S. GmbH zu
beantwortende fachliche Frage ist – **kein technischer Default**, keine vom Agenten
erfundene Kapazitätsannahme.

### Zwei getrennte "Systeme" beachten (wichtig für die Umsetzung)

Dieses Repository enthält zwei unterschiedliche Frontend-/Backend-Implementierungen:
1. `step7-active-learning/frontend/*.js` + `step7-active-learning/api.py` – die
   Warteschlange/Eskalations-Review/Entscheidungserfassung/Audit-Trail aus dem
   ursprünglichen MVP (B01–B09/F01–F07).
2. `step9-upload-interface/app.py` + `pipeline.py` (Streamlit) – das separate Werkzeug, in
   dem neue Aufträge tatsächlich erfasst werden (führt step5/step6 als Subprozesse gegen
   einen temporären Lauf-Ordner aus, zeigt das Ergebnis direkt im selben Bildschirm).

Story #13/#14 (Sonderauftrag erfassen, Wert erfassen) betreffen primär **System 2**
(Erfassung), Story #16 (Sichtbarkeit in der Warteschlange) primär **System 1**
(Review/Entscheidung) – daher die getrennten B14/F12- bzw. B10/F08/B11/F09-Tickets mit
unterschiedlichen Zieldateien.
