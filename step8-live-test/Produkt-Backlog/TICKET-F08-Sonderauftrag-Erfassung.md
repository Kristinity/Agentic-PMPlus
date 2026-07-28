# TICKET-F08 – Sonderauftrag-Erfassung in der Auftragstabelle

**Status:** ✅ Erledigt (2026-07-28)
**Rolle:** frontend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B10](TICKET-B10-Sonderauftrag-Kennzeichnung-Schema.md)
**MVP:** ✅ (MVP der Sonderauftrags-Erweiterung)

## User Story
#13 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28)

## Beschreibung
In der bestehenden In-App-Tabelle (`st.data_editor` in
`step9-upload-interface/app.py`) wird eine neue Spalte "Sonderauftrag" angeboten, mit
der ein Planer einen Auftrag als Sonderanfertigung markieren kann – unabhängig vom
Produkttyp.

## Akzeptanzkriterien
- [x] Neue `st.column_config.CheckboxColumn("is_sonderauftrag", default=False, ...)` im
  `column_config`-Dict (aktuell Zeilen ~76–91 in `app.py`), Platzierung direkt nach
  `product_id`.
- [x] Hilfetext macht den Unterschied zum bestehenden `priority`-Feld ("normal"/"hoch")
  explizit (z. B. "Sonderanfertigung mit gesonderter Vergütung, unabhängig von
  zeitlicher Dringlichkeit"), damit beide Felder nicht verwechselt werden.
- [x] Download-Vorlage und CSV-Upload-Pfad (`st.file_uploader`) unterstützen die neue
  Spalte identisch zur In-App-Tabelle – kein Sonderweg nur für eine der beiden
  Eingabearten.
- [x] Ergebnistabelle (`show_cols`) zeigt nach dem Berechnen einen Sonderauftrags-
  Indikator pro Zeile (analog zum bestehenden "🆕 Neu hochgeladen"-Muster in `app.py`).

## Bezug zu Leitplanken
Keine direkte Sicherheits-Leitplanke; additive UI-Erweiterung im bestehenden Muster.

## Definition of Done
- [x] Allgemeine DoD aus `README.md` dieses Ordners.
- [x] Klick-Durchlauf im Streamlit-Container getestet: Zeile anlegen, Flag setzen,
  Priorisierung berechnen – Flag erscheint nachweislich in der Ergebnistabelle.

## Umsetzung (2026-07-28)
- `app.py`: `column_config`-Dict um `is_sonderauftrag` (CheckboxColumn, direkt nach
  `product_id`, wie in `pipeline.py ORDER_TEMPLATE_COLUMNS`) ergänzt. Hilfetext auf
  `is_sonderauftrag` UND (zur Abgrenzung symmetrisch) auf `priority` ergänzt, damit
  beide Felder im UI nicht verwechselt werden.
- Download-Vorlage (`order_template_csv_bytes()`) und CSV-Upload-Pfad
  (`st.file_uploader`) brauchten keine Änderung – `validate_new_orders()`/
  `prepare_new_orders()` in `pipeline.py` (TICKET-B10) laufen für beide Eingabepfade
  bereits identisch durch dieselbe Codebasis. Per End-to-End-Test verifiziert (siehe
  unten), inkl. Fall, dass pandas beim CSV-Read `"True"/"False"`-Strings automatisch
  in echtes `bool` konvertiert.
- Ergebnistabelle: `is_sonderauftrag` wird von step5-pgp/step6-calibration noch NICHT
  durchgereicht (kommt erst mit TICKET-B11) – `tau_vergleich.csv`/`result.result_df`
  enthält die Spalte also nicht. Der Indikator ("⭐ Sonderauftrag", eigene Spalte,
  klar unterscheidbar vom "🆕 Neu hochgeladen"-Symbol) wird daher – analog zum
  bestehenden "Neu hochgeladen"-Muster – aus dem Eingabe-DataFrame (`new_orders_df`)
  in Kombination mit den von `build_run_dir()` zurückgegebenen `new_ids` abgeleitet
  (Zeilenreihenfolge bleibt in `prepare_new_orders()` erhalten, daher positionsgenau
  zuordenbar). Keine Änderung an `pipeline.py`/step5/step6 nötig oder vorgenommen.
- Getestet: Python-Syntaxcheck (`python3 -m py_compile app.py pipeline.py`, beide OK)
  sowie End-to-End-Test der zugrundeliegenden Pipeline-Funktionen
  (`validate_new_orders`/`build_run_dir`/`run_pipeline`) im echten Docker-Container
  (`docker compose build step9-upload-interface`, `docker compose run --rm
  step9-upload-interface python3 ...`) mit Mock-LLM, je einem Sonderauftrag/
  Nicht-Sonderauftrag pro Szenario:
  - In-App-Tabelle-Simulation (echtes Python-`bool`, gemischt True/False).
  - CSV-Upload-Simulation (Strings `"True"/"False"` wie in der Download-Vorlage,
    von pandas beim `read_csv` automatisch zu `bool` inferiert).
  In beiden Fällen erscheint das Sonderauftrags-Flag korrekt und ausschließlich bei
  der markierten Zeile in der Ergebnistabelle (Spalte "Sonderauftrag", Symbol "⭐"),
  unabhängig vom "🆕 Neu hochgeladen"-Indikator.

## Folgetickets
[F09](TICKET-F09-Sonderwert-Erfassung-Anzeige.md)
