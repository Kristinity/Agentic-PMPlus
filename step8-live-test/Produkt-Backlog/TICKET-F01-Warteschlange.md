# TICKET-F01 – Warteschlange mit Ampel-Status

**Rolle:** frontend-dev
**Priorität:** Hoch
**Abhängigkeiten:** [B04](TICKET-B04-GET-Eskalationen.md)
**MVP:** ✅

## User Story
#1, #4, #6 (`step8-live-test/Userstories.md`)

## Akzeptanzkriterien
- Liste aus `GET /eskalationen`, sortiert nach PGP-Rang.
- Ampel-Sprache exakt aus `Konzept-README.md` übernommen ("Robuste Übereinstimmung",
  "Trügerische Ruhe", "Klarer Fall für Experten-Review").
- `ampel_status: "unbekannt"` als eigener, sichtbarer Zustand – nicht als 🟢 dargestellt.

## Definition of Done
- Allgemeine DoD aus `README.md` dieses Ordners erfüllt.
- Gegen echte `GET /eskalationen`-Response (aus B04) getestet.
- Alle drei Ampel-Zustände + "unbekannt" sind visuell unterscheidbar.
