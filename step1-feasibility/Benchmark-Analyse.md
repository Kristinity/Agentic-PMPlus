# Benchmark-Analyse: Active Learning Loop + Preference-GP (PGP) + LLM in der PPS

**Stand:** 2026-07-26
**Kontext:** Recherche im Rahmen von Step 1 ("Recherche-Agent / Feasibility") des
Agentic-PMPlus-Konzepts. Das Gesamtkonzept kombiniert einen LLM-Agenten mit einem
**Preference Gaussian Process (PGP, μ/σ)** (Step 5), einer **Kalibrierung über
τ/σ-Schwellenwerte im Sinne einer Risk-Coverage-Kurve** (Step 6) und einem
**Active Learning Loop** (Step 7), um in der **Produktionsplanung und -steuerung (PPS)**
Entscheidungen zu treffen bzw. Planer zu unterstützen (siehe README.md).

Da kein publiziertes Paper gefunden wurde, das exakt "PGP + LLM + Active Learning Loop
in der PPS" in dieser Kombination beschreibt, wurden die 15 nachfolgenden Quellen aus
Google Scholar / OpenAlex / arXiv / Verlagsdatenbanken so ausgewählt, dass sie die
**Einzelbausteine** des Konzepts abdecken:

- Preference-Learning mit Gaussian Processes (PGP-Grundlagen) – #1, #2
- Aktives Preference-Learning / Preferential Bayesian Optimization (Active Loop + GP) – #3, #4, #16
- Gaussian-Process-Active-Learning direkt LLM-gesteuert (GP + Active Loop + LLM in einem System) – #17
- Preference-/RLHF-Learning mit LLMs – #6, #7, #8
- Active-Learning-Loops mit LLMs im Human-in-the-Loop-Setting – #9, #10
- Unsicherheitskalibrierung / Risk-Coverage bei LLMs – #11, #12
- LLM-Agenten in Produktionsplanung, -steuerung und Scheduling (PPS/ERP) – #13, #14, #15
- Context Engineering / RAG in der Fertigung (Step 4) – #5

Alle Angaben wurden über OpenAlex, arXiv, ACM DL, Springer, ScienceDirect, MDPI,
OpenReview bzw. NeurIPS-Proceedings verifiziert.

---

## 1. Preference learning with Gaussian processes

- **Jahr:** 2005
- **Autor(en):** Wei Chu, Zoubin Ghahramani
- **DOI-Link:** https://doi.org/10.1145/1102351.1102369 (ICML '05 / ACM DL)
- **Abstract:** The authors introduce a probabilistic kernel approach to preference
  learning based on Gaussian processes, with a new likelihood function proposed to
  capture preference relations in the Bayesian framework. The model is extended to
  multiclass problems and evaluated for its ability to learn latent utility functions
  from pairwise preference judgements.

## 2. Collaborative Gaussian Processes for Preference Learning

- **Jahr:** 2012
- **Autor(en):** Neil Houlsby, Ferenc Huszár, Zoubin Ghahramani, José Miguel Hernández-Lobato
- **DOI-Link:** https://papers.nips.cc/paper/4700-collaborative-gaussian-processes-for-preference-learning (NIPS 2012 Proceedings; kein separater DOI verfügbar)
- **Abstract:** A model based on Gaussian processes is presented for learning pairwise
  preferences expressed by multiple users, allowing the combination of supervised GP
  learning of user preferences with unsupervised dimensionality reduction. Inference is
  simplified via a preference kernel and approximated with expectation propagation and
  variational Bayes; an active learning strategy for selecting preference queries is
  also proposed.

## 3. Global optimization based on active preference learning with radial basis functions

- **Jahr:** 2020
- **Autor(en):** Alberto Bemporad, Dario Piga
- **DOI-Link:** https://doi.org/10.1007/s10994-020-05935-y
- **Abstract:** This work addresses optimization scenarios where decision-makers express
  preferences via pairwise comparisons rather than direct objective-function
  evaluations. The algorithm iteratively proposes new comparison pairs to actively
  learn a surrogate model of the latent objective function. A radial-basis-function
  surrogate, fitted via linear/quadratic programming, respects existing preferences
  while balancing exploration and exploitation through inverse-distance weighting and
  preference-probability maximization.

## 4. Multi-Objective Bayesian Optimization with Active Preference Learning

- **Jahr:** 2023
- **Autor(en):** Ryota Ozaki, Kazuki Ishikawa, Youhei Kanzaki, Shinya Suzuki, Shion Takeno, Ichiro Takeuchi, Masayuki Karasuyama
- **DOI-Link:** https://doi.org/10.48550/arXiv.2311.13460
- **Abstract:** The paper addresses real-world black-box optimization involving multiple
  simultaneous criteria. Rather than identifying the entire Pareto front, the authors
  focus on finding the decision maker's preferred solution via a Bayesian optimization
  approach that adaptively estimates preferences through interactive pairwise
  comparisons and improvement requests. The acquisition function incorporates
  uncertainty in both objective functions and preference estimation, with an active
  learning strategy minimizing interaction cost.

## 5. Empowering LLMs by hybrid retrieval-augmented generation for domain-centric Q&A in smart manufacturing

- **Jahr:** 2025
- **Autor(en):** Yuwei Wan, Zheyuan Chen, Ying Liu, Chong Chen, Michael Packianather
- **DOI-Link:** https://doi.org/10.1016/j.aei.2025.103212
- **Abstract:** Large language models demonstrate strong performance in generic
  question-answering but struggle with domain gaps and outdated knowledge in smart
  manufacturing. This research proposes a hybrid KG-Vector RAG framework integrating
  structured knowledge-graph metadata with vector retrieval, combining explicit
  reasoning with efficient similarity search. Evaluated on design-for-additive-
  manufacturing tasks, the method achieved 77.8% exact-match accuracy and 76.5% context
  precision.

## 6. A Survey on Human Preference Learning for Large Language Models

- **Jahr:** 2024
- **Autor(en):** Ruili Jiang, Kehai Chen, Xuefeng Bai, Zhixuan He, Juntao Li, Muyun Yang, Tiejun Zhao, Liqiang Nie, Min Zhang
- **DOI-Link:** https://doi.org/10.48550/arXiv.2406.11191
- **Abstract:** The survey examines how aligning increasingly capable foundation models
  with human intentions relies on preference learning. It categorizes human feedback by
  data source and format, analyzes modeling techniques for preference signals, explores
  methods for utilizing these signals, and reviews evaluation approaches for assessing
  LLM alignment — providing a comprehensive, preference-centered perspective.

## 7. Efficient Reinforcement Learning from Human Feedback via Bayesian Preference Inference

- **Jahr:** 2025
- **Autor(en):** Matteo Cercola, Valeria Capretti, Simone Formentin
- **DOI-Link:** https://doi.org/10.48550/arXiv.2511.04286
- **Abstract:** The paper proposes a hybrid framework that unifies RLHF's scalability
  with the query efficiency of Preferential Bayesian Optimization (PBO), integrating an
  acquisition-driven module into the RLHF pipeline. This enables more sample-efficient
  preference-data collection while maintaining performance on high-dimensional tasks
  such as language-model fine-tuning.

## 8. Pref-GUIDE: Continual Policy Learning from Real-Time Human Feedback via Preference-Based Learning

- **Jahr:** 2025
- **Autor(en):** Zhengran Ji, Boyuan Chen
- **DOI-Link:** https://doi.org/10.48550/arXiv.2508.07126
- **Abstract:** The authors address training RL agents when objectives are hard to
  express through traditional reward functions and offline trajectory comparisons are
  insufficient for real-time adaptation. Their framework converts real-time scalar
  feedback into preference-structured data to train the reward model, offering two
  variants — one mitigating temporal inconsistency via short-window comparisons, the
  other aggregating multi-user feedback for consensus preferences — matching
  expert-designed reward functions in testing.

## 9. LLMs in the Loop: Leveraging Large Language Model Annotations for Active Learning in Low-Resource Languages

- **Jahr:** 2024
- **Autor(en):** Nataliia Kholodna, Sahib Julka, Mohammad Khodadadi, Muhammed Nurullah Gumus, Michael Granitzer
- **DOI-Link:** https://doi.org/10.48550/arXiv.2404.02261
- **Abstract:** The paper addresses data-scarcity challenges in low-resource-language AI
  development by integrating large language models into active-learning annotation
  workflows. After initial inter-annotator-agreement assessment, a selected LLM is
  incorporated into a classifier's training loop; experiments with GPT-4-Turbo show
  strong performance with minimal labeled data, estimating potential cost savings of at
  least 42.45× versus human annotation.

## 10. Efficient Human-in-the-Loop Active Learning: A Novel Framework for Data Labeling in AI Systems

- **Jahr:** 2024
- **Autor(en):** Yiran Huang, Jian-Feng Yang, Haoda Fu
- **DOI-Link:** https://doi.org/10.48550/arXiv.2501.00277
- **Abstract:** Modern AI systems depend on labeled data, but labeling is expensive,
  particularly in specialized domains. Unlike conventional active learning, which only
  selects which data points require labels, this framework additionally determines
  optimal query strategies, integrating information from multiple query types via a
  data-driven exploration-exploitation mechanism. Tested on five real-world datasets,
  it achieved higher accuracy and lower loss than competing methods.

## 11. Uncertainty Quantification and Confidence Calibration in Large Language Models: A Survey

- **Jahr:** 2025
- **Autor(en):** Xiaoou Liu, Tiejin Chen, Longchao Da, Chacha Chen, Zhen Lin, Hua Wei
- **DOI-Link:** https://doi.org/10.48550/arXiv.2503.15850
- **Abstract:** LLMs excel in text generation, reasoning, and decision-making, enabling
  adoption in high-stakes domains such as healthcare, law, and transportation, but their
  reliability is a concern since they often produce plausible but incorrect responses.
  Uncertainty quantification (UQ) enhances trustworthiness by estimating output
  confidence and enabling selective prediction. The paper introduces a taxonomy of UQ
  methods by computational efficiency and uncertainty dimension (input, reasoning,
  parameter, prediction), evaluates existing techniques, and identifies open challenges
  toward scalable, interpretable, robust UQ.

## 12. Calibrating LLMs for Selective Prediction: Balancing Coverage and Risk (SelectLLM)

- **Jahr:** 2025
- **Autor(en):** Yuzhen Mao, Thibaut Durand, Nazanin Mehrasa, Jiawei He, Martin Ester
- **DOI-Link:** https://neurips.cc/virtual/2025/133203 (NeurIPS 2025)
- **Abstract:** Despite the impressive capabilities of LLMs, their outputs often exhibit
  inconsistent correctness and unreliable factual accuracy; in high-stakes domains,
  overconfident but incorrect predictions can have serious consequences. SelectLLM is an
  end-to-end method that integrates selective prediction into fine-tuning, optimizing
  model performance over the covered domain and achieving a better trade-off between
  predictive coverage and utility. On TriviaQA, CommonsenseQA and MedConceptsQA,
  SelectLLM significantly outperforms standard baselines, improving abstention behavior
  while maintaining high accuracy.

## 13. LLM actor-critic based dispatching rule generation for dynamic job shop scheduling

- **Jahr:** 2026
- **Autor(en):** Marvin Carl May, Shady Salama, Johannes Pflüger, Toshiya Kaihara
- **DOI-Link:** https://doi.org/10.1016/j.cirp.2026.04.007 (CIRP Annals, Vol. 75, Issue 1, S. 601–605)
- **Abstract:** Job shop scheduling is an NP-hard production problem for which
  traditional approaches require significant human expertise for heuristic design. The
  paper presents the first dual-LLM, critique-guided agentic framework for dispatching-
  rule generation in manufacturing: an actor LLM iteratively generates dispatching
  rules while a critic LLM provides performance- and structure-based feedback, combined
  with simulation-based evaluation. The resulting rules statistically dominate
  state-of-the-art dispatching rules in the evaluated scenarios.

## 14. Agentic LLM-based Contingency Management in Production Control

- **Jahr:** 2026
- **Autor(en):** Marvin Carl May, Paul Liang, Sang-Gook Kim
- **DOI-Link:** https://doi.org/10.1016/j.procir.2025.08.195 (Procedia CIRP)
- **Abstract:** The paper presents a framework utilizing localized LLM agents to
  support decision-makers facing production contingencies, addressing critical
  challenges in production planning and control — particularly managing stochastic,
  unforeseen or uninformed changes. The concept is implemented in a small-scale
  semiconductor-manufacturing testbed, where LLM agents collect historical and current
  decision reasoning, sensor data, and simulation outputs to propose contingency
  management reactions.

## 15. Large Language Model-Assisted Deep Reinforcement Learning from Human Feedback for Job Shop Scheduling

- **Jahr:** 2025
- **Autor(en):** Yuhang Zeng, Ping Lou, Jianmin Hu, Chunping Fan, Quan Liu, Jiwei Hu
- **DOI-Link:** https://doi.org/10.3390/machines13050361
- **Abstract:** The job shop scheduling problem is a classical NP-hard combinatorial
  optimization challenge with significant manufacturing relevance. While deep
  reinforcement learning (DRL) shows promise, practitioners face obstacles in reward-
  function design and state-feature representation, causing slow convergence and
  reduced effectiveness. The authors introduce an HFLLMDRL framework that uses few-shot
  prompt engineering with human feedback to craft instructive reward functions and
  accelerate policy convergence, combined with a self-adaptive symbolic Kolmogorov–
  Arnold Network (KAN) as the policy network for improved feature representation.
  Experiments show substantial gains in learning performance and convergence efficiency.

## 16. Active preference-based Gaussian process regression for reward learning and optimization

- **Jahr:** 2024
- **Autor(en):** Erdem Bıyık, Nicolas Huynh, Mykel J. Kochenderfer, Dorsa Sadigh
- **DOI-Link:** https://doi.org/10.1177/02783649231208729 (The International Journal of Robotics Research)
- **Abstract:** Designing reward functions is a longstanding challenge in AI and robotics.
  The authors present a preference-based learning approach in which human feedback takes
  the form of comparisons between trajectories, modeling the reward function with a
  Gaussian process instead of assuming a linear structure, and actively fitting this model
  using only preference comparisons. The paper addresses both the inflexibility of linear
  reward models and the data-inefficiency of naive active-learning approaches, presenting
  a reward-learning variant and a reward-optimization variant (for when only the optimal
  trajectory matters, not the full reward landscape). Simulation experiments and robot
  user studies show the method outperforms linear-model and random-querying baselines in
  both reward learning and reward optimization.

## 17. Bayesian Active Learning with Gaussian Processes Guided by LLM Relevance Scoring for Dense Passage Retrieval

- **Jahr:** 2026
- **Autor(en):** Junyoung Kim, Anton Korikov, Jiazhou Liang, Justin Cui, Yifan Simon Liu, Qianfeng Wen, Mark Zhao, Scott Sanner
- **DOI-Link:** https://doi.org/10.48550/arXiv.2604.17906
- **Abstract:** While LLMs exhibit exceptional zero-shot relevance modeling, their high
  computational cost necessitates framing passage retrieval as a budget-constrained global
  optimization problem. Existing approaches passively rely on first-stage dense
  retrievers, which fail to retrieve relevant passages in semantically distinct clusters
  and fail to propagate relevance signals to the broader corpus. The authors propose BAGEL
  (Bayesian Active Learning with Gaussian Processes guided by LLM relevance scoring), which
  propagates sparse LLM relevance signals across the embedding space via a query-specific
  Gaussian Process to guide global exploration, iteratively selecting passages for scoring
  by balancing exploitation of high-confidence regions against exploration of uncertain
  areas. Across four benchmark datasets and two LLM backbones, BAGEL outperforms LLM
  reranking methods under the same LLM budget.

---

## Einordnung zum Agentic-PMPlus-Konzept

Am nächsten am eigenen Konzept (LLM-Agent + PGP + Kalibrierung + Active Loop, konkret
in der PPS) liegen **#13** und **#14** (May et al.), die bereits LLM-Agenten direkt in
Produktionssteuerung/-planung und Job-Shop-Scheduling einsetzen, sowie **#3/#4/#16**
(Bemporad & Piga; Ozaki et al.; Bıyık et al.), die den methodischen Kern eines *aktiven*
Preference-/Reward-Learning-Loops mit Gaussian-Process-Surrogat liefern — genau die
Kombination, die Step 5 (PGP) und Step 7 (Active Learning Loop) im eigenen Konzept
vorsehen. **#17** (Kim et al., BAGEL) kombiniert methodisch am direktesten alle drei
technischen Kernbausteine PGP + Active Loop + LLM-Steuerung in einem einzigen System —
allerdings für Dense Passage Retrieval, nicht für die PPS, und ohne
τ/σ-Kalibrierungsschicht. Keine der gefundenen Quellen kombiniert alle vier Bausteine
(LLM-Agent + PGP + τ/σ-Kalibrierung + Active Loop) gleichzeitig in der PPS — das eigene
Konzept adressiert damit eine bislang in der Literatur nicht geschlossene Kombination und
erscheint auf Basis dieser Benchmark-Analyse **machbar, aber als neuartige Kombination
bestehender Bausteine** einzuordnen.
