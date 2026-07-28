# TICKET-B13 – Neuer Produkttyp "Sonderanfertigung" – Stammdaten (BOM/Routing)

**Status:** Offen
**Rolle:** backend-dev
**Priorität:** Niedrig (großer Scope, zurückgestellt hinter B10/B11/B12/B14 – s.
Produktanalyst-Bericht 2026-07-28; vom Nutzer am 2026-07-28 ausdrücklich als Teil
des Backlogs bestätigt, nicht verworfen)
**Abhängigkeiten:** –
**MVP:** nein (Post-MVP)

## User Story
#15 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28)

## Beschreibung
Der vom Nutzer genannte Beispielfall (Drehverschluss mit 20cm Durchmesser für
Events) ist strukturell **kein neues** `variant`, sondern ein neuer Produkttyp: Laut
`step3-erp-simulation/company_profile.example.yaml` ist der Durchmesser fix an
`product_id` gebunden (P-KK 26mm, P-DV 28mm), nicht über `variant` einstellbar, und
`bom.csv`/`routings.csv` werden von `step3-erp-simulation/main.py`
(`generate_bom`/`generate_routings`, Zeilen 58–78) ausschließlich nach `product_id`
aus der Produktliste des Profils erzeugt.

**Ausdrücklich als offene fachliche Frage gekennzeichnet, NICHT technisch
defaultiert:** Ob eine Sonderanfertigung mit z. B. 20cm Durchmesser auf einer
bestehenden Presse (`WC-Presse-DV-05`) mit zusätzlicher Rüstzeit gefertigt werden
kann, oder ob dafür eine eigene Presse/ein eigenes Werkzeug nötig ist – wie es die
bestehende Trennung zwischen `WC-Presse-KK-02` (Kronen-Crimpen) und
`WC-Presse-DV-05` (Gewindeformen) im Profil bereits für die beiden Standardprodukte
vorsieht, weil das laut Profil-Kommentar (Zeilen 96–97, 118–121) "mechanisch
verschiedene Prozesse" sind, die "nicht per einfachem Werkzeugwechsel auf derselben
Presse laufen" – ist eine reale, fertigungstechnische Frage, die nur K.S. GmbH
beantworten kann. **Kein technischer Default, keine erfundene Kapazitätsannahme
durch diesen Agenten.** Bis eine fachliche Antwort vorliegt, bleibt der
entsprechende Wert im Code als "Platzhalter, fachlich zu bestätigen" markiert.

## Akzeptanzkriterien
- Neue, generische `product_id` für Sonderanfertigungen (Namensvorschlag, fachlich
  zu bestätigen: z. B. `P-DV-SONDER` oder produktfamilien-übergreifend `P-SONDER`,
  je nachdem ob nur Drehverschlüsse oder auch Kronkorken als Sonderanfertigung
  vorkommen können – **offene Frage an den Nutzer**, hier nicht selbst
  entschieden) mit eigenem BOM- und Routing-Eintrag in `company_profile.yaml`,
  analog zu P-KK/P-DV.
- `step3-erp-simulation/main.py` generiert daraus `bom.csv`/`routings.csv`/ggf.
  `work_centers.csv`-Einträge, **ohne** bestehende P-KK/P-DV-Einträge zu verändern
  (Regressionstest: bestehende Baseline-Daten unverändert).
- `step9-upload-interface/pipeline.py`: `VALID_PRODUCT_IDS` um die neue
  `product_id` erweitert; Validierung bleibt strikt (kein Freitext-Produkttyp).
- `step5-pgp/main.py`: BOM-/Routing-Lookup (`build_lookup_tables`,
  `machine_scarcity_for_order`, `material_risk_for_order`) funktioniert für den
  neuen Produkttyp voraussichtlich ohne Codeänderung, da diese Funktionen bereits
  generisch nach `product_id` gruppieren (`routings.groupby("product_id")` etc.) –
  nur die Stammdaten müssen existieren. Falls sich beim Testen doch
  Codeänderungen als nötig erweisen, das explizit dokumentieren statt
  stillschweigend eine Annahme zu treffen.
- Explizit dokumentiert (im Code-Kommentar, nicht nur hier): Ob EIN generischer
  Sonderanfertigungs-Produkttyp für beliebige individuelle Maße ausreicht, oder ob
  jede neue Dimension (20cm, 25cm, ...) einen eigenen `product_id`-Eintrag
  braucht, ist ebenfalls eine offene fachliche Frage (s. Folgeticket F11:
  Freitext-Spezifikationsfeld als pragmatischer Kompromiss, solange nicht jede
  Maßvariante eine eigene Stücklistenzeile bekommt).

## Bezug zu Leitplanken
`step2-limits/Systemgrenzen.md` Teil A.6 (ERP-Simulationsdaten sind reines
Domänenwissen ohne Methodik-Beleg) – jede neue Kapazitätsannahme muss im Code als
Annahme gekennzeichnet sein, nicht stillschweigend erfunden werden; genau das
verlangt dieses Ticket ausdrücklich.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners.
- Mindestens ein Testauftrag mit dem neuen Produkttyp durchläuft step5/step6
  erfolgreich (kein Absturz durch fehlenden BOM-/Routing-Eintrag).
- Bestehende Produkttypen bleiben unverändert in Rang/Begründung
  (Regressionstest).
- Die im Beschreibungstext genannte Maschinen-/Werkzeug-Annahme ist im Code als
  offene, fachlich zu bestätigende Annahme markiert – nicht nur in diesem Ticket.

## Folgetickets
[F11](TICKET-F11-Sonderanfertigung-Auswahl-Spezifikation.md)
