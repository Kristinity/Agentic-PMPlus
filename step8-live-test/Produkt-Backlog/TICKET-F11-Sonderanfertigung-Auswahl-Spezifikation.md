# TICKET-F11 – Sonderanfertigung im Auftragsformular auswählbar + Spezifikationsfeld

**Status:** Offen
**Rolle:** frontend-dev
**Priorität:** Niedrig
**Abhängigkeiten:** [B13](TICKET-B13-Sonderanfertigung-Produkttyp-Stammdaten.md)
**MVP:** nein (Post-MVP)

## User Story
#15 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28)

## Beschreibung
Sobald B13 einen neuen `product_id` für Sonderanfertigungen bereitstellt, erscheint
er automatisch in der bestehenden `product_id`-Dropdown-Spalte
(`options=VALID_PRODUCT_IDS` in `step9-upload-interface/app.py`), da diese Liste
bereits generisch aus `pipeline.py` importiert wird – keine Codeänderung an der
Dropdown-Logik selbst nötig. Zusätzlich braucht es aber ein Freitextfeld für die
individuelle Spezifikation (z. B. "20cm Durchmesser"), da ein einzelner
Sonderanfertigungs-Produkttyp vermutlich nicht jede mögliche Maßvariante als eigene
BOM-Zeile abbildet (s. offene Frage in B13).

## Akzeptanzkriterien
- Neue optionale Textspalte `sonder_spezifikation` im data_editor (z. B. "20cm
  Durchmesser, kundenspezifisches Logo") – rein informativ/dokumentierend, fließt
  **nicht** in die PGP-Berechnung ein (das wäre eine eigene, hier nicht enthaltene
  Erweiterung; das Feld dient zunächst nur der Nachvollziehbarkeit für Planer/
  Fertigung, nicht der Priorisierung).
- Feld wird in der Ergebnistabelle mit angezeigt, wenn befüllt.
- UI macht sichtbar (z. B. Hilfetext), dass die Maschinen-/Werkzeugkapazität für
  den ausgewählten Sonderanfertigungs-Produkttyp auf der in B13 dokumentierten,
  ggf. noch unbestätigten fachlichen Annahme beruht – keine falsche Sicherheit
  vortäuschen, dass die Kapazitätsfrage bereits geklärt ist.

## Bezug zu Leitplanken
Fail-safe-/Transparenz-Prinzip (`.claude/agents/role/frontend-dev.md`) – keine
unbestätigte fachliche Annahme unsichtbar im UI verstecken.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners.
- Testlauf mit dem neuen Produkttyp und befülltem Spezifikationsfeld: Wert
  erscheint nachweislich in der Ergebnistabelle, Hilfetext zur offenen
  Kapazitätsfrage ist sichtbar.

## Folgetickets
–
