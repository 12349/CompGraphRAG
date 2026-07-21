# CompGraphRAG — Senior Review & Enhancement Plan

**Reviewer stance:** IEEE AI reviewer + healthcare AI researcher + enterprise knowledge-systems architect
**Reviewed document:** *CompGraphRAG: A Knowledge Graph-Augmented Retrieval Framework for Intelligent Enterprise Compliance Workflows — A HIPAA Case Study* (Phase 1 & Phase 2 draft)
**Verdict up front:** The draft is unusually disciplined about not fabricating citations, and its gap table is honest. But as written it is a **literature synthesis with a proposed architecture**, not yet a paper with a testable contribution. Every hypothesis (H1–H8) is currently unfalsifiable because there is no formal system, no metric definitions, no baseline implementation plan, and no dataset. This document tells you exactly what to build so the hypotheses become testable, and flags every place I would reject the paper as a reviewer today.

---

## PART A — SECTION-BY-SECTION REVIEW

### 1. Research Background

**Missing technical depth**
- The background asserts that GraphRAG "explicitly represents entities and relationships as a graph" but never defines *what a graph node/edge is* in the compliance domain. A reviewer will ask: is your graph a labeled property graph, an RDF/OWL graph, or an ad hoc LLM-extracted triple store? This decision cascades into your schema, your retrieval algorithm, and your explainability format — it needs to be made in Phase 1, not deferred to "Phase 3 implementation."
- "Explainability" is discussed only at the XAI-survey level (LIME/SHAP vs. TAXAI). There is no discussion of the *specific* literature on **graph-based/path-based explanation** in KGQA (e.g., subgraph-path extraction for KGQA, attention-over-paths methods) — this is the actual technical neighborhood CompGraphRAG's contribution lives in, not general healthcare XAI.

**Unsupported assumptions**
- The claim that "conventional RAG is relationally shallow" is supported only by the *Edge et al.* framing of global vs. local queries. That paper's argument is about *summarization* failure, not about *relational/multi-hop reasoning* failure per se — these are related but distinct failure modes, and the background conflates them. A rigorous version should separate: (a) failure on corpus-wide synthesis questions [Edge et al.], and (b) failure on multi-hop entity-chaining questions [HotpotQA/MuSiQue-style literature, see below]. Right now H1/H2 are aimed at (b) but the motivating citation is about (a).

**Additional literature to cite**
- **Multi-hop QA benchmarks** establishing what "multi-hop" failure actually looks like for dense retrieval, which is the real justification for H1/H2/H4/H8: <cite index="27-1">HotpotQA, MuSiQue, and 2WikiMultiHopQA are the three established multi-hop benchmark datasets used to evaluate cross-document reasoning</cite>, with <cite index="28-1">HotpotQA built around bridge and comparison questions requiring evidence combined across multiple passages, 2WikiMultiHopQA requiring comparison, composition, inference, and relation chaining over entities, and MuSiQue designed specifically to reduce shortcut/disconnected reasoning</cite>. These are the papers you should cite when you claim conventional RAG is "relationally shallow" — they are the standard empirical evidence base for that claim, not the Edge et al. summarization paper.
- **KG construction / ontology foundations** — the document itself flags this as unpopulated. A 2025 survey is a strong anchor: <cite index="4-1">recent work systematically analyzes how LLMs reshape the classical three-layered pipeline of ontology engineering, knowledge extraction, and knowledge fusion, reviewing schema-based paradigms that emphasize structure, normalization, and consistency versus schema-free paradigms that emphasize flexibility and open discovery</cite>. This directly resolves your Phase 2 "Category: Knowledge Graph construction/ontology" gap and gives you vocabulary (schema-based vs. schema-free construction) that your compliance schema decision should explicitly locate itself within.
- A concrete formal-ontology technique worth citing for your TBox/ABox design: <cite index="9-1">advanced knowledge-graph pipelines encode ontologies as TBox concept-class and property hierarchies populated via ABox instance assertions, with schema and ontology alignment validated through OWL/Turtle formalization and reasoning</cite>.

**Stronger framing**
- Reframe the background's final paragraph so the "current limitations" list separates *summarization-failure* literature from *multi-hop-failure* literature — this single change makes H1 and H2 individually defensible rather than both hanging off the same one citation.

**Originality opportunity**
- Nobody in the reviewed set combines document-intelligence extraction with a formally typed (TBox/ABox) compliance ontology. Explicitly adopting a schema-based (ontology-first) KG construction paradigm — rather than the schema-free LLM-triple-extraction style used by Microsoft GraphRAG — is a legitimate, citable design choice that differentiates CompGraphRAG from Edge et al.'s more emergent/schema-free graph. This is real originality, not just claims of it.

---

### 2. Problem Statement

**Missing technical depth:** The four numbered problems are well-framed rhetorically but none is operationalized. E.g., problem 1 says a determination "requires linking a policy clause, a data-flow description, a role/permission definition, and an incident log entry" — this is exactly your entity schema, and it should be pulled forward into a formal schema definition here (or cross-referenced to Section 9), not left as prose.

**Unsupported assumption:** The framing implicitly assumes HIPAA determinations decompose cleanly into a fixed small set of entity types. Real HIPAA determinations (e.g., minimum-necessary analysis) can require conditional/exception logic (business associate agreements, treatment/payment/operations carve-outs) that is closer to *rule-based reasoning over the graph* than *pure retrieval*. The problem statement should acknowledge this and specify whether CompGraphRAG performs retrieval-then-LLM-reasoning only, or also symbolic/rule-based post-retrieval checks (see §4, Compliance Reasoning Workflow, below).

**Recommended reframing of the closing research-problem question:** As written it bundles three separable questions (accuracy, explainability, deployment-constraint) into one sentence, which is fine for a proposal abstract but should be explicitly decomposed into the accuracy/explainability/deployment axes so each maps 1:1 onto an RQ — currently RQ1–RQ2 map to accuracy, RQ3 to explainability, RQ6 to deployment, but RQ4/RQ5 don't map back onto the problem statement at all. Either fold RQ4/RQ5 into the problem statement or mark them as secondary/engineering RQs distinct from the core research problem.

---

### 3. Research Gap (Gap Table)

This is the strongest section in the document — it is honest, sourced, and each row has a specific limitation. Two improvements:

1. Add a row for **KG-construction/ontology-quality** as its own gap (currently folded into "Document Intelligence"), since your Expected Contributions section separately claims a "compliance-domain knowledge graph schema" as a technical contribution — the gap table should justify that specific claim with its own row, citing the KG-construction survey literature above.
2. Add a row for **RAG/GraphRAG evaluation methodology** — right now your gap table has no row acknowledging that *general* RAG evaluation tooling (RAGAS, ARES) exists but is not compliance/audit-calibrated. This is directly relevant to your Evaluation Metrics section and to RQ3/H3.

---

### 4. Research Objectives / 5. Research Questions / 6. Hypotheses

**Core problem across all three:** none of RQ1–RQ6 or H1–H8 currently has a **falsifiable operational definition**. A reviewer's first question for H1 is: what is "retrieval precision" — precision@k over what k? Measured against what gold set? "Significantly" — what test, what alpha, what correction for multiple comparisons across H1–H8? Right now every hypothesis is a plausible-sounding claim, not a pre-registered test. Section E (Statistical Validation, below) gives you the fix.

**Unsupported assumption in H7:** "does not show a statistically significant accuracy degradation" is a *null-hypothesis-as-desired-outcome* framing, which is a known methodological trap (absence of significance ≠ absence of effect, especially with small compliance-QA sample sizes). You should pre-specify an **equivalence test** (e.g., TOST — two one-sided tests) with a pre-registered minimum-important-difference, rather than relying on a non-significant p-value from a standard difference test.

**H4/H8 are good, underused hypotheses.** They are the most *novel* empirically-testable claims in the document (graph benefit scales with hop-distance) — I'd elevate H4/H8 to be co-primary with H1/H2 in your abstract, since "graph RAG helps more on harder multi-hop questions, proportionally to hop count" is a cleaner, more publishable empirical claim than "graph RAG beats vector RAG," which is already well-established in the GraphRAG/HippoRAG/LightRAG literature.

---

### 5. Expected Contributions / Scope

**Reframing needed:** The "Scientific Contributions" bullet claims novelty ("extending existing GraphRAG evaluation, which has concentrated on open-domain/general corpora rather than compliance-specific corpora") — this is *plausible* but the document's own literature pass has not searched ACM DL or Springer directly, so this claim is currently only as strong as an arXiv/web-search pass. Keep the [VERIFY] tag, but also note in the roadmap (Part C) that this specific claim needs a dedicated Google Scholar / ACM DL / Springer search pass on terms like "regulatory GraphRAG," "compliance knowledge graph LLM," "audit-trail RAG," "legal GraphRAG" before final submission — I did not find a paper contradicting the novelty claim in the searches run for this review, but that is not the same as a systematic confirmation.

**Scope gap:** The Excluded list should explicitly exclude **automated legal liability determination and any output being used as the sole basis for a compliance decision without human review** — this is both good scientific hygiene and very likely something an IRB/ethics reviewer or venue reviewer will ask for explicitly given the healthcare/regulatory framing.

---

### 6. Proposed Framework (Section 9)

This is presently a **module list with no interfaces, no data contracts, and no algorithm**. See Part B (System Architecture, Retrieval Algorithm) below for the concrete fix. The single biggest missing piece: there's no answer to *"how does hybrid retrieval actually combine dense-similarity scores with graph-path scores into one ranked context set?"* — this is the central technical mechanism of the entire paper and currently doesn't exist even at pseudocode level.

---

### 7. Literature Review — Phase 2

**Strengths:** Honest flagging of the three unpopulated categories; literature matrix and comparative-analysis table are useful reviewer aids.

**Gaps to close before submission (with sources found in this review that you can now use):**

- *RAG/GraphRAG evaluation methodology* (previously unpopulated "AI Evaluation" category): <cite index="15-1">ARES is an automated evaluation framework for retrieval-augmented generation that fine-tunes lightweight LLM judges on synthetically generated queries and answers, scoring each RAG component separately — context relevance, answer faithfulness, and answer relevance — using only minimal human annotations, and was shown to out-rank the existing RAGAS framework on RAG system scoring accuracy</cite>. <cite index="16-1">RAGAS instead decomposes generated answers into atomic factual statements and evaluates each against retrieved context, providing high-resolution, statement-level feedback on hallucination</cite>. These two papers should anchor your Evaluation Metrics section and directly answer the "AI Evaluation" gap category.
- *Knowledge Graph construction / ontology foundations* (previously unpopulated category): use <cite index="4-1">the 2025 survey of LLM-empowered knowledge graph construction, which frames construction along schema-based vs. schema-free paradigms across the ontology-engineering, extraction, and fusion pipeline</cite> as your foundational KG-construction citation, supplemented by the TBox/ABox formalization pattern <cite index="9-1">in which ontologies are encoded as TBox concept/property hierarchies populated by ABox instance assertions, with schema alignment validated through OWL/Turtle formalization</cite>.
- *Enterprise/compliance-adjacent document benchmark* (previously unpopulated "Enterprise Search" category, and directly useful for your dataset problem): <cite index="32-1">CUAD (Contract Understanding Atticus Dataset) is an expert-annotated legal-contract-review dataset built with legal experts from The Atticus Project, containing over 13,000 annotations across commercial contracts</cite>, <cite index="34-1">spanning 41 clause-type labels used to evaluate contract-review automation via span-selection question answering</cite>. CUAD is not HIPAA-specific, but it is the closest existing *regulated-document, expert-annotated* benchmark to what you need, and it should be cited as (a) a template for how to construct your own HIPAA compliance-QA dataset (expert annotation protocol, clause-level gold labels), and (b) a candidate out-of-domain generalization test if you want to show CompGraphRAG's schema/pipeline transfers beyond HIPAA.
- *Multi-hop QA benchmarks* — cite as the standard cross-domain baseline suite for RQ4 scaling comparisons, per §1 above.

**One correction:** In the Literature Matrix, the row for "Hassani et al. (Legal Compliance LLM)" is marked "Knowledge Graph: Partial" — based on the paper's own described research problem (limitations of prior NLP/ML legal-compliance automation and how LLMs address them), there's no indication this paper uses a KG at all; recommend downgrading to "No" unless the full text confirms a graph component, since matrix accuracy will be checked closely by reviewers who read the cited papers.

---

## PART B — TECHNICAL / ARCHITECTURAL ENHANCEMENTS

### B1. Formal System Architecture

Currently: six named modules with no formal interfaces. Recommended fix — define the pipeline as a typed data-flow, e.g.:

```
D (raw docs) --DocIntel--> E (extracted spans+layout) --KGConstruct--> G = (V, E_rel, λ, μ)
Q (query) --QueryEncoder--> (q_dense, q_entities)
Retrieval: R(q) = HybridRank( DenseRetrieve(q_dense, D_chunks), GraphRetrieve(q_entities, G) )
Generation: A = LLM(prompt(Q, R(q))) --> (determination, confidence, justification_subgraph)
Audit: AuditRecord = (Q, R(q), A, justification_subgraph, timestamp, model_version, policy_version)
```

Formalizing this now (even before implementation) lets you write a Methods section a reviewer can actually evaluate, and lets you specify exactly what "graph-path recall" (an evaluation metric you already listed) is measuring against.

**Knowledge Graph formalism (proposed, label as CompGraphRAG's own design choice, not literature-derived):**
- G = (V, E, τ, λ_V, λ_E), a typed labeled property graph, where:
  - V = entities, τ: V → {Policy, Role, DataType, Obligation, Exception, Incident, Regulation, Clause}
  - E = typed relations, e.g. `governs`, `permits_access_to`, `has_role`, `subject_to_exception`, `logged_as`, `derived_from`
  - λ_V, λ_E = attribute maps (e.g., a Clause node carries source_document_id, page_span, effective_date)
- Ontology layer: define a TBox (class hierarchy: Regulation ⊃ Rule ⊃ Obligation; Role ⊃ {Covered Entity, Business Associate, Workforce Member}) separately from the ABox (instance assertions extracted per-document) — this directly operationalizes the schema-based construction paradigm noted above and gives you a concrete, defensible answer to "what is your knowledge graph schema" beyond a bullet list.

### B2. Hybrid Retrieval Algorithm (currently entirely missing)

Propose a concrete, testable scoring function (label explicitly as a proposed contribution, not literature):

```
score(passage_or_path | q) = α · cos(embed(q), embed(passage))
                             + β · GraphPathScore(q_entities, path)
                             + γ · RecencyOrAuthority(source)

GraphPathScore(entities, path) = f(path_length, edge_type_confidence, entity_link_confidence)
```

- Specify α, β, γ as either fixed hyperparameters swept via grid/Bayesian search on a validation split, or learned via a lightweight logistic/LTR (learning-to-rank) layer — this choice needs to be made and justified, since it is the crux of your "hybrid > pure vector or pure graph" hypothesis (H2).
- Specify the **entity-linking step** (query mention → graph node) explicitly — this is a known failure point in KGQA pipelines and currently isn't mentioned at all. State whether you're using exact/fuzzy string match, embedding-based entity linking, or LLM-mediated linking, and report entity-linking accuracy as its own metric (it will silently cap your ceiling retrieval performance if unaddressed).

### B3. Prompting Strategy (currently unaddressed)

Needs an explicit specification of:
1. The extraction prompt(s) used in the Knowledge Graph Construction Module (with schema constraints passed in-context, consistent with the schema-based construction paradigm).
2. The generation prompt template for the Compliance Reasoning & Generation Module, which should require the model to (a) state a determination, (b) cite specific node/edge IDs from the retrieved subgraph, and (c) flag uncertainty explicitly if the graph path is incomplete — this is the mechanism that actually produces the "traceable explanation" your paper claims, so it must be specified, not assumed.
3. A calibration instruction so the model doesn't over-assert compliance/non-compliance beyond what its retrieved evidence supports (directly relevant to your "requires review" output category).

### B4. Compliance Reasoning Workflow

Currently pure retrieve→generate. Recommend adding an explicit **post-retrieval rule-check layer** for exception logic (e.g., minimum-necessary carve-outs, treatment/payment/operations exceptions) that the LLM alone is unreliable at applying consistently. This can be a lightweight rule engine over the graph (if `Disclosure --subject_to_exception--> TPO_Exception` exists, surface it before generation) rather than full deontic logic — but some symbolic check should sit between retrieval and generation, or your explainability claims will rest entirely on LLM self-report, which is exactly the black-box problem you're positioning against.

### B5. Explainability Mechanism

Define precisely what "graph-path explanation" means as an artifact: is it (a) the literal subgraph (nodes+edges) returned as JSON/visual, (b) a natural-language walk of the path generated by the LLM, or (c) both? Recommend (c), with (a) as the audit-grade machine-readable record and (b) as the human-facing summary — and require that (b) is checked against (a) for faithfulness (i.e., does the natural-language explanation actually match the retrieved subgraph, or did the LLM hallucinate a plausible-sounding but ungrounded justification?). This faithfulness check is itself a metric you should report (see Evaluation, below).

---

## PART C — EVALUATION METHODOLOGY OVERHAUL

### C1. Evaluation Metrics — reuse existing frameworks, don't invent new ones from scratch
Adopt <cite index="16-1">RAGAS-style atomic-statement faithfulness scoring</cite> and/or <cite index="15-1">ARES-style component-level judge scoring (context relevance, answer faithfulness, answer relevance) calibrated with a modest human-annotated set</cite> as your generation-quality metrics, rather than defining ad hoc LLM-as-judge prompts with no precedent — this makes your evaluation reproducible and comparable to other RAG papers reviewers already know. Add your own compliance-specific metrics on top: graph-path recall (does the returned subgraph contain the gold evidence path), and explanation-faithfulness (does the NL explanation match the retrieved subgraph — a metric with no established name in the literature you reviewed, propose it as your own contribution).

### C2. Baseline Systems (currently named but not specified as runnable baselines)
Concretely commit to implementing, not just citing:
1. Vector-only RAG (dense bi-encoder + top-k, standard Lewis et al. paradigm).
2. Microsoft GraphRAG (open-source implementation exists; use as-is with community-summarization).
3. LightRAG (open-source; dual-level indexing).
4. HippoRAG (open-source; single-step multi-hop graph memory).
5. CompGraphRAG (yours).
All five run on the *same* corpus and query set — this is non-negotiable for RQ1/RQ2/RQ4 to be valid comparisons.

### C3. Benchmark Datasets
- Primary: a constructed HIPAA compliance-QA set, built using an **expert-annotation protocol modeled on CUAD's** <cite index="34-1">approach of expert-annotated span/clause labels validated by legal/compliance professionals</cite> — adapt this methodology (annotator guidelines, inter-annotator agreement reporting, adjudication process) rather than inventing an annotation protocol ad hoc.
- Secondary/cross-domain: report results on <cite index="27-1">HotpotQA, 2WikiMultiHopQA, and MuSiQue</cite> to demonstrate CompGraphRAG is not overfit to a hand-built HIPAA set and to enable direct numeric comparison against published GraphRAG/LightRAG/HippoRAG results on these standard benchmarks.
- Tertiary (optional, strengthens generalizability claim): a CUAD-derived compliance/contract-clause subtask, since CUAD is public, expert-annotated, and regulatory-adjacent (SEC-filed contracts), giving you a second real (not synthetic) regulated-document benchmark beyond your own HIPAA set.

### C4. Statistical Validation (currently entirely absent — this is the single most reviewer-visible gap)
For each hypothesis:
- **H1, H2, H4:** paired comparison across the same query set for each system (e.g., paired bootstrap resampling or a paired t-test/Wilcoxon signed-rank test on per-query metric deltas), with a pre-registered alpha (e.g., 0.01 given 8 hypotheses) and a **Bonferroni or Benjamini-Hochberg correction** across H1–H8 to control family-wise error / false discovery rate — currently nothing controls for the multiple-comparisons problem across 8 hypotheses.
- **H3:** inter-rater reliability (Cohen's/Fleiss' kappa) across human evaluators rating explanation traceability, then a paired test (e.g., Wilcoxon) comparing graph-path vs. citation-only explanation ratings from the *same* evaluators on the *same* questions.
- **H5:** report extraction-error rates (precision/recall on entity & relation extraction against a manually verified gold subset) with McNemar's test for paired classifier comparison (layout-aware vs. plain-text extraction on the same documents).
- **H6:** latency/cost as a function of corpus size — report with confidence intervals over repeated runs (indexing is often non-deterministic due to LLM sampling), not single-run numbers.
- **H7:** switch to an **equivalence test (TOST)** as noted in Part A, with a pre-registered minimum meaningful accuracy difference (e.g., 2 F1 points).
- **H8:** correlation coefficient (Spearman, since hop-count is ordinal/discrete) between graph-augmentation accuracy gain and hop-distance, with a reported confidence interval and sample size large enough to detect a moderate correlation (power analysis recommended before data collection, not after).

### C5. Ablation Studies (currently none specified)
Minimum required ablation set:
1. Graph retrieval only vs. dense only vs. hybrid (isolates H2's actual mechanism).
2. With vs. without document-intelligence (layout-aware) extraction feeding the KG construction module, holding everything else constant (isolates H5).
3. With vs. without the post-retrieval rule-check layer (B4) — does symbolic exception-checking change accuracy and/or explanation quality independent of retrieval mode?
4. Full hierarchical (Microsoft GraphRAG-style) indexing vs. LightRAG-style dual-level indexing, holding retrieval/generation constant (isolates H6, separate from the cross-system baseline comparison in C2, which conflates indexing strategy with several other architectural differences between systems).
5. Entity-linking method ablation (exact-match vs. embedding vs. LLM-mediated) to quantify its ceiling effect on graph retrieval (see B2).

### C6. Error Analysis (currently none specified)
Recommend a structured error taxonomy applied to a sample of failure cases post-hoc:
- Retrieval-miss errors (correct entities/passages never retrieved),
- Entity-linking errors (query concept not correctly mapped to graph node),
- Graph-incompleteness errors (correct entities retrieved but the connecting edge/relation was never extracted during KG construction — a distinct failure mode from retrieval),
- Generation/hallucination errors (retrieval correct, but LLM output not faithful to context),
- Exception/rule-logic errors (correct facts retrieved, but conditional/exception logic misapplied — directly relevant to B4).
This taxonomy should be reported with counts/percentages, not just anecdotal examples, and should specifically distinguish "graph-incompleteness" from "retrieval-miss" since these have different fixes (better KG construction vs. better retrieval ranking) and conflating them will understate what's actually broken when results disappoint.

### C7. Threats to Validity
- **Construct validity:** synthetic/de-identified HIPAA scenarios may not capture the ambiguity and adversarial phrasing of real compliance disputes — state this explicitly as a limitation, not just in the Constraints section.
- **Internal validity:** LLM API non-determinism (sampling temperature, model version drift) — mitigate by fixing seeds/temperature=0 where possible, pinning model versions, and reporting variance across repeated runs, not single-shot numbers.
- **External validity:** results on a HIPAA-specific schema may not generalize to GDPR/SOX/PCI-DSS even though the paper gestures at this in "Future Extensions" — don't claim generalizability without at least the CUAD cross-domain check in C3.
- **Evaluator bias:** if the same team both builds the gold-standard HIPAA QA set and rates explanation traceability (H3), this is a conflict of interest for construct validity — recommend blind, independent evaluators for the human-rated metrics, and report annotator background/qualification.
- **Baseline-implementation validity:** re-implementations of Microsoft GraphRAG/LightRAG/HippoRAG can diverge from the original papers' reported numbers if hyperparameters aren't matched; use the original open-source repos directly rather than re-implementing from the paper text, and report any deviations.

### C8. Reproducibility Checklist
- Release: KG schema (TBox) definition file, extraction prompts, retrieval scoring code (with α/β/γ or learned weights), generation prompt templates, evaluation scripts (RAGAS/ARES config), and the synthetic HIPAA QA dataset (or a de-identified/redacted subset if constraints prevent full release).
- Report: exact model versions/dates for every LLM used (extraction, generation, judge), hardware/latency measurement conditions, random seeds, and full hyperparameter grids searched (not just final values).
- Pre-register (e.g., via OSF or a dated repo commit) the hypotheses, alpha levels, and correction method **before** running the full evaluation, to avoid the appearance of post-hoc hypothesis fitting given how directly H1–H8 currently map onto "expected" results.

---

## PART D — PRIORITIZED ACTION LIST (highest impact first)

1. **Write the hybrid retrieval scoring function and entity-linking method concretely (B2).** Nothing else in the paper is testable without this; it is the actual technical contribution.
2. **Adopt RAGAS/ARES as evaluation backbone (C1)** instead of inventing ad hoc metrics — this alone resolves the "AI Evaluation" literature gap and gives you a defensible, citable methodology.
3. **Define the KG schema formally (TBox/ABox) (B1)** and cite the KG-construction survey literature to justify the schema-based design choice — resolves the "Knowledge Graph construction/ontology" gap.
4. **Build/adapt the HIPAA compliance-QA dataset using a CUAD-style expert-annotation protocol (C3)**, and add HotpotQA/2WikiMultiHopQA/MuSiQue as secondary cross-domain benchmarks — resolves the dataset [VERIFY] flag with the least invented effort.
5. **Add the statistical validation plan (C4) with multiple-comparison correction** before running any experiments — prevents the paper being desk-rejected for p-hacking-adjacent hypothesis testing across 8 hypotheses.
6. **Implement the four baselines from their original repos, not re-implementations (C2/C7)** — required for RQ1/RQ2/RQ4 to mean anything.
7. **Specify the post-retrieval rule-check layer (B4)** — without it, your explainability claim is just "the LLM says why," which is exactly the black-box problem you're arguing against.
8. **Run the ablation set (C5)** — isolates which module actually drives any observed gains; reviewers will ask for this regardless.
9. **Add the error taxonomy (C6)** distinguishing retrieval-miss vs. graph-incompleteness vs. hallucination vs. rule-logic errors.
10. **Finish the Phase-2 literature pass** (Enterprise Search, Enterprise AI adoption, formal KG/ontology foundational paper) using the sources surfaced in this review as a starting point, then do the ACM DL/Springer direct search the document itself flags as outstanding.

---

## PART E — ROADMAPS

### E1. Implementation Roadmap
- **Weeks 1–2:** Finalize TBox schema (entity/relation types) and pick graph store (property graph DB, e.g., Neo4j, or RDF triple store if you want OWL reasoning — this choice should be made based on whether you need formal DL reasoning for exception logic (B4) or just fast path traversal).
- **Weeks 3–4:** Build Document Intelligence ingestion (layout-aware extraction) and KG construction pipeline (LLM extraction against the TBox schema + entity resolution).
- **Weeks 5–6:** Implement hybrid retrieval scoring (B2) with the entity-linking module; stand up dense vector index alongside the graph store.
- **Weeks 7–8:** Implement generation module + explainability rendering (subgraph JSON + NL walk) + the post-retrieval rule-check layer (B4).
- **Weeks 9–10:** Stand up the four baselines from original repos on the same infrastructure/corpus.
- **Weeks 11–12:** Integrate RAGAS/ARES evaluation harness; wire in the audit-record logging.

### E2. Experimentation Roadmap
- **Weeks 1–3:** Build/annotate the HIPAA compliance-QA gold set (expert annotators, inter-annotator agreement check, adjudication).
- **Weeks 4–5:** Run RQ1/RQ2 experiments (retrieval precision/recall, answer accuracy) across all five systems on the HIPAA set; run the same on HotpotQA/2WikiMultiHopQA/MuSiQue for cross-domain validation.
- **Week 6:** Run RQ4 (latency/cost scaling) across corpus sizes.
- **Week 7:** Run RQ5 (document-intelligence extraction ablation) on scanned/table-heavy subset.
- **Week 8:** Run RQ6/H7 (secured vs. unconstrained deployment) equivalence test.
- **Weeks 9–10:** Human evaluation for RQ3/H3 (independent, blinded evaluators rating explanation traceability).
- **Week 11:** Run full ablation suite (C5) and error-taxonomy coding pass (C6).
- **Week 12:** Statistical analysis pass with pre-registered correction method; finalize all tables/figures.

### E3. Paper-Writing Roadmap
- **Draft 1:** Introduction + Related Work (incorporating the corrected citation mapping from Part A), Problem Statement, Formal Architecture (B1), Retrieval Algorithm (B2) — this is the section that currently doesn't exist and needs to be written first since it anchors everything else.
- **Draft 2:** Methodology (dataset construction protocol, baselines, metrics — C1–C3), Experimental Setup.
- **Draft 3:** Results (RQ1–RQ6 with statistical tests per C4), Ablations (C5), Error Analysis (C6).
- **Draft 4:** Discussion (Threats to Validity per C7, Limitations, Future Work), Reproducibility Statement (C8), final abstract/contributions rewrite once actual numbers exist (do not lock the "Expected Contributions" language until results are in — several claims are currently written as though the results are already known).
- **Final pass:** Verify every remaining [VERIFY] tag against a direct ACM DL/Springer/Google Scholar search (not just arXiv/web search) before submission, particularly the "no existing system combines X+Y+Z" gap claim, since that is the paper's central novelty assertion and the one most likely to be challenged by a reviewer who knows the compliance-NLP literature better than a single search pass can surface.

---

## Summary Note on Citation Integrity
Every specific claim above attributed to a source is drawn from material retrieved in this review session and is cited inline. Where I could not find literature support for a recommendation (e.g., the specific hybrid-retrieval scoring formula, the graph schema, the post-retrieval rule-check layer, the "explanation-faithfulness" metric), I have explicitly labeled it as a **proposed CompGraphRAG design contribution**, not an established literature finding — consistent with the original document's own [VERIFY] discipline. Recommend the same labeling convention throughout your final paper: literature-grounded claims cited, original design choices explicitly marked as your contribution.
