# TICKET-F12 – Sonderauftrag-Badge in der Warteschlange

**Status:** Offen
**Rolle:** frontend-dev
**Priorität:** Mittel
**Abhängigkeiten:** [B14](TICKET-B14-Eskalationen-Sonderauftrag-Feld.md) (lose: [F08](TICKET-F08-Sonderauftrag-Erfassung.md) für das zugrunde liegende Datenmodell)
**MVP:** nein (Post-MVP)

## User Story
#16 (`step8-live-test/Userstories.md`, Ergänzung 2026-07-28)

## Beschreibung
Sonderaufträge sollen in der bestehenden Warteschlange
(`step7-active-learning/frontend/app.js`, TICKET-F01) optisch erkennbar sein, auch
wenn ihr PGP-Rang sie nicht automatisch nach oben schiebt.

## Akzeptanzkriterien
- Auftragskarte (`renderOrderCard`) bekommt einen zusätzlichen Badge (z. B.
  "⭐ Sonderauftrag" + Wert, falls vorhanden), additiv zur bestehenden
  Kartenstruktur – kein Eingriff in die Ampel-Logik (🟢/🟡/🔴 bleibt unverändert
  und unvermischt mit dem neuen Badge, analog zur bereits in TICKET-F02
  etablierten Praxis additiver statt vermischender Erweiterungen).
- Fehlt das `sonderauftrag`-Feld in der Response (ältere Daten, s. B14), wird kein
  Badge angezeigt – nicht fälschlich "kein Sonderauftrag" behauptet, sondern
  schlicht keine Anzeige.
- Optionaler Filter "nur Sonderaufträge" (nice-to-have, kein Muss für dieses
  Ticket).

## Bezug zu Leitplanken
`step7-active-learning/Active-Learning-Loop-und-Frontend-Konzept.md` Abschnitt
2.3.1 (Warteschlange) – additive Erweiterung, keine neue Bildschirmstruktur.
Priorität laut Produktanalyst-Bericht (2026-07-28) bewusst hinter der
Provenienz-Story (B12/F10), da eine kosmetische Sichtbarkeitsverbesserung einer
Governance-Leitplanke nachgeordnet wird.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners.
- Testlauf gegen eine `GET /eskalationen`-Response mit mind. einem
  Sonderauftrags-Eintrag: Badge erscheint nachweislich nur bei diesem Eintrag.

## Folgetickets
–
