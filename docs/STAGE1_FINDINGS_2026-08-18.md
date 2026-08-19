# CompGraphRAG — Stage 1 Investigation Findings

**Date**: 2026-08-18  
**Role**: Adversarial technical auditor — investigation and diagnosis only.  
**Instruction**: No files edited (other than writing this report). No commits. No tags. No archiving.  
**Data sources**: Executed code, git history, raw JSON outputs, extracted paper text, and `CompGraphRAG_Phase1_Phase2.md` read in full.

---

## Task 1: `CompGraphRAG_Phase1_Phase2.md` — Full Report

### Q1. Two phases of one program, or two separate efforts?

**Two phases of one single, coherent research program.** The document is titled "Phase 1 & Phase 2 Research Foundation" and is explicitly labeled "a research-supervision working document." Phase 1 is the research background, problem statement, research gap, objectives, research questions (RQ1–RQ6), hypotheses (H1–H8), scope, and proposed framework description. Phase 2 is the literature review — 15 verified papers across 6 categories, a literature matrix, taxonomy, and comparative analysis.

The N=6 pilot and the N=24 study are not separately described in this document at all. The document describes the *research design intent* — it is the foundational planning document, written before any implementation. It does not report results. The N=6 vs N=24 split exists in the implementation artifacts (the paper, the harness, the dataset), not in this planning document.

The relationship between N=6 and N=24, as discernible from this document, is: the document explicitly recommends building "a synthetic/de-identified HIPAA compliance scenario dataset" as the evaluation set, with no fixed size specified. The N=6 pilot and the N=24 expansion are implementation decisions made after this foundation document was written.

### Q2. Which phase's results are meant for publication?

This document does not state which phase's results are meant for submission. It is a planning and literature-review document — not a results document. It explicitly flags several claims as **[VERIFY]** before submission-readiness and specifically notes: "This document is a living draft — several sections (marked below) require an expanded, dedicated literature pass before submission-readiness."

The closest the document comes to a submission statement is its list of "Flags for Follow-Up Before Submission" (four items: expand literature, verify public HIPAA benchmark existence, confirm gap claim against ACM/Springer, grow paper count from 15 to 20-25). None of these flags address result numbers or dataset size.

### Q3. Does it mention `all-MiniLM-L6-v2`, hash pseudo-embedding fallback, or encoder caveats?

**No. Not once.** The document contains zero references to `sentence-transformers`, `all-MiniLM-L6-v2`, hash pseudo-embeddings, any specific embedding model, or any caveat about encoder availability or fallback behavior. It describes the retrieval module conceptually as "dense vector retrieval (for semantic similarity) combined with graph-guided path retrieval" but makes no technical implementation commitment about which encoder to use.

### Q4. Does it mention specific statistical test values (p=0.664/0.655 or any harness p-values)?

**No. Not once.** The document contains no computed p-values, t-statistics, or Wilcoxon results of any kind. It describes statistical tests — paired t-tests, Wilcoxon, TOST, Holm-Bonferroni correction — only as *planned methods* in the hypotheses section (H1–H8), consistent with the paper's framing of statistics as a pre-registered plan. No numerical results appear anywhere in this document.

### Q5. Verbatim quotes (most relevant 2-3 sentences)

**On dataset construction:**
> "Since no public, gold-standard HIPAA multi-hop compliance QA benchmark was verified in this pass, the recommended strategy is to (1) construct a synthetic/de-identified HIPAA compliance scenario dataset grounded in the HIPAA Privacy/Security/Breach Notification Rules, annotated by domain experts, and (2) supplement with general-domain multi-hop QA benchmarks (e.g., those used in HippoRAG/GraphRAG evaluations) for cross-domain baseline comparison."

**On the gap claim (with explicit epistemic flag):**
> "No verified paper in this search pass jointly combines (a) document-intelligence-grade structured extraction, (b) graph-guided hybrid retrieval, and (c) HIPAA-specific compliance determination with an audit-trail explanation layer — this is the specific niche CompGraphRAG targets. **[VERIFY: a broader/final search pass, including ACM DL and Springer directly, is recommended before asserting this as a confirmed, un-filled gap in a submission-ready paper, since absence of evidence in this session's search is not conclusive absence in the literature.]**"

**On evaluation methodology intent:**
> "Human-rated traceability/auditability score (e.g., Likert-scale evaluation by compliance-domain experts), consistent with the trust-quantification direction recommended in recent clinical XAI work" [listed under Recommended Evaluation Metrics for explainability].

---

## Task 2: Encoder Mismatch — Full Investigation

### Step 1: Is `sentence-transformers` in requirements.txt?

**Yes.** `requirements.txt` line 7: `sentence-transformers>=2.2.0`. It is listed as a first-class dependency.

### Step 2: Installation result

`pip install` (system pip) and `pip3 install` both failed with PEP 668 ("externally managed environment" — Homebrew Python). A virtualenv was created at `/tmp/cgrag_venv` and `sentence-transformers` was installed there successfully:

```
Successfully installed sentence-transformers-6.0.0 torch-2.13.0 transformers-5.15.0 [... full dependency tree]
```

### Step 3: Does the code route to the real encoder once installed?

**Yes, automatically — no config flag needed.** The fallback in `retrieval/hybrid_scorer.py` lines 21-30 is:

```python
def _get_encoder(self):
    if self.force_hash_fallback:
        return False
    if self._st_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            self._st_model = False
    return self._st_model
```

When `sentence-transformers` is installed: the `try` block succeeds, `all-MiniLM-L6-v2` loads, and the real encoder is used. When not installed: `ImportError` is silently caught, `self._st_model = False`, and the hash fallback is used. **The fallback is purely a graceful degradation for a missing dependency.** It is not a deliberate test mode. The `--force-hash-fallback` CLI flag exists for isolation testing but is not active in normal runs.

The system-level Python (`python3` on the Mac) has `sentence-transformers` blocked by PEP 668. A virtualenv bypasses this. On the machine where the paper was presumably run, `sentence-transformers` was available — the git commit `536dcb9` is titled "Install real sentence-transformers encoder." This is the reason the paper-era harness (commit `acc5f37`) showed different numbers from the current environment run.

### Step 4: Real-encoder results — three runs (all identical)

The harness was run three times using `/tmp/cgrag_venv/bin/python3 run_demo.py --stats --baselines`. All three runs produced bit-for-bit identical output (the model is deterministic: fixed seeds, cached weights, float32 inference on CPU). **The model download occurs on first run; runs 2 and 3 use the cached model.**

```
Encoder Used: real sentence-transformers (all-MiniLM-L6-v2)
Total Queries Evaluated: 24 (Calibration: 12, Test: 12)

Overall CompGraphRAG Accuracy:   100.0%  (24/24)
Overall Vector RAG Accuracy:      87.5%  (21/24)
Naive-RAG Accuracy:               87.5%  (21/24)

Per-Hop Breakdown:
  1-Hop: CompGraphRAG = 100.0%,  Vector-RAG =  83.3%  (+16.7%)
  2-Hop: CompGraphRAG = 100.0%,  Vector-RAG =  66.7%  (+33.3%)
  3-Hop: CompGraphRAG = 100.0%,  Vector-RAG = 100.0%  ( +0.0%)
  4-Hop: CompGraphRAG = 100.0%,  Vector-RAG = 100.0%  ( +0.0%)

Mean Explanation Faithfulness F1: 0.9679
Expected Calibration Error (ECE): 0.0114

Paired t-test:  mean diff = +0.1250,  t = +1.8127,  p = 0.0830  (not significant at α=0.05)
Wilcoxon:                                            p = 0.0833  (not significant at α=0.05)
```

### Step 5: The exact code path that caused the hash fallback in the prior audit

The prior audit ran `python3 run_demo.py ...` using the system Python, which has `sentence-transformers` blocked by PEP 668. This caused `ImportError` silently caught at `hybrid_scorer.py:28`, setting `self._st_model = False`, so `encode_text()` routed to the word-bucket hash at lines 37-43. **No flag was set; the fallback was triggered purely by the import failure.** No code modification was needed or was made to switch encoders — only the Python environment changed.

---

## Task 3: Diagnosis of p-value Discrepancy (Paper vs. Harness)

### What the task prompt states as "paper PDF p-values" (p=0.664, p=0.655)

These values **do not appear in the paper (`CompGraphRAG_Paper_extracted.txt` or `CompGraphRAG_Paper.docx`)**, in the `CompGraphRAG_Phase1_Phase2.md` document, or anywhere in the git history in any `eval_results_raw.json`. After exhaustive search (grep on extracted text, strings on binary files, inspection of every commit's `results/eval_results_raw.json`), these specific values cannot be located in any repo artifact.

**Finding**: The paper's Section VI-D explicitly states: *"Given the pilot's N = 6 sample size, these tests are reported here as the pre-registered confirmatory-analysis plan rather than as results computed on the pilot data, since inferential statistics computed on six paired observations would not support the claims these tests are designed to make."* The paper does **not** report any inferential p-values as results. The values p=0.664 / p=0.655 are **unverified in any repo artifact**. They cannot be matched to any code path, dataset configuration, or git commit found in this checkout.

### The four p-value sets that do exist, with their sources

| Source | CG acc | VR acc | n | t-stat | t_p | wilcoxon_p | Origin |
|--------|--------|--------|---|--------|-----|------------|--------|
| `acc5f37` eval_results_raw.json | 100.0% | 66.7% | 24 | 3.3912 | 0.00251 | 0.00468 | Old N=24 harness, before bug-fix commits. This is the "compgraphrag_research_paper_guide" era. |
| `e21a8a6` eval_results_raw.json | 100.0% | 54.2% | ≥24 | 4.4115 | 0.00020 | 0.00091 | Earlier commit, different VR accuracy (higher CG advantage). |
| Hash-fallback runs (current system Python, 3 runs) | 70.8% | 79.2% | 24 | −0.6244 | 0.5385 | 0.5271 | Post-audit, hash encoder, current code. |
| **Real-encoder runs (venv, 3 runs)** | **100.0%** | **87.5%** | **24** | **+1.8127** | **0.0830** | **0.0833** | Current code, with `all-MiniLM-L6-v2` — **canonical current execution**. |

### Diagnosis

The harness compares `cg_scores` vs `vec_scores` — binary per-item accuracy arrays for CompGraphRAG vs. Vector-RAG across all 24 items. The `paired_difference_test()` function is straightforward `scipy.stats.ttest_rel` + `scipy.stats.wilcoxon`. There are no alternative dataset slices, no flag-gated alternate comparison, no code path that would produce p=0.664 / p=0.655 from any currently-existing configuration.

**Best-supported hypothesis**: The values p=0.664 and p=0.655 do not exist in the canonical paper and cannot be reproduced from any configuration in this checkout. They may originate from an even earlier local run not committed to this repo (the initial commit `205b086` existed before the bug-fix series), or they may be an incorrect citation of the values in the task brief itself. The paper correctly avoids reporting inferential p-values, labeling all statistical tests as a pre-registered plan.

**What cannot be determined**: Whether these values come from an uncommitted local run, a private workspace version of the code, or are simply erroneous references in the task description. This is flagged as an open question below.

---

## Task 4: Dataset Provenance Verification

### Item count and distribution

`datasets/hipaa_gold_dataset.json` contains exactly **24 items**: 6 at each of hop counts 1, 2, 3, 4. This matches the claimed distribution.

| Hop | Items | IDs |
|-----|-------|-----|
| 1-Hop | 6 | Q01–Q06 |
| 2-Hop | 6 | Q07–Q12 |
| 3-Hop | 6 | Q13–Q18 |
| 4-Hop | 6 | Q19–Q24 |

### Are items synthetic?

**Yes, all 24 items are clearly synthetic.** Every entity name is a generic placeholder (`CoveredEntity_A`, `CloudVendor_B`, `BusinessAssociate_1`, `SubcontractorHost_2`, `ITContractor_M`, `MobileApp_Vendor`, `Regional_HIE`, `StateHealthDept`, `HospitalSystem`, etc.). No real organization names, no real personal names, no real patient identifiers, no real case-law citations, no real incident numbers.

Regulatory citations are to 45 CFR sections (`§164.502`, `§164.506`, `§164.402`, `§164.524`, `§164.312(e)`, `§164.310`) which are the real HIPAA statutory references — but these are public law, not PHI, and do not constitute real-entity identifiers.

### Does any item reference real entities?

No item references a real named organization, person, or patient. The closest item to a real-world reference is Q20 ("Multi-site clinical trial sharing pseudonymized genomic data across IRB-approved institutions") and Q24 ("transmitting de-identified epidemiological records to the CDC during a national health emergency") — but these use generic role labels (`MultiSiteTrial`, `CDC_Mandate`, `StateHealthDept`), not real entity names.

**Verdict**: The dataset is synthetic, adequately de-identified, and consistent with the paper's constraint statement ("No live PHI will be used in academic evaluation; synthetic or de-identified compliance scenarios will be constructed instead").

---

## Task 5: Naive-RAG Three-Way Comparison

### Confirmation across all three hash-fallback runs

All three hash-fallback runs (prior audit) produced identical output. The ranking **Naive-RAG (83.3%) > Vector-RAG (79.2%) > CompGraphRAG (70.8%)** is confirmed stable across all three runs.

### Full three-way per-hop table — hash-fallback encoder

The `all_baselines_summary` in `results/eval_results_raw.json` stores Naive-RAG overall accuracy only (not per-hop). The per-hop breakdown was computed directly by running `baselines.runner` on the dataset, but a code-path issue (baseline runner's standalone invocation returns `REQUIRES-REVIEW` for all items when called outside the full harness context, which yields 0% outside the harness). The per-hop Naive-RAG breakdown **cannot be independently reconstructed** from the stored JSON or standalone invocation — it would require a code modification to track it inside `run_evaluation`. The per-hop data stored in the harness JSON is only for CompGraphRAG and Vector-RAG.

**What is available (confirmed, hash-fallback, 3 runs):**

| Model | 1-Hop | 2-Hop | 3-Hop | 4-Hop | Overall |
|-------|-------|-------|-------|-------|---------|
| Naive-RAG | *not tracked per-hop* | *not tracked per-hop* | *not tracked per-hop* | *not tracked per-hop* | **83.3%** |
| Vector-RAG | 66.7% | 66.7% | 83.3% | 100.0% | **79.2%** |
| CompGraphRAG | 83.3% | 50.0% | 66.7% | 83.3% | **70.8%** |

The per-hop Naive-RAG breakdown does not exist in the stored output. This is a structural gap in the harness's output schema: `naive_rag_correct` and `vector_rag_correct` are not stored per-item in `per_item_baseline_retrievals` (only the retrieved passage text is stored). The harness would need a code change to track Naive-RAG per-hop.

### Three-way comparison under real-encoder runs (all 3 identical):

| Model | 1-Hop | 2-Hop | 3-Hop | 4-Hop | Overall |
|-------|-------|-------|-------|-------|---------|
| Naive-RAG | *not tracked per-hop* | *not tracked per-hop* | *not tracked per-hop* | *not tracked per-hop* | **87.5%** |
| Vector-RAG | 83.3% | 66.7% | 100.0% | 100.0% | **87.5%** |
| CompGraphRAG | 100.0% | 100.0% | 100.0% | 100.0% | **100.0%** |

Under the real encoder: CompGraphRAG leads overall. Naive-RAG and Vector-RAG tie at 87.5% overall. **The Naive-RAG-leads-everything ranking exists only under the hash-fallback encoder.** Under the real encoder, the ranking reverses to CompGraphRAG > Naive-RAG = Vector-RAG.

---

## Summary: What Changes Between Hash-Fallback and Real-Encoder

| Metric | Hash-Fallback (system python3) | Real Encoder (venv, all-MiniLM-L6-v2) |
|--------|-------------------------------|----------------------------------------|
| CompGraphRAG Overall | **70.8%** | **100.0%** |
| Vector-RAG Overall | 79.2% | 87.5% |
| Naive-RAG Overall | 83.3% | 87.5% |
| CG leads overall? | **NO** (trails both baselines) | **YES** |
| H4/H8 monotonic scaling? | NOT supported | Partially supported (1-hop +16.7%, 2-hop +33.3%, 3-hop 0%, 4-hop 0%) |
| ECE | 0.1469 | **0.0114** |
| Faithfulness F1 | 0.9798 | 0.9679 |
| Paired t_p | 0.5385 (not sig.) | 0.0830 (not sig. at α=0.05) |
| Wilcoxon_p | 0.5271 (not sig.) | 0.0833 (not sig. at α=0.05) |

The cosine-similarity component of the hybrid score (weight α=0.40) is computed using 64-dimensional word-bucket hash vectors under the fallback, and 384-dimensional neural embeddings under the real encoder. The hash vectors are poorly discriminative (many queries map to overlapping buckets), causing the graph-path component (weight β=0.50) to be swamped by noise from the dense score, which scrambles path ranking. Under real embeddings, the dense score correctly discriminates relevant passages, making the full hybrid score function as designed — and CompGraphRAG's graph-path retrieval advantage materializes.

---

## Open Questions for the Author

1. **Which encoder state is authoritative?** The paper's N=6 pilot results were produced under some execution environment. If that environment had `sentence-transformers` installed (commit `536dcb9` says "Install real sentence-transformers encoder"), the N=6 results were produced with the real encoder. If not, they were produced with hash-fallback, and the pilot numbers in the paper may themselves reflect hash-fallback noise. **Which Python environment was used to produce the pilot results reported in the paper?**

2. **Where do p=0.664 and p=0.655 come from?** These values do not appear in any file in this repo — not in the extracted paper text, not in any `eval_results_raw.json` across any git commit, not in `CompGraphRAG_Phase1_Phase2.md`. Was this a reference to a version of the code that was never committed, a local run whose output was not saved, or a mistake in the task brief? **Can you point to the file or execution session that produced these specific values?**

3. **The real-encoder N=24 results are still not statistically significant (p=0.083 for both tests at α=0.05).** CompGraphRAG leads 100% vs 87.5% overall, but the per-item variance on 24 binary observations is large enough that neither test clears the threshold. The paper's plan calls for a sample-size-determined full study. **Has a power analysis been conducted to determine what N is needed for the pre-registered tests to have 80% power to detect the observed effect size?**

4. **Naive-RAG per-hop breakdown is not tracked.** The harness does not store per-hop Naive-RAG accuracy. Under the real encoder, both Naive-RAG and Vector-RAG score 87.5% overall — but their per-hop breakdown may differ, and the comparison to CompGraphRAG's per-hop profile is material for the H4/H8 claim. **Should the harness be instrumented to track Naive-RAG per-hop so the full comparison exists?**

5. **The H4/H8 claim is only partially supported under the real encoder.** CompGraphRAG leads at 1-hop (+16.7%) and 2-hop (+33.3%) but not at 3-hop (0%) or 4-hop (0%, where both CG and VR score 100%). This is because 3-hop and 4-hop items appear to be easier under the real encoder — both systems get them all right. The "monotonically growing advantage" hypothesis requires non-zero baseline error at each hop tier, otherwise the marginal benefit is trivially zero. **Is this a dataset calibration issue (4-hop items not hard enough for Vector-RAG) or an artifact of the specific 24-item set?**

6. **The faithfulness precision structural issue (flagged in prior audit as an open limitation) was not addressed.** Precision = 1.0 always because extracted triples are drawn from retrieved edges. This is still present in the current code. **Is this limitation acknowledged anywhere in the paper draft, and is a redesign of the IE extraction step planned?**
