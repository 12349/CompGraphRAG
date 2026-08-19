# CompGraphRAG — Locked Results

**Date locked**: 2026-08-18  
**Commit at lock**: `9c35c4e` (after faithfulness IE fix)  
**Encoder**: `real sentence-transformers (all-MiniLM-L6-v2)` via `/tmp/cgrag_venv`  
**Harness**: `python3 run_demo.py --stats --baselines` — 3 deterministic runs, identical output  
**Single source of truth**: Every number in the paper, README, and (when updated) trade article must match this file exactly. Any discrepancy is a bug, not a stylistic choice.

---

## Table 1: Overall and Per-Hop Accuracy (N=24)

| Hop Tier | n | CompGraphRAG | Vector-RAG | Naive-RAG | CG Marginal vs VR |
|:---------|:-:|:------------:|:----------:|:---------:|:-----------------:|
| 1-Hop    | 6 | **100.0%**   | 83.3%      | 66.7%     | +16.7%            |
| 2-Hop    | 6 | **100.0%**   | 66.7%      | 83.3%     | +33.3%            |
| 3-Hop    | 6 | **100.0%**   | 100.0%     | 100.0%    | 0.0%              |
| 4-Hop    | 6 | **100.0%**   | 100.0%     | 100.0%    | 0.0%              |
| **Overall** | **24** | **100.0%** | **87.5%** | **87.5%** | **+12.5%** |

> GraphRAG, LightRAG, HippoRAG: **NOT MEASURED** (not installed). All comparisons are against Vector-RAG and Naive-RAG only.

---

## Table 2: Explanation Faithfulness F1 — Per-Item Distribution

Encoder: real `all-MiniLM-L6-v2`. IE extractor: text-only regex (post-fix, commit `9c35c4e`).

| Item | Hop | Precision | Recall | F1 |
|------|-----|-----------|--------|----|
| Q01-1HOP | 1 | 1.0000 | 1.0000 | 1.0000 |
| Q02-1HOP | 1 | 1.0000 | 1.0000 | 1.0000 |
| Q03-1HOP | 1 | 1.0000 | 1.0000 | 1.0000 |
| Q04-1HOP | 1 | 1.0000 | 1.0000 | 1.0000 |
| Q05-1HOP | 1 | 1.0000 | 1.0000 | 1.0000 |
| Q06-1HOP | 1 | 1.0000 | 1.0000 | 1.0000 |
| Q07-2HOP | 2 | 1.0000 | 1.0000 | 1.0000 |
| Q08-2HOP | 2 | 1.0000 | 1.0000 | 1.0000 |
| Q09-2HOP | 2 | 1.0000 | 1.0000 | 1.0000 |
| Q10-2HOP | 2 | 1.0000 | 1.0000 | 1.0000 |
| Q11-2HOP | 2 | 1.0000 | 1.0000 | 1.0000 |
| Q12-2HOP | 2 | 1.0000 | 1.0000 | 1.0000 |
| Q13-3HOP | 3 | 1.0000 | 1.0000 | 1.0000 |
| Q14-3HOP | 3 | 1.0000 | 1.0000 | 1.0000 |
| Q15-3HOP | 3 | 1.0000 | 1.0000 | 1.0000 |
| Q16-3HOP | 3 | 1.0000 | 1.0000 | 1.0000 |
| Q17-3HOP | 3 | 1.0000 | 1.0000 | 1.0000 |
| Q18-3HOP | 3 | 1.0000 | **0.6667** | **0.8000** |
| Q19-4HOP | 4 | 1.0000 | **0.7500** | **0.8571** |
| Q20-4HOP | 4 | 1.0000 | 1.0000 | 1.0000 |
| Q21-4HOP | 4 | 1.0000 | 1.0000 | 1.0000 |
| Q22-4HOP | 4 | 1.0000 | **0.7500** | **0.8571** |
| Q23-4HOP | 4 | 1.0000 | **0.7500** | **0.8571** |
| Q24-4HOP | 4 | 1.0000 | **0.7500** | **0.8571** |

**Mean F1: 0.9679** (19/24 items = 1.0; 5 items < 1.0 due to stochastic intermediate-edge abstraction)  
**Mean Precision: 1.0000** (Precision=1.0 for all items — connector templates are regex-parseable, but structural guarantee is broken: unit test proves Precision=0.0 on corrupted input)  
**Mean Recall: 0.9271** (Recall < 1.0 for 5 items with stochastically omitted intermediate edges)

---

## Table 3: Statistical Validation

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Paired t-test mean diff | +0.1250 | CG − VR per-item difference |
| t-statistic | 1.8127 | |
| Paired t-test p-value | **0.0830** | Not significant at α=0.05 |
| Wilcoxon signed-rank p-value | **0.0833** | Not significant at α=0.05 |
| Cohen's d (paired) | **0.3700** | Medium effect size |
| Current study power (n=24) | **40%** | Substantially underpowered |
| n needed for 80% power (d=0.37) | **60** | At observed pilot effect size |
| n needed for 80% power (d=0.20) | **~197** | At conservative pre-registration estimate |
| ECE | **0.0114** | Well-calibrated |
| Holm-Bonferroni adjusted p-values | [0.0830, 1.0] | Not significant |

**On p=0.664 / p=0.655**: These values do not exist in any recoverable artifact — no committed JSON, no source file, no paper text, no stash, no branch, no backup file. Investigated exhaustively. Permanently retired from consideration.

---

## Table 4: Discordant Items (CG correct, VR wrong)

| ID | Hop | Gold | CG | VR | NR | Mechanism |
|----|-----|------|----|----|----|-----------|
| Q03-1HOP | 1 | COMPLIANT | ✓ | ✗ | ✗ | Entity linker surfaces `JudicialSubpoena_Exception`; VR retrieves p05 (law-enforcement passage) via "subpoena" keyword overlap |
| Q11-2HOP | 2 | NON-COMPLIANT | ✓ | ✗ | ✓ | `UnencryptedEmail` entity triggers security-violation path; VR retrieves billing-COMPLIANT passage by topic match |
| Q12-2HOP | 2 | COMPLIANT | ✓ | ✗ | ✗ | `DeIdentifiedData` entity triggers HIPAA inapplicability; VR lands on BAA-required passage at near-tie cosine gap (0.013) |

---

## Table 5: Benchmark Validity Notes

| Observation | Value | Implication |
|-------------|-------|-------------|
| Q20 cosine sim (query to correct passage) | 0.8889 | Near-paraphrase; trivially solved by dense retrieval |
| Queries with cosine gap > 0.15 to correct passage | 12/24 | Correct passage is clear outlier for these items |
| VR accuracy at 3-hop | 100.0% | No discriminative signal at this tier |
| VR accuracy at 4-hop | 100.0% | No discriminative signal at this tier |
| Number of hard distractor passages | 2 (d01, d02) | Both about unrelated topics; not tier-specific hard distractors |

The H4/H8 hypothesis (monotonically growing CG advantage with hop count) is **not testable on this benchmark**. Both baselines achieve 100% at 3-hop and 4-hop. The 3 CG/VR discordant items are all at ≤2-hop. This is a benchmark design limitation, not evidence that the hypothesis is false.

---

## Faithfulness Fix Note (Task 1, Stage 3)

**Before fix (pre-commit `9c35c4e`)**: IE extracted triples by iterating over `included_edges` and checking if entity names appeared in the narrative. Since the narrative was generated FROM included_edges, they always appeared → Precision=1.0 structurally guaranteed, not measured.

**After fix**: IE runs regex over narrative TEXT ONLY. Three patterns match the three connector templates. A misstatement would produce an extracted triple that doesn't match `retrieved_path`, correctly reducing Precision below 1.0. Unit test `test_precision_fails_on_corrupted_entity_name` proves Precision=0.0 on a deliberately corrupted entity name.

**Observed post-fix F1: 0.9679** — unchanged from pre-fix. Reason: all three connector templates produce text that is exactly regex-parseable, so Precision remains 1.0 for all current generated narratives. Recall was already the limiting factor (stochastic intermediate-edge abstraction in 3-hop and 4-hop items). The fix makes the metric independently computable and defensible; it does not change the numerical output on current data.

---

## Change Log Since Last Lock

| Commit | Description | Effect on numbers |
|--------|-------------|-------------------|
| `06b1a1f` | Add Naive-RAG per-hop tracking (additive, Stage 2 Task 4) | None — instrumentation only |
| `9c35c4e` | Faithfulness IE fix: text-only regex extractor | F1 unchanged at 0.9679 |
