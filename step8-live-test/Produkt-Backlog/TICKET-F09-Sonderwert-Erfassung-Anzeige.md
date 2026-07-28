# TICKET-F09 – Sondervergütungswert erfassen und im Ergebnis anzeigen

**Status:** Offen
**Rolle:** frontend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B11](TICKET-B11-Sonderwert-PGP-Feature.md), [F08](TICKET-F08-Sonderauftrag-Erfassung.md)
**MVP:** ✅ (MVP der Sonderauftrags-Erweiterung)

## User Story
#14 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28)

## Akzeptanzkriterien
- Neue `st.column_config.NumberColumn("sonderwert_eur", min_value=0, ...)`-Spalte im
  data_editor. Streamlit kann Spalten nicht dynamisch je Zeile ein-/ausblenden –
  daher stattdessen Hilfetext, dass das Feld nur bei gesetztem
  `is_sonderauftrag`-Flag in der Priorisierung berücksichtigt wird (s. B11).
- Ergebnistabelle (`show_cols`) ergänzt um `sonderwert_eur` (wenn vorhanden/> 0) –
  zusätzlich zum bereits über B11 in `pgp_begruendung` sichtbaren Text, damit der
  Wert selbst (nicht nur der Begründungssatz) sichtbar ist.
- `sonderwert_eur` wird nie unkommentiert/ohne Einheit gezeigt (immer mit "€"-Angabe),
  analog zur Leitplanke aus `frontend-dev.md` ("Rohwerte... immer mit
  Einordnung... begleiten"), hier auf einen ökonomischen statt statistischen Rohwert
  übertragen.

## Bezug zu Leitplanken
`.claude/agents/role/frontend-dev.md`, Arbeitsprinzip "Zielgruppe ernst nehmen" –
Rohwerte nie isoliert zeigen.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners.
- Testlauf mit mindestens einem Sonderauftrag mit gesetztem Wert: Wert erscheint
  nachweislich sowohl in der Eingabetabelle als auch in der Ergebnistabelle.

## Folgetickets
[F12](TICKET-F12-Warteschlange-Sonderauftrag-Badge.md) (Sichtbarkeit im separaten
Warteschlangen-System)
