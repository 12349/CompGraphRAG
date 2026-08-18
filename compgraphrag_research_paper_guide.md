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

## Verified Real Numbers (N=24, hash-embedding encoder)

| Metric | Value |
|--------|-------|
| CompGraphRAG Overall Accuracy | **70.8%** (17/24) |
| Vector-RAG Overall Accuracy | **79.2%** (19/24) — Vector-RAG leads |
| Naive-RAG Overall Accuracy | **83.3%** (20/24) |
| 1-Hop: CG=83.3%, VR=66.7% | CG leads (+16.7%) |
| 2-Hop: CG=50.0%, VR=66.7% | VR leads (−16.7%) |
| 3-Hop: CG=66.7%, VR=83.3% | VR leads (−16.7%) |
| 4-Hop: CG=83.3%, VR=100.0% | VR leads (−16.7%) |
| Faithfulness F1 (mean) | **0.9798** |
| ECE | **0.1469** |
| Paired t-test | t=−0.6244, p=0.5385 **(NOT significant)** |
| Wilcoxon | p=0.5271 **(NOT significant)** |
| H4/H8 monotonic scaling | **NOT supported** |
| GraphRAG / LightRAG / HippoRAG | **NOT MEASURED** |

The mathematical formulations (scoring equation, conformal predictor, faithfulness F1) in the original document remain correct and are unchanged in the archived version.
