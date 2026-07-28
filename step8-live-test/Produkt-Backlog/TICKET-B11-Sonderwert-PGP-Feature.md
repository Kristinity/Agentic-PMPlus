# TICKET-B11 – Sondervergütungswert als PGP-Feature

**Status:** Offen
**Rolle:** backend-dev
**Priorität:** Hoch (Kern der Nutzeranforderung – "besonders teuer vergütet")
**Abhängigkeiten:** [B10](TICKET-B10-Sonderauftrag-Kennzeichnung-Schema.md)
**MVP:** ✅ (MVP der Sonderauftrags-Erweiterung)

## User Story
#14 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28)

## Beschreibung
`step5-pgp/main.py` dokumentiert im Modulkopf (Zeilen 17–19) explizit: "vertraglich
festgelegter Bruttopreis -> KEIN Preisfeld im Datenmodell; quantity als grobe, klar
markierte Ersatzgroesse". Das Gewicht von `quantity_proxy` (0.3) ist das niedrigste
von sieben Gewichten in `WEIGHTS` (Zeile 288) – ein mengenmäßig kleiner, aber
wirtschaftlich wichtiger Sonderauftrag bekäme dadurch kaum erhöhte Priorität. Dieses
Ticket schließt diese Lücke **nur für als Sonderauftrag markierte Aufträge** (Scope
vom Nutzer am 2026-07-28 bestätigt), nicht als generisches Preisfeld für alle
Aufträge – das wäre ein deutlich größerer, hier bewusst nicht gewählter Scope.

## Akzeptanzkriterien
- Neues optionales Feld `sonderwert_eur` (Zahl, EUR) in `ORDER_TEMPLATE_COLUMNS`/
  `NEW_ORDER_OPTIONAL_DEFAULTS` (Default `None`). `validate_new_orders` gibt einen
  Hinweis (nicht zwingend einen blockierenden Fehler) aus, wenn `sonderwert_eur`
  gesetzt ist, aber `is_sonderauftrag=False`, oder umgekehrt `is_sonderauftrag=True`
  ohne Wert – ein Sonderauftrag ohne bereits bekannten Wert muss trotzdem erfassbar
  bleiben.
- `step5-pgp/main.py` (`build_features`): neues Feature `sonderwert_proxy`
  (Normalisierung analog zu `quantity_proxy`, z. B. `min(sonderwert_eur / X, 1.0)`
  mit einem im Code als Startannahme gekennzeichneten Referenzwert `X` – kein aus
  echten Daten abgeleiteter Wert, da noch keine historischen Sonderauftragswerte
  vorliegen). Für Aufträge mit `is_sonderauftrag=False` ist der Wert immer 0.
- `WEIGHTS` (Zeile 288) wird um ein **zusätzliches, eigenes** Gewicht erweitert –
  **nicht** durch Erhöhen des bestehenden `quantity_proxy`-Gewichts (0.3) gelöst, weil
  das fälschlich auch alle Nicht-Sonderaufträge beeinflussen würde. Gewicht ist laut
  bestehendem Muster (`compute_heuristic_utility`-Docstring) eine "dokumentierte
  Startannahme, keine gelernte/validierte Größe".
- `generate_begruendung`: neuer `reasons`-Eintrag bei hohem `sonderwert_proxy`
  (z. B. "hoher Sondervergütungswert (Sonderauftrag)"), analog zu den bestehenden
  Einträgen (SLA-Eskalation, Materialengpass-Präzedenzfall, ...).
- Modulkopf-Docstring (Zeilen 17–19) wird **präzisiert, nicht stillschweigend
  gelöscht**: "kein generisches Preisfeld für alle Aufträge; für als Sonderauftrag
  markierte Aufträge existiert seit TICKET-B11 ein optionaler Wert-Proxy
  (`sonderwert_eur`)".
- **Ausdrücklich NICHT Teil dieses Tickets:** `sonderwert_eur`/`sonderwert_proxy` in
  den LLM-Kontext einspeisen (`step6-calibration/main.py:load_open_orders` holt
  aktuell nur `order_date`/`quantity` aus `orders.csv`, s. Zeile 147). Laut
  `Konzept-README.md` hat der PGP "volle Einsicht", das LLM "eingeschränkte
  Einsicht" – würde der Wert auch dem LLM zugespielt, correlated das künstlich
  PGP- und LLM-Einschätzung und schwächt τ als unabhängiges Signal. Eine bewusste
  Weitergabe an das LLM wäre ein eigenes, separat zu entscheidendes Ticket.
- Bekannte Abhängigkeit dokumentieren: da sich `WEIGHTS` ändert, ist die bestehende
  Bootstrap-Kalibrierung (TICKET-B07) betroffen. Keine neue Kalibrierung in diesem
  Ticket zwingend erforderlich (Bootstrap-Charakter ist laut Docstring, Zeilen 33–38,
  ohnehin vorläufig), aber im PR/Code-Kommentar erwähnen.

## Bezug zu Leitplanken
`Konzept-README.md` ("PGP volle Einsicht, LLM eingeschränkte Einsicht") – die AC zur
bewussten Nicht-Weitergabe an das LLM ist die praktische Umsetzung dieser Trennung
für dieses neue Feld.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners.
- Docker-Testlauf mit mindestens einem Sonderauftrag mit hohem `sonderwert_eur` und
  niedriger `quantity`, der nachweislich höher rankt als ohne das Feature.
- Regressionstest: ein Standardauftrag ohne `is_sonderauftrag` bleibt in seinem Rang
  gegenüber dem Stand vor diesem Ticket unverändert (Vergleich gegen bestehende
  `output_2025`/`output_2026`-Daten ohne die neue Spalte).

## Folgetickets
[F09](TICKET-F09-Sonderwert-Erfassung-Anzeige.md), [B14](TICKET-B14-Eskalationen-Sonderauftrag-Feld.md)
