# Instructions: Umsetzung des Agentic-PMPlus-Konzepts

**Stand:** 2026-07-26
**Erstellt von:** Search-Buddy (Recherche-Agent, `.claude/agents/role/search-buddy.md`)
**Grundlage:** `README.md` (Gesamtkonzept, 8 Steps + Prestep) und
`step1-feasibility/Benchmark-Analyse.md` (15 verifizierte Quellen, referenziert als **#1–#15**)

Dieses Dokument leitet aus dem README-Konzept eine Schritt-für-Schritt-Umsetzung ab und
verankert jeden Step methodisch in den Quellen der Benchmark-Analyse, soweit dort eine
passende Quelle existiert. Wo keine der 15 Quellen thematisch passt, ist das explizit
vermerkt statt eine Quelle künstlich zuzuordnen. Die Abhängigkeitskette folgt exakt der
`depends_on`-Reihenfolge in `docker-compose.yml`:
`prestep → step1 → step2 → step3 → step4 → step5 → step6 → step7 → step8`.

---

## Prestep – Setup-Check

**Ziel (README):** Kein fachlicher Inhalt; reiner Container-/Umgebungs-Check, bevor die
eigentliche Kette startet.

**Umsetzungsschritte:**
1. `main.py` so implementieren, dass geprüft wird: `shared/data`-Verzeichnis beschreibbar,
   `.env` vorhanden (für die Steps, die einen API-Key brauchen), Python-Abhängigkeiten aus
   `requirements.txt` importierbar.
2. Exit-Code ungleich 0 bei fehlender Voraussetzung, damit `docker compose up` die Kette
   nicht mit einem kaputten Fundament startet.

**Relevante Benchmark-Quellen:** Keine — dieser Step ist reine Infrastruktur ohne
fachliche/methodische Entsprechung in der Literaturliste.

**Offene Fragen:** Keine.

---

## Step 1 – Feasibility (Recherche-Agent)

**Ziel (README):** `step1-feasibility/` ist der "Recherche-Agent (Feasibility)" – prüft,
ob das Gesamtkonzept technisch/wissenschaftlich tragfähig ist.

**Umsetzungsschritte:**
1. Diesen Step als abgeschlossen betrachten für die Recherche-Ebene: `Benchmark-Analyse.md`
   liegt bereits vor.
2. `main.py` so erweitern, dass es (a) die Machbarkeits-Einschätzung aus der
   Benchmark-Analyse maschinenlesbar zusammenfasst (z. B. als JSON in `shared/data/`), damit
   Step 2 (Grenzen) direkt darauf aufsetzen kann.

**Relevante Benchmark-Quellen:**
- **#13** (LLM actor-critic dispatching rule generation) und **#14** (Agentic LLM-based
  Contingency Management in Production Control) belegen, dass LLM-Agenten bereits produktiv
  in Produktionssteuerung/-planung eingesetzt werden – das stützt die grundsätzliche
  Machbarkeit des Gesamtkonzepts.
- Die Einordnung am Ende der Benchmark-Analyse selbst ("machbar, aber neuartige Kombination
  bestehender Bausteine") ist das zentrale Ergebnis dieses Steps.

**Offene Fragen:** Keine der 15 Quellen kombiniert LLM-Agent + PGP + Kalibrierung + Active
Loop gleichzeitig in der PPS (siehe Einordnung in der Benchmark-Analyse) – das bleibt das
Kernrisiko des Gesamtkonzepts und sollte in Step 2 quantifiziert werden.

---

## Step 2 – Limits (Grenzen technisch/ökonomisch)

**Ziel (README):** `step2-limits/` – technische und ökonomische Grenzen des Konzepts
ausloten.

**Umsetzungsschritte:**
1. Technische Grenzen: Rechenaufwand/Latenz einer PGP-Inferenz (kubische Laufzeit bei
   klassischen GPs) sowie Kosten der LLM-Aufrufe pro Planungsentscheidung abschätzen.
2. Ökonomische Grenzen: Kosten pro Preference-Query (menschliches Feedback) gegen den Wert
   der dadurch vermiedenen Fehlentscheidungen in der PPS abwägen.
3. Ergebnis als Schwellenwert-Vorschlag für Step 6 (Kalibrierung) dokumentieren.

**Relevante Benchmark-Quellen:**
- **#7** (Efficient RLHF via Bayesian Preference Inference) diskutiert explizit den
  Trade-off zwischen RLHF-Skalierbarkeit und der Query-Effizienz von Preferential Bayesian
  Optimization – direkt relevant für die ökonomische Grenze "wie viele menschliche
  Preference-Queries sind nötig/leistbar".
- **#11** (UQ-Survey) benennt Rechenaufwand/Decoding-Inkonsistenzen als praktische Grenze
  von Unsicherheitsquantifizierung bei LLMs.
- **#12** (SelectLLM) zeigt den Coverage-vs-Risk-Trade-off, der auch die ökonomische
  Grenze "wie viel Automatisierung ist bei welchem Risiko vertretbar" strukturiert.

**Offene Fragen:** Keine der Quellen liefert konkrete Kostenmodelle für den
PPS-Anwendungsfall – die Kostenparameter (z. B. € pro Planer-Feedback) müssen im Projekt
selbst erhoben werden.

---

## Step 3 – ERP-Simulation

**Ziel (README):** `step3-erp-simulation/` – simulierte ERP-Daten erzeugen (CSV in
`shared/data/`), die in Step 4/5 weiterverwendet werden.

**Umsetzungsschritte:**
1. Synthetische ERP-Datensätze (Aufträge, Bestände, Kapazitäten, Liefertermine) generieren,
   die realistische Planungskonflikte enthalten, damit später Preference-Paare (Step 5) und
   Active-Learning-Queries (Step 7) einen sinnvollen Entscheidungsraum haben.
2. Ausgabe als CSV in `shared/data/`, kompatibel mit dem Volume-Mount aus
   `docker-compose.yml`.

**Relevante Benchmark-Quellen:** Keine der 15 Quellen behandelt ERP-Datensimulation direkt;
dieser Step ist reine Dateninfrastruktur ohne unmittelbare methodische Entsprechung in der
Benchmark-Analyse.

**Offene Fragen:** Wie realistisch die simulierten Daten sein müssen, damit die in #13–#15
beschriebenen Scheduling-/Dispatching-Ansätze später sinnvoll evaluierbar sind, ist nicht
durch die Quellenlage geklärt.

---

## Step 4 – Context Engineering (RAG)

**Ziel (README):** `step4-context-engineering/` – RAG-Index/Context Engineering aufsetzen
(`shared/context/`). Im README als "PRÄMISSE/KONZEPT" markiert – erst grob prototypen.

**Umsetzungsschritte:**
1. Vektor- bzw. hybriden KG-Vektor-Index über die ERP-Daten aus Step 3 und relevante
   Planungsregeln/Domänenwissen aufbauen.
2. Retrieval-Schicht so gestalten, dass der LLM-Agent in späteren Steps (5–8) domänenspezifische
   Fakten (Kapazitäten, Regeln, Historie) korrekt abrufen kann, statt zu halluzinieren.

**Relevante Benchmark-Quellen:**
- **#5** (Empowering LLMs by hybrid retrieval-augmented generation for domain-centric Q&A
  in smart manufacturing) ist die direkt einschlägige Quelle: hybrides KG-Vector-RAG für
  Fertigungsdomänen, mit gemessener Exact-Match-Genauigkeit von 77,8 % – als methodisches
  Vorbild für den hier zu bauenden Context-Engineering-Layer geeignet.

**Offene Fragen:** #5 wurde für additive Fertigung evaluiert, nicht für PPS/Scheduling –
Übertragbarkeit auf ERP-/Planungsdaten ist eine Annahme, keine belegte Tatsache.

---

## Step 5 – PGP (Preference Gaussian Process, μ/σ)

**Ziel (README):** `step5-pgp/` – trainierte PGP-Modelle (`shared/models/`); lernt aus
Präferenzen (z. B. Planer-Feedback) eine Nutzenfunktion mit Unsicherheitsschätzung (μ, σ).

**Umsetzungsschritte:**
1. Pairwise-Preference-Datenmodell implementieren: Planungsalternativen paarweise
   vergleichen lassen (durch Planer oder LLM-Agent als Proxy).
2. Gaussian-Process-Preference-Modell trainieren, das aus Vergleichen eine latente
   Nutzenfunktion mit Mittelwert (μ) und Unsicherheit (σ) pro Planungsoption schätzt.
3. Modell-Artefakte in `shared/models/` ablegen, damit Step 6 (Kalibrierung) und Step 7
   (Active Learning) darauf zugreifen können.

**Relevante Benchmark-Quellen:**
- **#1** (Chu & Ghahramani, Preference Learning with Gaussian Processes) liefert den
  probabilistischen Kernel-Ansatz und die Likelihood-Funktion für Präferenzrelationen –
  die methodische Grundlage für das PGP selbst.
- **#2** (Collaborative Gaussian Processes for Preference Learning) relevant, falls
  mehrere Planer/Stakeholder unterschiedliche Präferenzen haben (Multi-User-Erweiterung
  des PGP über einen Preference-Kernel).
- **#3** (Bemporad & Piga, active preference learning mit RBF) und **#4** (Ozaki et al.,
  Multi-Objective BO with Active Preference Learning) zeigen, wie ein PGP-artiges
  Surrogatmodell *aktiv* durch iterative Paarvergleiche verfeinert wird – direkte Vorlage
  für die Kopplung von Step 5 (PGP) mit Step 7 (Active Learning Loop).

**Offene Fragen:** Wie der LLM-Agent (statt eines menschlichen Planers) valide
Preference-Urteile für das PGP liefern soll, ist in keiner der 15 Quellen für den
PPS-Kontext konkret ausgearbeitet – hier besteht das größte methodische Risiko des
Gesamtkonzepts (vgl. Einordnung in der Benchmark-Analyse).

---

## Step 6 – Calibration (τ/σ-Schwellenwerte, Risk-Coverage)

**Ziel (README):** `step6-calibration/` – Kalibrierung von τ/σ-Schwellenwerten im Sinne
einer Risk-Coverage-Kurve, um zu entscheiden, wann dem PGP/LLM-Agenten vertraut wird und
wann eine menschliche Entscheidung nötig ist.

**Umsetzungsschritte:**
1. Aus den σ-Werten des PGP (Step 5) eine Risk-Coverage-Kurve ableiten: bei welchem
   Unsicherheits-Schwellenwert τ wird die Agenten-Empfehlung automatisch übernommen vs. an
   einen Planer eskaliert.
2. Schwellenwert τ so kalibrieren, dass ein gewünschtes Risikoniveau (z. B. max. X %
   Fehlentscheidungen) bei maximaler Coverage (Automatisierungsgrad) eingehalten wird.

**Relevante Benchmark-Quellen:**
- **#11** (Uncertainty Quantification and Confidence Calibration in LLMs: A Survey)
  liefert die Taxonomie und den Rahmen für Risk-Coverage-basierte selektive Vorhersage bei
  LLMs, auf dem dieser Step methodisch aufbauen kann.
- **#12** (SelectLLM – Calibrating LLMs for Selective Prediction: Balancing Coverage and
  Risk) ist die direkteste Vorlage: Integration von selektiver Vorhersage ins Fine-Tuning,
  um Coverage und Risiko explizit gegeneinander abzuwägen – genau das Prinzip, das Step 6
  auf das PGP (statt auf Fine-Tuning) übertragen soll.

**Offene Fragen:** #11/#12 kalibrieren Unsicherheit *des LLM selbst* (z. B. Antwort-Konfidenz),
nicht die σ-Ausgabe eines nachgelagerten PGP – die Übertragung des Risk-Coverage-Prinzips
vom LLM-Output auf ein GP-Unsicherheitsmaß ist eine Annahme des Agentic-PMPlus-Konzepts,
die durch keine der 15 Quellen direkt validiert ist.

---

## Step 7 – Active Learning Loop

**Ziel (README):** `step7-active-learning/` – im README als "PRÄMISSE/KONZEPT" markiert.
Loop, der gezielt neue Preference-Queries auswählt, um das PGP effizient zu verbessern.

**Umsetzungsschritte:**
1. Akquisitionsfunktion implementieren, die basierend auf PGP-Unsicherheit (σ aus Step 5)
   die informativsten nächsten Paarvergleiche auswählt.
2. Loop so gestalten, dass ausgewählte Vergleiche entweder an einen menschlichen Planer
   oder (unterhalb des τ-Schwellenwerts aus Step 6) an den LLM-Agenten als Proxy gehen.
3. Neue Feedback-Daten zurück ins PGP-Training (Step 5) einspeisen (geschlossener Loop).

**Relevante Benchmark-Quellen:**
- **#3** und **#4** liefern die methodische Blaupause für den Active-Loop selbst:
  iterative Auswahl von Vergleichspaaren zur Minimierung der Interaktionskosten bei
  gleichzeitiger Verbesserung des Surrogatmodells.
- **#7** (Efficient RLHF via Bayesian Preference Inference) und **#8** (Pref-GUIDE) zeigen
  ergänzend, wie Preference-Feedback in Echtzeit bzw. mit begrenzter Abfrageanzahl in ein
  lernendes System zurückgespielt wird.
- **#9** (LLMs in the Loop) und **#10** (Efficient Human-in-the-Loop Active Learning)
  liefern das allgemeine Active-Learning-Loop-Muster mit LLM-Beteiligung
  (Unsicherheits-/Query-Strategie-Auswahl), das sich auf die Preference-Query-Auswahl
  hier übertragen lässt.

**Offene Fragen:** #9/#10 wenden Active Learning auf Klassifikations-/Annotationsaufgaben
an, nicht auf Preference-Paare in einer PPS – die konkrete Akquisitionsfunktion für den
PGP-Kontext muss aus #3/#4 abgeleitet und für PPS-Entscheidungen angepasst werden.

---

## Step 8 – Live-Test / Integration

**Ziel (README):** `step8-live-test/` – Live-Test bzw. Integration des Gesamtsystems.

**Umsetzungsschritte:**
1. Gesamte Kette (Step 3–7) an einem realitätsnahen (simulierten) PPS-Szenario end-to-end
   testen: ERP-Daten → RAG-Kontext → PGP-Empfehlung → Kalibrierungsentscheidung →
   Active-Learning-Feedback.
2. Erfolgsmetriken definieren (z. B. Anteil automatisch übernommener vs. eskalierter
   Entscheidungen, Planungsgüte gegenüber Baseline).

**Relevante Benchmark-Quellen:**
- **#13** und **#14** (May et al.) sind die direkten Vorbilder für den Live-Test-Aufbau:
  beide evaluieren LLM-Agenten in einem konkreten (Halbleiter-)Fertigungs-Testbed bzw. in
  simulationsbasierter Evaluierung von Dispatching-Regeln – als methodisches Vorbild für
  Testbed-Design und Erfolgsmessung in Step 8.
- **#15** (HFLLMDRL für Job Shop Scheduling) liefert zusätzlich ein Beispiel für den
  experimentellen Vergleich von LLM-gestützten Verfahren gegen Baselines in einem
  Scheduling-Setting.

**Offene Fragen:** Keine der Quellen testet die volle PGP+Kalibrierung+Active-Loop-Kette;
der Live-Test in Step 8 ist damit der erste Punkt, an dem das Gesamtkonzept als Ganzes
(nicht nur einzelne Bausteine) empirisch geprüft wird.

---

## Abhängigkeitsübersicht

```
prestep
  └─→ step1-feasibility        (Recherche/Machbarkeit — Benchmark-Analyse.md)
        └─→ step2-limits        (technische/ökonomische Grenzen)
              └─→ step3-erp-simulation   (ERP-Daten)
                    └─→ step4-context-engineering  (RAG über ERP-Daten, #5)
                          └─→ step5-pgp            (PGP-Training, #1–#4)
                                └─→ step6-calibration  (τ/σ Risk-Coverage, #11/#12)
                                      └─→ step7-active-learning (Loop, #3/#4/#7/#8/#9/#10)
                                            └─→ step8-live-test (Integration, #13/#14/#15)
```

Jeder Step setzt auf den Artefakten des vorherigen auf (`shared/data`, `shared/context`,
`shared/models`); ein Step kann erst sinnvoll implementiert werden, wenn der vorherige
mindestens einen lauffähigen Platzhalter-Output liefert. Steps 4, 5 und 7 sind laut README
bewusst als Konzept/Prämisse markiert und sollten zuerst grob prototypisch validiert
werden, bevor die Docker-Struktur weiter verfeinert wird.
