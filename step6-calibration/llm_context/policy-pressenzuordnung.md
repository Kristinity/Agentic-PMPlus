# Maschinenzuordnung Kronen- vs. Gewindeformen

> Policy-Auszug für den LLM-Ranking-Agenten (Step 6). Beschreibt eine strukturelle
> Fertigungsregel, keine live abgefragte Maschinenauslastung (die sieht ausschließlich
> der PGP über `work_centers.csv`/`disruptions.csv`). Quelle:
> `step4-context-engineering/rag_documents/prozess-pressenzuordnung.md`.

Kronen-Crimpen (Produkt Kronkorken) und Gewindeformen (Produkt Drehverschluss) laufen auf
getrennten Pressen, da beide Umformverfahren mechanisch unterschiedliche Werkzeugsätze
benötigen.

## Regel

Ein Rückstau auf der Kronkorken-Presse darf planerisch **nicht** durch Ausweichen auf die
Drehverschluss-Presse aufgelöst werden - ein kurzfristiger Produktwechsel zwischen
Kronkorken und Drehverschluss auf derselben Presse ist technisch nicht vorgesehen und würde
einen vollständigen Werkzeugumbau (mehrere Stunden) erfordern.

## Konsequenz für die Priorisierung

Kapazitätsengpässe bei der Kronkorken-Presse müssen über Priorisierung innerhalb der
Kronkorken-Aufträge oder über Schichtausweitung gelöst werden, nicht über eine
Umverteilung auf die Drehverschluss-Presse. Ein Planungsvorschlag, der das ignoriert, ist
technisch nicht umsetzbar.
