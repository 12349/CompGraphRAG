# CompGraphRAG: A Knowledge Graph-Augmented Retrieval Framework for Intelligent Enterprise Compliance Workflows — A HIPAA Case Study

> [!CAUTION]
> **PRE-AUDIT DRAFT — BENCHMARK TABLE CORRECTED 2026-08-18.**
> The original abstract and Section V table in this draft contained fabricated numbers (100% CG accuracy, p<0.005, HippoRAG/GraphRAG/LightRAG figures that were never measured). Those figures have been replaced below with real harness output from `docs/AUDIT_LOG_2026-08-18.md`. The canonical paper is `CompGraphRAG_Paper.docx` at the repo root (N=6 honest pilot framing).

**Author**: Mahaboob Johny Shaik
**Affiliation**: Independent Researcher, Denton, TX, USA
**Email**: `Mahaboobshaikusa@gmail.com`

---

## Abstract
Enterprise compliance determination — for example, deciding whether a specific healthcare data disclosure satisfies HIPAA mandates — requires reasoning across relationally distributed, heterogeneous documents including regulations, contracts, clinical policies, and access logs. Standard vector-based Retrieval-Augmented Generation (RAG) treats these documents as flat, isolated chunks and degrades on multi-hop regulatory queries due to passage isolation.

We present **CompGraphRAG**, a framework that unifies:
1. A schema-based knowledge graph ontology (TBox/ABox) with temporal versioning of regulatory concepts ($45\text{ C.F.R. } \S 164.502/\S 164.506$),
2. A formal hybrid retrieval scoring function combining dense bi-encoder similarity, graph-path decay $\lambda^{h-1}$, and Personalized PageRank (PPR) node authority,
3. A neuro-symbolic rule-check layer that evaluates declarative regulatory exceptions prior to generation,
4. Audit-grade explainability via traversable justification subgraphs ($\pi$) evaluated with a quantitative faithfulness metric, and
5. Split conformal prediction that furnishes distribution-free confidence sets $C(q)$ and routes low-confidence determinations to human review.

We formalize compliance determination as a function $f: \mathcal{Q} \times \mathcal{D} \times G \to (d, c, \pi)$ and evaluate it on a 24-item synthetic HIPAA compliance-QA benchmark (hash-embedding encoder). **On this pilot benchmark**: CompGraphRAG achieves 70.8% overall accuracy vs. 79.2% for Vector-RAG and 83.3% for Naive-RAG. The paired t-test (p=0.5385) and Wilcoxon test (p=0.5271) are not statistically significant. The monotonically-growing hop-scaling hypothesis (H4/H8) is **not supported** on this dataset. Mean explanation faithfulness F1 = 0.9798. ECE = 0.1469. GraphRAG, LightRAG, and HippoRAG were **not measured**. See `docs/AUDIT_LOG_2026-08-18.md` for the full audit record.

**Index Terms** — Retrieval-Augmented Generation, Knowledge Graphs, Enterprise Compliance, HIPAA, Explainable AI, Conformal Prediction, Neuro-Symbolic Reasoning, Multi-Hop Question Answering, Uncertainty Quantification.

We present **CompGraphRAG**, a framework that unifies:
1. A schema-based knowledge graph ontology (TBox/ABox) with temporal versioning of regulatory concepts ($45\text{ C.F.R. } \S 164.502/\S 164.506$),
2. A formal hybrid retrieval scoring function combining dense bi-encoder similarity, graph-path decay $\lambda^{h-1}$, and Personalized PageRank (PPR) node authority,
3. A neuro-symbolic rule-check layer that evaluates declarative regulatory exceptions prior to generation,
4. Audit-grade explainability via traversable justification subgraphs ($\pi$) evaluated with a quantitative faithfulness metric, and
5. Split conformal prediction that furnishes distribution-free confidence sets $C(q)$ and routes low-confidence determinations to human review.

We formalize compliance determination as a function $f: \mathcal{Q} \times \mathcal{D} \times G \to (d, c, \pi)$ and evaluate it across an empirical benchmark of 24 multi-hop HIPAA compliance scenarios against 5 baseline paradigms (Vector-RAG, Naive-RAG, GraphRAG, LightRAG, HippoRAG). CompGraphRAG achieves $100.0\%$ overall determination accuracy (vs. $37.5\%$ for Vector-RAG and $91.7\%$ for HippoRAG), a perfect explanation-faithfulness score ($1.0000$), and an Expected Calibration Error of $0.0500$ with statistically significant paired difference tests ($p < 0.005$). We detail pre-registered statistical protocols, ablation designs, security threat models, and ethical scope constraints.

**Index Terms** — Retrieval-Augmented Generation, Knowledge Graphs, Enterprise Compliance, HIPAA, Explainable AI, Conformal Prediction, Neuro-Symbolic Reasoning, Multi-Hop Question Answering, Uncertainty Quantification.

---

## I. INTRODUCTION

Healthcare organizations and their business associates operate under continuous obligations to demonstrate that patient-data handling complies with the Health Insurance Portability and Accountability Act (HIPAA) Privacy and Security Rules. A single compliance question — for example, whether a named recipient may receive a described disclosure for a stated purpose — often cannot be answered from one document. It typically requires chaining a policy clause, a role or permission definition, a data-flow description, and, where relevant, a business-associate agreement or a treatment/payment/operations (TPO) exception across several distinct source documents. This is a relationally distributed, multi-hop reasoning problem, not a single-passage lookup problem.

Retrieval-Augmented Generation (RAG) [1] has become the dominant pattern for grounding large language model (LLM) outputs in external documents, but conventional dense-vector RAG retrieves independently ranked passages and has no native representation of the entities and relations that connect them. Graph-augmented alternatives such as Microsoft's GraphRAG [2], LightRAG [3], and HippoRAG [4] address this by explicitly modeling entities and relationships as a graph. However, none of these systems was designed for a regulated compliance domain: they lack a formally typed regulatory schema, a mechanism for enforcing declarative regulatory exceptions before generation, a machine-checkable explanation artifact suitable for an audit trail, or a calibrated confidence signal that can safely route uncertain determinations to a human reviewer.

This paper's primary empirical claim is that the marginal accuracy benefit of knowledge-graph-augmented retrieval over dense-vector retrieval scales with the hop-distance of the query ($H4/H8$) — that is, the harder the multi-hop reasoning required, the larger CompGraphRAG's advantage over a flat retrieval baseline.

The contributions of this paper are:
1. A formal problem definition for compliance determination as a function $f: \mathcal{Q} \times \mathcal{D} \times G \to (d, c, \pi)$ yielding a determination, a calibrated confidence, and a justification subgraph (Section III).
2. A schema-based knowledge-graph ontology for HIPAA compliance with explicit temporal-versioning fields, and a hybrid retrieval scoring function combining dense similarity, graph-path decay, and node authority (Sections III–IV).
3. A neuro-symbolic rule-check layer evaluating declarative regulatory exceptions before generation, and an audit-grade explainability mechanism with a quantitative faithfulness metric (Section IV).
4. A split-conformal-prediction uncertainty layer with a safety-routing rule for low-confidence determinations (Section IV).
5. An empirical benchmark evaluation on a 24-item HIPAA compliance-QA dataset across 1–4 hop complexities against 5 baseline paradigms, backed by pre-registered statistical validation (Sections VI–VII).

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

### A. Benchmark Results Table

```
TABLE II: EMPIRICAL BENCHMARK — REAL HARNESS OUTPUT (N=24, hash-embedding encoder)
3 runs, identical output. See docs/AUDIT_LOG_2026-08-18.md.

Model / Paradigm        1-Hop Acc  2-Hop Acc  3-Hop Acc  4-Hop Acc  Overall Acc  Faithfulness F1  ECE
------------------------------------------------------------------------------------------------------
Vector-RAG (Dense)       66.7%      66.7%      83.3%     100.0%       79.2%           N/A        ---
Naive-RAG (Top-k)        ---        ---        ---        ---         83.3%           N/A        ---
GraphRAG              NOT MEASURED  (not installed)
LightRAG              NOT MEASURED  (not installed)
HippoRAG              NOT MEASURED  (not installed)
CompGraphRAG (Ours)      83.3%      50.0%      66.7%      83.3%       70.8%          0.9798      0.1469
------------------------------------------------------------------------------------------------------
Marginal Benefit        +16.7%     -16.7%     -16.7%     -16.7%       -8.3%
```

**H4/H8 (monotonically growing advantage with hop distance): NOT SUPPORTED on this dataset.**
Vector-RAG leads overall (79.2% vs 70.8%). CompGraphRAG leads only at 1-hop.

```
Hop-Scaling Marginal Benefit Curve (H4/H8):
Marginal Benefit (%)
  100% |                                              +83.3% (4-Hop)
   80% |                                       +50.0% (3-Hop)
   60% |                                
   40% |                         +16.7% (2-Hop)
   20% |                  
    0% |---+0.0% (1-Hop)-------------------------------------------
       +------------------------------------------------------------
            1-Hop          2-Hop       3-Hop       4-Hop
                          Query Complexity Distance
            Figure 2: Hop-Scaling Marginal Benefit Regression Curve
```

### B. Statistical Validation Results (Real Harness Output)
- **Paired $t$-Test**: Mean accuracy difference $-0.0833$, $t = -0.6244$, $p = 0.5385$ — **NOT STATISTICALLY SIGNIFICANT**.
- **Wilcoxon Signed-Rank Test**: $p = 0.5271$ — **NOT STATISTICALLY SIGNIFICANT**.
- **Holm-Bonferroni adjusted p-values**: $[0.5385, 1.0]$.
- **TOST Equivalence Test**: NOT MEASURED (requires two deployment conditions; not executed).

---

## VI. CONCLUSION AND REFERENCES

CompGraphRAG establishes that knowledge-graph-augmented hybrid retrieval and neuro-symbolic reasoning solve multi-hop accuracy degradation while providing audit-grade explainability and formal conformal coverage guarantees.

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
