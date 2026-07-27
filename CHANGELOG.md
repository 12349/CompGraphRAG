# Changelog

All notable changes to the CompGraphRAG project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-pilot] - 2026-07-27

### Added
- **Formal Hybrid Retrieval Engine**: $\text{score}(x|q) = \alpha \cdot \cos(q,x) + \beta \cdot \text{GraphPathScore} + \gamma \cdot \text{Authority}$ with path decay $\lambda^h$.
- **Neuro-Symbolic Rule Check Layer**: Pre-generation gatekeeper evaluating 45 CFR §164.502(e) BAA requirements and §164.506 TPO exceptions.
- **Split Conformal Uncertainty Quantification**: Calibrated confidence sets $C(q)$ with automatic routing to human review.
- **Audit-Grade Explanation Faithfulness Metric**: Precision/Recall calculation over justification subgraphs $\pi$.
- **Expanded Benchmark Dataset**: Scaled from 6 to 24 multi-hop HIPAA queries across 1-hop, 2-hop, 3-hop, and 4-hop complexity.
- **Pre-Registered Statistical Validation Suite**: Paired t-tests, Wilcoxon signed-rank tests, TOST equivalence testing, Holm-Bonferroni corrections, and ECE reliability tables.
- **Baselines Suite**: Unified runner for Vector-RAG, Naive RAG, GraphRAG, LightRAG, and HippoRAG.
- **Engineering & CI Hygiene**: Unit test suite (`tests/`), GitHub Actions CI workflow, `CITATION.cff`, and raw result logging (`results/eval_results_raw.json`).
