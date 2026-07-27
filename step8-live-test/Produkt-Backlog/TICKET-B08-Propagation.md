# TICKET-B08 – Propagation mit harter Obergrenze N

**Status:** ✅ Erledigt (2026-07-27)
**Rolle:** backend-dev
**Priorität:** Hoch (sicherheitsrelevant)
**Abhängigkeiten:** [B05](TICKET-B05-POST-Entscheidung.md)
**MVP:** nein (Post-MVP)

## Beschreibung
Validierte Entscheidung wirkt auf ähnliche, noch offene Fälle – aber gedrosselt (siehe
`step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md` Abschnitt 1.3 für die
Design-Idee).

## Akzeptanzkriterien
- Feste, konfigurierbare Obergrenze N (Startwert 5). ✅ Env-Var `PROPAGATION_LIMIT_N`,
  Default 5 (`step7-active-learning/propagation.py`).
- Fälle über N: erneute Eskalation statt automatischer Übernahme. ✅ Werden schlicht
  nicht in die Entscheidungs-DB geschrieben, bleiben also weiterhin unentschieden/
  eskaliert.
- `propagierte_faelle` in der `POST /entscheidung`-Response korrekt befüllt (löst den
  Platzhalter aus B05 ab). ✅

## Umsetzung (Kurzfassung)
- **Ähnlichkeitsmaß** (`propagation.find_similar_open_orders`, bewusste
  Implementierungsentscheidung, keine bewiesene Methode, s. Modulkopf in
  `propagation.py`): gleiches `product_id` UND `due_date` innerhalb eines Zeitfensters
  von `PROPAGATION_WINDOW_DAYS` Tagen (Default 7) – identisch zum bereits in
  `step5-pgp/main.py:contention_for_orders` etablierten Muster für „strukturell
  verwandte Aufträge", hier wiederverwendet statt neu erfunden. `tau_vergleich.csv`
  enthält keine rohen PGP-Feature-Vektoren, daher keine echte
  Embedding-Raum-Distanz wie bei #17/BAGEL verfügbar.
- Nur `wahl` ∈ {`folgt_pgp`, `folgt_llm`} wird propagiert. `eigene_reihenfolge` ist
  fallspezifischer Freitext und wird nie propagiert (bewusste Zusatz-Einschränkung,
  s. `propagation.py`-Modulkopf).
- Propagierte Fälle landen mit `entschieden_von="agent"` in der Entscheidungs-DB
  (`store.save_propagierte_entscheidung`, neue Funktion analog zu `save_entscheidung`)
  – Provenienz-Pflicht aus Systemgrenzen.md Teil D. Sie werden **nicht** nach
  `validated_preferences.csv` exportiert, damit agentengenerierte Fälle sich nicht
  selbst als menschliches Trainingssignal für Step 5 ausgeben (Systemgrenzen.md D.1).

## Bezug zu Leitplanken
`step2-limits/Systemgrenzen.md` Teil D.1 – keine der 17 Quellen validiert sichere
Propagation bei realen Konsequenzen. Die Obergrenze ist die im Architektur-Dokument
geforderte Sicherheitsgrenze, **nicht optional**.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt. ✅ Docker-Build + Live-Test
  gegen frisch regenerierte echte `output_2025`-Daten (`pmplus-step5-pgp` mit
  `AS_OF_DATE=2026-01-01`, `pmplus-step6-calibration` mit `MOCK_LLM_RESPONSE=1`).
- Testfall mit mehr als N ähnlichen offenen Aufträgen zeigt nachweislich, dass nur N
  automatisch mit-angepasst werden, der Rest eskaliert bleibt. ✅ Auftrag `O-03791`
  (Produkt `P-KK`, fällig 2026-01-01) hat 13 ähnliche offene Kandidaten (gleiches
  `product_id`, `due_date` innerhalb 7 Tagen). `POST /entscheidung`
  (`wahl=folgt_pgp`, N=5 Default) propagiert nachweislich genau 5
  (`propagierte_faelle: [O-03816, O-03837, O-03776, O-03775, O-03831]`),
  `GET /verlauf` zeigt 1×`entschieden_von=mensch` + 5×`entschieden_von=agent`; die
  verbleibenden 8 ähnlichen `P-KK`-Aufträge tauchen nachweislich **nicht** im Verlauf
  auf (bleiben eskaliert). Zusatztests: mit `PROPAGATION_LIMIT_N=2` werden nachweislich
  nur 2 propagiert; Aufträge mit anderem `product_id` (`P-DV`) werden nie propagiert;
  `wahl=eigene_reihenfolge` liefert immer `propagierte_faelle: []`; propagierte
  (agent-)Fälle tauchen nachweislich **nicht** in `validated_preferences.csv` auf (nur
  die menschliche Quellentscheidung).

## Folgetickets
[F03](TICKET-F03-Entscheidungserfassung.md) (Propagations-Vorschau)
