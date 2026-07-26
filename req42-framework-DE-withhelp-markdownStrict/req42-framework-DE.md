# 

**Über req42**

req42, das Framework zur Sammlung, Dokumentation und Kommunikation von
Anforderungen im agilen Umfeld.

Erstellt von Dr. Peter Hruschka, Markus Meuten und Mitwirkenden.

Template Revision: 2.0 DE (asciidoc-based), MÄRZ 2023

© We acknowledge that this document uses material from the req42
architecture framework, <https://req42.de>

Diese Version des Frameworks enthält Hilfen und Erläuterungen. Sie dient
der Einarbeitung in req42 sowie dem Verständnis der Konzepte. Für die
Dokumentation eigener System verwenden Sie besser die *plain* Version.

# Visionen und Ziele

Inhalt

Die Business-Ziele Ihrer Produktentwicklung bzw. Ihres Projekts.
Stakeholder-verständlich und transparent.

Motivation

Die Ziele müssen so weit präzisiert und abgestimmt werden, dass alle
Beteiligten eine klare Vorstellung davon haben, was in welchen
Zeiträumen erreicht werden soll.

Die Festlegung von Visionen und Zielen leitet das Team bei der
Ausarbeitung der detaillierten Anforderungen und vermeidet Verzettelung.

Vielleicht haben Ihnen Ihre Auftraggeber grobe Ziele oder eine Vision
mitgegeben, als man Sie mit der Rolle des Product Owners betraut hat.
Oft reicht jedoch die Präzision dieser Vorgaben nicht aus, um ein Team
systematisch zum Erfolg zu führen.

Für uns gilt: Ziele sind Anforderungen! Oder präziser: Ziele sind die
Anforderungen, die sich hoffentlich in dem Zeitraum, für den sie
definiert werden, stabil bleiben.

Form

Zur Definition von Zielen stehen Ihnen verschiedenste Ausdrucksmittel
zur Verfügung, die Sie nach Lust und Laune wählen können.

Unsere Empfehlung:

- Notation in Form von PAM (Purpose, Advantage, Metric)

Alternative Notationsformen:

- Produktkoffer

- News from the Future

- Product Canvas

- Value Proposition

Nur eines sollten Sie nie machen: Ohne explizite Ziele oder Visionen zu
arbeiten.

Zieldefinitionen nach PAM:

Ziel 1:

Vorteil 1:

Metrik 1:

Ziel 2:

Vorteil 2:

Metrik 2:

Ziel 3:

Vorteil 3:

Metrik 3:

# Stakeholder

Inhalt

Eine (priorisierte) Liste Ihrer Stakeholder, zusammen Angaben, wo diese
Stakeholder bei der Analysearbeit helfen (oder hindern) können.

Motivation

Stakeholder sind die wichtigsten Quellen für Anforderungen. Deshalb
sollten Sie diese kennen und dokumentieren. Sie müssen wissen, wer davon
Ihnen wobei helfen oder Sie in welcher Form behindern kann. Sie müssen
wissen, wer welchen Einfluss hat – und bei unterschiedlichen Meinungen
müssen Sie vermitteln oder entscheiden.

Ohne explizit identifizierte Stakeholder ist das alles schwierig.

Notationen/Tools

- Tabellen oder Listen (einfache Form)

- Evtl. Stakeholder-Map (komplexere Form)

Nachfolgend haben wir als Beispiel eine einfache Stakeholder-Liste
eingefügt.

Die Reihenfolge "Rolle vor Person" ist bewusst gewählt. Diese
Reihenfolge hat sich bewährt da Anforderungen normalerweise immer
Bedarfe aus Sicht einer Rolle darstellen, die Person, welche die Rolle
einnimmt während des Projektes aber durchaus wechseln kann.

Sie können bei Bedarf auch gerne weitere Spalten hinzufügen
(Kontaktdaten, …) – bedenken Sie aber den Aufwand für deren Pflege.

<table>
<colgroup>
<col style="width: 16%" />
<col style="width: 19%" />
<col style="width: 32%" />
<col style="width: 32%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Rolle</th>
<th style="text-align: left;">Person</th>
<th style="text-align: left;">Thema</th>
<th style="text-align: left;">Einfluss</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><em>&lt;Rolle-1&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Person-1&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Thema-1&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Einfluss-1&gt;</em></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><em>&lt;Rolle-2&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Person-2&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Thema-2&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Einfluss-2&gt;</em></p></td>
</tr>
</tbody>
</table>

# Scope-Abgrenzung

Inhalt

Ihr Produkt mit allen externen Schnittstellen zu (menschlichen und
automatisierten) Nachbarn, bzw. Nachbarsystemen

Motivation

Scope ist der Bereich, den Sie beeinflussen können. Die Umgebung des
Produktes, zu dem es sicherlich viele Schnittstellen gibt stellt den
Kontext dar. Der Kontext kann (normalerweise) nicht von Ihnen allein
entschieden werden, kann aber oft verhandeln werden. Um Klarheit zu
gewinnen ist es wichtig beides möglichst zu beschreiben und vor allem
die Grenze zwischen den beiden Bereichen zu definieren. req42 empfiehlt
Ihnen mit dem Business-Scope zu beginnen und nicht zu früh den
Product-Scope einzuschränken.

Die Entscheidung über die Produktgrenze sollte eine bewusste
Entscheidung sein. Mehr über dieses unverzichtbare Thema lesen Sie im
Blog-Beitrag „Scope ist nicht gleich Scope“. In unseren Kursen üben Sie
die Scope-Abgrenzung anhand einer realistischen Fallstudie.

Notationen/Tools

Zur Darstellung der Scope-Abgrenzung gibt es viele verschiedene
Ausdrucksmittel, aber eine gute Scope-Abgrenzung macht die
Schnittstellen zum Kontext explizit (z.B. in Form von Ein- und Ausgaben,
von angebotenen und benötigten Services, …​)

- Diverse Formen von Kontextdiagrammen

- Kontexttabelle

*&lt;Kontextdiagramm&gt;* oder *&lt;Kontexttabelle&gt;* hier einfügen.

Optional: Tabelle mit Erläuterungen der Schnittstellen ergänzen:

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 75%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Bedeutung</th>
<th style="text-align: left;">Erläuterung</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><em>&lt;IF-1&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Erläuterung-1&gt;</em></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><em>&lt;IF-2&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Erläuterung-2&gt;</em></p></td>
</tr>
</tbody>
</table>

# Product Backlog

Inhalt

Eine geordnete Liste von Product Backlog Items (auf verschiedenem
Granularitätsstufen: z.B. Epics, Features und User Storys.)
Backlog-Items sollen untereinander priorisiert (besserer Ausdruck:
geranked) sein. Die Items mit dem größten Mehrwert bezogen auf den
Umsetzungsaufwand sollten sich entsprechend oben im Backlog
wiederfinden, um als nächstes umgesetzt zu werden. Was Mehrwert für Sie
und Ihre Entwicklung bedeutet müssen Sie explizit festlegen. Die
einfachste Ausprägung ist der Business Mehrwert für den Kunden bei
Umsetzung der Anforderung.

Motivation

Der Scrum Guide definiert:

„Das Product Backlog ist eine geordnete Liste von allem, von dem bekannt
ist, dass es im Produkt enthalten sein soll. Es dient die einzige
Anforderungsquelle für alle Änderungen am Produkt. Der Product Owner ist
für das Product Backlog, seine Inhalte, den Zugriff darauf und die
Reihenfolge der Einträge verantwortlich. Ein Product Backlog ist niemals
vollständig. Während seiner ersten Entwicklungsschritte zeigt es die
anfangs bekannten und am besten verstandenen Anforderungen auf. Das
Product Backlog entwickelt sich mit dem Produkt und dessen Einsatz
weiter. Es ist dynamisch; es passt sich konstant an, um für das Produkt
klar herauszustellen, was es braucht, um seiner Aufgabe angemessen zu
sein, im Wettbewerb zu bestehen und den erforderlichen Nutzen zu
bieten.“

Solange ein Produkt existiert, existiert auch sein Product Backlog. Sie
sehen also: das Product Backlog ist wirklich wichtig für die
erfolgreiche Arbeit als Product Owner. Aber bitte füllen sie auch die
anderen Artefakt. Ihr Job fängt vielleicht nicht mit dem Product Backlog
an und hört sicherlich nicht mit dem Product Backlog auf.

Notationen/Tools

Bewährt hat sich (unabhängig von der Granularität) für Epics, Features
und User-Storys die Formel:

Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;* damit
*&lt;Vorteil&gt;*.

Für die abstrakteren Ebenen (Epics, Features) eignen sich unter
Umständen auch zusammengesetzte Substantive zum Beschreiben der
Funktionalität.

Nutzen Sie ALM Tools bzw. Ticket-Systeme (JIRA oder Azure DevOps) oder
Wikis (wie Confluence), um Ihre Epics, Features und Storys (verlinkt und
geordnet) zu verwalten.

Besonders bewährt hat sich eine zweidimensionale Darstellung des Product
Backlogs in Form einer Story-Map.

EPIC 1: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;* damit
*&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

FEATURE 1.1: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;*
damit *&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

STORY 1.1.1.: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;*
damit *&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

STORY 1.1.x.: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;*
damit *&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

EPIC 2: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;* damit
*&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

FEATURE 2.1: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;*
damit *&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

STORY 2.1.1.: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;*
damit *&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

STORY 2.1.2: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;*
damit *&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

FEATURE 2.2: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;*
damit *&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

STORY 2.2.1.: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;*
damit *&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

STORY 2.2.2: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;*
damit *&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

EPIC 3: Als *&lt;Rolle&gt;* möchte ich *&lt;Funktionalität&gt;* damit
*&lt;Vorteil&gt;* *&lt;optional. Link zu Modellen&gt;*.

# Modelle zur Unterstützung

Inhalt

Jegliche Art von grafischen Modellen, die das Verständnis (von
Zusammenhängen) von Backlog Items erleichtern. Die Diagramme sollten mit
Items aus dem Product Backlog verlinkt sein.

Motivation

In der agilen Welt hat es sich weit verbreitet, Anforderungen in Form
von Epics, Features oder User Storys auf Kärtchen zu schreiben oder in
äquivalenter Form in Tools abzulegen.

Trotzdem wird die Kommunikation unter allen Beteiligten manchmal
erheblich einfacher, wenn man zusätzlich auch die Hilfsmittel verwendet,
die wir in den letzten Jahrzehnten zur Präzisierung der Umgangssprache
kennengelernt haben. Scheuen Sie also nicht davor zurück Modelle zu
verwenden, wenn sie die Kommunikation fördern.

Keine Angst: diese Modelle müssen nicht perfekt sein. Aber insbesondere
mit anwachsender Komplexität (Schleifen oder Fallunterscheidungen)
fördert eine grafische Visualisierung der Schritte eines
Geschäftsprozesses das Verständnis besser als viele Tickets im System
ohne erkennbare Abfolgen und Abhängigkeiten.

Notationen/Tools

- Flussdiagramme

- Aktivitätsdiagramme

- BPMN

- Zustandsmodelle

- Datenmodelle

- UI-Prototypen

- Mock-ups

- Wireframes

Einfache Modellierungstools wie Gliffy, Diagrams.Net (früher DrawIO),
…​…​, oder DSLs wie PlantUML, Kroki, …​ oder UML-Modellierungstools wie
Enterprise Architect, Visual Paradigm, MagicDraw eignen sich zum
Erstellen der Modelle. Die Modelle sollten mit Ihren Backlog-Items
verlinkt sein (in beide Richtungen)

*&lt;Diagrammtitel 1:&gt;*. *&lt;hier Diagramm und evtl. Erläuterungen
einfügen&gt;* *&lt;optional: Link zu Epics, Features oder Storys&gt;*

*&lt;Diagrammtitel 2:&gt;*. *&lt;hier Diagramm und evtl. Erläuterungen
einfügen&gt;* *&lt;optional: Link zu Epics, Features oder Storys&gt;*

*&lt;Diagrammtitel 3:&gt;*. *&lt;hier Diagramm und evtl. Erläuterungen
einfügen&gt;* *&lt;optional: Link zu Epics, Features oder Storys&gt;*

    .
    .
    .

*&lt;Diagrammtitel n:&gt;*. *&lt;hier Diagramm und evtl. Erläuterungen
einfügen&gt;* *&lt;optional: Link zu Epics, Features oder Storys&gt;*

# Qualitätsanforderungen

Inhalt

Anforderungen an Qualitäten sind das "Wie" zum "Was" – qualitative
Definitionen oder Präzisierungen der funktionalen Anforderungen.

Motivation

Unsere Erfahrung zeigt: Qualitätsanforderungen sind (leider) nicht nur
in der agilen Welt immer noch heftig unterschätzt. Jeder will qualitativ
gute Produkte und Services, aber nur wenige machen es explizit, was
damit genau gemeint ist.

Einige Qualitätsanforderungen (wie Antwortzeiten) lassen sich vielleicht
direkt in eine Story integrieren (oder als Abnahmekriterium
dazuschreiben).

Die große Mehrheit an Qualitätsanforderungen bezieht sich jedoch auf
viele, wenn nicht sogar auf alle funktionalen Anforderungen des Product
Backlogs.

Deshalb brauchen Sie als Product Owner irgendwo die Möglichkeit, die
gewünschten Qualitäten Ihrer Produkte und Services zu spezifizieren und
zuzuweisen. Für diese Tätigkeit stehen Ihnen industrie-erprobten
Checklisten (wie Q42, ISO 25010 und andere) zur Verfügung, welche Ihnen
helfen, rasch die wichtigsten Kategorien zu identifizieren und managen
zu können.

Notationen/Tools

Einfache textuelle Szenarien, evtl. nach den Kapiteln des ISO 25010
Qualitätsbaums oder nach VOLERE gegliedert.

*&lt;Text Qualitätsanforderungen bzw. -Szenario 1&gt;* : *&lt;Link auf
funktionale Anforderungen bzw. Gültigkeitsbereich&gt;*

*&lt;Text Qualitätsanforderungen bzw. -Szenario 2&gt;* : *&lt;Link auf
funktionale Anforderungen bzw. Gültigkeitsbereich&gt;*

*&lt;Text Qualitätsanforderungen bzw. -Szenario 3&gt;* : *&lt;Link auf
funktionale Anforderungen bzw. Gültigkeitsbereich&gt;* . . . *&lt;Text
Qualitätsanforderungen bzw. -Szenario n&gt;* : *&lt;Link auf funktionale
Anforderungen bzw. Gültigkeitsbereich&gt;*

# Randbedingungen

Inhalt

Technologische oder organisatorische Randbedingungen, bzw.
Randbedingungen für den Entwicklungsprozess, wie verpflichtende
Tätigkeiten, vorgeschriebene Dokumente und deren Inhalt, einzuhaltenden
Meilensteine, …​

Motivation

Auch solche Randbedingungen sind Anforderungen. Und da sie oft für
mehrere oder sogar alle funktionalen Anforderungen gelten, sind sie
schwer in dem geordneten Product Backlog unterzubringen. Stellen Sie
einfach sicher, dass alle Beteiligten diese Randbedingungen kennen und
bei Bedarf Zugriff dazu haben.

Notationen/Tools

Einfache Listen, evtl. nach Kategorien geordnet.

## Organisatorische Randbedingungen

\* \* \*

## Technische Randbedingungen

\* \* \*

# Domänenbegriffe

Inhalt

Ein Glossar von fachlichen Begriffen mit Definitionen.

Motivation

In jedem Epic, Feature oder Story kommen Begriffe aus Ihrer Domäne vor.
Diese Begriffe sollten allen Beteiligten klar sein. Und deshalb ist es
wünschenswert, für ein Projekt oder eine Produktentwicklung ein Glossar
solcher Begriffe zu haben.

Stellen Sie sicher, dass alle Beteiligten eine gemeinsame Sprache
sprechen – und im Zweifelsfall Zugriff auf vereinbarte
Begriffsdefinitionen haben, statt in jedem Meeting wieder neue Wörter
ins Spiel zu bringen.

Notationen/Tools

Alphabetisch geordnete Liste von Begriffsdefinitionen

<table>
<colgroup>
<col style="width: 25%" />
<col style="width: 75%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Bedeutung</th>
<th style="text-align: left;">Erläuterung</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><em>&lt;Begriff-1&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Erläuterung-1&gt;</em></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><em>&lt;Begriff-2&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Erläuterung-2&gt;</em></p></td>
</tr>
</tbody>
</table>

# Betriebsmittel und Personal

Inhalt

Unter Betriebsmittel und Personal („Assets“) fassen wir das zusammen,
was Ihnen Ihre Auftraggeber oder Chefs mitgeben, um Sie als Product
Owner (zusammen mit Ihrem Team) zu befähigen, Ihren Job erfolgreich
auszuführen.

Die Assets schließen auf jeden Fall Zeit und Budget ein, d.h. Mittel,
die man Ihnen für Ihre Aufgabe zur Verfügung stellt. Vielleicht müssen
Sie sich Ihr Team mit diesen Mitteln selbst besorgen oder man stellt
Ihnen auch Personal (Ihr Team), Arbeitsräume, Infrastruktur, etc. zur
Verfügung.

Motivation

Wenn Sie den Job als Product Owner übernehmen, dann müssen Sie über
diese Assets mit Ihren Auftraggebern verhandeln und sicherlich im
Endeffekt über deren Verwendung auch (durch hoffentlich erfolgreiche
Ergebnisse) Rechenschaft ablegen.

Auf jeden Fall sollten Sie wissen, was Ihnen an Geld, Personal, Zeit,
Infrastruktur, …​ zur Verfügung steht. Diese Assets sind eine wesentliche
Randbedingung für Ihre Arbeit als Product Owner.

Notationen/Tools

Einfache Listen, Tabellen

## Budget

(evtl. gegliedert nach Roadmap oder Zwischenzielen, bzw. aufgeteilt in
Personalbudget, Sachbudget, …​)

## Zeitrahmen/Endtermin

## Teammitglieder

(Aufzählung oder aber ein Link auf komplexe Teamstruktur in Abschnitt
10)

## Externe Ressourcen

# Teamstruktur

Inhalt

Bei kleinen Produktentwicklungen mit nur einem Entwicklungsteam kann
dieser Abschnitt entfallen, da die Teammitglieder bereits im vorherigen
Abschnitt aufgeführt sind. Bei skalierten großen Produkten sollte hier
das Organigramm Ihrer Teams stehen und eine Zuordnung zu den Themen
(z.B. Epics, Features, …​), für die dieses Team zuständig ist.

Motivation

Wenn Sie über mehrere Teams verfügen, ist es selbstverständlich, dass
Sie einen Überblick darüber haben, wer in welchem (Sub-)Team arbeitet
und wie diese Teams organisiert sind.

Der Fokus sollte darauf liegen, dass die (Teil-)Teams so organisiert
sind, dass sie möglichst selbstständig Funktionen/Features oder
Teilprodukte liefern können, ohne sich ständig mit allen anderen
abstimmen zu müssen.

Notationen/Tools

Listen von Teams (jeweils mit zugewiesenen Personen und zugewiesenen
Themen aus der Roadmap oder aus dem Product Backlog (z. B. Epics oder
Features).

<table>
<colgroup>
<col style="width: 20%" />
<col style="width: 40%" />
<col style="width: 40%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Team</th>
<th style="text-align: left;">Team-Mitglied</th>
<th style="text-align: left;">Themen</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><em>&lt;Team-1&gt;</em></p></td>
<td style="text-align: left;"><p>PO: <em>&lt;Name&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Teilprodukt-A&gt;</em></p></td>
</tr>
<tr>
<td style="text-align: left;"></td>
<td style="text-align: left;"><p><em>&lt;Team-Member-1&gt;</em></p></td>
<td style="text-align: left;"></td>
</tr>
<tr>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
</tr>
<tr>
<td style="text-align: left;"><p><em>&lt;Team-2&gt;</em></p></td>
<td style="text-align: left;"><p>PO: <em>&lt;Name&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Teilprodukt-B&gt;</em></p></td>
</tr>
<tr>
<td style="text-align: left;"></td>
<td style="text-align: left;"><p><em>&lt;Team-Member-1&gt;</em></p></td>
<td style="text-align: left;"></td>
</tr>
<tr>
<td style="text-align: left;"></td>
<td style="text-align: left;"><p><em>&lt;Team-Member-2&gt;</em></p></td>
<td style="text-align: left;"></td>
</tr>
<tr>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
</tr>
</tbody>
</table>

# Roadmaps

Inhalt

"Liefergegenstände auf die Zeitleiste gelegt" – wer liefert wann was?

Motivation

Auch agile Projekte brauchen einen Plan. Je weiter ein Ziel in der Ferne
liegt, desto ungenauer kann der Plan sein. Je näher, desto genauer. Eine
explizit bekannte Roadmap ermöglicht allen Beteiligten sich
untereinander abzustimmen und mitzudenken und daher bei kurzfristigen
Entscheidungen zu berücksichtigen, was da mittelfristig noch alles
kommen wird.

Wenn Sie nur von der Hand in den Mund leben, treffen Sie unter Umständen
unwissentlich kurzfristig Entscheidungen, die dem längerfristigen
Produkterfolg entgegenstehen. In unseren Kursen zeigen wir Ihnen, wie
grob oder fein eine Roadmap sein kann, darf oder sollte.

Notationen/Tools

Was auch immer Sie als Planungswerkzeug im Einsatz haben oder was Ihnen
erlaubt, möglichst auf einer Seite einen entsprechenden Überblick über
einen längeren Zeitraum darzustellen.

*&lt; Hier Ihre Planung einfügen &gt;*

# Risiken und Annahmen

Inhalt

(Priorisierte) Listen von Risiken, die Sie erkannt haben und eine Liste
von Annahmen, die Sie als Grundlage für Entscheidungen getroffen haben.

Motivation

„Risikomanagement ist Projektmanagement für Erwachsene“ sagt Tim Lister
von der Atlantic Systems Guild“. In diesem Sinne sollten Sie Ihre
Risiken als Product Owner im Griff halten.

req42 gibt Ihnen die Mittel an die Hand, Risiken bewusst zu managen.
Insbesondere beim Priorisieren Ihrer Anforderungen sollten Sie
ausgewogen zwischen Business Value und Risk Reduction abwägen.

Notationen/Tools

Einfache Tabellen oder Listen reichen oft bereits aus.

## Risiken

<table style="width:100%;">
<colgroup>
<col style="width: 7%" />
<col style="width: 38%" />
<col style="width: 7%" />
<col style="width: 7%" />
<col style="width: 38%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Nr.</th>
<th style="text-align: left;">Text</th>
<th style="text-align: left;">Wahrschein-lichkeit</th>
<th style="text-align: left;">Schadens-höhe</th>
<th style="text-align: left;">Evtl. Maßnahmen</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><em>1</em></p></td>
<td style="text-align: left;"><p><em>&lt;Risiko-1&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;%-1&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Höhe-1&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Maßnahme-1&gt;</em></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><em>2</em></p></td>
<td style="text-align: left;"><p><em>&lt;Risiko-2&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;%-2&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Höhe-2&gt;</em></p></td>
<td style="text-align: left;"><p><em>&lt;Maßnahme-1&gt;</em></p></td>
</tr>
</tbody>
</table>

## Annahmen

<table>
<colgroup>
<col style="width: 9%" />
<col style="width: 90%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Nr.</th>
<th style="text-align: left;">Text</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><em>1</em></p></td>
<td style="text-align: left;"><p><em>&lt;Annahme-1&gt;</em></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><em>2</em></p></td>
<td style="text-align: left;"><p><em>&lt;Annahme-2&gt;</em></p></td>
</tr>
</tbody>
</table>
