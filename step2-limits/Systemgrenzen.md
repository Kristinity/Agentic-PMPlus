# Systemgrenzen des Agentic-PMPlus-Konzepts

**Stand:** 2026-07-26
**Erstellt von:** Search-Buddy (Recherche-Agent, `.claude/agents/role/search-buddy.md`)
**Grundlage:** `README.md` (Gesamtkonzept), `step1-feasibility/Benchmark-Analyse.md`
(15 verifizierte Quellen, referenziert als **#1–#15**) und
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

---

## Fazit

Die technischen Systemgrenzen (Teil A) markieren durchgehend **Übertragungslücken**: Jeder
Baustein ist einzeln durch mindestens eine Quelle gestützt, aber die Übertragung auf den
PPS-Kontext bzw. die Kombination der Bausteine ist an jeder Nahtstelle unbelegte Annahme.
Auf Managementebene (Teil B) übersetzt sich das in eine klare Empfehlung: **Pilotierung mit
engem Feedback-Loop statt Vollausrollung**, mit expliziter vorheriger Klärung von
Verantwortlichkeiten bei automatisierten Entscheidungen.
