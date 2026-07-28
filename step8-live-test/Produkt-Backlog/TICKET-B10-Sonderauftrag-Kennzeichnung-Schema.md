# TICKET-B10 – Sonderauftrags-Kennzeichnung (Datenschema)

**Status:** ✅ Erledigt (2026-07-28)
**Rolle:** backend-dev
**Priorität:** Hoch
**Abhängigkeiten:** –
**MVP:** ✅ (MVP der Sonderauftrags-Erweiterung, s. README dieses Ordners)

## User Story
#13 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28) – ergänzt #4, ersetzt es nicht.

## Beschreibung
Neues, bewusst **generisches** (nicht an einen konkreten Produkttyp/Durchmesser
gebundenes) Flag `is_sonderauftrag`, das einen Auftrag als Sonderanfertigung mit
gesonderter Vergütung kennzeichnet. Wird **nicht** über das bestehende, laut
`step5-pgp/main.py` nirgends gelesene `priority`-Feld ("normal"/"hoch") abgebildet –
dieses Feld ist semantisch für zeitliche Dringlichkeit reserviert (Wortlaut "hoch"),
eine Vermischung mit "wirtschaftlich besonders wertvoll" wäre verwirrend
(Produktanalyst-Empfehlung vom 2026-07-28, vom Nutzer bestätigt statt selbst
entschieden).

## Akzeptanzkriterien
- `step9-upload-interface/pipeline.py`: `ORDER_TEMPLATE_COLUMNS` um `is_sonderauftrag`
  erweitert (Platzierung direkt nach `product_id`), `NEW_ORDER_OPTIONAL_DEFAULTS`
  bekommt `"is_sonderauftrag": False` als Default, analog zum bestehenden Umgang mit
  `is_rush`. ✅
- `validate_new_orders`: unbekannte/nicht-boolesche Werte in dieser Spalte werden
  abgefangen und als Fehlermeldung ausgegeben, nicht stillschweigend als `False`
  interpretiert. ✅
- `order_template_csv_bytes()` (Download-Vorlage) enthält die neue Spalte mit
  Beispielwert. ✅
- `step3-erp-simulation/main.py` (Spaltenliste beim Schreiben von `orders.csv`,
  aktuell `["order_id", "customer", "product_id", "variant", "order_date", "due_date",
  "is_rush", "priority", "quantity"]`) wird um `is_sonderauftrag` ergänzt, damit neu
  simulierte Baseline-Daten und hochgeladene Aufträge dasselbe Schema teilen.
  Bestehende `output_2024`/`output_2025`/`output_2026`-CSVs ohne diese Spalte bleiben
  lesbar (fehlende Spalte wird beim Einlesen als `False` behandelt, nicht als Fehler). ✅
- Docstring-Ergänzung in `pipeline.py`, dass dieses Feld – anders als `variant`/
  `priority` – ab TICKET-B11 tatsächlich in der PGP-Berechnung gelesen wird, damit es
  nicht erneut als "totes Feld" endet wie die beiden genannten Bestandsfelder. ✅

## Umsetzung (Kurzfassung)
- **`step9-upload-interface/pipeline.py`**: `is_sonderauftrag` direkt nach
  `product_id` in `ORDER_TEMPLATE_COLUMNS` platziert (auch in
  `empty_new_orders_editor_df()`, da diese Funktion `ORDER_TEMPLATE_COLUMNS` filtert –
  keine separate Änderung nötig). Neue Helper-Funktion `_is_valid_boolean_value()`
  akzeptiert nur echte `bool`-Objekte (data_editor-Checkbox) oder Strings
  `"true"/"false"/"1"/"0"` (Groß-/Kleinschreibung egal, wie in der Vorlage); alles
  andere (Freitext, `2`, `"ja"`) wird von `validate_new_orders()` als Fehler
  gemeldet, nicht stillschweigend zu `False`. `prepare_new_orders()` normalisiert
  anschließend auf echtes `bool`, damit die kombinierte `orders.csv` einen
  einheitlichen Typ hat statt eines Gemischs aus `"True"`-Strings und `bool`.
- **Rückwärtskompatibilität** (`build_run_dir`): nach `pd.concat(existing, prepared)`
  entstehen für ältere Baseline-Zeilen ohne die Spalte `NaN`-Werte (da `prepared`
  die Spalte über `ORDER_TEMPLATE_COLUMNS` immer mitbringt) – ein `fillna(False)`
  danach macht daraus explizit "kein Sonderauftrag". Fehlt die Spalte hingegen in
  *beiden* Dateien (z. B. wenn gar keine neuen Aufträge hochgeladen werden), bleibt
  die 1:1-kopierte `orders.csv` unverändert, kein Crash.
- **`step3-erp-simulation/main.py`** (`generate_orders`, Zeile beim Schreiben von
  `orders.csv`): `is_sonderauftrag` immer `False` für simulierte Aufträge – bewusst
  keine erfundene Zufallsquote, da die Simulation (`company_profile.example.yaml`)
  keine Erzeugungslogik für Sonderaufträge kennt (ehrliche Auskunft statt
  Scheingenauigkeit).
- **Bewusst unverändert:** `step5-pgp/main.py` (`load_erp_data` liest `orders.csv`
  bereits vollständig, keine Spalten-Whitelist) und `step6-calibration/main.py`
  (`load_open_orders` selektiert weiterhin explizit nur
  `["order_id", "order_date", "quantity"]` aus `orders.csv`) – Letzteres ist
  gewünscht: `is_sonderauftrag` erreicht dadurch **nicht** automatisch den
  LLM-Kontext, das bleibt PGP-Feature-Arbeit von TICKET-B11.

### Test (Docker, echte Daten)
- Unit-artiger Test von `pipeline.py` (`agentic-pmplus-step9-upload-interface`-Image,
  `docker run ... python <script>`): `order_template_csv_bytes()` enthält die neue
  Spalte; `validate_new_orders()` akzeptiert `True/False/1/0/None` und lehnt
  `"vielleicht"` mit einer eigenen Fehlermeldung ab; `prepare_new_orders()`
  normalisiert auf echtes `bool` mit korrektem Default `False`.
- **Regressionstest (DoD):** `build_run_dir()` gegen die echte, committete
  `step3-erp-simulation/output_2026/orders.csv` (bestätigt ohne `is_sonderauftrag`-
  Spalte) – (a) mit zwei neuen Aufträgen (einer `is_sonderauftrag=True`, einer ohne
  Angabe) läuft fehlerfrei durch, alte Zeilen werden zu `False` aufgefüllt, keine
  `NaN` übrig; (b) ganz ohne neue Aufträge bleibt die Datei unverändert (kein Crash,
  keine Spalte hinzugefügt). Gegenprobe mit einer frisch simulierten Baseline, die
  die Spalte bereits enthält (`step3-erp-simulation`-Image, `WEEKS=4`) – auch dort
  fehlerfrei.
- **Voller Pipeline-Durchlauf:** `build_run_dir()` + `run_pipeline()` (wie in
  `app.py`) gegen `step5-pgp` + `step6-calibration` als echte Subprozesse
  (`MOCK_LLM_RESPONSE=1`, `AS_OF_DATE=2026-08-01`) mit einem gepinnten
  Sonderauftrag (`is_sonderauftrag=True`) und einem Normalauftrag – Ergebnis `ok:
  True`, beide neuen Aufträge tauchen nachweislich in `tau_vergleich.csv` auf.
  Bestätigt zusätzlich den bereits dokumentierten Befund: `is_sonderauftrag` landet
  nicht im step6-LLM-Kontext (nur `order_id/order_date/quantity` werden gemerged).
- **`step3-erp-simulation`-Image** frisch gebaut und mit `WEEKS=4` gegen ein
  Scratch-Verzeichnis laufen lassen: erzeugte `orders.csv` enthält
  `is_sonderauftrag` an der erwarteten Position, Wert `False` für alle Zeilen.
  Committete `output_2024`/`output_2025`/`output_2026`-Ordner wurden dabei **nicht**
  angefasst (nur in ein Scratch-Verzeichnis außerhalb des Repos geschrieben).

## Bezug zu Leitplanken
Keine direkte Sicherheits-Leitplanke betroffen. Grundlage für B11, B12, B14 und die
zugehörigen Frontend-Tickets (F08–F10, F12).

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners.
- Rückwärtskompatibilitätstest: bestehende CSV-Uploads/Baseline-Daten ohne die neue
  Spalte laufen nachweislich weiterhin fehlerfrei durch die gesamte Pipeline
  (`build_run_dir`/`run_pipeline`).

## Folgetickets
[F08](TICKET-F08-Sonderauftrag-Erfassung.md), [B11](TICKET-B11-Sonderwert-PGP-Feature.md),
[B12](TICKET-B12-Sonderauftrag-Provenienz-Log.md)
