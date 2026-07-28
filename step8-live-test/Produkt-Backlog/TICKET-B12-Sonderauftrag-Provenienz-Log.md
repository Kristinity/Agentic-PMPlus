# TICKET-B12 – Provenienz-Log für Sonderauftrags-/Wertangaben

**Status:** Offen
**Rolle:** backend-dev
**Priorität:** Mittel-Hoch (Governance-relevant, für Demo-Prototyp nicht blockierend)
**Abhängigkeiten:** [B10](TICKET-B10-Sonderauftrag-Kennzeichnung-Schema.md) (lose: [B11](TICKET-B11-Sonderwert-PGP-Feature.md))
**MVP:** nein (Post-MVP, vor einem echten Pilotbetrieb aber wichtig)

## User Story
#17 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28)

## Beschreibung
`step2-limits/Systemgrenzen.md` Teil D fordert Provenienz-Unterscheidung Mensch- vs.
Agent-Feedback für **Entscheidungen** (bereits umgesetzt in TICKET-B08/F05). Dieses
Ticket überträgt dieselbe Grundidee erstmals auf eine **Dateneingabe**
(Produktanalyst-Empfehlung vom 2026-07-28): ein frei eintragbares Wert-/
Sonderauftrags-Feld ohne jede Nachvollziehbarkeit könnte sonst zur künstlichen
Hochpriorisierung genutzt werden (Bezug Systemgrenzen Teil C.2, Punkt 2 – dort für
Signalverbreitung, hier auf Signalherkunft übertragen).

## Akzeptanzkriterien
- Jeder `run_pipeline`-Aufruf mit mindestens einem Auftrag, bei dem
  `is_sonderauftrag=True` gesetzt ist, hängt einen Eintrag an ein neues,
  einfaches Append-Only-Log an (z. B. `shared/feedback/sonderauftrag_log.csv`,
  analog zur bestehenden `shared/feedback/entscheidungen.db`-Konvention aus
  `step7-active-learning`, hier aber bewusst CSV statt SQLite, weil
  `step9-upload-interface` aktuell komplett zustandslos pro Lauf arbeitet, s.
  `build_run_dir`/`shutil.rmtree` in `pipeline.py`) mit: Zeitstempel, `order_id`,
  `is_sonderauftrag`, `sonderwert_eur`.
- Da aktuell keine Authentifizierung existiert (bewusst aus dem bestehenden
  Backlog ausgeklammert, s. `Produkt-Backlog/README.md` "Nicht in diesem
  Backlog"), wird das Feld für die eintragende Person mit einem festen
  Platzhalterwert (z. B. `"unbekannt (keine Authentifizierung im Prototyp)"`)
  befüllt – **explizit als bekannte Lücke**, nicht stillschweigend weggelassen
  (gleiches Muster wie bereits in TICKET-F05 für `entschieden_von` bei fehlender
  Auth dokumentiert).
- Das Log wird **nicht** aus `RUNS_DIR` gelöscht (anders als der temporäre
  `run_dir`), damit die Historie über mehrere Streamlit-Läufe erhalten bleibt.

## Bezug zu Leitplanken
`step2-limits/Systemgrenzen.md` Teil D (Provenienz) – hier erstmals auf
Dateneingabe statt nur auf Entscheidungen angewendet; bewusste Erweiterung der
bestehenden Leitplanke, kein Widerspruch dazu.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners.
- Zwei aufeinanderfolgende Streamlit-Läufe mit Sonderaufträgen erzeugen
  nachweislich zwei (nicht nur einen) Log-Einträge.

## Folgetickets
[F10](TICKET-F10-Sonderauftrag-Provenienz-Anzeige.md)
