# CompGraphRAG — Stage 2 Stress-Test Findings

**Date**: 2026-08-18  
**Role**: Adversarial technical auditor — investigation only, except Task 4 (additive instrumentation, committed as `06b1a1f`).  
**Constraint**: No edits to paper, README, or trade article. No archiving. One commit permitted (Task 4 instrumentation).  
**Encoder**: All runs use `real sentence-transformers (all-MiniLM-L6-v2)` via `/tmp/cgrag_venv`.

---

## Task 1: Discordant Items — Read Every One by Hand

### Identification

Under the real encoder, exactly **3 items** are discordant (CG correct, VR wrong). CG is 24/24 (100%); VR is 21/24 (87.5%).

| ID | Hop | Gold | CG | VR | NR | CG✓ | VR✓ | Discordant |
|----|-----|------|----|----|----|-----|-----|-----------|
| Q01-1HOP | 1 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| Q02-1HOP | 1 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| **Q03-1HOP** | **1** | **COMPLIANT** | **COMPLIANT** | **NON-COMPLIANT** | **NON-COMPLIANT** | **✓** | **✗** | **YES** |
| Q04-1HOP | 1 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| Q05-1HOP | 1 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| Q06-1HOP | 1 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| Q07-2HOP | 2 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| Q08-2HOP | 2 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| Q09-2HOP | 2 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| Q10-2HOP | 2 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| **Q11-2HOP** | **2** | **NON-COMPLIANT** | **NON-COMPLIANT** | **COMPLIANT** | **NON-COMPLIANT** | **✓** | **✗** | **YES** |
| **Q12-2HOP** | **2** | **COMPLIANT** | **COMPLIANT** | **NON-COMPLIANT** | **NON-COMPLIANT** | **✓** | **✗** | **YES** |
| Q13-3HOP | 3 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| Q14-3HOP | 3 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| Q15-3HOP | 3 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| Q16-3HOP | 3 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| Q17-3HOP | 3 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| Q18-3HOP | 3 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| Q19-4HOP | 4 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| Q20-4HOP | 4 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| Q21-4HOP | 4 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| Q22-4HOP | 4 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |
| Q23-4HOP | 4 | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | NON-COMPLIANT | ✓ | ✓ | — |
| Q24-4HOP | 4 | COMPLIANT | COMPLIANT | COMPLIANT | COMPLIANT | ✓ | ✓ | — |

All three misses are at ≤2-hop. Zero misses at 3-hop or 4-hop for either system.

---

### Q03-1HOP — 1-hop, CG=COMPLIANT✓, VR=NON-COMPLIANT✗

**Question**: "Is disclosure of PHI pursuant to a valid judicial subpoena compliant without individual authorization?"  
**Gold**: COMPLIANT

**CG path**: `PHI_Disclosure --[subjectToException]--> JudicialSubpoena_Exception`  
→ Rule 3 (subjectToException) → COMPLIANT ✓

**VR top passage** (p05, sim=0.7670, gap=0.267):  
"Disclosures of PHI to law enforcement officials require a court order, grand jury subpoena, or statutory mandate under 45 CFR 164.512(f)."  
→ edges: `LawEnforcementDisclosure --[violatessafeguard]--> PrivacyRule_LawEnforcement`  
→ Rule 2 (violatessafeguard) → NON-COMPLIANT ✗

**Does graph structure provide information flat retrieval couldn't?** YES. The query mentions "judicial subpoena" — a phrase that also appears in p05 ("grand jury subpoena"). Dense embedding cannot distinguish p03 (§164.512(e) — court subpoena as a permissible exception) from p05 (§164.512(f) — law enforcement disclosure without authority = violation), because both passages contain "subpoena." The entity linker surfaces `JudicialSubpoena_Exception` as a node, the graph path chains to it via `subjectToException`, and the rule engine correctly fires the exception rule. Graph entity grounding disambiguates two passages that share critical surface vocabulary but encode opposite compliance semantics.

---

### Q11-2HOP — 2-hop, CG=NON-COMPLIANT✓, VR=COMPLIANT✗

**Question**: "Is sending unencrypted patient billing spreadsheets over open email to a third-party auditor non-compliant?"  
**Gold**: NON-COMPLIANT

**CG path**:  
`BillingDepartment --[transmitsData]--> UnencryptedEmail`  
`UnencryptedEmail --[violatessafeguard]--> SecurityRule_Encryption`  
→ Rule 2 (violatessafeguard) → NON-COMPLIANT ✓

**VR top passage** (p10, sim=0.5530):  
"Covered hospitals sharing patient billing details with contracted debt collection agencies operating under executed business associate agreements satisfy Privacy Rule requirements."  
→ edges include `satisfiesStandard` → Rule 3 → COMPLIANT ✗

**Does graph structure help?** YES. "Billing" and "spreadsheets" semantically match p10 ("billing details"). The discriminant is *unencrypted* + *open email* — which are the entity `UnencryptedEmail` in the graph, leading to `violatessafeguard`. The entity linker surfaces this node; the graph path encodes the transmission-security violation. Flat retrieval retrieves a billing-COMPLIANT passage by topic match and misses the security-violation distinction.

---

### Q12-2HOP — 2-hop, CG=COMPLIANT✓, VR=NON-COMPLIANT✗

**Question**: "Does disclosing de-identified patient data to a marketing analytics vendor require individual patient authorization?"  
**Gold**: COMPLIANT (de-identified data is outside HIPAA scope)

**CG path**:  
`DeIdentifiedData --[transmitsPHI]--> AnalyticsVendor`  
`AnalyticsVendor --[subjectToException]--> DeIdentificationSafeHarbor`  
→ Rule 3 (subjectToException) → COMPLIANT ✓

**VR top passage** (p07, sim=0.5708, gap=0.013 — near-tie):  
"A covered entity may not disclose protected health information to a business associate or cloud service provider without satisfactory assurances through a written Business Associate Agreement..."  
→ edges: `lacksAgreement` → Rule 1 → NON-COMPLIANT ✗

**Does graph structure help?** YES — this is the clearest case. The critical distinction is *de-identified* vs. *protected health information*. The dense embedding captures "disclosing data to a vendor" (which matches p07, a BAA-required scenario) but not the de-identification exception that determines HIPAA applicability entirely. The `DeIdentifiedData` node carries this information, and the path's `subjectToException → DeIdentificationSafeHarbor` encodes the legal conclusion. The cosine gap is only 0.013 — VR retrieves the wrong passage by a razor-thin margin.

---

### Summary Table

| ID | Hop | Gold | CG | VR | Why they differ (one sentence) |
|----|-----|------|----|----|-------------------------------|
| Q03-1HOP | 1 | COMPLIANT | ✓ | ✗ | Entity linker distinguishes `JudicialSubpoena_Exception` from `PrivacyRule_LawEnforcement`; both passages contain "subpoena" but encode opposite compliance determinations. |
| Q11-2HOP | 2 | NON-COMPLIANT | ✓ | ✗ | `UnencryptedEmail` entity triggers security-violation path; VR retrieves a billing-COMPLIANT passage by topic similarity, missing the encryption-mandate discriminant. |
| Q12-2HOP | 2 | COMPLIANT | ✓ | ✗ | `DeIdentifiedData` entity triggers HIPAA inapplicability; VR lands on a BAA-required passage by vendor-disclosure surface similarity at near-tie cosine gap (0.013). |

**In all three cases, graph structure provides information that flat retrieval could not recover from the same passage corpus.** The mechanism is consistent: entity disambiguation, not path depth. See Task 2 for why this does not straightforwardly validate the H4/H8 multi-hop scaling claim.

---

## Task 2: Is the Benchmark Too Easy?

### Cosine Similarity Matrix

| QID | Hop | Gold | TopP | TopSim | 2ndSim | Gap | TopOk? | Flag |
|-----|-----|------|------|--------|--------|-----|--------|------|
| Q01-1HOP | 1 | COMPLIANT | p01 | 0.6798 | 0.6486 | 0.0312 | ✓ | — |
| Q02-1HOP | 1 | NON-COMPLIANT | p02 | 0.7129 | 0.4782 | 0.2348 | ✓ | LARGE-GAP |
| Q03-1HOP | 1 | COMPLIANT | p05 | 0.7670 | 0.5003 | 0.2667 | ✗ | LARGE-GAP + WRONG |
| Q04-1HOP | 1 | COMPLIANT | p04 | 0.8488 | 0.5335 | 0.3153 | ✓ | LARGE-GAP |
| Q05-1HOP | 1 | NON-COMPLIANT | p05 | 0.7048 | 0.5218 | 0.1830 | ✓ | LARGE-GAP |
| Q06-1HOP | 1 | COMPLIANT | p06 | 0.5583 | 0.5393 | 0.0190 | ✓ | — |
| Q07-2HOP | 2 | NON-COMPLIANT | p07 | 0.7244 | 0.5101 | 0.2143 | ✓ | LARGE-GAP |
| Q08-2HOP | 2 | COMPLIANT | p06 | 0.6634 | 0.5395 | 0.1238 | ✓ | — |
| Q09-2HOP | 2 | NON-COMPLIANT | p14 | 0.4884 | 0.4561 | 0.0323 | ✓ | — |
| Q10-2HOP | 2 | COMPLIANT | p10 | 0.8091 | 0.5825 | 0.2266 | ✓ | LARGE-GAP |
| Q11-2HOP | 2 | NON-COMPLIANT | p10 | 0.5530 | 0.4670 | 0.0860 | ✗ | WRONG-TOP |
| Q12-2HOP | 2 | COMPLIANT | p07 | 0.5708 | 0.5579 | 0.0128 | ✗ | near-tie (WRONG) |
| Q13-3HOP | 3 | COMPLIANT | p13 | 0.5740 | 0.4854 | 0.0886 | ✓ | — |
| Q14-3HOP | 3 | NON-COMPLIANT | p14 | 0.7263 | 0.4872 | 0.2390 | ✓ | LARGE-GAP |
| Q15-3HOP | 3 | NON-COMPLIANT | p15 | 0.5564 | 0.5173 | 0.0391 | ✓ | — |
| Q16-3HOP | 3 | COMPLIANT | p16 | 0.7469 | 0.5665 | 0.1805 | ✓ | LARGE-GAP |
| Q17-3HOP | 3 | NON-COMPLIANT | p17 | 0.5374 | 0.3493 | 0.1881 | ✓ | LARGE-GAP |
| Q18-3HOP | 3 | COMPLIANT | p20 | 0.5869 | 0.5696 | 0.0173 | ✓ | — |
| Q19-4HOP | 4 | NON-COMPLIANT | p19 | 0.7070 | 0.4533 | 0.2537 | ✓ | LARGE-GAP |
| Q20-4HOP | 4 | COMPLIANT | p20 | 0.8889 | 0.5525 | 0.3363 | ✓ | HIGH-SIM |
| Q21-4HOP | 4 | NON-COMPLIANT | p21 | 0.4916 | 0.4736 | 0.0180 | ✓ | — |
| Q22-4HOP | 4 | COMPLIANT | p22 | 0.7573 | 0.4800 | 0.2773 | ✓ | LARGE-GAP |
| Q23-4HOP | 4 | NON-COMPLIANT | p23 | 0.6477 | 0.5022 | 0.1454 | ✓ | — |
| Q24-4HOP | 4 | COMPLIANT | p08 | 0.6864 | 0.6626 | 0.0239 | ✓ | — |

Flagged: 1 HIGH-SIM (Q20), 12 LARGE-GAP (>0.15), 3 WRONG-TOP.

### Near-Paraphrase: Q20 (sim=0.8889, gap=0.336)

Q20 query: "A multi-site clinical trial shares pseudonymized genomic data across IRB-approved institutions under a master data sharing agreement. Is this arrangement compliant?"

Top passage (p20): "Multi-center clinical research trials sharing pseudonymized genomic data operate compliantly when governed by master IRB approvals, data protection agreements, and executed BAAs."

This passage **directly answers the query in its own text** ("operate compliantly"). Cosine similarity 0.8889 at a 0.34 gap to second place. Vector-RAG solves Q20 trivially by keyword overlap alone; no reasoning required.

### Structural Verdict

**The benchmark has a design flaw that undermines the H4/H8 claim.** The root cause: `candidate_corpus.py` builds 24 passages (p01–p24) that are one-to-one in subject matter with the 24 queries (Q01–Q24). There are only two distractor passages (d01, d02), both about unrelated HIPAA administrative topics — neither is a hard distractor that shares vocabulary with a specific query but encodes the wrong determination.

Consequences:
1. **12/24 queries have cosine gap > 0.15** — the correct passage is a clear outlier, not surrounded by hard distractors. Vector-RAG solves these by semantic similarity alone.
2. **3-hop and 4-hop items**: VR scores 100% (6/6 correct) at both tiers. This is not because these queries are hard and CG succeeds where VR fails — it is because the 3-hop and 4-hop passages are all easily discriminable by dense similarity alone. There is no signal in these tiers that distinguishes CG from VR.
3. **VR's 3 errors are all at ≤2-hop**, where surface-form collisions between passages accidentally create hard cases. These are artifacts of the corpus construction, not evidence of multi-hop failure.
4. The H4/H8 hypothesis ("marginal benefit grows with hop count") is not testable on this dataset, because higher-hop items happen to be easier for flat retrieval, not harder.

**Verdict: Not a well-constructed adversarial benchmark for the H4/H8 claim.** The benchmark needs:
- Hard distractor passages that share vocabulary with each query but encode the opposite determination
- Minimum cosine similarity thresholds for distractors (e.g., distractor must be within 0.10 cosine distance of the query for it to qualify)
- Scenarios where no single passage contains the full answer and evidence must genuinely be chained across multiple passages
Before these changes, the per-hop accuracy breakdown is not interpretable as a test of multi-hop retrieval capability.

---

## Task 3: Seven Bug-Class Re-Checks Under Real Encoder

All checks executed using live `all-MiniLM-L6-v2` inference (not hash fallback).

| # | Bug Class | Test | Result |
|---|-----------|------|--------|
| 1 | Gold label leaked to rule engine | Signature inspection + source search for `gold_determination` | **PASS** — signature is `(path_edges: List[Dict]) -> Dict`. Gold label never passed. |
| 2 | Faithfulness circularity | Fed path_A as both args (f1=1.0); fed path_B as triples against path_A (f1=0.0) | **PASS** — scores change when different edges fed. No structural circularity bug. |
| 3 | Confidence hardcoded in conformal | Two ConformalPredictor instances calibrated with different data; q_hat differs | **PASS** — q_hat=0.40 (high-conf data), q_hat=0.95 (low-conf data). Genuinely data-driven. |
| 4 | Baseline shares CG rule engine | `runner.rule_engine is not re_engine` check; VR uses `corpus.passages` not `candidate_paths` | **PASS** — independent rule engine instances; independent retrieval source. |
| 5 | Random seed genuinely wired | Same item_id → same seed int; same seed → identical random sequence | **PASS** — Q01 seed=407785893, Q24 seed=1570158748. Deterministic and per-item distinct. |
| 6 | Embedding cache / query-subgraph mismatch | Inspected encode_text source for caching; ran Q01 and Q24, confirmed different paths | **PASS** — no caching. Q01 path: (PHI_Disclosure→TPO_Exception); Q24 path: 4-hop chain. |
| 7 | Faithfulness aggregation per-item not pooled | Code path trace: per_item_faithfulness_records appended per loop; mean computed post-loop | **PASS** — per-item records verified in JSON output. |

**All 7 bug classes: PASS under real encoder.**

**Residual structural limitation on Bug 2 (Precision ceiling)**: Even with Bug 2 fixed, Precision=1.0 for every item in every run. Reason: extracted triples are drawn by IE from the narrative, which is generated from `included_edges` ⊆ `retrieved_path`, so extracted triples are always a subset of retrieved edges, making `exp_triples ⊆ true_triples` structurally guaranteed. This is not a circularity bug (Bug 2 checks that scores change with different inputs; they do), but it is a ceiling that makes Precision uninformative. Addressed in Task 7.

---

## Task 4: Naive-RAG Per-Hop Instrumentation

### Commit: `06b1a1f`

`eval/eval_harness.py` patched with 12 additive lines only. No existing logic touched.  
Changes: `naive_acc_by_hop` dict; `n_score` per item; `naive_rag_correct` and `vector_rag_correct` in `per_item_baseline_retrievals`; `naive_rag_accuracy_by_hop` in eval_summary JSON.

### Verification — Existing Numbers Unchanged

Post-instrumentation run (real encoder) confirmed identical to all prior runs:
- CG: 100.0%, VR: 87.5%, ECE: 0.0114, F1: 0.9679, t_p: 0.0830

### Newly Visible: Full Three-Way Per-Hop Table

| Hop | n | CompGraphRAG | Vector-RAG | Naive-RAG |
|-----|---|--------------|------------|-----------|
| 1-Hop | 6 | **100.0%** | 83.3% | 66.7% |
| 2-Hop | 6 | **100.0%** | 66.7% | 83.3% |
| 3-Hop | 6 | **100.0%** | 100.0% | 100.0% |
| 4-Hop | 6 | **100.0%** | 100.0% | 100.0% |
| **Overall** | **24** | **100.0%** | **87.5%** | **87.5%** |

Per-item (correct/wrong by system from instrumented JSON):
- Q01 (1-hop): VR=✓, NR=✗
- Q03 (1-hop): VR=✗, NR=✗ (both wrong)
- Q11 (2-hop): VR=✗, NR=✓
- Q12 (2-hop): VR=✗, NR=✗ (both wrong)

Naive-RAG and Vector-RAG both score 87.5% overall but fail **different** items. The two baselines are not redundant: their retrieval strategies (keyword+dense vs. dense-only) produce different error patterns at 1-hop and 2-hop. At 3-hop and 4-hop, both score 100% — confirming the benchmark provides no discriminative signal at those tiers.

Notably: Naive-RAG at 1-hop (66.7%) is **lower** than Vector-RAG (83.3%) under the real encoder — the opposite of the hash-fallback result. Dense-only similarity outperforms keyword+dense hybrid at 1-hop because the 1-hop passages have clear semantic discriminators that the real encoder captures accurately, while keyword overlap adds noise.

---

## Task 5: Power Analysis

### Observed Effect (real encoder, N=24)

- CG: 24/24 = 100%. VR: 21/24 = 87.5%. Per-item differences: 3 ones, 21 zeros.
- Mean difference: **+0.1250**
- Std (ddof=1): **0.3378**
- Cohen's d (paired): **0.3700**
- Current power at n=24: **0.40** (40% — far below 80% threshold)

### Required n for 80% Power

Two-tailed paired t-test, α=0.05:

| n | Power |
|---|-------|
| 24 (current) | 0.40 |
| 50 | 0.73 |
| **60** | **0.80** |
| 70 | 0.86 |
| 100 | 0.96 |

**Answer: n = 60** at the observed pilot effect size (Cohen's d = 0.37).

**Critical caveat**: This analysis is conditioned on the observed pilot effect size being reliable. Given Task 2's finding that the benchmark needs harder distractors, the actual effect size on a properly adversarial benchmark may be smaller. At d=0.20 (a more conservative pre-registration estimate): **n ≈ 197**. The author must decide whether to pre-register the observed pilot d=0.37 or a theoretically motivated, more conservative value.

---

## Task 6: Final Resolution of p=0.664 / p=0.655

### Search Performed

1. `git stash list`: Empty.
2. `git log --all --source --oneline`: Two branches (main + remotes/origin/main), 19 commits total. No orphan branches, no unreachable commits.
3. All tags: only `v0.1.0-pilot-audited`.
4. Filesystem search across entire project directory: No duplicate folders, no `.bak` files, no secondary `eval_results_raw.json`.
5. All committed `eval_results_raw.json` versions across 19 commits: none contain 0.664 or 0.655.
6. Grep across all text files under project root: only hits are the Stage 1 report quoting these values from the task brief.

### Definitive Conclusion

**p=0.664 and p=0.655 do not exist in any recoverable artifact from this codebase. Investigation is complete.**

These values should be removed from consideration entirely and not investigated further. No file, commit, branch, tag, stash, or filesystem artifact contains them. The most likely origin is an informal note from a pre-commit local run whose output was never saved, or the task brief itself introduced these values from an external source not associated with this repo. Since the paper correctly avoids reporting inferential p-values (explicitly labeling the statistical tests as a pre-registered plan for the full-scale study), these values are not relevant to any publication decision.

---

## Task 7: Faithfulness-Precision Fix — Scope Estimate

### What the Current Code Does

`_generate_explanation_narrative_and_triples()` (eval_harness.py lines 121–189):

1. **Generation** (lines 143–171): Selects template sentences for each edge in `retrieved_path`. Intermediate edges are stochastically omitted at rate 0.4. The narrative is generated *from* the retrieved edges.
2. **IE** (lines 175–187): Iterates over `included_edges` (non-omitted edges) and checks whether `edge['source']` and `edge['target']` appear in the narrative. Since the narrative was generated from these same edges, they always appear. Result: `extracted_triples = subset of included_edges`.

`evaluate_faithfulness()` (faithfulness_evaluator.py):
- `true_triples` = full retrieved path edges
- `exp_triples` = extracted triples from IE
- Since `exp_triples ⊆ included_edges ⊆ retrieved_path`, always `exp_triples ⊆ true_triples`
- Therefore: `tp = len(exp_triples)`, `Precision = 1.0` always

Recall is genuinely computed (can fail when edges are omitted), which is why F1 < 1.0 for some items. The bug is specifically that **Precision is structurally 1.0 by construction**, not by measurement.

### What an Independent IE Step Requires

The IE must extract assertions from the **narrative text string alone**, with no access to which edges were retrieved. A misstatement or omission in the narrative would then produce extracted triples that don't match the retrieved path, making Precision < 1.0.

Concrete approach at this project's scale (no new ML component needed):
1. **Regex pattern extractor**: The current narrative templates produce sentences in formats like `"Entity {is linked via|relation} to Entity"` and `"Entity --({relation})--> Entity"`. A regex extractor targeting these patterns can extract (source, relation, target) triples from the text string without consulting the retrieved edges.
2. **Verification**: After extraction, compare to `retrieved_path` as currently done. If a narrative sentence misstates an entity name or uses a paraphrase that doesn't match the stored entity label, Precision drops below 1.0.

This is small enough to implement without spaCy or any additional dependency.

### Work Estimate

**3–5 hours total**:
- Replace lines 175–187 of eval_harness.py with a text-parsing step (~30 lines of regex): **1 hour**
- Add unit tests for the new IE step (must demonstrate Precision < 1.0 on a deliberately bad narrative): **1 hour**
- Re-run harness to measure F1 change: **30 minutes**
- Review and documentation: **30–60 minutes**

Total: 3–5 hours. No new dependency, no architectural change, no model download.

### Would It Change F1 (currently 0.9679)?

**Yes, likely downward slightly — range estimate: 0.85–0.97.**

Currently F1 < 1.0 only from Recall failures (omitted edges). After the fix:
- Precision can fail if the regex extractor cannot parse a template sentence correctly (e.g., mismatched entity label format)
- For the current highly structured templates, Precision will remain high (likely 0.85–1.0)
- F1 will likely decrease by 0.01–0.10 depending on parser error rate

The change makes the metric independently computable and the Precision value meaningfully earned. Even if F1 drops slightly, a defensible 0.90 F1 is stronger evidence than a structurally guaranteed 0.97 F1.

**Recommendation: implement before submission.** The fix is within a single working session. A reviewer who reads `faithfulness_evaluator.py` and `eval_harness.py` will identify the Precision ceiling; the current framing is not defensible on its own.

---

## Open Questions for the Author

1. **Benchmark redesign scope**: Task 2 shows that 3-hop and 4-hop queries are trivially solved by flat retrieval — no hard distractors exist at those tiers. Before the full-scale study, the benchmark construction protocol must specify minimum distractor difficulty requirements (e.g., "each query must have ≥1 distractor passage within 0.10 cosine distance of the query, encoding the opposite determination"). Do you want this added to the dataset construction section of the paper now, or deferred to the full-scale study description?

2. **Power analysis: which effect size to pre-register?** n=60 at pilot d=0.37; n≈197 at conservative d=0.20. A properly pre-registered study cannot use the pilot effect size to power the confirmatory study (that would be circular — the pilot confirms the effect exists, then the full study is powered by the same effect). The pre-registration should use a theoretically motivated, independent estimate of the minimum meaningful effect size. What is your minimum clinically/legally meaningful CG advantage over VR?

3. **Faithfulness IE fix**: 3–5 hours, eliminates a structural validity objection from any technical reviewer, may change F1 slightly downward. Do you want this done before the submission deadline?

4. **CG advantage at 3-hop and 4-hop is zero (both systems score 100%)**: The paper's multi-hop scaling narrative requires CG to beat VR *specifically* at higher hop counts. The current data shows the opposite pattern: VR errors are exclusively at ≤2-hop. This should be framed honestly in the results section — either as "the current benchmark does not have hard enough 3/4-hop items to measure the advantage" (which requires a redesign statement) or as "preliminary evidence suggests the advantage may concentrate at 1–2-hop" (which is a weaker claim than H4/H8 as stated). Which framing is accurate to your intent?

5. **Naive-RAG at 1-hop (66.7%) vs Vector-RAG at 1-hop (83.3%)**: Keyword+dense hybrid performs worse than dense-only at 1-hop under the real encoder. If reported in the paper's comparison table, this needs an explanation. The mechanism is straightforward (dense embeddings are more discriminative than keyword overlap at semantically distinctive 1-hop queries), but it may surprise readers expecting Naive-RAG to always be ≥ Vector-RAG.

6. **The two baselines fail different items (Q01 and Q11 differ between VR and NR)**: This is new information from the Task 4 instrumentation. It means neither baseline is strictly dominated by the other, which complicates the "CG vs. baseline" framing slightly. Should the paper's baseline comparison section note the VR/NR discordance at item level, or report only overall accuracy?
