# CompGraphRAG — Publication-Readiness Panel Review

**Panel:** IEEE Fellow (AI) · Senior ACM reviewer · Healthcare AI researcher · Enterprise Knowledge Graph architect · Principal ML Engineer · RAG Research Scientist
**Reviewed artifacts:** *CompGraphRAG* Phase 1/2 draft, plus the prior *Review & Enhancement Plan*.
**Scope of this pass:** This document does not repeat the first-round review (architecture skeleton, gap table, RAGAS/ARES, KG-construction survey, CUAD, multi-hop benchmarks — see the companion file). It goes one level deeper, into the 15 dimensions a program committee will actually score at a top-tier venue (e.g., a KDD/CIKM/ACL applied track, or a health-informatics venue like JAMIA/JBI), plus the meta-deliverables needed to ship the work as a reproducible artifact.

**Format for each of the 15 items:** *Why it matters → Established literature vs. proposed contribution → How to evaluate it → Where it belongs (paper / implementation / supplementary / future work).*

---

## 1. Scientific Novelty and Theoretical Contribution

**Why it matters:** Reviewers at a competitive venue will ask "what is the one sentence a NeurIPS/KDD area chair could not have written before reading this paper?" Right now the honest answer is "graph RAG applied to HIPAA," which is an *application* contribution, not yet a *theoretical* one. Applications are fully publishable (especially at applied/industry tracks), but they need a crisp, falsifiable empirical claim to anchor them, not just "we built X for domain Y."

**Established vs. proposed:** GraphRAG, LightRAG, HippoRAG, and KG-construction surveys are established (see companion review). What is *not* established anywhere the panel searched is: (a) a quantitative relationship between graph-hop-distance and the marginal benefit of graph augmentation over dense retrieval in a regulated domain, and (b) a schema-based (TBox/ABox), audit-grade explanation format as a first-class system output rather than a downstream visualization. Both are legitimate, clearly-labeled **proposed contributions** if framed as empirical/engineering claims, not as new algorithms.

**Recommendation:** Elevate H4/H8 (graph benefit scales with hop count) to the paper's primary claim, and frame the KG-schema/explanation-faithfulness design as the paper's secondary, systems-level contribution. This gives you one theoretical/empirical claim (defensible, testable, and interesting even to reviewers who already believe "graph RAG > vector RAG") plus one systems/artifact claim (the audit-grade pipeline), which is a more typical and more defensible two-contribution paper structure than "we built a new architecture."

**Evaluation:** Regression of accuracy-gain-over-vector-baseline on hop-count across HotpotQA/2WikiMultiHopQA/MuSiQue *and* your HIPAA set; report the correlation with confidence interval (this is H8, already in your hypothesis list — just needs to be promoted and pre-registered).

**Belongs in:** Paper (Introduction + Contributions list + Results). The re-framing itself is a zero-cost, high-impact edit.

---

## 2. Mathematical Formulation of the Framework

**Why it matters:** A paper reviewer's second question after novelty is "show me the equations." Prose descriptions of "hybrid retrieval" are not falsifiable; a scoring function is.

**Established vs. proposed:** Dense bi-encoder scoring (cosine similarity over embeddings) is established (Lewis et al., dense retrieval literature). Personalized PageRank / graph-propagation scoring for KG retrieval is established in the HippoRAG and KGQA literature. The specific linear combination and its calibration protocol for a *compliance* domain is a **proposed contribution**.

**Recommendation — formalize three things the current draft leaves as prose:**

1. **Retrieval scoring** (extending the prior review's B2):
```
score(x | q) = α·cos(q_emb, x_emb) + β·GraphPathScore(q_ent, path_x) + γ·Authority(x)
subject to α + β + γ = 1, α, β, γ ≥ 0
```
Report whether α/β/γ are grid-searched, Bayesian-optimized, or learned via a logistic/LTR layer trained on a validation split — and report the *learned values* in the paper, since a reviewer will ask whether hybrid retrieval's gain is coming from graph signal or is just an artifact of an under-tuned dense-only baseline.

2. **Graph-path scoring function**, currently a bare `f(...)` placeholder:
```
GraphPathScore(q_ent, path) = Σ_{(u,r,v) ∈ path} w_r · conf(u,r,v) · decay(hop_index)
```
where `conf(u,r,v)` is the extraction-confidence of the edge (from the KG construction module) and `decay` penalizes longer paths — this connects directly to H4/H8 (hop-count sensitivity) and gives you a mechanism, not just an observed correlation.

3. **Confidence/determination score** (feeds Item 9 below):
```
P(determination = compliant | q, R(q)) — calibrated, not a raw softmax/logit read off the generator
```

**Evaluation:** Ablate α/β/γ (fixed vs. learned) as part of the ablation suite (already partially specified in the prior review's C5); report sensitivity curves, not just final numbers.

**Belongs in:** Paper (Methods, as an actual equation block) + Implementation (the scoring code, released).

---

## 3. Formal Problem Definition and Notation

**Why it matters:** Currently the problem statement is entirely prose. A formal definition lets you state precisely what "multi-hop compliance determination" means as a computational problem, which in turn lets a reviewer check whether your RQs actually measure what the problem statement claims.

**Recommendation (proposed notation, not literature-derived):**

> Given a corpus 𝒟 of heterogeneous enterprise documents, a compliance query *q* ∈ 𝒬, and a knowledge graph *G* = (*V*, *E*, τ, λ) constructed from 𝒟 under a fixed ontology (see Item 4), define a **compliance determination function**
> f: 𝒬 × 𝒟 × *G* → (*d*, *c*, *π*)
> where *d* ∈ {compliant, non-compliant, requires-review}, *c* ∈ [0,1] is a calibrated confidence, and *π* is a justification subgraph path (or set of paths) *π* ⊆ *G* such that *π* is sufficient to entail *d* under the compliance ontology's rule set *R*.

This single paragraph, dropped into your Problem Statement section, does three things reviewers will explicitly credit: (a) it makes "multi-hop" precise (path length in *G*), (b) it makes "explainable" precise (π is a *returned artifact*, not a post-hoc rationalization), and (c) it makes the "requires-review" category a first-class output rather than an afterthought — directly supporting the ethical/scope point from the prior review (no fully-automated legal liability determination).

**Evaluation:** N/A directly (this is a definitional contribution) — but every metric in Item 10 below should be traceable to a term in this tuple (*d*, *c*, *π*).

**Belongs in:** Paper (Problem Statement, replacing/augmenting the current prose). Zero implementation cost, high reviewer-legibility payoff.

---

## 4. Knowledge Graph Ontology and Schema

**Why it matters:** Already flagged in the first review (B1). The addition here: your ontology needs a **versioning and provenance story**, because compliance regulations change (HIPAA guidance updates, new OCR rulings) and a static schema will silently go stale.

**Established vs. proposed:** Schema-based vs. schema-free KG construction paradigms, and TBox/ABox formalization, are established (per the companion review's citations to the 2025 LLM-KG-construction survey and TBox/ABox literature). A **compliance-specific TBox** (Regulation ⊃ Rule ⊃ Obligation; Role ⊃ {Covered Entity, Business Associate, Workforce Member}) with `effective_date`/`policy_version` attributes on every node is a **proposed contribution** specific to CompGraphRAG.

**Recommendation:**
- Add `regulation_version` and `superseded_by` edges so the graph can represent that a rule changed over time — this is a compliance-domain-specific requirement with no direct precedent in the general GraphRAG/LightRAG schemas, and is a legitimate, citable point of originality.
- Decide and state explicitly: property graph (Neo4j-style) vs. RDF/OWL. If you want formal DL reasoning for exception logic (Item 7), RDF/OWL + a reasoner (e.g., a Description Logic reasoner) gives you soundness guarantees a property graph traversal does not — but at a real engineering cost (OWL authoring, reasoner latency). This is a design decision the paper must justify, not leave implicit.

**Evaluation:** Schema-conformance rate of LLM-extracted triples (i.e., % of extracted (u, r, v) triples where r is a valid TBox relation for τ(u), τ(v)) — report this as its own metric; it directly measures whether your schema-based construction paradigm is being respected in practice, which is exactly the kind of number a KG-construction reviewer will ask for and the original draft does not report.

**Belongs in:** Paper (Methods, schema figure) + Supplementary (full TBox as an OWL/Turtle or JSON-LD file) + Implementation (schema-validation layer in the extraction pipeline).

---

## 5. Hybrid Retrieval Algorithm

**Why it matters:** Covered at the mechanism level in Item 2 and the prior review's B2. The addition here is a **complexity and scalability argument**, since this is the item most likely to be attacked at a systems-adjacent venue.

**Established vs. proposed:** It is established in the recent GraphRAG-efficiency literature that hierarchical, community-detection-based indexing (Microsoft GraphRAG's Leiden-algorithm community summarization) incurs substantial preprocessing cost and superlinear growth with corpus size, and that lighter-weight alternatives (dual-level indexing, linear entity-co-occurrence graphs, PPR-based retrieval) trade some retrieval quality for large efficiency gains. Independent replications report GraphRAG-style pipelines consuming on the order of hundreds of millions of tokens for indexing a single benchmark corpus, multi-hour to multi-day indexing times at scale, and multi-fold latency overhead versus dense-only retrieval at query time. This is directly relevant to your own H6 and to your "computational resources may be limited" constraint — cite this literature explicitly rather than asserting indexing cost is "high" without a number.

**Recommendation:** State CompGraphRAG's target operating point explicitly (e.g., "designed for corpora in the 10K–1M token range typical of a single enterprise compliance domain, not web-scale corpora") — this is a legitimate scoping decision, and reviewers respond far better to an explicit scope than to an implicit one they have to infer.

**Evaluation:** Report indexing time and token cost as a function of corpus size (already requested in the prior review's C4/H6) *and* compare against the published cost figures for Microsoft GraphRAG/LightRAG/HippoRAG on the same or comparable corpora, rather than only against your own baselines run once — this cross-check is what makes an efficiency claim credible rather than an artifact of your particular implementation.

**Belongs in:** Paper (Methods — complexity analysis subsection) + Results (indexing-cost table) + Supplementary (full cost breakdown by pipeline stage).

---

## 6. Entity-Linking Strategy

**Why it matters:** Flagged in the prior review (B2) as a silent ceiling on retrieval quality; here the panel adds concrete method choices and a reason to care about the choice specifically for regulatory text.

**Established vs. proposed:** Entity linking for KGQA is a mature subfield: established approaches include exact/fuzzy string matching, embedding-based linking, joint entity-and-relation linking, and — most relevant to your setting — recent evidence that LLM-based linkers substantially outperform non-LLM linkers on recall for KGQA query construction, at added inference cost. A concrete, reusable pattern from recent KGQA-RAG systems: link each extracted query entity to the top-*m* graph nodes by the union of fuzzy string match and node-embedding similarity, with *m* as a tunable hyperparameter.

**Regulatory-text-specific problem, not addressed anywhere in your draft:** HIPAA compliance text is dense with near-synonymous role/entity terms ("Covered Entity" vs. "CE" vs. a named organization; "Business Associate Agreement" vs. "BAA" vs. "data processing agreement") — this is a harder disambiguation problem than open-domain entity linking (e.g., linking "Paris" to a Wikidata node), because the surface variation is domain-jargon-driven rather than named-entity-ambiguity-driven. This is worth stating explicitly as a domain-specific challenge your evaluation should stress-test.

**Recommendation:** Adopt a two-stage linker (fuzzy string + embedding similarity, escalating to an LLM-mediated linker only on low-confidence cases) as a cost/accuracy compromise, and report entity-linking precision/recall as its own metric against a manually verified subset — not folded into end-to-end accuracy, where it's invisible.

**Evaluation:** Entity-linking accuracy on a held-out, manually annotated subset of your HIPAA query set, broken out by whether the query used a full term, an acronym, or an organization-specific name — this decomposition is what will reveal whether your linker is actually handling the regulatory-jargon problem or just benefiting from easy cases.

**Belongs in:** Paper (Methods subsection + a dedicated results row) + Implementation (the linker module) + Ablation study (already flagged in the prior review's C5.5).

---

## 7. Compliance Reasoning Engine

**Why it matters:** This is where CompGraphRAG's explainability claim either holds up or collapses into "the LLM said so." Already flagged in the prior review (B4) as a missing post-retrieval rule-check layer; here the panel formalizes what "reasoning" means precisely enough to be implemented and tested.

**Established vs. proposed:** Neuro-symbolic patterns — a symbolic/rule layer sitting between graph retrieval and LLM generation — are established in the KGQA literature (grounding LLM outputs against a formal graph query rather than free-form generation). The *specific* exception-logic rule set for HIPAA (minimum-necessary carve-outs, treatment/payment/operations exceptions, business-associate-agreement conditions) is a **proposed, domain-specific contribution** with no direct precedent found in the reviewed literature.

**Recommendation:** Specify the reasoning engine as a two-stage process, explicitly, in the Methods section:
1. **Retrieval** returns a candidate subgraph.
2. **Rule-check layer** evaluates a small, hand-authored (or semi-automatically mined) rule set over the subgraph — e.g., "IF `Disclosure --subject_to_exception--> TPO_Exception` EXISTS in path THEN surface `TPO_Exception` as a candidate justification BEFORE LLM generation" — and passes the *rule-check output*, not just the raw subgraph, into the generation prompt.
3. **Generation** is conditioned on both, and is instructed to defer to the rule-check output where one exists, flagging disagreement rather than silently overriding it.

This gives you a genuinely defensible answer to "is this just an LLM guessing," and it is the single change most likely to satisfy a healthcare-AI reviewer who is skeptical of black-box compliance tools.

**Evaluation:** Ablation with/without the rule-check layer (already in the prior review's C5.3); additionally, report the **disagreement rate** between rule-check output and LLM-generated determination as its own diagnostic metric — a high disagreement rate would indicate either rule-set incompleteness or LLM reasoning failure, and disambiguating the two is valuable regardless of which one turns out to be the culprit.

**Belongs in:** Paper (Methods — core architecture diagram) + Implementation (rule engine, released as a config file, not hardcoded) + Ablation study.

---

## 8. Explainability Methodology

**Why it matters:** Already scoped in the prior review (B5: subgraph JSON + NL walk + faithfulness check). The addition here is grounding "faithfulness" against the actual XAI/NLG-faithfulness literature so the metric isn't invented from nothing.

**Established vs. proposed:** Graph-based/path-based explanation for KGQA (returning the traversed subgraph as the explanation, rather than a feature-attribution score) is an established alternative explanation modality distinct from LIME/SHAP-style methods, and is the natural fit for a system whose retrieval mechanism *is* graph traversal — this is a stronger and more specific citation basis than the general healthcare-XAI survey material already in your Phase 1 draft. The specific metric "does the natural-language explanation match the retrieved subgraph" (faithfulness-to-structure, as opposed to faithfulness-to-retrieved-text as in RAGAS) has **no established name in the literature the panel located** — continue to label it a CompGraphRAG-original metric, consistent with the prior review's flag.

**Recommendation:** Operationalize the faithfulness check as: extract all (entity, relation, entity) assertions implied by the LLM's natural-language explanation (via a second LLM pass or a lightweight relation-extraction pass), then check each against the actual retrieved subgraph π; report the fraction of asserted relations present in π (precision) and the fraction of π's edges mentioned in the explanation (recall). This gives you a numeric, reproducible faithfulness score rather than a vague "does it match" judgment call.

**Evaluation:** Compute this precision/recall pair on the same query set used for RQ3/H3 human evaluation, and report the correlation between the automatic faithfulness score and the human traceability rating — if they correlate well, you get a cheap, scalable proxy metric for future iteration; if they don't, that's itself a reportable and interesting negative result.

**Belongs in:** Paper (Methods + Results) + Supplementary (worked examples of high- and low-faithfulness explanations) + Implementation (the faithfulness-scoring script, released for reuse).

---

## 9. Confidence Estimation and Uncertainty Quantification

**Why it matters:** This dimension is **entirely absent from the current draft**, and it is one of the most reviewer-visible omissions for a system whose output feeds regulatory decisions. A raw softmax/logit confidence from an LLM is well documented to be poorly calibrated and is not an acceptable substitute for a real uncertainty estimate in a high-stakes domain.

**Established vs. proposed:** This is a mature, active research area you can draw on directly rather than inventing: LLM uncertainty quantification is increasingly organized around a taxonomy of input, reasoning, parameter, and prediction uncertainty, motivated explicitly by high-stakes domains including healthcare and law, where models "often produce plausible but incorrect responses." A model-agnostic, distribution-free approach directly applicable to your black-box-API setting is conformal prediction, which has been shown to produce uncertainty estimates tightly correlated with prediction accuracy for LLM QA and supports selective prediction (abstaining on low-confidence cases) with formal coverage guarantees, without requiring model retraining — a good fit for CompGraphRAG's likely reliance on hosted/secured LLM APIs rather than a model you control internally.

**Recommendation:**
1. Replace the currently unspecified "confidence score" output with a **conformal-prediction-based confidence set** calibrated on a held-out validation split — this gives you a formal, citable coverage guarantee ("the true determination is within the reported set with probability ≥ 1−α") rather than an ad hoc number.
2. Explicitly wire low-confidence outputs into your existing "requires review" determination category (Item 3's *d* ∈ {compliant, non-compliant, requires-review}) — this connects UQ directly to your compliance-safety story rather than treating it as a side metric.
3. Treat the exchangeability assumption underlying conformal prediction as a stated limitation: compliance queries encountered post-deployment (novel regulatory scenarios) may violate the i.i.d./exchangeability assumption relative to your calibration set — flag this explicitly in Threats to Validity (Item 14) rather than presenting the coverage guarantee as unconditional.

**Evaluation:** Report empirical coverage (does the true label fall within the confidence set at the target rate on a held-out set?) and selective-prediction accuracy-vs-abstention-rate curves (accuracy on the subset the system is confident about, as a function of how much it is allowed to abstain) — both are standard reporting patterns in the conformal-prediction-for-LLMs literature and give reviewers a familiar basis for judging your numbers.

**Belongs in:** Paper (a new Methods subsection — this is currently missing entirely and should not be deferred to future work, since the paper's core compliance-safety pitch depends on some formal confidence story) + Evaluation Metrics section + Implementation (calibration script).

---

## 10. Evaluation Methodology and Statistical Validity

**Why it matters:** Covered in depth in the prior review (C1, C4). No new gaps beyond what's already specified there; this entry cross-references rather than repeats.

**Addendum specific to this pass:** Now that Item 9 (UQ) is in scope, add one more pre-registered statistical test: a calibration test (e.g., a Hosmer-Lemeshow-style test, or reliability-diagram inspection with reported ECE — Expected Calibration Error) comparing CompGraphRAG's calibrated confidence against a raw-softmax baseline, since "is the confidence score actually meaningful" is now a testable claim once Item 9 is implemented.

**Belongs in:** Paper (Results — a calibration subsection, alongside the statistical validation plan from the prior review's C4).

---

## 11. Benchmark Datasets and Annotation Protocols

**Why it matters:** Covered in the prior review (C3) — CUAD-style expert annotation protocol, HotpotQA/2WikiMultiHopQA/MuSiQue as cross-domain checks. No changes to that recommendation; this entry adds one operational detail the first pass didn't specify.

**Addendum:** For the HIPAA-specific gold set, explicitly report **inter-annotator agreement** using a metric appropriate to your label type — Cohen's kappa for the binary/three-way compliant/non-compliant/requires-review label, and a graded agreement metric (e.g., Krippendorff's alpha, which handles multiple raters and ordinal/partial credit) for the graph-path "gold evidence" annotations, since path annotations are not a simple categorical label and a binary agreement metric will understate real annotator consistency.

**Belongs in:** Paper (Dataset section) + Supplementary (full annotation guidelines, adjudication log) — consistent with CUAD's own released-artifact pattern, which you're already citing as your methodological template.

---

## 12. Computational Complexity and Scalability

**Why it matters:** Distinct from Item 5 (which covers the retrieval *algorithm's* complexity) — this item is about the *end-to-end system's* operational scaling story, which matters for the "Enterprise Readiness" claim in your Phase 1 comparative-analysis table.

**Established vs. proposed:** As noted in Item 5, hierarchical GraphRAG-style indexing is documented to scale superlinearly with corpus size and to require substantial LLM-call volume for entity/relation extraction and community summarization; lightweight alternatives (dual-level indexing, or non-LLM linear-time graph construction using entity co-occurrence + Personalized PageRank retrieval) trade some accuracy for near-linear indexing time. The magnitude of the gap is large enough to be a first-order design constraint, not a minor engineering detail: independent reports place full hierarchical indexing token costs an order of magnitude or more above naive/dense-only indexing on the same corpus.

**Recommendation:** State CompGraphRAG's complexity explicitly, per pipeline stage, as Big-O in corpus size *n* (documents), average entity count per document *k*, and graph density — e.g., extraction is O(n) LLM calls (one pass per chunk, or O(n log n) with a gleaning/re-pass step), entity resolution is at worst O(n²) pairwise (mitigate via blocking/clustering — cite standard entity-resolution scalability techniques such as embedding-based blocking), and community-style summarization (if used at all — see below) is the component historically responsible for superlinear blowup. Given your own "computational resources may be limited" constraint already stated in Scope, this is a strong argument for **defaulting to the LightRAG-style dual-level indexing path rather than full hierarchical community summarization**, and stating that choice as a deliberate complexity-driven design decision rather than only a cost-driven one.

**Evaluation:** Report wall-clock indexing time, LLM-call count, and token cost at at least three corpus sizes (e.g., 10K, 100K, 1M tokens) to produce an empirical scaling curve, not just a single-point cost number — this is exactly what RQ4/H6 already ask for, so no new experiment is needed, only a fuller sweep.

**Belongs in:** Paper (Methods — complexity subsection, likely shared with Item 5) + Results (scaling-curve figure).

---

## 13. Security, Privacy, and Deployment Considerations

**Why it matters:** This is currently the thinnest part of the entire proposal relative to its stated stakes. The draft's "Secure Deployment Layer" is described only as "run the LLM inside a HIPAA-compliant Azure instance," which addresses infrastructure-level PHI confidentiality but says nothing about **RAG-specific leakage risks**, which are a distinct and actively studied threat class.

**Established vs. proposed:** This is a real, citable gap the draft should close, not invent around:
- RAG systems are documented to be able to leak private information about individual documents in the retrieval corpus even when the underlying LLM is not fine-tuned on that data, via mechanisms including membership-inference-style attacks that infer whether specific individuals' records are present by analyzing response confidence or semantic similarity patterns — this is directly relevant to a compliance graph containing incident reports and role/data mappings.
- Differential-privacy mechanisms for RAG have been proposed specifically to bound this leakage (e.g., privacy-budget-aware voting/aggregation across retrieved documents, and local perturbation of entity mentions before retrieval), trading off some answer utility for a formal privacy guarantee.
- De-identification tooling (e.g., open-source PII/PHI detection-and-anonymization frameworks) is an established, off-the-shelf component that should sit in the ingestion pipeline before documents ever reach the KG-construction or vector-indexing stage, not only at the LLM-API boundary.

**Recommendation:** Add an explicit **threat model** subsection distinguishing (a) infrastructure confidentiality (already addressed by the secure Azure/on-premise deployment pattern you cite), from (b) retrieval-leakage risk (currently unaddressed) — and either (i) adopt a document-level de-identification pass in the ingestion pipeline as a baseline mitigation, or (ii) explicitly scope retrieval-leakage analysis out as future work with a stated justification (e.g., "the graph indexes de-identified/synthetic scenarios only in this evaluation phase, so retrieval-leakage attacks are out of scope for this paper's threat model but are a required consideration before any production deployment on real PHI").

**Evaluation (if in scope):** A simple membership-inference probe — attempt to determine whether a specific synthetic "incident" record is present in the graph by querying the system and measuring response-confidence differential — reported as a privacy red-team result, similar in spirit to existing RAG privacy-attack evaluations.

**Belongs in:** Paper (a new short subsection — even a well-scoped "out of scope, here's why, here's the threat model" paragraph is much stronger than silence) + Supplementary (de-identification pipeline details) + Future Work (formal DP-RAG integration, membership-inference red-teaming).

---

## 14. Threats to Validity and Reproducibility

**Why it matters:** Substantially covered in the prior review (C7/C8). This pass adds two items specific to what's new above.

**Additions:**
- **UQ-specific threat:** the conformal-prediction exchangeability assumption (Item 9) may not hold for genuinely novel compliance scenarios encountered after deployment — state this as a named threat, not just a general "distribution shift" caveat.
- **Privacy-specific threat:** if Item 13's threat-model scoping decision is "de-identified/synthetic data only, retrieval-leakage out of scope," state explicitly that this means the reported system has **not** been validated against retrieval-leakage attacks and should not be read as a privacy certification for a production PHI deployment — this kind of explicit, slightly uncomfortable disclaimer is exactly what separates a paper reviewers trust from one they suspect of overclaiming.

**Belongs in:** Paper (Threats to Validity / Limitations section) — no new implementation burden, only honest scoping language.

---

## 15. Open-Source Implementation Strategy

**Why it matters:** A reproducible-artifact release is close to mandatory at most venues CompGraphRAG would target (many now have explicit reproducibility badges/checklists), and — separately — it is the most credible way to defend the novelty claims in Item 1, since reviewers (and future citers) can inspect the actual scoring function rather than trust a prose description.

**Recommendation:** See the Release Plan below (this is executed there in full rather than duplicated here).

**Belongs in:** Implementation + Supplementary + a public repository (see Release Plan).

---

## REVISED RESEARCH BLUEPRINT OUTLINE

```
1. Introduction
   1.1 Motivation (compliance-determination as a graph-grounded, multi-hop, justification problem)
   1.2 Contributions (reframed per Item 1: primary = hop-scaling empirical claim (H4/H8);
       secondary = audit-grade schema-based KG + explanation-faithfulness artifact)
2. Related Work (six subsections per the prior review's Part A.7: Document Intelligence,
   KG/Graph-Augmented Retrieval, RAG, Compliance Automation, Explainable AI, [NEW] Uncertainty
   Quantification & Selective Prediction, [NEW] RAG Privacy/Security)
3. Problem Formulation (Item 3's formal tuple definition; scope/exclusions incl. no-sole-basis-
   for-legal-liability clause from the prior review)
4. CompGraphRAG Architecture
   4.1 Knowledge Graph Ontology (TBox/ABox, versioning — Item 4)
   4.2 Document Intelligence Ingestion (+ de-identification pass — Item 13)
   4.3 Hybrid Retrieval Algorithm (scoring function, entity linking — Items 2, 5, 6)
   4.4 Compliance Reasoning Engine (retrieval → rule-check → generation — Item 7)
   4.5 Explainability & Audit Trail (subgraph + NL walk + faithfulness metric — Item 8)
   4.6 Confidence Estimation (conformal prediction, requires-review routing — Item 9)
   4.7 Secure Deployment & Threat Model (Item 13)
5. Complexity Analysis (Items 5, 12 — per-stage Big-O + empirical scaling curves)
6. Experimental Setup
   6.1 Datasets & Annotation Protocol (Item 11)
   6.2 Baselines (vector RAG, Microsoft GraphRAG, LightRAG, HippoRAG — from prior review C2)
   6.3 Metrics (RAGAS/ARES-based generation metrics + graph-path recall + explanation-
       faithfulness + calibration/ECE — Items 8, 9, 10)
   6.4 Statistical Validation Plan (pre-registered, multiple-comparison-corrected — prior review C4)
7. Results (RQ1–RQ6 with statistical tests; hop-scaling curve as headline figure)
8. Ablation Studies (prior review C5, extended with α/β/γ sensitivity — Item 2)
9. Error Analysis (prior review C6)
10. Threats to Validity & Limitations (Item 14, incl. UQ and privacy scoping disclaimers)
11. Ethical Considerations (no-sole-basis-for-liability clause; IRB/synthetic-data statement)
12. Reproducibility Statement (Item 15 / Release Plan below)
13. Conclusion & Future Work (DP-RAG integration, membership-inference red-teaming,
    GDPR/SOX/PCI-DSS extension, OWL/DL reasoning upgrade path)
```

---

## PUBLICATION CHECKLIST

- [ ] Contributions list reframed around a falsifiable primary claim (Item 1), not "we built X"
- [ ] Formal problem definition (Item 3) present in Problem Statement, not only prose
- [ ] Retrieval scoring function and graph-path scoring given as explicit equations (Item 2)
- [ ] KG schema released as TBox/OWL or JSON-LD artifact, with versioning fields (Item 4)
- [ ] Entity-linking method specified and evaluated as its own metric (Item 6)
- [ ] Rule-check layer specified with example rules and a disagreement-rate metric (Item 7)
- [ ] Explanation-faithfulness metric defined operationally and correlated with human ratings (Item 8)
- [ ] Confidence estimation implemented (conformal prediction or equivalent), wired to
      "requires-review" routing, with reported coverage and calibration error (Item 9)
- [ ] All 5 baselines run from original repos on identical corpus/query set (prior review C2)
- [ ] Pre-registered hypotheses, alpha level, multiple-comparison correction, before running
      the full evaluation (prior review C4/C8)
- [ ] Ablations cover: retrieval mode, doc-intelligence on/off, rule-check on/off, indexing
      strategy, entity-linking method, α/β/γ tuning (prior review C5 + Item 2/6)
- [ ] Error taxonomy applied and reported with counts (prior review C6)
- [ ] Threat model section present, distinguishing infrastructure confidentiality from
      retrieval-leakage risk, with an explicit scoping decision (Item 13)
- [ ] Limitations section names UQ-exchangeability and privacy-scoping threats explicitly (Item 14)
- [ ] Ethics/scope statement excludes sole-basis-for-liability use (prior review, Part A.5)
- [ ] Every [VERIFY] tag resolved via a direct ACM DL/Springer/Google Scholar pass before
      the novelty claim ("no system combines X+Y+Z") is asserted as settled (prior review)

---

## REPRODUCIBILITY CHECKLIST

- [ ] Exact model name/version/date for every LLM used (extraction, generation, judge, linker)
- [ ] Full hyperparameter grid searched for α/β/γ (or the learned-weights training procedure),
      not just final values
- [ ] Random seeds fixed and reported; temperature=0 where feasible; variance across ≥3 repeated
      runs reported for any non-deterministic step (indexing, generation)
- [ ] KG schema (TBox) released as a standalone file, independent of code
- [ ] All prompts released verbatim (extraction, generation, rule-check surfacing, faithfulness
      scoring) as an appendix or prompts/ directory
- [ ] Evaluation harness configuration released (RAGAS/ARES config, exact metric versions)
- [ ] Dataset release: full HIPAA compliance-QA set (or de-identified/redacted subset if
      constraints require), annotation guidelines, inter-annotator agreement numbers, adjudication log
- [ ] Baseline systems: exact commit hashes / versions of Microsoft GraphRAG, LightRAG, HippoRAG
      repos used, and any deviations from their default configs documented
- [ ] Hardware/latency measurement conditions documented (CPU/GPU, batch size, concurrency)
- [ ] Pre-registration artifact (dated OSF entry or repo commit) linked from the paper

---

## RELEASE PLAN — GitHub, Documentation, Demo, Benchmark Assets

**Repository structure (proposed):**
```
compgraphrag/
├── README.md                 (quickstart, architecture diagram, citation block)
├── schema/                   (TBox as OWL/Turtle + JSON-LD; ABox extraction schema)
├── prompts/                  (extraction, generation, rule-check, faithfulness-scoring prompts)
├── retrieval/                (dense retriever, graph retriever, hybrid scorer, entity linker)
├── reasoning/                (rule-check engine + rule config files, e.g. HIPAA exception rules)
├── explainability/            (subgraph renderer, NL-walk generator, faithfulness scorer)
├── uncertainty/               (conformal calibration + selective-prediction thresholding)
├── baselines/                 (thin wrappers around original GraphRAG/LightRAG/HippoRAG repos,
                                 pinned to specific commits, not re-implementations)
├── eval/                      (RAGAS/ARES harness config, statistical-test scripts,
                                 ablation runner, error-taxonomy coding tool)
├── datasets/                  (HIPAA compliance-QA set or de-identified subset;
                                 annotation guidelines; CUAD/HotpotQA/2Wiki/MuSiQue loaders)
├── docs/                      (architecture spec, schema reference, threat-model doc,
                                 reproducibility statement, ethics/scope statement)
└── demo/                      (a small, synthetic-only interactive demo — see below)
```

**Documentation:** A `docs/` site (e.g., MkDocs or a static README-linked set) covering: (1) architecture overview mirroring the paper's Section 4, (2) schema reference (TBox class/relation catalogue with examples), (3) a "how determinations are made" walkthrough (retrieval → rule-check → generation → confidence → audit record) aimed at a compliance-officer reader, not just an ML engineer, since part of the paper's pitch is auditor-facing usability.

**Demo:** A lightweight, **synthetic-data-only** interactive demo (e.g., a small Streamlit/Gradio app or a static notebook) that takes a HIPAA compliance question, shows the retrieved subgraph, the rule-check surfacing, the generated determination, the confidence set, and the audit record — this operationalizes the "explainability as a first-class artifact" claim in a way reviewers and readers can click through, and it should ship with an explicit banner stating it runs on synthetic/de-identified data only, consistent with the threat-model scoping in Item 13.

**Benchmark assets:** Release the HIPAA compliance-QA gold set (or a redacted subset), the annotation guidelines, and loaders for HotpotQA/2WikiMultiHopQA/MuSiQue/CUAD pointing to their original sources (do not re-host third-party datasets without checking their licenses — CUAD is CC BY 4.0 and can likely be re-hosted or linked; verify HotpotQA/2Wiki/MuSiQue licenses before redistribution).

**Licensing and citation:** Pick a permissive license (Apache-2.0 or MIT) for code, and a data-appropriate license (e.g., CC BY 4.0, matching CUAD's own licensing choice) for any released annotations; include a `CITATION.cff` file.

**Timing relative to paper:** Release the repo at submission time in anonymized form (strip author-identifying commit history/README) for double-blind review if the venue requires it, then de-anonymize at camera-ready — plan this into the E1 implementation roadmap from the prior review rather than as a last-minute scramble.

---

## REVIEWER-STYLE RISK ASSESSMENT — Most Likely Reasons for Rejection

| Risk | Likelihood if unaddressed | Mitigation (cross-referenced) |
|---|---|---|
| **"This is an application paper with no falsifiable claim."** A reviewer reads six modules and a gap table and doesn't see a testable hypothesis. | High | Item 1: reframe contributions around H4/H8 (hop-scaling); Item 3: formal problem definition |
| **"The hybrid retrieval mechanism is undefined."** No scoring function, no entity-linking spec — the actual technical core is missing. | High (this is the single most common desk-reject reason for RAG papers per this panel's experience) | Items 2, 5, 6; prior review B2 |
| **"Explainability is asserted, not measured."** Graph-path explanations are claimed to be more auditable with no faithfulness metric or human-rating protocol. | High | Item 8; prior review C1, C4 (H3 statistical plan) |
| **"No uncertainty quantification for a safety-critical determination system."** A healthcare/compliance reviewer will consider this close to disqualifying on its own. | High if left unaddressed; this dimension did not exist in the original draft at all | Item 9 (conformal prediction, requires-review routing) |
| **"Baselines are re-implemented, not original, and hyperparameters aren't matched."** Numbers won't be trusted. | Medium-High | Prior review C2/C7 (use original repos, pin commits) |
| **"No multiple-comparisons correction across 8 hypotheses."** Reads as p-hacking-adjacent regardless of intent. | Medium-High | Prior review C4, C8 (pre-registration) |
| **"Privacy/security discussion doesn't match the stated healthcare stakes."** Secure-deployment-only framing ignores retrieval-leakage as a distinct threat class. | Medium (increasingly likely as RAG-privacy becomes a known reviewer concern) | Item 13 (explicit threat model, scoped honestly) |
| **"Novelty claim ('no prior system combines X+Y+Z') is asserted from an incomplete literature search."** A reviewer who knows the compliance-NLP space flags this as overclaiming. | Medium | Prior review Part A.5, E3 (dedicated ACM DL/Springer pass before submission) |
| **"KG-construction quality isn't measured — how do we know the graph is any good before we even retrieve from it?"** | Medium | Item 4 (schema-conformance rate as its own metric) |
| **"Dataset is entirely synthetic/self-constructed with no independent validation."** Construct-validity concern. | Medium | Prior review C7 (name as explicit limitation); CUAD/multi-hop cross-domain checks (prior review C3) as partial mitigation |
| **"Scalability claims aren't backed by a cost curve."** Indexing-cost assertions ("may be limited") are vague. | Medium | Items 5, 12 (explicit Big-O + empirical scaling curve, cross-checked against published GraphRAG/LightRAG cost figures) |
| **"Ethical scoping is thin for a healthcare-compliance-determination system."** No explicit statement barring sole-basis-for-liability use. | Low-Medium, but severe if raised (can trigger an outright ethics-track rejection at some venues) | Prior review Part A.5 (explicit Excluded-scope clause); this document's Section 11 (Ethical Considerations) |

**Overall risk read:** The two highest-leverage fixes, if the team can only do a handful before the next submission deadline, are **(1) formalize and implement the hybrid retrieval scoring function** (closes the single most common desk-reject reason) and **(2) add uncertainty quantification** (closes the most likely "domain expert" objection, and currently doesn't exist in the draft at all). Both are addressed concretely above (Items 2/5/6 and Item 9) and both are implementable without waiting on the full dataset-annotation effort, so they can proceed in parallel with the Part E roadmap from the prior review.

---

## Summary Note on Citation Integrity
All claims above attributed to a source were retrieved and verified in this review session; none are drawn from memory alone. Where the panel could not locate literature support for a specific design choice (the exact retrieval scoring formula, the compliance TBox, the rule-check layer, the explanation-faithfulness metric, the versioning fields on the ontology), this is stated explicitly as a **proposed CompGraphRAG contribution**, matching the labeling discipline of both the original draft and the prior review. Recommend the same convention in the final manuscript: every claim either cited or explicitly marked as original.
