---
doc_id: "PROC-PRESSE-001"
doc_type: "prozessanweisung"
title: "Maschinenzuordnung Kronen- vs. Gewindeformen"

kunde: null
produkt: null
work_center: "WC-Presse-KK-02"
tags: ["prozess", "maschinenzuordnung", "presse", "ruesten"]

gueltig_ab: "2026-01-01"
gueltig_bis: null

autor: "Produktionsleitung K.S. GmbH"
vertrauensstufe: "intern-verifiziert"
---

# Maschinenzuordnung Kronen- vs. Gewindeformen

Kronen-Crimpen (Produkt `P-KK`, Arbeitsplatz `WC-Presse-KK-02`) und
Gewindeformen (Produkt `P-DV`, Arbeitsplatz `WC-Presse-DV-05`) laufen auf
getrennten Pressen, da beide Umformverfahren mechanisch unterschiedliche
Werkzeugsätze benötigen (siehe `company_profile.example.yaml`, Kommentar zu
`resources.work_centers`).

## Kernaussage

Ein Rückstau auf `WC-Presse-KK-02` darf planerisch nicht durch Ausweichen
auf `WC-Presse-DV-05` aufgelöst werden - ein kurzfristiger Produktwechsel
zwischen Kronkorken und Drehverschluss auf derselben Presse ist technisch
nicht vorgesehen und würde einen vollständigen Werkzeugumbau (mehrere
Stunden, nicht durch `setup_minutes` abgebildet) erfordern.

## Konsequenz für die Planung

Kapazitätsengpässe bei `WC-Presse-KK-02` müssen über Priorisierung
innerhalb der Kronkorken-Aufträge oder über Schichtausweitung gelöst
werden, nicht über eine Umverteilung auf `WC-Presse-DV-05`. Ein
Planungsvorschlag, der das ignoriert, ist technisch nicht umsetzbar und
sollte vom Agenten als ungültig verworfen werden.
