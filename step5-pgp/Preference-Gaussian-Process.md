# Preference Gaussian Process (PGP) – Mathematische und technische Bedingungen

**Stand:** 2026-07-27
**Kontext:** Dieses Dokument spezifiziert die Bedingungen für den **Preference Gaussian
Process (PGP)** aus Step 5 des Agentic-PMPlus-Konzepts (siehe `README.md` im Repo-Root).
Im Gesamtkonzept liefert der PGP bei jeder Vorhersage **zwei Werte gleichzeitig**:

- eine **Rang-/Präferenz-Prognose μ** (welche Planungsoption/Reihenfolge wird bevorzugt), und
- eine **Selbstunsicherheit σ** (wie sicher ist sich das Modell dabei).

μ und σ werden anschließend gegen die unabhängige Einschätzung des LLM-Agenten
verglichen; bei zu großer Diskrepanz bzw. zu hoher σ wird über die τ/σ-Schwellenwerte
aus Step 6 (Kalibrierung, Risk-Coverage) eine Eskalation an einen menschlichen Planer
ausgelöst. Der PGP ist damit die statistische Rückfallebene, die die LLM-Einschätzung
absichert – siehe `step1-feasibility/Benchmark-Analyse.md`, Abschnitt "Einordnung zum
Agentic-PMPlus-Konzept", wo dieselbe Rollenverteilung (PGP = Step 5, Kalibrierung =
Step 6, Active Learning Loop = Step 7) beschrieben ist.

Dieses Dokument fasst zusammen: (1) was aus der bestehenden Benchmark-Analyse zu den
mathematischen/technischen Bedingungen des PGP bereits bekannt ist, (2) was ergänzend
recherchiert wurde, und (3) welche offenen Fragen für die konkrete Umsetzung in Step 5
bestehen bleiben.

> **Nachtrag (2026-07-27):** Nach Erstellung dieses Dokuments wurde `main` in
> `step5-pgp` gemergt; `step2-limits/Systemgrenzen.md` und der reale Datenschema-Output
> von Step 3 (`step3-erp-simulation/output_2024|2025/*.csv`) sind jetzt verfügbar. Die
> Abschnitte 1.5, 2.2 und 5 wurden entsprechend aktualisiert, ursprüngliche
> "existiert nicht"-Hinweise sind durch die tatsächlichen Fundstellen ersetzt.

---

## 1. Mathematische Modellbedingungen

### 1.1 Grundmodell: latente Nutzenfunktion + Präferenzkernel

Ein PGP modelliert keine direkten Zielwerte, sondern eine **latente Nutzen-/Score-
Funktion** f(x) über Planungsoptionen x (z. B. Auftragsreihenfolgen, Dispatching-
Entscheidungen). Beobachtet werden nicht f(x) selbst, sondern **paarweise
Präferenzurteile** "Option A wird gegenüber Option B bevorzugt". Dieses Grundmodell
geht auf Chu & Ghahramani (2005) zurück, die dafür eine eigene Likelihood-Funktion für
Präferenzrelationen im GP-Rahmen einführen (siehe Benchmark-Analyse #1). Houlsby et al.
(2012) erweitern dies um einen expliziten **Präferenzkernel**, der Paare (x_i, x_j) auf
einen gemeinsamen Merkmalsraum abbildet, sodass ein Standard-GP auf Paardaten
angewendet werden kann (Benchmark-Analyse #2).

**Bedingung für Step 5:** Der Kernel muss auf einem Merkmalsraum definiert werden, der
Planungsoptionen aus der ERP-Simulation (Step 3) vergleichbar macht (z. B. Auftrags-
Attribute, Durchlaufzeiten, Prioritäten). Die konkrete Feature-Definition ist in der
bisherigen Literaturbasis **nicht** festgelegt und muss in Step 5 domänenspezifisch
entschieden werden (offene Frage, siehe Abschnitt 5).

### 1.2 Likelihood-Modell für Paarvergleiche

Für die Wahrscheinlichkeit, dass Option A gegenüber B bevorzugt wird, wird in der
Literatur durchgängig ein **probit-/Bernoulli-artiges Likelihood-Modell** auf Basis der
Differenz f(x_A) − f(x_B) verwendet:

- Chu & Ghahramani (2005) führen die "preference likelihood" ein, die genau diese
  Differenz durch eine kumulative Normalverteilung (Probit) auf eine Erfolgswahr-
  scheinlichkeit abbildet (Benchmark-Analyse #1).
- González et al. (2017) verwenden für "Duelle" explizit ein **GP mit Bernoulli-
  Likelihood** zur Modellierung des Ausgangs jedes Paarvergleichs (neu recherchiert,
  s. Abschnitt 3.2).

**Bedingung für Step 5:** Da diese Likelihood **nicht konjugiert** zum GP-Prior ist
(anders als bei Standard-Regressions-GPs), ist exakte Inferenz nicht in geschlossener
Form möglich – es braucht ein Approximationsverfahren (siehe 1.3).

### 1.3 Inferenzverfahren: Laplace-Approximation, EP, Variational Bayes

Für die nicht-konjugierte Präferenz-Likelihood kommen in der Literatur drei
Standardverfahren zum Einsatz:

- **Laplace-Approximation:** approximiert die Posterior-Verteilung über die latenten
  Funktionswerte durch eine Gauß-Verteilung um das Modus der wahren Posterior. Dies ist
  das kanonische Verfahren für GP-Klassifikation/-Präferenzlernen und wird in Rasmussen
  & Williams (2006), *Gaussian Processes for Machine Learning*, Kap. 3 ("Classification")
  im Detail hergeleitet (neu recherchiert, s. Abschnitt 3.4).
- **Expectation Propagation (EP) und Variational Bayes:** Houlsby et al. (2012)
  approximieren die Inferenz für ihr kollaboratives Präferenz-GP explizit über EP und
  Variational Bayes, um Skalierbarkeit auf mehrere Nutzer/Präferenzquellen zu erreichen
  (Benchmark-Analyse #2).

**Bedingung für Step 5:** Die Wahl zwischen Laplace (einfacher zu implementieren,
weniger präzise Unsicherheitsschätzung) und EP/VB (aufwändiger, aber i. d. R. bessere
Kalibrierung der Posterior-Varianz) hat direkten Einfluss auf die Qualität von σ – und
damit auf die Eskalationsentscheidung in Step 6. Dies ist eine zentrale Designentscheidung,
die in der bisherigen Literaturbasis nicht eindeutig für den PPS-Kontext beantwortet wird.

### 1.4 Wie μ und σ aus dem Modell gewonnen werden

Nach Fitten des GP (Posterior über die latente Funktion f, approximiert wie in 1.3)
liefert die Vorhersage für eine neue Planungsoption x* eine **Gauß-verteilte
Prädiktivverteilung**:

- **μ(x\*)** = Posterior-Mittelwert der latenten Präferenz-/Nutzenfunktion an x*
  (bestimmt den Rang bzw. die relative Präferenz gegenüber anderen Optionen),
- **σ²(x\*)** = Posterior-Varianz an x* (bestimmt die Selbstunsicherheit; hoch in
  Regionen mit wenigen/keinen bisherigen Präferenzvergleichen, niedrig in gut
  abgedeckten Regionen).

Dieses Muster – Mittelwert als Punktschätzung, Varianz als Unsicherheitsmaß – ist der
Kern jedes GP-Modells und wird in allen Preference-GP-Arbeiten der Benchmark-Analyse
(#1–#4) vorausgesetzt; es ist die mathematische Grundlage für den im Gesamtkonzept
vorgesehenen μ/σ-Output des PGP.

### 1.5 Rechenkomplexität und Skalierbarkeit

Exakte GP-Inferenz (Berechnung/Inversion der n×n-Kovarianzmatrix) skaliert mit
**O(n³)** in der Anzahl n der Trainingspunkte (bzw. Präferenzpaare) und **O(n²)**
im Speicherbedarf. Für PPS-Szenarien mit vielen Aufträgen/Planungsoptionen und
laufend neu hinzukommenden Präferenzurteilen (Active Learning Loop, Step 7) wird n
kontinuierlich größer – die O(n³)-Skalierung ist damit ein **hartes Skalierbarkeits-
limit** für exakte Inferenz.

Zwei in der Literatur etablierte Gegenmaßnahmen (neu recherchiert, s. Abschnitt 3.1/3.2):

- **Sparse-GP-Approximationen mit induzierenden Punkten** (Titsias, 2009): approximiert
  den vollen GP durch m ≪ n induzierende Punkte, reduziert die Komplexität auf
  **O(n·m²)**. Die induzierenden Punkte werden variational mitgelernt.
- **Stochastic Variational GP (SVGP)** (Hensman, Fusi & Lawrence, 2013): erweitert den
  Sparse-Ansatz um stochastische Variational Inference und Minibatch-Training, wodurch
  GP-Modelle auf Datensätzen mit Millionen von Punkten trainierbar werden – explizit
  auch für nicht-Gauß'sche Likelihoods (wie die Präferenz-Likelihood aus 1.2) vorgesehen.

**Bedingung für Step 5:** `step2-limits/Systemgrenzen.md` (Abschnitt A.2, "PGP (Step 5) –
Skalierungs- und Dateneffizienzgrenzen") bestätigt genau diese Grenze aus Sicht des
Projekts: Chu & Ghahramani sowie Houlsby et al. basieren auf klassischen GPs mit
kubischer Skalierung, was für eine PPS mit vielen täglichen Planungsentscheidungen "eine
harte Rechengrenze [ist], sobald die Zahl gesammelter Preference-Paare wächst". Ein
konkreter Schwellenwert für n wird dort **ebenfalls nicht genannt** – die "O³-Frage" ist
damit als Systemgrenze anerkannt, aber weiterhin nicht quantifiziert, und muss empirisch
mit den inzwischen vorliegenden Step-3-Datenvolumina ermittelt werden (`orders.csv` aus
`step3-erp-simulation/output_2024|2025`: 3990 Aufträge/Jahr; offene Frage, Abschnitt 5).

---

## 2. Technische Bedingungen

### 2.1 Implementierungsvoraussetzungen (Bibliotheken/Frameworks)

Die Benchmark-Analyse selbst benennt keine konkreten Softwarebibliotheken. Auf Basis der
oben verifizierten Inferenzverfahren (Laplace, EP/VB, sparse/stochastic variational GP)
kommen für Step 5 in der Praxis vor allem Python-GP-Bibliotheken infrage, die
nicht-Gauß'sche Likelihoods und Sparse-/SVGP-Inferenz nativ unterstützen (z. B.
GPy, GPflow oder GPyTorch – alle implementieren Laplace- bzw. variational/EP-Inferenz
und Sparse-GP-Erweiterungen im Sinne von Titsias 2009 bzw. Hensman et al. 2013).
**Dies ist eine aus der recherchierten Methodik abgeleitete technische Anforderung,
keine explizite Empfehlung aus einer der 15+ Quellen** – die konkrete Bibliothekswahl
ist offen (siehe Abschnitt 5).

### 2.2 Datenformat: ERP-Simulation (Step 3) als Input

Step 3 liefert inzwischen ein konkretes, generiertes Datenschema
(`step3-erp-simulation/output_2024|2025/*.csv`, erzeugt aus `company_profile.example.yaml`
für das Beispielunternehmen Krasser Spass GmbH):

- **`orders.csv`** – `order_id, customer, product_id, variant, order_date, due_date,
  is_rush, priority, quantity`: die naheliegendsten Präferenzkernel-Features (Dringlichkeit,
  Priorität, Liefertermin-Puffer, Kunde, Produkt).
- **`routings.csv`/`work_centers.csv`** – Arbeitspläne und Maschinenverfügbarkeit; relevant
  für Features wie Kapazitätsauslastung/Engpass-Nähe einer Planungsoption.
- **`disruptions.csv`** – Maschinenausfälle, Materialengpässe, Prioritätswechsel; potenzielle
  Quelle für die *Kontrastpaare*, an denen ein PGP tatsächlich etwas lernen kann (ein Auftrag
  vor/nach einer Störung ist ein natürlicher A-vs-B-Vergleich).
- **`produktionsauftraege.csv`** – dieselben Aufträge im Schema eines realen ERP-Exports
  (u. a. `durchlaufzeit_bkt`, `auftragsart`, `kundenstatus`) für Vergleichbarkeit mit
  externen Referenzdaten.

**Bedingung für Step 5:** Das Datenschema ist damit erstmals konkret, aber **noch nicht als
Präferenzkernel-Feature-Raum spezifiziert** – welche der obigen Spalten (und in welcher
Normierung/Kombination) den Merkmalsraum aus Abschnitt 1.1 bilden, ist eine Designentscheidung,
die in Step 5 getroffen werden muss (offene Frage, Abschnitt 5). Zu beachten: Die Simulation
bildet aktuell nur *ein* Beispielunternehmen ab (Verpackungs-/Kronkorken-Fertigung); wie gut
sich daraus abgeleitete Kernel-Features auf andere PPS-Branchen generalisieren, ist ungeklärt.

### 2.3 Trainingsdatenbedarf für Präferenzpaare

Die Benchmark-Analyse liefert keine quantitativen Angaben zur benötigten Anzahl an
Präferenzpaaren für ein produktionsreifes Präferenzmodell. Qualitativ lässt sich jedoch
aus #3, #4, #9 und #10 ableiten, dass **aktives Sampling** (gezielte Auswahl der
nächsten Vergleichsanfrage statt zufälliger Paare) den Bedarf an menschlichen/LLM-
Urteilen deutlich reduziert – Kholodna et al. (2024, #9) beziffern für ihren
Active-Learning-Loop mit LLM-Annotationen z. B. Kosteneinsparungen von mind. 42,45× ggü.
rein menschlicher Annotation, allerdings in einem NLP-Klassifikationskontext, nicht PPS.
Die neu recherchierte Quelle von Bıyık et al. (2024, Abschnitt 3.3) bestätigt diesen
Effekt explizit für **Präferenz-GP-Reward-Learning**: aktive Auswahl informativer
Trajektorienpaare reduziert den Datenbedarf gegenüber zufälliger Paarauswahl. Eine exakte
Zielgröße (z. B. "N Präferenzpaare pro Auftragstyp") ist damit weiterhin **offen** und
muss in Step 5/7 empirisch bestimmt werden.

### 2.4 Retraining-Frequenz und Latenzanforderungen

Der Active Learning Loop (Step 7) sieht laufend neue Präferenzurteile vor, die das PGP-
Modell aktualisieren sollen. Zwei Betriebsmodi sind aus der Literatur ableitbar:

- **Volles Retraining** nach jedem neuen Batch an Präferenzpaaren – korrekt, aber mit
  O(n³)-Kosten bei exakter Inferenz (s. Abschnitt 1.5) bei wachsendem n zunehmend
  unpraktikabel.
- **Inkrementelles/stochastisches Update** über Minibatches, wie es SVGP (Hensman et al.,
  2013) explizit ermöglicht – geeigneter für einen laufenden Active-Learning-Betrieb mit
  Latenzanforderungen, da nicht bei jedem neuen Paar der volle Datensatz neu verarbeitet
  werden muss.

**Bedingung für Step 5:** Konkrete Latenz-/Frequenz-Vorgaben (z. B. "Retraining alle
X Minuten" oder "Inferenz muss unter Y ms liegen, damit der LLM-Agent nicht blockiert")
sind in keiner der verfügbaren Quellen oder Projektdokumente festgelegt und müssen als
Systemanforderung für Step 5/7 noch definiert werden (offene Frage, Abschnitt 5).

---

## 3. Best Practices aus der Literatur

### 3.1 Bereits aus `Benchmark-Analyse.md` bekannt

| # | Quelle | Relevanz für PGP-Bedingungen |
|---|--------|-------------------------------|
| #1 | Chu & Ghahramani (2005), *Preference learning with Gaussian processes*, https://doi.org/10.1145/1102351.1102369 | Grundlegendes Likelihood-Modell für Paarvergleiche (probit-artig), Basis für 1.2/1.3 |
| #2 | Houlsby, Huszár, Ghahramani, Hernández-Lobato (2012), *Collaborative Gaussian Processes for Preference Learning*, https://papers.nips.cc/paper/4700-collaborative-gaussian-processes-for-preference-learning | Präferenzkernel, EP/VB-Inferenz, aktive Query-Auswahl – Basis für 1.1/1.3 |
| #3 | Bemporad & Piga (2020), *Global optimization based on active preference learning with radial basis functions*, https://doi.org/10.1007/s10994-020-05935-y | Aktives Sampling reduziert Anzahl nötiger Präferenzvergleiche (Bezug zu 2.3) |
| #4 | Ozaki et al. (2023), *Multi-Objective Bayesian Optimization with Active Preference Learning*, https://doi.org/10.48550/arXiv.2311.13460 | Unsicherheit in Zielfunktion **und** Präferenzschätzung wird gemeinsam in der Akquisitionsfunktion berücksichtigt – Vorbild für μ/σ-Nutzung in Step 6/7 |
| #9 | Kholodna et al. (2024), *LLMs in the Loop*, https://doi.org/10.48550/arXiv.2404.02261 | Quantifizierter Effizienzgewinn durch Active-Learning-Loop mit LLM-Annotation (Bezug zu 2.3) |
| #11/#12 | Liu et al. (2025); Mao et al. (2025), Uncertainty-Quantification-/Selective-Prediction-Surveys | Kontext für Kalibrierung von σ ggü. LLM-Konfidenz (Step 6), nicht PGP-spezifisch, aber methodisch anschlussfähig |

### 3.2 Neu recherchiert (verifiziert über PMLR/arXiv/SAGE, 27.07.2026)

- **Titsias, M. (2009). *Variational Learning of Inducing Variables in Sparse Gaussian
  Processes*. Proceedings of AISTATS 2009 (PMLR Vol. 5), S. 567–574.**
  Link: https://proceedings.mlr.press/v5/titsias09a.html
  Abstract (verifiziert): Führt induzierende Punkte als variationale Parameter ein, die
  über Minimierung der KL-Divergenz zur wahren Posterior mitgelernt werden; reduziert
  die Inferenzkosten von O(n³) auf O(n·m²) mit m ≪ n induzierenden Punkten.
  **Einordnung:** Zentral für Abschnitt 1.5 (Skalierbarkeit) und Abschnitt 2.4
  (Retraining-Effizienz) – relevant für Step 5, sobald die Anzahl der Präferenzpaare aus
  Step 7 (Active Learning Loop) über eine mit exakter Inferenz noch praktikable Größe
  hinauswächst.

- **Hensman, J., Fusi, N., & Lawrence, N. D. (2013). *Gaussian Processes for Big Data*.
  Proceedings of UAI 2013, S. 282–290.**
  Link: https://arxiv.org/abs/1309.6835
  Abstract (verifiziert): Führt stochastische Variational Inference für GPs ein, die GP-
  Training auf Datensätzen mit Millionen Punkten ermöglicht, inklusive Erweiterung auf
  nicht-Gauß'sche Likelihoods.
  **Einordnung:** Direkt anschlussfähig an die Präferenz-Likelihood aus Abschnitt 1.2;
  liefert die technische Grundlage für inkrementelles/minibatch-basiertes Retraining
  (Abschnitt 2.4) im Active Learning Loop (Step 7).

- **González, J., Dai, Z., Damianou, A., & Lawrence, N. D. (2017). *Preferential
  Bayesian Optimization*. Proceedings of ICML 2017 (PMLR Vol. 70), S. 1282–1291.**
  Link: https://proceedings.mlr.press/v70/gonzalez17a.html
  Abstract (verifiziert): Modelliert den Ausgang von paarweisen "Duellen" über ein GP mit
  Bernoulli-Likelihood; entwickelt Akquisitionsfunktionen, die Korrelationen zwischen
  Duellen ausnutzen, um die Anzahl nötiger Vergleiche zu reduzieren.
  **Einordnung:** Konkretisiert das Likelihood-Modell aus Abschnitt 1.2 und liefert ein
  direktes methodisches Vorbild für die Kombination aus PGP (Step 5) und Active Learning
  Loop (Step 7) – ergänzt #3/#4 aus der Benchmark-Analyse um eine explizite
  GP-Bernoulli-Formulierung.

- **Rasmussen, C. E., & Williams, C. K. I. (2006). *Gaussian Processes for Machine
  Learning*. MIT Press. Kapitel 3 ("Classification"), frei verfügbar unter
  https://gaussianprocess.org/gpml/chapters/RW3.pdf**
  Inhalt (verifiziert): Kanonische Herleitung der Laplace-Approximation für GP-
  Klassifikation (Abschnitt 3.4) sowie Multiclass-Erweiterung (3.5), inkl. Algorithmus
  für Vorhersage aus dem approximierten Posterior-Modus.
  **Einordnung:** Referenzquelle für das in Abschnitt 1.3 genannte Laplace-
  Approximationsverfahren als einfachste Inferenzoption für den PGP.

- **Bıyık, E., Huynh, N., Kochenderfer, M. J., & Sadigh, D. (2024). *Active
  preference-based Gaussian process regression for reward learning and optimization*.
  The International Journal of Robotics Research.**
  DOI: https://doi.org/10.1177/02783649231208729
  Abstract (verifiziert): Datenffizientes Verfahren zum Lernen von Belohnungsfunktionen
  aus Präferenzvergleichen mittels GP-Modellierung und aktiver Auswahl informativer
  Trajektorienpaare; vermeidet restriktive Linearitätsannahmen bei vertretbarer
  Rechenkomplexität; validiert in drei Simulationsumgebungen und einer Nutzerstudie mit
  einem Manipulator-Roboter.
  **Einordnung:** Direkt relevantes, aktuelles Beispiel für "PGP + aktive Query-
  Auswahl" außerhalb reiner Optimierungs-Benchmarks (näher an realer
  Mensch-Feedback-Anwendung als #3/#4) – stützt Abschnitt 2.3 (Trainingsdatenbedarf).

- **Melo, L. C., Tigas, P., Abate, A., & Gal, Y. (2024). *Deep Bayesian Active Learning
  for Preference Modeling in Large Language Models*.**
  arXiv: https://arxiv.org/abs/2406.10023
  Abstract (verifiziert): Stellt BAL-PM vor, ein Verfahren zur Auswahl der
  informativsten Beispiele für menschliches Feedback beim Training von Präferenz-
  modellen; kombiniert epistemische Unsicherheit mit Diversität im Feature-Raum der
  ausgewählten Prompts; erzielt 33–68 % weniger benötigte Präferenz-Labels gegenüber
  bestehenden Bayesian-Acquisition-Methoden.
  **Einordnung:** Ergänzt #9/#10 der Benchmark-Analyse um eine explizit
  unsicherheitsbasierte (statt rein LLM-gestützte) Query-Auswahl-Strategie für Active
  Learning bei Präferenzmodellen – methodisch relevant für Step 7, wenn σ aus dem PGP
  (nicht nur LLM-Konfidenz) zur Steuerung der nächsten Abfrage genutzt werden soll.

---

## 4. Zusammenfassung: μ/σ-Erzeugung im Überblick

1. Präferenzpaare (A > B) aus Step 3/7 → Likelihood-Modell (probit/Bernoulli, 1.2)
2. GP-Prior + Präferenzkernel über Planungsoptionen (1.1)
3. Approximative Inferenz: Laplace (einfach) oder EP/VB/SVGP (skalierbar, 1.3/1.5)
4. Prädiktivverteilung an neuer Option x*: **μ(x\*)** = Rang-/Präferenzprognose,
   **σ(x\*)** = Selbstunsicherheit (1.4)
5. μ/σ → Vergleich mit LLM-Einschätzung → τ/σ-Schwellenwert (Step 6) → ggf. Eskalation

---

## 5. Offene Fragen und Risiken für die Umsetzung in Step 5

1. **O³-Frage weiter unquantifiziert:** `Systemgrenzen.md` A.2 bestätigt die kubische
   Skalierung als harte Rechengrenze, nennt aber ebenfalls keinen Schwellenwert für n. Muss
   empirisch mit den jetzt vorliegenden Step-3-Datenvolumina (3990 Aufträge/Jahr, siehe 2.2)
   getestet werden, ggf. mit Sparse-GP/SVGP (Titsias 2009; Hensman et al. 2013) als
   Ausweichoption ab einer noch zu bestimmenden Schwelle.
2. **Kernel-/Feature-Definition offen:** Das Datenschema aus Step 3 liegt jetzt vor (2.2),
   welche Spalten/Kombinationen daraus den Merkmalsraum für den Präferenzkernel bilden, ist
   aber weiterhin nicht entschieden.
3. **Inferenzverfahren-Wahl (Laplace vs. EP/VB vs. SVGP) nicht entschieden:** Trade-off
   zwischen Implementierungsaufwand und Kalibrierungsgüte von σ ist in der Literatur
   dokumentiert (Abschnitt 1.3/1.5), aber nicht für den PPS-Anwendungsfall entschieden.
4. **Trainingsdatenbedarf (Anzahl Präferenzpaare) nicht quantifiziert:** Qualitative
   Hinweise auf Effizienzgewinne durch aktives Sampling liegen vor (#3, #4, #9, Bıyık et
   al. 2024), aber keine konkrete Zielgröße für den PPS-Kontext.
5. **Retraining-Frequenz/Latenzbudget nicht definiert:** Es fehlt eine explizite
   Systemanforderung (z. B. maximale Inferenzzeit, Retraining-Takt), die sich aus dem
   Zusammenspiel mit dem LLM-Agenten und Step 7 (Active Learning Loop) ergeben müsste.
6. **Bibliothekswahl offen:** GPy/GPflow/GPyTorch sind plausible Kandidaten (aus den
   verifizierten Inferenzverfahren abgeleitet), aber nicht durch eine Quelle explizit für
   diesen Anwendungsfall empfohlen; Auswahl sollte Sparse-/SVGP-Unterstützung und
   Kompatibilität mit dem Docker/Python-Stack der übrigen Steps berücksichtigen.
7. **Kalibrierungs-Rückkopplung zu Step 6:** Wie σ aus dem PGP konkret mit der
   LLM-Konfidenz kombiniert bzw. gegen τ-Schwellenwerte verglichen wird, ist Gegenstand
   von Step 6 und hier bewusst nicht vorweggenommen.
