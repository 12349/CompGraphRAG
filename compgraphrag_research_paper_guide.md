# CompGraphRAG Research Paper Guide — NOTICE

> [!CAUTION]
> The numbers that previously appeared in this file's benchmark table were fabricated and have been replaced by this notice following the adversarial technical audit of 2026-08-18.
>
> The pre-audit version of this document (with its false statistics) has been preserved verbatim at `docs/archive/compgraphrag_research_paper_guide_PRE_AUDIT.md` as an audit trail artifact.

## What Replaced It

For **verified empirical results**, see:
- `README.md` — benchmark table from 3 real harness runs
- `results/eval_results_raw.json` — raw harness output
- `docs/AUDIT_LOG_2026-08-18.md` — full discrepancy report

For **the canonical paper** (with its honest N=6 pilot framing), see:
- `CompGraphRAG_Paper.docx` (repo root)
- `CompGraphRAG_Paper_extracted.txt` (repo root)

## Verified Real Numbers (N=24, real `all-MiniLM-L6-v2` encoder)

> Locked to `docs/LOCKED_RESULTS_2026-08-18.md` (commit `9c35c4e`). All canonical numbers below are real-encoder figures.

| Metric | Value |
|--------|-------|
| CompGraphRAG Overall Accuracy | **100.0%** (24/24) |
| Vector-RAG Overall Accuracy | **87.5%** (21/24) |
| Naive-RAG Overall Accuracy | **87.5%** (21/24) |
| 1-Hop: CG=100.0%, VR=83.3% | CG leads (+16.7%) |
| 2-Hop: CG=100.0%, VR=66.7% | CG leads (+33.3%) |
| 3-Hop: CG=100.0%, VR=100.0% | Tied — no signal |
| 4-Hop: CG=100.0%, VR=100.0% | Tied — no signal |
| Faithfulness F1 (mean) | **0.9679** (post-fix, IE text-only) |
| ECE | **0.0114** |
| Paired t-test | t=+1.8127, p=0.0830 (not significant at α=0.05) |
| Wilcoxon | p=0.0833 (not significant at α=0.05) |
| Cohen's d | 0.37 (medium effect) |
| Study power (n=24) | 40% — underpowered |
| n for 80% power | 60 (at d=0.37) |
| H4/H8 monotonic scaling | **NOT TESTABLE** on current benchmark |
| GraphRAG / LightRAG / HippoRAG | **NOT MEASURED** |

> **Retired numbers (hash-encoder, do not use)**: CG=70.8%, VR=79.2%, F1=0.9798, ECE=0.1469. These came from the hash-bucket pseudo-embedding fallback and are preserved only in audit-trail documents.



The mathematical formulations (scoring equation, conformal predictor, faithfulness F1) in the original document remain correct and are unchanged in the archived version.
