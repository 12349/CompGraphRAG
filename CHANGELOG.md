# Changelog

All notable changes to the CompGraphRAG framework will be documented in this file.

## [v0.1.0-pilot] - 2026-07-27

### Added
- **Scaled Benchmark Dataset:** Expanded `hipaa_gold_dataset.json` to 24 multi-hop queries across 1-hop, 2-hop, 3-hop, and 4-hop compliance paths.
- **Pre-Registered Statistical Validation:** Integrated paired t-test, Wilcoxon signed-rank test, TOST equivalence testing, Holm-Bonferroni p-value adjustment, and ECE calculation into `eval_harness.py` and `run_demo.py --stats`.
- **Dense Vector Encoder & Hybrid Scorer Integration:** Added `SentenceTransformer` dense text embedding and cosine similarity scoring with bag-of-words fallback to `retrieval/hybrid_scorer.py`.
- **External Baseline Suite:** Added `baselines/runner.py` wrapper for Vector-RAG, Naive RAG, GraphRAG, LightRAG, and HippoRAG.
- **Raw Results Artifact:** Created `results/eval_results_raw.json` storing automated benchmark execution metrics.
- **Unit Testing Suite & CI:** Created `tests/` directory with 8 unit tests and GitHub Actions workflow `.github/workflows/ci.yml`.
- **Annotation Protocol & Citation:** Created `docs/annotation_protocol.md` and `CITATION.cff`.
