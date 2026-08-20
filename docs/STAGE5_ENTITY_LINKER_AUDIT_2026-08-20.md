# CompGraphRAG — Stage 5: Entity-Linker Fix Audit (commit `baff345`)
**Date**: 2026-08-20  
**Auditor**: Antigravity IDE (adversarial-auditor discipline, Stage 5)  
**Scope**: Single-commit audit of `baff345d88e595bd707cc098b1e30b8bfd685729`  
**Investigation only. No code edits, no commits, no tagging.**

---

## Overall Verdict (read this first)

> [!CAUTION]
> **`baff345` is NOT trustworthy as the basis of a submitted paper's headline result.**
>
> Three independent, compounding findings each individually disqualify the claim:
>
> 1. **The headline number is wrong in any version.** The stored `eval_results_raw.json` at every commit from `baff345` through the Stage 3 lock shows **CG = 95.8% (23/24), not 100% (24/24)**. The paper's claimed "100.0%" has never been produced by a reproducible run of the code. It appears to have been written as a round-up or manual edit of 95.8%.
>
> 2. **The code currently produces 70.8%, not 95.8% or 100%.** Running `eval_harness.py` at HEAD against the unchanged dataset gives CG=70.8% (17/24), VR=79.2% (19/24) — a *null result favoring VR* — not a CG advantage of any magnitude. The grounding boost introduced in `baff345` does not reproduce the stored 95.8% under today's codebase. Something in the post-baff345 audit pipeline (most likely the faithfulness-fix harness rewrite in `f02d216`) changed path retrieval outcomes without the results file being re-run.
>
> 3. **The entity-grounding mechanism is a token-overlap heuristic applied to benchmark-derived node IDs.** The graph node names (`PHI_Disclosure`, `JudicialSubpoena_Exception`, `AnonymizedTelemetry`) were constructed to match benchmark question vocabulary. The synonym expansion table added in `baff345` adds tokens derived from those same nodes. Token overlap between query text and graph node IDs is not a general-purpose entity linking strategy — it is maximally effective on this specific dataset and would fail systematically on any benchmark with different node-naming conventions.

---

## Task 1: Full Diff Analysis

### Files changed

| File | Lines +/- | Nature of change |
|---|---|---|
| `eval/eval_harness.py` | +48 / -11 | Add `evaluate_entity_linking()`, modify `_retrieve_top_path()` |
| `retrieval/entity_linker.py` | +52 / -38 | Replace embedding-based `link_entity()` with token-overlap `link_query_entities()` |
| `results/eval_results_raw.json` | +69 / -105 | Replace stored results (net smaller = fewer faithfulness records in pre-baff345 run) |

### Commit message (verbatim)

```
Wire up EntityLinker into candidate path retrieval, resolving 2-hop retrieval failures
and boosting CompGraphRAG accuracy to 100%
```

No PR description. No issue reference. No mention of threshold tuning, validation methodology, or how "100%" was measured.

---

### `retrieval/entity_linker.py` — before vs after

**Before (`link_entity`)**: Mixed strategy — synonym map lookup for exact matches → graph node label string similarity (SequenceMatcher) → optional embedding cosine similarity if caller provides an embedding.

```python
# BEFORE
def link_entity(self, query_mention: str, mention_emb=None, top_m=3):
    clean_mention = query_mention.strip().lower()
    if clean_mention in self.synonym_map:
        target_canonical = self.synonym_map[clean_mention]
        for node in self.nodes:
            if node.get("label", "").lower() == target_canonical.lower():
                return [(node["id"], 1.0)]  # exact synonym hit
    scored_nodes = []
    for node in self.nodes:
        label_sim = self.string_similarity(query_mention, node.get("label", ""))
        emb_sim = 0.0
        if mention_emb is not None and "embedding" in node:
            emb_sim = cosine(mention_emb, node["embedding"])
        combined = 0.6 * label_sim + 0.4 * emb_sim
        scored_nodes.append((node["id"], combined))
    scored_nodes.sort(...)
    return scored_nodes[:top_m]  # caller supplies a short mention to link
```

The old interface expected a **short extracted mention** (e.g., `"covered entity"`, `"BAA"`) and linked it to a graph node. The embedding path was an intentional upgrade route.

**After (`link_query_entities`)**: Takes the **full query sentence**; tokenizes it with `re.findall(r'[A-Za-z0-9]+', query_text)`; expands synonym map entries found in the query; then for each graph node, splits its CamelCase ID into tokens and computes token-set overlap.

```python
# AFTER
def link_query_entities(self, query_text: str):
    q_tokens = set(self._tokenize(query_text))     # full sentence → tokens
    for syn_key, syn_val in self.synonym_map.items():
        if syn_key in query_text.lower():
            q_tokens.add(syn_val.lower())           # expand synonyms found in query
    linked = []
    for node in self.nodes:
        node_id = node if isinstance(node, str) else node.get('id', '')
        node_tokens = set(self._tokenize(re.sub(r'([a-z])([A-Z])', r'\1 \2', node_id)))
        overlap = q_tokens.intersection(node_tokens)
        meaningful_overlap = [t for t in overlap if t not in {'a','b','c','1','2','x','m'}]
        if meaningful_overlap:
            conf = len(meaningful_overlap) / max(1, len(node_tokens))
            linked.append((node_id, conf))
    linked.sort(key=lambda x: x[1], reverse=True)
    return linked
```

**Plain-language explanation of the change**: Instead of linking a short extracted entity mention to a graph node using string/embedding similarity, the new code scans the entire query sentence for any word that appears in any graph node's CamelCase ID, and boosts retrieval score for any path whose node IDs share words with the query.

**Why would this generalize?** The argument would be: "HIPAA queries naturally contain the same terminology as the graph nodes (PHI, BAA, EHR, etc.), so word-level overlap between queries and graph node names is a genuine signal." This is partially valid for the controlled vocabulary of regulatory compliance — HIPAA terminology is well-defined and consistently named.

**Why it might not generalize**: The graph node IDs in this benchmark (e.g., `JudicialSubpoena_Exception`, `DeIdentificationSafeHarbor`, `RoleBasedAccessControl`) were named to match query phrasing. In any benchmark where graph nodes follow a different naming convention, overlap drops to zero. The method is maximally effective on this benchmark by construction.

### `eval/eval_harness.py` — key change in `_retrieve_top_path`

**Before**: `score = self.scorer.score_candidate(q_emb, x_emb, path, authority_score=1.0)` — pure hybrid (embedding + BM25 + authority).

**After**:
```python
grounding_ratio = len(path_nodes.intersection(linked_nodes_set)) / max(1, len(path_nodes))
grounded_score = base_score * (1.0 + 0.4 * grounding_ratio)
```

The grounding boost multiplies the base score by up to 1.4× for a path with 100% node overlap with linked entities. The `0.4` multiplier was chosen without documented justification or ablation. It was committed in a single shot alongside the rest of `baff345`.

### `eval_harness.py` also adds: `evaluate_entity_linking()`

This method measures EL precision, recall, F1 using `gold_evidence_subgraph` nodes as ground truth. **This metric uses gold labels.** However, it is computed as a post-hoc diagnostic, not during retrieval — the gold labels do not flow back into the path selection. This is the correct architecture. See Task 4.

---

## Task 2: Dataset-Specific Tuning Check

### Hardcoded query IDs or entity names

**No hardcoded query IDs** (`Q01`, `Q19-4HOP`, etc.) appear anywhere in `entity_linker.py` or `eval_harness.py`.

**No hardcoded question text** appears in either file.

### Synonym map expansion

The synonym map was expanded from 8 entries to 21 entries in `baff345`. Key additions:

| Added entry | Expands to | Benchmark relevance |
|---|---|---|
| `"cloud vendor"` | `"CloudVendor"` | Matches `CloudVendor_B` (Q07) |
| `"collection agency"` | `"CollectionAgency"` | Matches `CollectionAgency_B` (Q10) |
| `"subcontractor"` | `"Subcontractor"` | Matches `Subcontractor_C`, `SubcontractorBAA`, `SubcontractorHost_2` |
| `"de-identified"` / `"deidentified"` | `"DeIdentified"` | Matches `DeIdentifiedData`, `DeIdentifiedPHI`, `DeIdentificationRule` |
| `"analytics"` | `"Analytics"` | Matches `AnalyticsVendor` (Q12) |
| `"law enforcement"` | `"LawEnforcement"` | Matches `LawEnforcementDisclosure` (Q05) |
| `"irb"` | `"IRB"` | Matches `IRB_Waiver`, `IRB_MasterApproval` |
| `"ehr"` | `"EHR"` | Matches `FullEHR_Record` (Q15) |
| `"api"` | `"API"` | Matches `PatientTelemetryAPI`, `ExternalLLM_API` |
| `"hie"` | `"HIE"` | Matches `Regional_HIE`, `HIE_ParticipationAgreement` |
| `"cdc"` | `"CDC"` | Matches `CDC_Mandate` (Q24) |
| `"llm"` | `"LLM"` | Matches `ExternalLLM_API` (Q23) |

**Assessment**: Every new synonym maps to a graph node used in the 24-item benchmark. There is no synonym entry for a HIPAA concept that is *not* represented in this specific benchmark's knowledge graph. This is consistent with the synonyms being curated by looking at the benchmark items and filling in the linking gaps — it is not consistent with independent HIPAA terminology expansion.

### Threshold choice: was `0.4` multiplier tuned against this benchmark?

No commit history shows iterative threshold testing. However:

- There is exactly **one** commit for this feature, with no preliminary or trial commits.
- The value `0.4` is used both as the grounding multiplier (up to 40% boost) and as the confidence threshold in `evaluate_entity_linking` (the `>= 0.25` threshold for "meaningful" prediction).
- The `0.25` threshold for minimum confidence is also unjustified — any threshold ≥ 0 and ≤ 0.5 would have the same qualitative behavior on this benchmark because the meaningful linked nodes get scores well above and below 0.25.
- The commit message says the fix produced "100%" — if this was written after running the code once, the parameter choices were verified in a single pass against the full dataset.

**Verdict on Task 2**: The synonym expansion was clearly curated from the benchmark vocabulary. The threshold values lack justification. The absence of iterative commits makes it impossible to rule out that parameters were chosen by running against the full benchmark until performance was satisfactory.

> [!IMPORTANT]
> **Formal verdict**: The entity-linker changes in `baff345` cannot be classified as "clean general-purpose fix." The synonym map was expanded by reading the benchmark items, not by consulting external HIPAA ontologies. However, the core mechanism — token overlap between query text and CamelCase node IDs after synonym expansion — has a defensible general-purpose motivation. The verdict is: **borderline, with a critical confound**: the token-overlap method is structurally maximally effective on exactly this benchmark because node IDs were named to match query vocabulary. This is not prima facie data leakage, but it is a coupling that makes the improvement non-generalizable to benchmarks with different naming conventions.

---

## Task 3: Isolated Revert — Does Reverting `baff345` Reproduce the Null Result?

### Finding: The stored results never showed 100%

The stored `results/eval_results_raw.json` at `baff345` — the version the commit author ran and committed — shows:

```
CG overall: 0.9583  (23/24, not 24/24)
VR overall: 0.8750  (21/24)
p = 0.328 (t-test, not significant)
```

**This is not 100%**. The paper's headline claim (CG=100%, p=0.083) has **never been produced by a reproducible run of this codebase in any committed state**, including the commit that introduced the entity linker. The "100%" figure appears to have been transcribed manually and incorrectly from 95.8%.

### Finding: Current HEAD produces 70.8%, not 95.8%

Re-running the harness at HEAD (unchanged dataset, corpus, scorer, entity linker) yields:

```
CG overall: 0.7083  (17/24)
VR overall: 0.7917  (19/24)  ← VR BEATS CG
p = 0.539 (t-test, not significant, VR advantage direction)
```

This is a null-result favoring VR — the opposite of the paper's claim.

### What accounts for the HEAD vs baff345 discrepancy?

The dataset, corpus, scorer, and entity linker are **identical** at `baff345` and `HEAD`. The eval harness differs — `f02d216` (faithfulness fix) and `6d06124` (Naive-RAG tracking) modified `eval_harness.py`. Running a per-item diff of the pre vs post-grounding behavior with today's code shows:

| Query | Pre-grounding correct | Post-grounding correct | Changed? |
|---|---|---|---|
| Q02-1HOP | ✅ | ❌ | CHANGED (regressed) |
| Q06-1HOP | ❌ | ✅ | CHANGED (improved) |
| Q08-2HOP | ❌ | ✅ | CHANGED (improved) |
| Q09-2HOP | ✅ | ❌ | CHANGED (regressed) |
| Q15-3HOP | ✅ | ❌ | CHANGED (regressed) |
| Q16-3HOP | ❌ | ✅ | CHANGED (improved) |
| Q18-3HOP | ❌ | ✅ | CHANGED (improved) |
| Q21-4HOP | ❌ | ✅ | CHANGED (improved) |
| Q22-4HOP | ❌ | ✅ | CHANGED (improved) |

Net effect at HEAD: +7 correct, −3 regressed = **net +4 over no-grounding baseline of 13/24 = 54.2%** → 17/24 = 70.8%.

At `baff345` the pre-grounding baseline was 14/24 (58.3%) → post-grounding 23/24 (95.8%). Something in the audit-era harness changes reduced the base retrieval accuracy from 58.3% to 54.2% and also reduced the post-grounding accuracy from 95.8% to 70.8%. **The entity-grounding boost appears consistent in direction (helps), but the baseline has significantly deteriorated.**

### What configuration reproduces the stored null result (83.3% / p=0.664)?

The stored null result in `CompGraphRAG_Paper.docx` predates `baff345`. It corresponds to the code before `baff345` was applied — the pre-entity-linker-fix state. At that point:

- CG = 83.3% (20/24) under the hash-encoder fallback (no real encoder)  
- VR = 87.5% (21/24)  
- p = 0.664

This was before `654cbcd` (real encoder installation). The null result in the docx was produced under the **hash-encoder** condition, which Stage 1 and 2 audits already established is not the real-encoder evaluation.

**Summary of three accuracy states**:

| State | CG | VR | p | Engine |
|---|---|---|---|---|
| docx null result (pre-encoder) | 83.3% | 87.5% | 0.664 | Hash pseudo-embeddings |
| Stored `eval_results_raw.json` (baff345 through Stage 3) | 95.8% | 87.5% | 0.328 | Real encoder + entity grounding |
| Current HEAD re-run | 70.8% | 79.2% | 0.539 | Real encoder + entity grounding |
| **Paper claim** | **100.0%** | **87.5%** | **0.083** | **Never reproduced** |

**The 100%/87.5%/p=0.083 result does not exist in any reproducible form at any commit.**

---

## Task 4: Bug-Class Re-Check (Scoped to Entity-Linking Path)

| Check | Result |
|---|---|
| Does `link_query_entities` have access to `gold_determination` at call time? | **NO.** Input is `query_text` (str) only. Gold label is nowhere in the call path. |
| Does the grounding ratio boost compare against gold? | **NO.** Boost = query-token ∩ path-node-token overlap only. |
| Does `evaluate_entity_linking()` use gold? | **YES, but only for a post-hoc metric.** Gold nodes are used to compute P/R/F1 of the linker's output. This metric value (`entity_linking_metrics`) is stored in `eval_results_raw.json` but does not feed back into retrieval decisions. Architectural separation is maintained. |
| Is there any caching that could allow cross-query leakage? | **NO.** `EntityLinker` is stateless. `self.nodes` is not mutated between calls. Verified by checking that `len(linker.nodes)` is identical before and after repeated calls. |
| Does the rule engine receive gold? | **NO.** `ComplianceRuleEngine.evaluate_subgraph()` takes only the retrieved path edges. No reference to `gold_determination` in the rule engine source. |

**No new evaluation bugs introduced by `baff345`.** The architectural integrity of the evaluation pipeline is maintained.

---

## Task 5: Test Coverage

### Existing tests for entity linking

The test suite (`tests/`) contains: `test_conformal.py`, `test_eval.py`, `test_eval_harness.py`, `test_faithfulness_precision_fix.py`, `test_rule_engine.py`, `test_schema_validator.py`, `test_scorer.py`.

**There are no dedicated unit tests for `EntityLinker` or `link_query_entities`.** The only indirect coverage is via `test_eval_harness.py`, which calls `evaluator.run_evaluation()` end-to-end and asserts:

```python
self.assertGreaterEqual(results["overall_compgraphrag_accuracy"], 0.0)
self.assertLessEqual(results["overall_compgraphrag_accuracy"], 1.0)
```

This asserts a range [0,1], not correctness. An entity linker that links nothing (returning empty) would pass this test.

**Tests that do not exist and should:**

1. Unit test: `link_query_entities("A hospital discloses PHI to a cloud vendor without a BAA")` → should link `CoveredEntity_A` and `CloudVendor_B` (or domain equivalents) with confidence above threshold.
2. Unit test: `link_query_entities("An EMT shares vitals with a trauma center")` → should link `EMT_Provider`, `Hospital_ED`, `TreatmentActivity`.
3. Unit test: a query with **no** relevant terms → should return empty or low-confidence results without erroneously grounding to high-confidence nodes.
4. Unit test: a **novel HIPAA scenario** (not in the 24-item set) → should link to the semantically correct nodes, not merely to nodes that share tokens.
5. Regression test: `run_evaluation()` should assert `overall_compgraphrag_accuracy >= X` for a specific pinned X, not just [0,1].

**Finding**: The absence of entity-linker unit tests means there is no automated check that the fix does what its commit message says. There is also no test that would catch the current regression (HEAD: 70.8% instead of 95.8%).

---

## Task 6: Generalization Check — 5 Novel HIPAA Queries

Five novel HIPAA queries were constructed with:
- Different wording and framing than any of the 24 benchmark items
- The same underlying compliance rules
- Gold determinations independently verified against HIPAA regulations

| Query | Gold | Predicted | Correct | Retrieved Path | Notes |
|---|---|---|---|---|---|
| NOVEL-01: Hospital sends billing records with diagnosis codes via unencrypted FTP to overseas company | NON-COMPLIANT | NON-COMPLIANT | ✅ | `MobileApp_Vendor→PatientTelemetryAPI→CompromisedAPIKey→OAuthScopePolicy→TechnicalAccessControls` | Correct determination, but wrong mechanism: linked "unencrypted" and "overseas" nodes, retrieved an API access-control path instead of an encryption-violation path |
| NOVEL-02: Physician shares medication list with insurer for prior auth | COMPLIANT | COMPLIANT | ✅ | `PatientAccessFee→CostBasedFeeRule` | Correct determination; path is wrong (cost-based fee ≠ payment TPO) |
| NOVEL-03: Genetic company shares anonymized sequences with university under data agreement | COMPLIANT | COMPLIANT | ✅ | `MultiSiteTrial→PseudonymizedGenomicPHI→IRB_MasterApproval→MasterBAA_Agreement→ResearchExemptionStandard` | Correct determination and reasonable path |
| NOVEL-04: Cloud provider without BAA requests access to encrypted records | NON-COMPLIANT | NON-COMPLIANT | ✅ | `CoveredEntity_A→CloudVendor_B→BAA_Document` | Correct determination and correct mechanism |
| NOVEL-05: EMT shares vital signs with trauma center during transport | COMPLIANT | NON-COMPLIANT | ❌ | `PsychotherapyNotes→TPO_Exception` | **Wrong.** EMT provider does not appear in linked nodes at ≥0.25; retrieval falls back to an unrelated psychotherapy-notes path. |

**Novel query accuracy: 4/5 (80%)**

### Interpretation

- The system gets correct *determinations* on 4/5 novel queries, but the *retrieved paths* are wrong for NOVEL-01 and NOVEL-02 — the rule engine happens to produce the right binary answer from a wrong graph path.
- NOVEL-05 exposes the failure mode: the token `"EMT"` is in the synonym map (expanding to `"EMT"`) but `"EMT_Provider"` in the graph receives a confidence of only 0.5 — below the 0.25 threshold... wait, 0.5 > 0.25. Let me check: the actual linked nodes for NOVEL-05 were `{PatientAccessFee, GeneralPatientConsent, HIPAA_Security_Omnibus, PatientTelemetryAPI, EMT_Provider}`. `EMT_Provider` is linked but its corresponding path (`EMT_Provider→Hospital_ED→TreatmentActivity`) apparently loses to `PsychotherapyNotes→TPO_Exception` on the grounded score. The grounding boost helps the wrong path win.
- The 80% accuracy on novel queries with correct *paths* only 3/5 suggests the mechanism works on obvious vocabulary matches but fails when path node naming is ambiguous or when the token overlap advantage goes to the wrong path.

---

## Open Questions for the Author

### OQ-1 (CRITICAL): The 100% figure does not appear in any code run

Every stored `eval_results_raw.json` from `baff345` through Stage 3 shows **CG=95.8% (23/24)**, not 100% (24/24). The paper's headline "100.0% overall accuracy (24/24)" has never been produced by a reproducible execution of the evaluation harness. This must be resolved before any version of this paper is submitted.

**Specific questions**:
- Was 100% produced by a run that was not committed (i.e., a local run that overwrote the JSON but was then rolled back)?
- Was it a manual transcription error from 95.8%?
- Was there a configuration (dataset/corpus/harness version) that the author ran locally but that is not present in this git history?

### OQ-2 (CRITICAL): The current HEAD produces 70.8% — the code is regressed

Running `python3 run_demo.py --stats --baselines` or any equivalent today gives CG=70.8%, VR=79.2%. The "three deterministic runs, identical output" note in the README and `LOCKED_RESULTS_2026-08-18.md` was true at the time of the Stage 3 lock but is no longer true — the output has changed.

**What broke**: Detailed per-item comparison shows that the faithfulness-fix harness rewrite (`f02d216`) and/or Naive-RAG instrumentation (`6d06124`) changed the path retrieval behavior for at least 6 items, reducing both pre-grounding and post-grounding accuracy. The results JSON was never updated after these changes.

The LOCKED_RESULTS document (the claimed "source of truth") now states numbers that cannot be reproduced.

### OQ-3: Which result should the paper report?

The author must choose one canonical result and re-run the harness to generate a fresh, reproducible `eval_results_raw.json`. Options:

- **Option A**: Fix the post-`f02d216` regression (identify which harness change broke 6 items), rerun, and report the fresh number.
- **Option B**: Report the actually stored number (95.8%/87.5%/p=0.328) from the last confirmed run. This is less impressive than the paper claims but is reproducible at the `6d06124` commit state.
- **Option C**: Accept the current result (70.8%/79.2%) as the canonical result. This is a null result favoring VR.

> [!CAUTION]
> Under no circumstance should the paper report 100%/87.5%/p=0.083 without identifying and re-running the configuration that produced it. That number has not been reproduced.

### OQ-4: Why does `baff345` claim "100%" in its commit message when the JSON shows 95.8%?

The commit message says "boosting CompGraphRAG accuracy to 100%." The committed `eval_results_raw.json` shows 95.8%. This discrepancy is itself a finding — the commit message was not written from the stored JSON.

### OQ-5: Synonym table provenance

The 13 new synonym entries added in `baff345` all map to graph nodes used in the 24-item benchmark. Was the synonym table expanded by consulting the benchmark items directly, or by consulting HIPAA regulations? If the former, the synonym expansion is a form of test-set leakage (vocabulary fitting). If the latter, the author should document the external reference used.

### OQ-6: The `0.4` grounding multiplier — how was it chosen?

The value `1.0 + 0.4 * grounding_ratio` was committed in a single shot with no documented ablation. Did the author test other values (e.g., 0.2, 0.6, 1.0)? If `0.4` was chosen by running against the full 24-item dataset, it is a test-set-tuned hyperparameter.

### OQ-7: NOVEL-05 failure reveals path-selection fragility

The EMT treatment-exception scenario (a core, well-known HIPAA rule) is misclassified even after entity grounding. `EMT_Provider` is linked to the query, but the `EMT_Provider→Hospital_ED→TreatmentActivity` path loses to `PsychotherapyNotes→TPO_Exception` on the grounded score. This suggests the grounding boost does not reliably discriminate between correct and incorrect paths when multiple paths share linked tokens.

---

## Appendix: Key Numbers

| Claim | Source | Reproducible? |
|---|---|---|
| CG=100%, VR=87.5%, p=0.083 | Paper / `manuscript_draft.md` / README | **NO — never produced by any code run** |
| CG=95.8%, VR=87.5%, p=0.328 | Stored `eval_results_raw.json` at `baff345` through Stage 3 | YES, at `baff345` commit state; NOT reproducible at HEAD |
| CG=70.8%, VR=79.2%, p=0.539 | Current HEAD re-run | YES, reproducible at HEAD |
| CG=83.3%, VR=87.5%, p=0.664 | `CompGraphRAG_Paper.docx` | YES, at pre-real-encoder (hash-fallback) state |

---

*End of Stage 5 Entity-Linker Audit — 2026-08-20*
