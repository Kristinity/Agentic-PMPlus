---
doc_id: "INC-2025-014"
doc_type: "stoerungsbericht"
title: "Weissblech-Lieferengpass Q4 2025 - Vorgehen und Lehre"

kunde: null
produkt: null
work_center: null
tags: ["stoerung", "material_shortage", "weissblech", "lieferkette"]

gueltig_ab: "2025-11-01"
gueltig_bis: null

autor: "Einkauf/Produktionsleitung K.S. GmbH"
vertrauensstufe: "intern-verifiziert"
---

# Weissblech-Lieferengpass Q4 2025 - Vorgehen und Lehre

Im vierten Quartal 2025 verzögerte sich eine Weissblech-Coil-Lieferung um
9 Tage (Ø-Lieferzeit laut Stückliste: 10 Tage, siehe `bom.csv` /
`disruptions.csv`, Typ `material_shortage`). Betroffen waren sowohl
Kronkorken- als auch Drehverschluss-Aufträge, da beide Produkte dasselbe
Vormaterial nutzen.

## Kernaussage

Die damalige Entscheidung, zunächst alle Becks-Aufträge aus dem
verbleibenden Bestand zu bedienen und lokale Brauereien auf die folgende
Woche zu verschieben, hielt die Becks-Liefertreue bei 100 %, senkte aber
die Liefertreue gegenüber kleineren Kunden auf ca. 80 % in dieser Woche.
Keiner der kleineren Kunden hat deswegen den Auftrag storniert.

## Konsequenz für die Planung

Bei einem `material_shortage`-Ereignis auf der gemeinsamen
Weissblech-Komponente ist die Priorisierung von Becks-Aufträgen gegenüber
dem Sammelposten kleinerer Kunden ein akzeptierter, bereits erprobter
Kompromiss - ein Planungsvorschlag muss diesen Fall also nicht zwingend an
einen Menschen eskalieren, sollte die Verschiebung kleinerer Aufträge aber
weiterhin im Audit-Trail begründen.
