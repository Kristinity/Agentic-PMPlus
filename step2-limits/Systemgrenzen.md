# Systemgrenzen des Agentic-PMPlus-Konzepts

**Stand:** 2026-08-01
**Erstellt von:** Search-Buddy (Teil A/B), Security-Buddy (Teil C) und Safety-Buddy (Teil D)
— `.claude/agents/role/{search,security,safety}-buddy.md`
**Grundlage:** `README.md` (Gesamtkonzept), `step1-feasibility/Benchmark-Analyse.md`
(17 verifizierte Quellen, referenziert als **#1–#17**) und
`step1-feasibility/Instructions.md` (Umsetzungsanleitung mit offenen Fragen pro Step)

Dieses Dokument beantwortet für Step 2 ("Grenzen technisch/ökonomisch") die Frage: **Wo
hört das tragen die 15 recherchierten Quellen das Konzept noch, und wo beginnt
unbelegtes Neuland?** Es gliedert sich in zwei Ebenen: eine technische Analyse für das
Entwicklungsteam und eine sprachlich vereinfachte Fassung für das Management, die dieselben
Grenzen ohne Fachbegriffe in Entscheidungsfragen übersetzt.

---

## Teil A – Technische Systemgrenzen

### A.1 Kein Beleg für die Gesamtkombination

Keine der 15 Quellen in der Benchmark-Analyse kombiniert **LLM-Agent + Preference-GP (PGP)
+ τ/σ-Kalibrierung + Active Learning Loop** gleichzeitig in der PPS (siehe Einordnung am
Ende der Benchmark-Analyse). Jede Quelle deckt maximal ein bis zwei Bausteine ab. Die
Systemgrenze: **Das Gesamtsystem ist eine unvalidierte Neukombination**, nicht die
Anwendung eines bereits erprobten Verfahrens. Jede Integrationsstelle zwischen den
Bausteinen (z. B. "PGP-σ speist Kalibrierungs-τ") ist eine Design-Annahme des Projekts
selbst, keine aus der Literatur übernommene, geprüfte Schnittstelle.

### A.2 PGP (Step 5) – Skalierungs- und Dateneffizienzgrenzen

- Die PGP-Grundlagen (**#1** Chu & Ghahramani, **#2** Houlsby et al.) basieren auf
  klassischen Gaussian Processes; deren Inferenz skaliert kubisch mit der Anzahl der
  Vergleichspaare. Für eine PPS mit vielen täglichen Planungsentscheidungen ist das eine
  harte Rechengrenze, sobald die Zahl gesammelter Preference-Paare wächst.
- **#1/#2** setzen zudem voraus, dass Präferenzurteile von Menschen stammen. Wie ein
  LLM-Agent stattdessen valide Preference-Urteile für das PGP liefern soll (statt eines
  Planers), ist in keiner Quelle für den PPS-Kontext ausgearbeitet (siehe Instructions.md,
  Step 5) – hier liegt die größte methodische Unsicherheit des gesamten Konzepts.

### A.3 Kalibrierung (Step 6) – Übertragungsgrenze LLM-Unsicherheit → GP-Unsicherheit

- **#11** und **#12** kalibrieren die Unsicherheit **des LLM selbst** (z. B.
  Antwort-Konfidenz bei Frage-Antwort-Aufgaben), nicht die σ-Ausgabe eines nachgelagerten
  Preference-GP. Die im Konzept vorgesehene Übertragung des Risk-Coverage-Prinzips vom
  LLM-Output auf ein GP-Unsicherheitsmaß ist folglich eine Annahme, keine belegte Methode.
- **#11** benennt zusätzlich generische Grenzen von Unsicherheitsquantifizierung bei LLMs:
  Rechenaufwand und Inkonsistenzen durch das Decoding selbst – relevant, sobald der
  LLM-Agent zusätzlich zur PGP-Unsicherheit eine eigene Konfidenz einbringen soll.

### A.4 Active Learning Loop (Step 7) – Aufgaben-Mismatch

- **#9** (LLMs in the Loop) und **#10** (Efficient Human-in-the-Loop Active Learning)
  belegen Active-Learning-Loops mit LLM-Beteiligung nur für **Klassifikations-/
  Annotationsaufgaben**, nicht für Preference-Paare in einer PPS.
- **#3** (Bemporad & Piga) und **#4** (Ozaki et al.) liefern zwar die methodische
  Blaupause für aktives Preference-Learning, wurden aber an generischen
  Optimierungs-Benchmarks bzw. Hyperparameter-Tuning evaluiert – nicht an
  Produktionsplanungsszenarien. Die Übertragung der Akquisitionsfunktion auf PPS-Kontexte
  (Kapazitäten, Termine, Kosten als konkurrierende Ziele) ist ungetestet.

### A.5 Context Engineering / RAG (Step 4) – Domänentransfer

- **#5** ist die einzige einschlägige Quelle und wurde für **additive Fertigung**
  evaluiert (77,8 % Exact-Match-Genauigkeit), nicht für ERP-/PPS-Planungsdaten. Ob die
  gleiche Genauigkeit bei Termin-/Kapazitätsdaten erreichbar ist, ist unbelegt.

### A.6 ERP-Simulation (Step 3) und Prestep – keine methodische Deckung

- Für die Simulation realistischer ERP-Daten (Step 3) und den reinen Infrastruktur-Check
  (Prestep) liefert keine der 15 Quellen eine methodische Grundlage. Die Qualität der
  synthetischen Daten – und damit die Aussagekraft aller nachgelagerten Steps – hängt
  vollständig von projektinternem Domänenwissen ab, nicht von externen Belegen.

### A.7 Ökonomische/Betriebsgrenze: Kosten des Feedbacks

- **#7** (Efficient RLHF via Bayesian Preference Inference) zeigt den grundsätzlichen
  Trade-off zwischen RLHF-Skalierbarkeit und der Query-Effizienz von Preferential Bayesian
  Optimization, liefert aber kein konkretes Kostenmodell. Die zentrale offene Größe bleibt:
  **wie viele menschliche Preference-Urteile pro Zeiteinheit sind in einer realen PPS
  überhaupt leistbar**, bevor der Active Learning Loop (Step 7) an der Kapazität der
  Planer statt an der Modellgüte scheitert.

### A.8 Präferenzpaare aus dem Active Learning Loop sind keine Grundlage für ein eigenes LLM

- Ein Preference-GP (**#1**, **#2**) ist gezielt dateneffizient konzipiert – der Sinn von
  aktivem Preference-Learning (**#3**, **#4**, **#16**) ist gerade, mit *möglichst wenigen*
  Vergleichsurteilen auszukommen. Die für den PGP-Betrieb ausreichende Datenmenge liegt
  damit strukturell weit unter dem, was Fine-Tuning oder Training eines eigenen LLM braucht
  (typischerweise Größenordnungen mehr Beispiele) – keine der 17 Quellen adressiert diesen
  Übergang, weil beide Verfahrensklassen (GP-Preference-Learning vs. LLM-Training)
  grundsätzlich unterschiedliche Datenbedarfsordnungen haben.
- Die Idee, über den Active Learning Loop (Step 7) langfristig genug Präferenzpaare für ein
  eigenes, lokal gehostetes LLM zu sammeln, widerspricht damit der eigenen Projektprämisse
  (README.md, Ausgangssituation): "Wenig 'gut' strukturierte Daten für ein eigenes LLM oder
  das Feintuning/Training eines Drittanbieter-LLMs" ist der ausdrückliche Grund, warum die
  PGP+eingeschränktes-LLM+RAG-Architektur überhaupt gewählt wurde – der Loop liefert
  strukturell nie genug Volumen, um zu dem zurückzukehren, was die Prämisse selbst als
  nicht machbar ausschließt.
- Die Context-Anreicherung (RAG, Step 4) ist davon unabhängig zu betrachten: validierte
  Fälle fließen laut Konzept ohnehin zurück ins Context Engineering, unabhängig vom
  PGP-Datenbedarf – das deckt den Wunsch nach "langfristig besserem Kontext" bereits ab,
  ohne dass dafür ein eigenes LLM trainiert werden müsste.

---

## Teil B – Systemgrenzen auf Managementebene (sprachlich vereinfacht)

Diese Fassung übersetzt die technischen Grenzen aus Teil A in Aussagen ohne Fachbegriffe,
so wie sie gegenüber Entscheider:innen oder Planer:innen kommuniziert werden sollten.

**1. Es gibt kein Vorbild für das Gesamtsystem.**
Es existieren einzelne Bausteine in der Forschung, die belegen, dass Teile der Idee
funktionieren – aber niemand hat bisher genau diese Kombination gebaut und getestet. Das
bedeutet: Das Projekt ist Neuland, kein Nachbau eines bewährten Systems. Ein Pilotbetrieb
mit engem Monitoring ist nötig, bevor eine breite Nutzung sinnvoll ist.

**2. Das System lernt nur, wenn Menschen ihm regelmäßig Rückmeldung geben.**
Der "lernende" Teil des Systems (das Preference-Modell) braucht laufend Vergleichsurteile
– im Zweifel von den Planer:innen selbst. Je mehr Entscheidungen automatisiert werden
sollen, desto mehr solcher Rückmeldungen werden anfangs gebraucht. Das ist ein
Zeit-/Personalaufwand, der eingeplant werden muss – er lässt sich aus der aktuellen
Studienlage nicht beziffern, nur qualitativ begründen.

**3. Die "Ich bin mir unsicher"-Funktion des Systems ist nicht 1:1 auf unseren Anwendungsfall übertragen.**
Das System soll erkennen können, wann es sich bei einer Empfehlung nicht sicher genug ist,
und dann eine Person einbeziehen. Diese Fähigkeit ist in der Forschung bisher nur für
andere Anwendungsfälle (Text-Antworten von Sprachmodellen) nachgewiesen, nicht für die Art
Unsicherheit, die unser Planungssystem intern erzeugt. Das heißt: Die Schwelle, ab wann das
System "an einen Menschen abgibt", muss im eigenen Betrieb erst erprobt und nachjustiert
werden – sie ist zu Beginn nicht verlässlich.

**4. Die Wissensbasis des Systems (Kontext-Suche) wurde bisher nur in einem
verwandten, aber anderen Fertigungsbereich erprobt.**
Es gibt einen guten Beleg dafür, dass Sprachmodelle mit angebundenem Fachwissen in der
Fertigung gut funktionieren können – allerdings in einem anderen Teilbereich (additive
Fertigung/3D-Druck), nicht direkt in der Produktionsplanung mit ERP-Daten. Die Übertragung
auf unsere Datenlage ist plausibel, aber nicht bewiesen.

**5. Die Testdaten am Anfang sind künstlich erzeugt – die Aussagekraft früher
Ergebnisse ist entsprechend begrenzt.**
Da reale ERP-Daten zu Beginn nicht eins-zu-eins verwendet werden (Simulation in Step 3),
gilt: Erste positive Ergebnisse zeigen zunächst nur, dass das System mit den erzeugten
Testszenarien zurechtkommt – nicht zwangsläufig mit der vollen Komplexität des realen
Tagesgeschäfts.

**6. Verantwortlichkeit bei automatisierten Entscheidungen muss vorab geklärt werden.**
Sobald das System unterhalb einer bestimmten Unsicherheitsschwelle automatisch entscheidet
(statt eine Person zu fragen), stellt sich die Governance-Frage, wer für diese
Entscheidungen verantwortlich zeichnet. Das ist keine technische, sondern eine
organisatorische Grenze, die vor einem Produktivbetrieb geklärt sein sollte.

**7. Der Active Learning Loop ist kein Weg zu einem eigenen KI-Modell.**
Die über den Loop gesammelten menschlichen Entscheidungen reichen von der Menge her aus, um
das eingebaute Vorhersagemodell (PGP) zu verbessern – aber nicht annähernd, um daraus ein
eigenes, im Haus betriebenes Sprachmodell zu trainieren. Das war auch nie das Ziel: Das
Projekt wurde bewusst so aufgebaut, weil zu wenig geeignete Daten für ein eigenes Modell
vorhanden sind (siehe README.md, Ausgangssituation) – dieselbe Datenknappheit gilt für die
über den Loop gesammelten Rückmeldungen. Ein besserer, laufend wachsender Kontext für das
LLM ist trotzdem möglich – das läuft aber über die separate Rückführung validierter Fälle
ins Context Engineering (Step 4), nicht über das Trainieren eines eigenen Modells.

---

## Teil C – Sicherheitsbezogene Systemgrenzen (Security-Buddy)

### C.1 Technisch

**Keine Quelle deckt Schutz gegen manipulierte Wissensquellen ab.** **#5** (RAG in Smart
Manufacturing) misst Retrieval-Genauigkeit, prüft aber nicht, ob das System gegen absichtlich
präparierte Dokumente (Prompt Injection über den RAG-Kontext in Step 4) robust ist. Für den
im Konzept vorgesehenen Aufbau gibt es damit keine belegte Verteidigung gegen Dokumente, die
den LLM-Agenten zu ungewolltem Verhalten verleiten.

**#17** (Kim et al., BAGEL) zeigt zusätzlich eine strukturelle Verstärkungsgefahr: Das
GP-Surrogat propagiert dort bewusst *sparse* LLM-Relevanzsignale über den gesamten
Embedding-Raum, um mit wenigen Bewertungen eine globale Explorationsstrategie zu steuern.
Überträgt man dieses Prinzip auf Step 5/7 (PGP + Active Learning Loop), folgt daraus eine
Systemgrenze, die in keiner der 17 Quellen adressiert wird: **ein einzelnes manipuliertes
Preference- oder Relevanz-Urteil wirkt nicht nur auf eine Entscheidung, sondern verzerrt über
das GP-Surrogat potenziell viele nachgelagerte Planungsentscheidungen zugleich** — die
Verteidigung gegen Data Poisoning an der Feedback-Quelle ist damit kritischer als in einem
System ohne globale Signal-Propagierung.

**Secrets- und Modell-Artefakt-Handling ohne Forschungsbezug.** Weder das sichere Ablegen von
`ANTHROPIC_API_KEY` (`.env`, `.gitignore`) noch die sichere (De-)Serialisierung von
PGP-Modell-Artefakten in `shared/models/` (Step 5) werden von einer der 17 Quellen
behandelt — das sind reine Software-Engineering-/DevOps-Fragen, die durch Standardpraxis
(Secret-Management, keine unsichere Deserialisierung fremder Dateien, minimal-privilegierte
Docker-Container) abgedeckt werden müssen, nicht durch die zugrunde liegende Forschung.

### C.2 Managementebene

**1. Die Wissensquelle des Systems ist bisher nicht auf Manipulationssicherheit geprüft.**
Die Forschung, auf der Step 4 (Kontext-Suche) beruht, zeigt nur, dass das System bei
sauberen Daten gute Antworten liefert — nicht, dass es unempfindlich gegen absichtlich
falsch platzierte Informationen ist. Bis das geprüft ist, sollten Wissensquellen, mit denen
das System arbeitet, kuratiert und nicht frei von außen erweiterbar sein.

**2. Ein einzelnes falsches Signal kann sich weiterverbreiten.**
Weil das System Rückmeldungen nutzt, um viele ähnliche Entscheidungen auf einmal
anzupassen (das ist gerade seine Stärke), gilt das auch für falsche oder manipulierte
Rückmeldungen: Ein einziger Fehler kann größere Wirkung haben als in einem System, das
jede Entscheidung einzeln und unabhängig trifft. Das erhöht den Wert einer sorgfältigen
Prüfung, wer Feedback geben darf.

**3. Zugangsdaten- und Modell-Sicherheit sind Standard-IT-Hygiene, keine offene
Forschungsfrage.** Das lässt sich mit etablierten Sicherheitsprozessen lösen und muss nicht
auf eine wissenschaftliche Grundlage warten.

---

## Teil D – Entscheidungssicherheits-Systemgrenzen (Safety-Buddy)

### D.1 Technisch

**Exploration wurde bisher nur in folgenlosen Kontexten getestet.** **#3, #4, #16** und
**#17** — alle Quellen, die dem Konzept die Logik für den Active Learning Loop liefern —
werten ihre aktive Explorations-/Exploitations-Strategie an generischen Optimierungs-
Benchmarks, Hyperparameter-Tuning, Robotik-Simulationen bzw. Passage-Retrieval aus. In
all diesen Kontexten kostet das "Ausprobieren" einer unsicheren Option nichts Reales. Für
Step 7/8 in der PPS bedeutet dieselbe Explorationslogik im Zweifel eine tatsächlich
durchgeführte Produktionsentscheidung mit realen, teils irreversiblen Folgen. **Keine der
17 Quellen validiert, dass sich eine für folgenlose Kontexte entwickelte
Explorationsstrategie sicher auf einen Kontext mit realen Konsequenzen übertragen lässt** —
das ist eine eigenständige Systemgrenze, nicht nur die bereits in Teil A.4 genannte
Aufgaben-Verschiedenheit.

**Kein belegter Fail-safe-Default bei Kalibrierungsversagen.** **#11** und **#12**
optimieren den Coverage-Risiko-Trade-off im statistischen Mittel über einen Datensatz,
treffen aber keine Aussage darüber, was im Einzelfall passieren soll, wenn die
Kalibrierung selbst unsicher oder falsch ist. Ob Step 6 im Zweifel automatisiert
entscheidet (fail-open) oder eskaliert (fail-safe), ist folglich eine Projektentscheidung,
keine aus der Literatur ableitbare.

**Keine Provenienz-Unterscheidung Mensch- vs. Agent-Feedback.** **#8** (Pref-GUIDE) zeigt
Mechanismen zur Aggregation von Preference-Feedback mehrerer Nutzer, adressiert aber nicht,
wie im Audit-Trail unterschieden wird, ob ein Preference-Urteil von einem Menschen oder
vom LLM-Agenten selbst (als Proxy, siehe Instructions.md Step 5) stammt. Ohne diese
Unterscheidung kann sich das System unbemerkt an seinen eigenen früheren Ausgaben
"bestätigen", statt an echtem menschlichem Feedback zu lernen.

**Keine Governance-Vorlage selbst in den nächstliegenden PPS-Quellen.** Auch **#13**,
**#14** und **#15** — die einschlägigsten Quellen für LLM-Agenten in Produktionssteuerung/
-planung — adressieren nicht, wer im Unternehmen für eine automatisierte Entscheidung
verantwortlich zeichnet. Die in Teil B.6 benannte Governance-Frage bleibt damit auch nach
Einbeziehung der nächstverwandten Literatur ungeklärt.

### D.2 Managementebene

**1. Das System darf anfangs nicht selbst "ausprobieren dürfen".**
Die eingebaute Lernstrategie funktioniert, indem das System gezielt unsichere Optionen
testet. Bisher wurde das nur dort erprobt, wo ein Fehlversuch nichts kostet. In der
Produktionsplanung könnte ein "Versuch" eine echte, teure oder schwer rückgängig zu
machende Entscheidung sein. Deshalb: In der Einführungsphase muss jeder "Testfall" vorher
von einem Menschen freigegeben werden.

**2. Im Zweifel entscheidet ein Mensch — nicht das System.**
Es gibt aktuell keinen belegten Standardfall dafür, was passieren soll, wenn das System
nicht einmal sicher weiß, wie sicher es sich ist. Diese Regel muss das Projekt selbst
festlegen, mit klarer Vorgabe: im Zweifel wird eskaliert, nie automatisch entschieden.

**3. Es muss immer erkennbar sein, ob eine Empfehlung von einem Menschen oder vom
System selbst stammt**, damit sich das System nicht unbemerkt an seinen eigenen früheren
Vorschlägen bestätigt, statt echtes menschliches Feedback zu lernen.

**4. Wer verantwortlich ist, wenn eine automatisierte Entscheidung falsch war, klärt keine
der zugrunde liegenden Studien** — auch nicht die, die dem eigenen Anwendungsfall am
nächsten kommen. Diese Verantwortlichkeit muss vor einem Produktivbetrieb intern
festgelegt werden, unabhängig vom technischen Fortschritt des Systems.

---

## Fazit

Die technischen Systemgrenzen (Teil A) markieren durchgehend **Übertragungslücken**: Jeder
Baustein ist einzeln durch mindestens eine Quelle gestützt, aber die Übertragung auf den
PPS-Kontext bzw. die Kombination der Bausteine ist an jeder Nahtstelle unbelegte Annahme.
Security-Buddy (Teil C) ergänzt, dass insbesondere der Schutz der Wissens- und
Feedback-Quellen gegen Manipulation ungeprüft ist — mit potenziell größerer Reichweite
einzelner Fehler, weil das System Signale gezielt über viele Entscheidungen propagiert.
Safety-Buddy (Teil D) ergänzt, dass die eingebaute Explorationslogik des Active Learning
Loops bislang nur in folgenlosen Forschungskontexten erprobt wurde und kein belegter
Fail-safe-Default für Kalibrierungsversagen existiert.

Auf Managementebene (Teile B–D) übersetzt sich das durchgehend in dieselbe Empfehlung:
**Pilotierung mit engem Feedback-Loop statt Vollausrollung**, mit expliziter vorheriger
Klärung von Verantwortlichkeiten bei automatisierten Entscheidungen, kuratierten statt
frei erweiterbaren Wissensquellen, und einem strikten Fail-safe-Default (im Zweifel wird
eskaliert, nie automatisiert), solange keine der drei Perspektiven (technisch, Security,
Safety) Gegenteiliges belegt.
