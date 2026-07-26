---
doc_id: "SLA-BECKS-001"
doc_type: "sla"
title: "Liefertreue-Vereinbarung Becksbrauerei"

kunde: "Becksbrauerei"
produkt: null
work_center: null

gueltig_ab: "2026-01-01"
gueltig_bis: null

autor: "Vertrieb K.S. GmbH"
vertrauensstufe: "intern-verifiziert"
tags: ["sla", "becks", "liefertreue", "eskalation"]
---

# Liefertreue-Vereinbarung Becksbrauerei

Becksbrauerei ist mit 68 % Umsatzanteil der wichtigste Kunde von K.S. GmbH
und verlangt vertraglich eine On-Time-Delivery-Quote von 98 % (siehe
`kpis.on_time_delivery_target_pct` im ERP-Unternehmensprofil).

## Kernaussage

Bei drohender Terminüberschreitung eines Becks-Auftrags muss die Planung
diesen Auftrag automatisch als "hoch"-Priorität einstufen, sobald weniger
als 3 Arbeitstage Puffer bis zum Liefertermin verbleiben. Unterschreitet die
gleitende 4-Wochen-Liefertreue für Becks 98 %, ist der Vertrieb (nicht nur
die Produktionsplanung) unverzüglich zu informieren.

## Konsequenz für die Planung

Ein Planungsvorschlag, der einen Becks-Auftrag zugunsten eines
Nicht-Becks-Auftrags verspätet, benötigt eine explizite Begründung im
Audit-Trail (vgl. `step2-limits/Systemgrenzen.md`, Teil D zur
Nachvollziehbarkeit automatisierter Entscheidungen) und sollte, sofern die
PGP-Unsicherheit hierzu nicht eindeutig ist, an einen Menschen eskaliert
werden statt automatisch entschieden zu werden.
