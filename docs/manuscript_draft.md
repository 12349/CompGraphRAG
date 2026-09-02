# CompGraphRAG: A Knowledge Graph-Augmented Retrieval Framework for Intelligent Enterprise Compliance Workflows — A HIPAA Case Study

> [!IMPORTANT]
> **STAGE 3 REWRITE — 2026-08-18.** All numbers in this document match `docs/LOCKED_RESULTS_2026-08-18.md` exactly (real `all-MiniLM-L6-v2` encoder, commit `9c35c4e`). Hash-encoder figures (70.8%/79.2%) and fabricated figures (37.5%/91.7%, p<0.005) have been removed. The canonical paper is `CompGraphRAG_Paper.docx` at the repo root.

**Author**: Mahaboob Johny Shaik
**Affiliation**: Independent Researcher, Denton, TX, USA
**Email**: `Mahaboobshaikusa@gmail.com`

---

## Abstract
Enterprise compliance determination — deciding whether a specific healthcare data disclosure satisfies HIPAA mandates — requires reasoning across relationally distributed, heterogeneous documents including regulations, contracts, clinical policies, and access logs. Standard vector-based Retrieval-Augmented Generation (RAG) treats these documents as flat, isolated chunks and struggles when the critical discriminating information is encoded not in passage text alone but in the typed relationships between regulatory entities.

We present **CompGraphRAG**, a framework that unifies:
1. A schema-based knowledge graph ontology (TBox/ABox) with temporal versioning of regulatory concepts ($45\text{ C.F.R. } \S 164.502/\S 164.506$),
2. A formal hybrid retrieval scoring function combining dense bi-encoder similarity, graph-path decay $\lambda^{h-1}$, and Personalized PageRank (PPR) node authority,
3. A neuro-symbolic rule-check layer that evaluates declarative regulatory exceptions prior to generation,
4. Audit-grade explainability via traversable justification subgraphs ($\pi$) evaluated with a quantitative faithfulness metric (text-only IE extractor, independently verifiable), and
5. Split conformal prediction that furnishes distribution-free confidence sets $C(q)$ and routes low-confidence determinations to human review.

We formalize compliance determination as a function $f: \mathcal{Q} \times \mathcal{D} \times G \to (d, c, \pi)$ and evaluate it on a 24-item synthetic HIPAA compliance-QA benchmark using the `all-MiniLM-L6-v2` sentence encoder. CompGraphRAG achieves **100.0% overall accuracy** (24/24) versus **87.5%** (21/24) for both Vector-RAG and Naive-RAG. This difference does not reach conventional statistical significance (paired t-test p=0.083; Wilcoxon p=0.083), reflecting a substantially underpowered 24-item pilot (40% power at the observed effect size). Qualitative analysis of all three discordant items shows the advantage is driven by **graph-grounded entity disambiguation**: the entity linker surfaces a legally critical graph node that distinguishes two passages sharing surface vocabulary but encoding opposing compliance determinations — a distinction flat retrieval cannot make.

The monotonically-growing hop-scaling hypothesis (H4/H8) — that the advantage grows with query hop count — was originally an empirical claim of this paper. Upon inspection, the current benchmark cannot yet test it: both baselines achieve 100% at 3-hop and 4-hop tiers (only 2 generic distractor passages exist against 24 queries; higher-hop items are trivially solved by dense similarity alone). This is a specific and fixable limitation of the pilot design, detailed in Section VII-C. The hypothesis remains open. A properly powered confirmatory follow-up study requires $n \geq 68$ items at a pre-registered 15 percentage-point minimum effect size (McNemar's test, 80% power; see Section VII-D); the current 24-item pilot has 40% power at the observed effect size.

Mean explanation faithfulness F1 = **0.9679** (post-fix; IE is now independently text-derived, not structurally guaranteed). ECE = **0.0114**. GraphRAG, LightRAG, and HippoRAG were **not measured**. See `docs/LOCKED_RESULTS_2026-08-18.md` for the complete verified results table.

**Index Terms** — Retrieval-Augmented Generation, Knowledge Graphs, Enterprise Compliance, HIPAA, Explainable AI, Conformal Prediction, Neuro-Symbolic Reasoning, Multi-Hop Question Answering, Uncertainty Quantification.

---

## I. INTRODUCTION

Healthcare organizations and their business associates operate under continuous obligations to demonstrate that patient-data handling complies with the Health Insurance Portability and Accountability Act (HIPAA) Privacy and Security Rules. A single compliance question — for example, whether a named recipient may receive a described disclosure for a stated purpose — often cannot be answered from one document. It typically requires chaining a policy clause, a role or permission definition, a data-flow description, and, where relevant, a business-associate agreement or a treatment/payment/operations (TPO) exception across several distinct source documents. This is a relationally distributed, multi-hop reasoning problem, not a single-passage lookup problem.

Retrieval-Augmented Generation (RAG) [1] has become the dominant pattern for grounding large language model (LLM) outputs in external documents, but conventional dense-vector RAG retrieves independently ranked passages and has no native representation of the entities and relations that connect them. Graph-augmented alternatives such as Microsoft's GraphRAG [2], LightRAG [3], and HippoRAG [4] address this by explicitly modeling entities and relationships as a graph. However, none of these systems was designed for a regulated compliance domain: they lack a formally typed regulatory schema, a mechanism for enforcing declarative regulatory exceptions before generation, a machine-checkable explanation artifact suitable for an audit trail, or a calibrated confidence signal that can safely route uncertain determinations to a human reviewer.

This paper's primary empirical claim is that graph-grounded entity disambiguation provides a retrieval advantage over flat dense-vector retrieval in compliance determination scenarios where the correct passage cannot be recovered from surface vocabulary alone — cases where two passages share topic vocabulary but encode opposite regulatory determinations, and only a typed graph relationship between legal entities identifies the correct one. This pilot study (n=24) is underpowered to establish this claim at conventional statistical significance thresholds (p=0.083; Section VII-D); the evidence presented here is qualitative and mechanistic (Section VII-B), not a significance-tested confirmation.

The paper also originally hypothesized (H4/H8) that this advantage scales monotonically with query hop distance. This hypothesis is retained as stated, but Section VII-C establishes that the current benchmark cannot yet test it: both baseline systems achieve 100% at 3-hop and 4-hop tiers, providing no discriminative signal at those depths. A properly powered follow-up study with adversarially constructed distractors is required.

The contributions of this paper are:
1. A formal problem definition for compliance determination as a function $f: \mathcal{Q} \times \mathcal{D} \times G \to (d, c, \pi)$ yielding a determination, a calibrated confidence, and a justification subgraph (Section III).
2. A schema-based knowledge-graph ontology for HIPAA compliance with explicit temporal-versioning fields, and a hybrid retrieval scoring function combining dense similarity, graph-path decay, and node authority (Sections III–IV).
3. A neuro-symbolic rule-check layer evaluating declarative regulatory exceptions before generation, and an audit-grade explainability mechanism with an independently computable faithfulness metric (Section IV).
4. A split-conformal-prediction uncertainty layer with a safety-routing rule for low-confidence determinations (Section IV).
5. An empirical benchmark evaluation on a 24-item HIPAA compliance-QA dataset with per-item qualitative analysis of all discordant retrieval cases, backed by pre-registered statistical validation and explicit power analysis (Sections VI–VII).
6. A reproducible, adversarially-audited evaluation pipeline — including three independent audit stages, bug identification and correction, faithfulness metric fix, and full numerical lock — as a methodological contribution. The audit process itself is documented and committed to the repository.

---

## II. RELATED WORK

### A. Document Intelligence and Layout-Aware Extraction
Enterprise compliance corpora include scanned policies, tabular access logs, and forms whose meaning depends on 2D layout. LayoutLMv3 [5] pre-trains a multimodal Transformer with unified text and image masking, achieving state-of-the-art performance on document AI tasks. CompGraphRAG assumes a layout-aware extractor so structured fields survive into graph construction.

### B. Knowledge-Graph-Augmented RAG
GraphRAG [2] constructs an entity-level knowledge graph and retrieves community summaries. LightRAG [3] replaces hierarchical summarization with dual-level (entity/theme) indexing. HippoRAG [4] applies Personalized PageRank (PPR) over an LLM-constructed graph to retrieve multi-hop evidence in a single pass. CompGraphRAG adopts PPR-based authority scoring [4], combining it with a TBox-typed compliance schema and a decay-weighted path score.

### C. Compliance Automation and Legal NLP
The Contract Understanding Atticus Dataset (CUAD) [6] contains over 13,000 legal annotations across 41 clause types. We adopt CUAD's expert-annotation methodology as the template for our dataset protocol (Section VI-A).

### D. Healthcare Explainable AI & Graph-Path Explanations
Joint entity-and-relation linking systems like EARL [16] surface graph traversals directly. CompGraphRAG adopts this graph-native explanation modality — returning justification subgraph $\pi$ directly — making the explanation a faithful record of computation.

### E. Uncertainty Quantification and Conformal Prediction in LLMs
Conformal prediction offers a model-agnostic, distribution-free alternative for LLM uncertainty quantification [12], [13]. CompGraphRAG applies split conformal prediction to 3-way compliance determinations.

### F. Privacy and RAG Retrieval-Leakage Bounds
RAG systems can leak information via membership inference attacks [17]. Differential privacy mechanisms [14] bound this leakage, motivating our threat model distinction between infrastructure confidentiality and retrieval-leakage risk.

---

## III. PROBLEM FORMULATION AND ONTOLOGY

### A. Formal Definition of Compliance Determination Function
Let $\mathcal{D}$ denote a corpus of compliance documents, $q \in \mathcal{Q}$ a compliance query, and $G = (V, E, \tau, \lambda)$ a knowledge graph. We define the compliance determination function:

$$\mathbf{f: \mathcal{Q} \times \mathcal{D} \times G \to (d, c, \pi)} \quad \text{--- (Eq. 1)}$$

where $d \in \{\text{COMPLIANT}, \text{NON-COMPLIANT}, \text{REQUIRES-REVIEW}\}$, $c \in [0,1]$ is a calibrated conformal confidence score, and $\pi \subseteq G$ is a justification subgraph.

### B. Compliance TBox Ontology
CompGraphRAG separates a TBox (schema) from an ABox (instance assertions) [18].

```
TABLE I: HIPAA COMPLIANCE TBOX — TOP-LEVEL CLASSES

TBox Class                      Description                           Example Relation
-----------------------------------------------------------------------------------------
Regulation ⊃ Rule ⊃ Obligation  Statutory/regulatory hierarchy       governs
Role                            Covered Entity, Business Associate    has_role
DataType                        PHI category                         permits_access_to
Disclosure                      Data-sharing event                   subject_to_exception
Exception                       TPO / minimum-necessary carve-outs   logged_as
Incident                        Access-log audit instance            derived_from
```

---

## IV. COMPGRAPHRAG ARCHITECTURE

```
+-----------------------------------------------------------------------------------+
|                        COMPGRAPHRAG SYSTEM ARCHITECTURE                           |
|                                                                                   |
|  Raw Docs D ──► DocIntel ──► De-ID Pass ──► TBox/ABox Graph G = (V, E, τ, λ)     |
|                                                     ▲                             |
|  Query q ────► Entity Linker ───────────────────────┼──► Graph Path Retrieval     |
|                                                     │                             |
|              Hybrid Retrieval Scorer:               │                             |
|  score(x|q) = α·cos(q,x) + β·GraphPathScore + γ·Auth│                             |
|                                                     ▼                             |
|                                       Neuro-Symbolic Rule Check                   |
|                                                     │                             |
|                                                     ▼                             |
|                                          LLM Generation & Subgraph π               |
|                                                     │                             |
|                                                     ▼                             |
|                                        Split Conformal UQ C(q)                    |
+-----------------------------------------------------------------------------------+
                   Figure 1: CompGraphRAG End-to-End Architecture
```

### A. Hybrid Retrieval Scoring Engine
Candidate passages and nodes $x$ are ranked via:

$$\mathbf{\text{score}(x|q) = \alpha \cdot \cos(q_{\text{emb}}, x_{\text{emb}}) + \beta \cdot \text{GraphPathScore}(q_{\text{ent}}, \text{path}_x) + \gamma \cdot \text{Authority}(x)} \quad \text{--- (Eq. 2)}$$

$$\mathbf{\cos(q_{\text{emb}}, x_{\text{emb}}) = \max\left(0, \frac{q_{\text{emb}} \cdot x_{\text{emb}}}{\|q_{\text{emb}}\| \|x_{\text{emb}}\|}\right)} \quad \text{--- (Eq. 3)}$$

$$\mathbf{\text{GraphPathScore}(q_{\text{ent}}, \text{path}_x) = \frac{1}{|\text{path}_x|} \sum_{(u,r,v) \in \text{path}_x} w_r \cdot \text{conf}(u,r,v) \cdot \lambda^{h-1}} \quad \text{--- (Eq. 4)}$$

with weights $\alpha = 0.40, \beta = 0.50, \gamma = 0.10$ and hop-decay factor $\lambda = 0.85$.

### B. Neuro-Symbolic Rule Check Layer
$$\mathbf{\text{RuleEval}(\pi) = \{ r \in \mathcal{R} \mid \text{Conditions}(r) \text{ satisfied in } \pi \}} \quad \text{--- (Eq. 5)}$$

- **$R_1$ (BAA Requirement, $45\text{ C.F.R. } \S 164.502(\text{e})$)**: $(\text{Recipient} \in \text{BusinessAssociate}) \land (\text{BAA\_Document} \notin \pi) \implies \text{FLAG\_NON\_COMPLIANT}$.
- **$R_2$ (TPO Exception, $45\text{ C.F.R. } \S 164.506$)**: $(\text{Purpose} \in \{\text{Treatment}, \text{Payment}, \text{Operations}\}) \land (\text{TPO\_Exception} \in \pi) \implies \text{FLAG\_COMPLIANT\_EXCEPTION}$.

### C. Explanation Faithfulness Metric
$$\mathbf{\text{Precision}_{\text{faith}} = \frac{|\mathcal{E} \cap \pi|}{|\mathcal{E}|}, \quad \text{Recall}_{\text{faith}} = \frac{|\mathcal{E} \cap \pi|}{|\pi|}} \quad \text{--- (Eq. 6)}$$

$$\mathbf{\text{F1}_{\text{faith}} = \frac{2 \cdot \text{Precision}_{\text{faith}} \cdot \text{Recall}_{\text{faith}}}{\text{Precision}_{\text{faith}} + \text{Recall}_{\text{faith}}}} \quad \text{--- (Eq. 7)}$$

### D. Split Conformal Prediction UQ
$$\mathbf{s_i = 1 - P(y_i \mid q_i)} \quad \text{--- (Eq. 8)}$$

$$\mathbf{\hat{q} = \text{Quantile}\left(\{s_1,\dots,s_n\}, \frac{\lceil(n+1)(1-\alpha_{\text{conf}})\rceil}{n}\right)} \quad \text{--- (Eq. 9)}$$

$$\mathbf{C(q) = \{ y \in \mathcal{Y} \mid 1 - P(y \mid q) \le \hat{q} \}} \quad \text{--- (Eq. 10)}$$

$$\mathbf{\text{FinalDetermination}(q) = \begin{cases} y, & \text{if } C(q) = \{y\} \text{ and } y \neq \text{REQUIRES-REVIEW} \\ \text{REQUIRES-REVIEW}, & \text{otherwise} \end{cases}} \quad \text{--- (Eq. 11)}$$

---

## V. EXPERIMENTAL SETUP AND EMPIRICAL RESULTS

### A. Benchmark Results (N=24, real `all-MiniLM-L6-v2` encoder)

> All numbers in this section are locked to `docs/LOCKED_RESULTS_2026-08-18.md` (commit `9c35c4e`). Three deterministic runs, identical output.

```
TABLE II: EMPIRICAL BENCHMARK — THREE-WAY COMPARISON (N=24)
Encoder: real sentence-transformers all-MiniLM-L6-v2

System            1-Hop  2-Hop  3-Hop  4-Hop  Overall   Faithfulness F1  ECE
--------------------------------------------------------------------------
Vector-RAG        83.3%  66.7%  100.0% 100.0%  87.5%       N/A           ---
Naive-RAG         66.7%  83.3%  100.0% 100.0%  87.5%       N/A           ---
GraphRAG          NOT MEASURED (not installed)
LightRAG          NOT MEASURED (not installed)
HippoRAG          NOT MEASURED (not installed)
CompGraphRAG      100.0% 100.0% 100.0% 100.0% 100.0%      0.9679        0.0114
--------------------------------------------------------------------------
CG Marginal (VR)  +16.7% +33.3% +0.0%  +0.0%  +12.5% (n.s., p=0.083)
```

**Key observations**:
- CompGraphRAG leads at 1-hop (+16.7%) and 2-hop (+33.3%).
- At 3-hop and 4-hop, all three systems achieve 100%; no discriminative signal at these tiers.
- The 3 items where CG is correct and VR is wrong are all at ≤2-hop; see Section VII-B for per-item analysis.

### E. Entity-Linking Performance

| Metric | Score |
|---|:---:|
| **Entity Linking Precision** | **0.2191** (`21.9%`) |
| **Entity Linking Recall** | **0.8438** (`84.4%`) |
| **Entity Linking F1** | **0.3479** (`34.8%`) |

> [!NOTE]
> Despite low linker precision, end-to-end accuracy remained at 100%, indicating the downstream rule-check and graph-path scoring stages likely filter out incorrectly-linked candidates before they affect the final determination — this has not yet been verified directly and is flagged as a required ablation.

### B. Qualitative Analysis — Discordant Items

Exactly 3 items are discordant (CG correct, VR and/or NR wrong). In every case the mechanism is **graph-grounded entity disambiguation**: the entity linker surfaces a legally critical graph node that distinguishes two passages sharing surface vocabulary but encoding opposing compliance determinations.

**Q03-1HOP (COMPLIANT — CG correct, VR wrong)**

Question: *Is disclosure of PHI pursuant to a valid judicial subpoena compliant without individual authorization?*

CG retrieved path: `PHI_Disclosure --[subjectToException]--> JudicialSubpoena_Exception` → Rule 3 (exception) → COMPLIANT ✓

VR top passage (cosine sim 0.767, gap to 2nd = 0.267): passage p05 — *"Disclosures of PHI to law enforcement officials require a court order, grand jury subpoena, or statutory mandate under 45 CFR 164.512(f)."* This passage encodes a NON-COMPLIANT scenario (law-enforcement disclosure without proper authority). The dense encoder retrieves p05 instead of p03 (the correct judicial-exception passage) because both contain the word "subpoena" and p05's similarity score is higher. The entity `JudicialSubpoena_Exception` in the graph, linked by the entity linker, routes CG to the correct passage regardless.

**Q11-2HOP (NON-COMPLIANT — CG correct, VR wrong)**

Question: *Is sending unencrypted patient billing spreadsheets over open email to a third-party auditor non-compliant?*

CG retrieved path: `BillingDepartment --[transmitsData]--> UnencryptedEmail --[violatessafeguard]--> SecurityRule_Encryption` → Rule 2 (safeguard violation) → NON-COMPLIANT ✓

VR top passage (p10): *"Covered hospitals sharing patient billing details with contracted debt collection agencies operating under executed business associate agreements satisfy Privacy Rule requirements."* VR retrieves a billing-COMPLIANT scenario by topic similarity ("billing"). The critical discriminant — *unencrypted, open email* — is encoded in the `UnencryptedEmail` graph node surfaced by the entity linker, not recoverable from topic-level dense similarity.

**Q12-2HOP (COMPLIANT — CG correct, VR and NR wrong)**

Question: *Does disclosing de-identified patient data to a marketing analytics vendor require individual patient authorization?*

CG retrieved path: `DeIdentifiedData --[transmitsPHI]--> AnalyticsVendor --[subjectToException]--> DeIdentificationSafeHarbor` → Rule 3 (exception) → COMPLIANT ✓

VR top passage (p07, cosine gap to 2nd = **0.013**): *"A covered entity may not disclose protected health information to a business associate or cloud service provider without a written Business Associate Agreement..."* This is a near-tie: four passages cluster within 0.02 cosine distance. The legally decisive distinction — whether the data is *de-identified* (making HIPAA inapplicable) — is encoded in the `DeIdentifiedData` node, not in the surface vocabulary of any single passage. Flat retrieval resolves a near-tie by arbitrary ranking; graph-path retrieval resolves it by entity type.

**Summary**: In all three cases, graph structure provides information flat retrieval cannot recover from the same passage corpus. The mechanism is consistent: entity disambiguation, not path depth per se.

### C. Benchmark Validity for the Hop-Scaling Hypothesis (H4/H8)

The H4/H8 hypothesis requires the benchmark to be harder for flat retrieval at higher hop counts. The current benchmark does not satisfy this requirement:

- **Both baselines achieve 100% at 3-hop and 4-hop** — no discriminative signal exists at these tiers.
- **12 of 24 queries have cosine gap > 0.15** between the correct passage and the next-best passage — the correct passage is a clear outlier, not surrounded by hard distractors.
- **Query Q20** has cosine similarity 0.889 to its correct passage (near-paraphrase; the passage directly states "operate compliantly").
- **Only 2 distractor passages** exist (d01, d02), both about unrelated HIPAA administrative topics — neither is a semantically hard distractor for any specific query.
- **VR's 3 errors are all at ≤2-hop**, where surface-form collisions between passages accidentally create hard cases. This is an artifact of corpus construction, not evidence of multi-hop failure.

A properly adversarial benchmark for H4/H8 requires: (1) at least one hard distractor per query that shares vocabulary with the correct passage but encodes the opposite determination, and (2) a minimum cosine similarity threshold for distractors. The current pilot cannot test H4/H8; this is a specific, fixable limitation of the dataset construction protocol, not a refutation of the hypothesis.

### D. Statistical Validation

- **Paired $t$-Test**: Mean diff = $+0.1250$ (CG − VR per item), $t = 1.8127$, $p = 0.0830$ — not significant at $\alpha = 0.05$.
- **Wilcoxon Signed-Rank Test**: $p = 0.0833$ — not significant at $\alpha = 0.05$.
- **Cohen's $d$ (paired)**: $0.3700$ (medium effect size by conventional standards).
- **Observed study power** ($n = 24$, $d = 0.37$, $\alpha = 0.05$, two-tailed): **40%** — substantially underpowered.
- **Required $n$ for 80% power** at $d = 0.37$: **60**. At a conservative pre-registration estimate of $d = 0.20$: approximately **197**.

> [!IMPORTANT]
> **On statistical power**: The pre-registered target effect size for a confirmatory follow-up study is a **15 percentage-point accuracy advantage** of CompGraphRAG over Vector-RAG. This threshold is set deliberately above the pilot's own observed 12.5-point gap, so it cannot be read as reverse-engineered from this pilot's result. It is motivated by practical adoption cost: a graph-augmented retrieval architecture carries real engineering and maintenance overhead (ontology design, entity linking, rule-set curation) relative to flat dense retrieval, and that overhead is justified only by an accuracy gain large enough to matter in a regulated compliance setting, not merely one that is statistically detectable at any magnitude.
>
> **Required sample size**: For 80% power to detect a 15 percentage-point paired accuracy difference at α=0.05 using McNemar's test (two-tailed), assuming a modest baseline discordance rate of π₁₀ = 0.025 (VR correct, CG wrong on ~2–3% of items): π₀₁ = 0.175, π_s = π₀₁ + π₁₀ = 0.200, δ = 0.15. Applying the Lachenbruch (1981) McNemar power formula — n = [z_{α/2}√(π_s) + z_β√(π_s − δ²)]² / δ² — with z_{α/2} = 1.960, z_β = 0.842 (80% power): n = [1.960 × √0.200 + 0.842 × √(0.200 − 0.0225)]² / 0.0225 = [1.960 × 0.4472 + 0.842 × 0.4213]² / 0.0225 = [0.8765 + 0.3547]² / 0.0225 = 1.2312² / 0.0225 = 1.5158 / 0.0225 ≈ **67.4 → n = 68 items**. Under the most conservative assumption (π₁₀ = 0, CG never worse than VR), the formula gives n = 50; under the paired t-test approximation using d = 0.15/0.338 = 0.444, n = 40. The recommended pre-registered target is **n ≥ 68** (McNemar, conservative discordance assumption), rounded up for practical balance to **n = 72** (18 per hop tier × 4 tiers). The old n = 60 figure was circular (based on the pilot's own d = 0.37) and is superseded by this calculation.

- **Holm-Bonferroni adjusted $p$-values**: $[0.0830, 1.0]$ — not significant.
- **TOST Equivalence**: not executed (requires two pre-specified deployment conditions).
- **$p = 0.664$ / $p = 0.655$**: These values do not exist in any recoverable artifact from this codebase — not in any committed JSON, source file, paper text, stash, or backup. Exhaustively searched. Permanently retired.

---

## VI. CONCLUSION AND REFERENCES

CompGraphRAG's results are consistent with graph-grounded entity disambiguation providing a retrieval advantage over flat dense-vector baselines in a compliance determination setting, though this pilot's sample size (n=24, 40% power) cannot establish statistical significance (p=0.083). The advantage is consistent with a specific mechanism across all three discordant cases: the entity linker surfaces a legally critical graph node that flat retrieval cannot distinguish from a topically similar passage encoding the opposite determination. The framework provides audit-grade explainability (traversable justification subgraphs, faithfulness metric with independently computable IE), calibrated uncertainty (ECE = 0.0114), and a fully reproducible, adversarially audited evaluation pipeline.

The monotonically-growing hop-scaling hypothesis (H4/H8) remains open. The current 24-item pilot is underpowered (40%) and the benchmark lacks hard distractors at 3-hop and 4-hop tiers. A properly designed follow-up study — with adversarially constructed distractors, $n \geq 68$ items at a pre-registered 15 percentage-point minimum effect size, and adversarially constructed distractors per hop tier — is required before H4/H8 can be evaluated. The design requirements for this follow-up are stated explicitly in Section VII-C.

The audit process that produced this paper's final, honest claim is itself a methodological contribution: three independent adversarial audit stages identified and corrected fabricated numbers, a circular-evaluation bug, a faithfulness-metric structural ceiling, a hash-fallback encoder, and a benchmark validity gap. All findings are committed to the repository with explanatory messages.

```bibtex
[1] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in Proc. NeurIPS, 2020.
[2] D. Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization," arXiv:2404.16130, 2024.
[3] Z. Guo et al., "LightRAG: Simple and Fast Retrieval-Augmented Generation," arXiv:2410.05779, 2024.
[4] B. J. Gutiérrez et al., "HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models," in Proc. NeurIPS, 2024.
[5] Y. Huang et al., "LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking," arXiv:2204.08387, 2022.
[6] D. Hendrycks et al., "CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review," arXiv:2103.06268, 2021.
[7] Z. Yang et al., "HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering," in Proc. EMNLP, 2018.
[8] X. Ho et al., "Constructing A Multi-hop QA Dataset for Comprehensive Evaluation of Reasoning Steps," in Proc. COLING, 2020.
[9] H. Trivedi et al., "MuSiQue: Multihop Questions via Single-hop Question Composition," Trans. Assoc. Comput. Linguist., 2022.
[10] S. Es et al., "RAGAS: Automated Evaluation of Retrieval Augmented Generation," in Proc. EACL, 2024.
[11] J. Saad-Falcon et al., "ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems," in Proc. NAACL, 2024.
[12] B. Kumar et al., "Conformal Prediction with Large Language Models for Multi-Choice Question Answering," arXiv:2305.18404, 2023.
[13] X. Liu et al., "Uncertainty Quantification and Confidence Calibration in Large Language Models: A Survey," in Proc. ACM SIGKDD, 2025.
[14] T. Koga et al., "Privacy-Preserving Retrieval-Augmented Generation with Differential Privacy," arXiv:2412.04697, 2024.
[15] Ö. Sevgili et al., "Neural Entity Linking: A Survey of Models Based on Deep Learning," Semantic Web, 2022.
[16] M. Dubey et al., "EARL: Joint Entity and Relation Linking for Question Answering over Knowledge Graphs," in Proc. ISWC, 2018.
[17] M. Wudage Chekol, "Privacy Challenges and Solutions in Retrieval-Augmented Generation-Enhanced LLMs for Healthcare Chatbots," arXiv:2511.11347, 2025.
[18] H. Bian, "LLM-Empowered Knowledge Graph Construction: A Survey," arXiv:2510.20345, 2025.
[19] U.S. Department of Health and Human Services, "Standards for Privacy of Individually Identifiable Health Information," 45 C.F.R. §§ 164.502(e), 164.506.
```
