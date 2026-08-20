# CompGraphRAG — Locked Results (2026-08-20)
**Supersedes**: `docs/LOCKED_RESULTS_2026-08-18.md` — see that file for the prior source of truth and why it was superseded.  
**Commit**: `b6ebec2` (Stage 6 ground truth restore)  
**Date locked**: 2026-08-20  
**Reproduced**: 3 independent runs, identical output.

---

## Why This Supersedes the Prior Lock

The 2026-08-18 lock reported `CG=100.0%, VR=87.5%, p=0.083` based on numbers that were not reproducible at the time of writing. Stage 6 identified two bugs that had been silently degrading the measurement:

1. A Python namespace collision (`datasets/` local package shadowing the HuggingFace `datasets` library) that silently activated the hash-encoder fallback instead of the real sentence-transformers model.
2. No model-revision pin, meaning the encoder behavior was tied to whatever library version happened to be installed.

After fixing both bugs, the harness now produces CG=100.0% with the real encoder — matching the number that was always claimed but had never been produced reproducibly. The fixes are documented in [`docs/STAGE6_GROUND_TRUTH_RESTORED_2026-08-20.md`](file:///Volumes/Johnys%20Extreme%20Pro/Johny%27s%20MiniX/Downloads/o1aprofileevaluationwithjinee/Research%20Papers/CompGraphRAG%20%20RP1/docs/STAGE6_GROUND_TRUTH_RESTORED_2026-08-20.md).

---

## Canonical Results (Real Encoder, Three Verified Runs)

### Encoder

| Parameter | Value |
|---|---|
| Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Revision (pinned) | `1110a243fdf4706b3f48f1d95db1a4f5529b4d41` |
| Embedding dim | 384 |
| Library | sentence-transformers 5.6.1 |

### Overall Accuracy

| System | Correct | Total | Accuracy |
|---|---|---|---|
| **CompGraphRAG** | **24** | **24** | **100.0%** |
| Vector-RAG baseline | 21 | 24 | 87.5% |
| Naive-RAG baseline | 21 | 24 | 87.5% |

### Per-Hop Accuracy

| Hop Count | N | CompGraphRAG | Vector-RAG | Naive-RAG | CG Margin |
|---|---|---|---|---|---|
| 1-Hop | 6 | **100.0%** | 83.3% | 66.7% | +16.7% |
| 2-Hop | 6 | **100.0%** | 66.7% | 83.3% | +33.3% |
| 3-Hop | 6 | **100.0%** | 100.0% | 100.0% | 0.0% |
| 4-Hop | 6 | **100.0%** | 100.0% | 100.0% | 0.0% |
| **Overall** | **24** | **100.0%** | **87.5%** | **87.5%** | **+12.5%** |

> [!IMPORTANT]
> The 3-hop and 4-hop marginal benefit is 0.0% because both baselines also achieve 100% at those tiers. The measurable advantage is concentrated in the ≤2-hop items (3 discordant items: Q07, Q09, Q11, all 2-hop). This is a benchmark design limitation noted in the paper.

### Statistical Validation

| Test | Statistic | p-value | Significant at α=0.05? |
|---|---|---|---|
| Paired t-test | t=1.803 | **p=0.0830** | No |
| Wilcoxon signed-rank | W=15.0 | **p=0.0833** | No |
| Holm-Bonferroni adjusted | — | [0.0830, 1.0] | No |
| Cohen's d | d=0.378 | — | Small-to-medium effect |

Power analysis (pre-registered, n=68 required for 80% power at α=0.05, d=0.4):  
Current n=24 provides ~42% power. The result is directionally consistent with the H1 hypothesis (CG > VR) but does not reach statistical significance on this sample.

### Entity Linking Metrics

| Metric | Value |
|---|---|
| Precision | 0.219 |
| Recall | 0.844 |
| F1 | 0.348 |

High recall, low precision: the linker correctly finds gold nodes but also links many non-gold nodes. The low precision does not impair path selection because the grounding boost is multiplicative (irrelevant linked nodes do not cancel correct signal) rather than filtering.

### Faithfulness

| Metric | Value |
|---|---|
| Mean Faithfulness F1 | **0.9679** |
| IE extraction method | Text-only regex (Pattern A/B/C) |
| Seed strategy | Item-ID MD5 deterministic hash |

### Calibration

| Metric | Value |
|---|---|
| Expected Calibration Error (ECE) | **0.0114** |
| Conformal predictor α | 0.10 |

---

## Generalization on Novel Queries (Post-Fix)

Five novel HIPAA questions not present in the benchmark, evaluated with the real encoder:

| ID | Scenario | Gold | Predicted | Correct |
|---|---|---|---|---|
| N01 | Hospital billing → unencrypted FTP → overseas vendor | NON-COMPLIANT | NON-COMPLIANT | ✓ |
| N02 | Physician shares medication list with insurer for prior auth | COMPLIANT | COMPLIANT | ✓ |
| N03 | Genetic company shares anonymized sequences with university | COMPLIANT | COMPLIANT | ✓ |
| N04 | Cloud provider without BAA hosts encrypted records | NON-COMPLIANT | NON-COMPLIANT | ✓ |
| N05 | EMT shares vital signs with trauma center during transport | COMPLIANT | COMPLIANT | ✓ |

**Novel accuracy: 5/5 (100%)** — full-phrase "emergency medical technician" (without the "EMT" acronym) is a documented gap in the synonym table and would fail to link `EMT_Provider`. The N05 query here uses "EMT" explicitly.

**Combined generalization rate (24 benchmark + 5 novel): 29/29 (100%)** under the real encoder.

> [!NOTE]
> The synonym table was curated from benchmark vocabulary (see OQ-5 in Stage 6 report). 100% on 29 items does not constitute evidence of general-purpose generalization. It is an honest measurement on the combined set as currently defined.

---

## Reproduce

```bash
# From repo root at commit b6ebec2 or later
python3 -c "
from eval.eval_harness import CompGraphRAGEvaluator
r = CompGraphRAGEvaluator('datasets/hipaa_gold_dataset.json').run_evaluation()
print(f'CG={r[\"overall_compgraphrag_accuracy\"]:.4f}  VR={r[\"overall_vector_rag_accuracy\"]:.4f}')
print(f'p={r[\"statistical_validation\"][\"paired_difference\"][\"t_p_value\"]:.4f}')
"
# Expected output:
# CG=1.0000  VR=0.8750
# p=0.0830
```

Three runs produce identical output. If the CG or VR value changes, one of the following has occurred:

1. The `benchmark_datasets/` package has been renamed or deleted (re-activating hash fallback)
2. The ST model revision pin has been removed or changed
3. The dataset or corpus has been modified
4. The rule engine or scoring weights have changed

The regression test `tests/test_entity_linker.TestEvalHarnessAccuracyRegression.test_harness_accuracy_pinned` will catch any of these.

---

## Limitations and Disclosures (Unchanged from Prior Lock)

- **Statistical significance**: The result is not significant at α=0.05 (p=0.083). A pre-registered n=68 study is required for 80% power.
- **Benchmark design**: No measurable CG advantage at 3-hop and 4-hop; all three systems achieve 100% there.
- **Synonym table**: Expanded entries in `baff345` were curated from benchmark vocabulary (see Stage 6 OQ-5). General-purpose claim is limited.
- **Multiplier `0.4`**: Chosen without documented ablation; not independently justified.
- **Sample size**: n=24 is too small for the significance framing used in the paper without the power caveat.

---

*Previous locked results: [`LOCKED_RESULTS_2026-08-18.md`](file:///Volumes/Johnys%20Extreme%20Pro/Johny%27s%20MiniX/Downloads/o1aprofileevaluationwithjinee/Research%20Papers/CompGraphRAG%20%20RP1/docs/LOCKED_RESULTS_2026-08-18.md) — superseded by this file.*
