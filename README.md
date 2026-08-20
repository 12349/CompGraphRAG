# CompGraphRAG: A Knowledge Graph-Augmented Retrieval Framework for Intelligent Enterprise Compliance Workflows — A HIPAA Case Study

**Author**: Mahaboob Johny Shaik (Independent Researcher, Denton, TX, USA. Email: `Mahaboobshaikusa@gmail.com`)

---

## 🏛️ Overview
CompGraphRAG is an open-source, knowledge-graph-augmented hybrid retrieval and reasoning framework designed for high-stakes enterprise compliance workflows (with HIPAA as a case study). It unifies:

1. **Formal Hybrid Retrieval Scoring Engine**: $\text{score}(x|q) = \alpha \cdot \cos(q,x) + \beta \cdot \text{GraphPathScore} + \gamma \cdot \text{Authority}$.
2. **Neuro-Symbolic Pre-Generation Rule Engine**: Evaluates 45 CFR regulatory exception carve-outs prior to generator invocation.
3. **Audit-Grade Explainability**: Returns machine-readable justification subgraphs ($\pi$) and natural language walks evaluated via quantitative faithfulness metrics.
4. **Split Conformal Uncertainty Quantification**: Produces calibrated confidence sets $C(q)$ with automatic safety routing for low-confidence decisions.
5. **Interactive Web Suite & Palantir Control Room**: A live, serverless web audit interface.

---

## 📊 Quickstart & Execution

### 1. Installation
```bash
git clone https://github.com/12349/CompGraphRAG.git
cd CompGraphRAG
pip install -r requirements.txt
```

### 2. Run Unit Tests
```bash
python3 -m unittest discover tests
```

### 3. Run Benchmark Harness & Pre-Registered Statistics
```bash
python3 run_demo.py --stats --baselines
```

Raw evaluation metrics will be written automatically to `results/eval_results_raw.json`.

---

## 📂 Repository Structure

```
compgraphrag/
├── README.md                 (quickstart, architecture spec, code availability)
├── CITATION.cff              (citation metadata)
├── CHANGELOG.md              (version history)
├── requirements.txt          (python dependencies)
├── run_demo.py               (main CLI launcher & evaluation runner)
├── schema/                   (OWL/Turtle & JSON-LD HIPAA TBox ontologies)
├── prompts/                  (extraction, generation, and faithfulness prompts)
├── retrieval/                (hybrid scorer, entity linker, PPR graph retriever)
├── reasoning/                (neuro-symbolic rule engine & HIPAA exception rules)
├── explainability/            (subgraph extractor & faithfulness evaluator)
├── uncertainty/               (conformal predictor & safety router)
├── eval/                      (evaluation harness & statistical validator)
├── baselines/                 (comparative baseline runners for Vector-RAG, LightRAG, HippoRAG)
├── datasets/                  (24-query HIPAA gold benchmark set)
├── results/                   (raw JSON output metrics logging)
├── tests/                     (unittest test suite)
├── docs/                      (architecture spec, threat model, reproducibility, annotation protocol)
├── demo/                      (CLI audit demo application)
└── index.html / styles.css    (interactive Palantir-style web audit control panel)
```

---

## 📊 Verified Benchmark Results (N=24, real `all-MiniLM-L6-v2` encoder)

> Results from `python3 run_demo.py --stats --baselines` — three deterministic runs, identical output. Locked to `docs/LOCKED_RESULTS_2026-08-18.md` (commit `9c35c4e`). See `docs/AUDIT_LOG_2026-08-18.md` for full audit history.

| Hop Tier | n | Vector-RAG | Naive-RAG | CompGraphRAG | CG vs VR |
|:---------|:-:|:----------:|:---------:|:------------:|:--------:|
| 1-Hop    | 6 | 83.3%      | 66.7%     | **100.0%**   | +16.7%   |
| 2-Hop    | 6 | 66.7%      | 83.3%     | **100.0%**   | +33.3%   |
| 3-Hop    | 6 | 100.0%     | 100.0%    | **100.0%**   | +0.0%    |
| 4-Hop    | 6 | 100.0%     | 100.0%    | **100.0%**   | +0.0%    |
| **Overall** | **24** | **87.5%** | **87.5%** | **100.0%** | **+12.5% (n.s., p=0.083)** |

- **Explanation Faithfulness F1**: 0.9679 (mean across 24 items; 19/24 = 1.0, 5 items < 1.0 due to stochastic edge abstraction)
- **ECE**: 0.0114 (well-calibrated)
- **Paired t-test**: mean diff = +0.1250, t = 1.8127, p = 0.0830 — not significant at α=0.05
- **Wilcoxon**: p = 0.0833 — not significant at α=0.05
- **Cohen's d**: 0.37 | **Study power at n=24**: 40% | **n needed for 80% power**: 68 (at pre-registered 15pp target; McNemar) — supersedes old n=60 circular estimate
- **GraphRAG / LightRAG / HippoRAG**: NOT MEASURED (not installed)

**What the advantage is**: All 3 discordant items (CG correct, VR/NR wrong) are explained by **graph-grounded entity disambiguation** — the entity linker surfaces a legally critical node (e.g. `JudicialSubpoena_Exception`, `UnencryptedEmail`, `DeIdentifiedData`) that distinguishes two passages sharing surface vocabulary but encoding opposite compliance determinations. Flat retrieval is fooled by topic similarity; graph-path retrieval is not.

**What the advantage is NOT (yet)**: The hop-scaling hypothesis (H4/H8) is untestable on this benchmark — both baselines achieve 100% at 3-hop and 4-hop. The benchmark needs adversarially constructed hard distractors per tier before H4/H8 can be evaluated. This is a design limitation of the current pilot, documented in `docs/STAGE2_FINDINGS_2026-08-18.md`.

> **Note on hash-encoder runs**: Earlier runs (pre-Stage 1 audit) used a hash-bucket pseudo-embedding fallback, producing 70.8%/79.2% CG/VR numbers. Those are retired. All canonical numbers above use the real sentence-transformers encoder.

---

## 📜 Code & Data Availability Statement
- **Repository Access**: All software code, schemas, dataset benchmarks, evaluation scripts, and unit tests are publicly available under the MIT License.
- **Raw Evaluation Artifacts**: Executed benchmark metrics are deterministically logged in `results/eval_results_raw.json`.
- **Canonical Paper**: `CompGraphRAG_Paper.docx` at the repo root. The shorter file in `docs/archive/` is an earlier draft.
- **License**: Code is licensed under [MIT](LICENSE); annotations and dataset artifacts under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).


---

## ✒️ Citation
If you use CompGraphRAG in your research, please cite:
```bibtex
@article{shaik2026compgraphrag,
  title={CompGraphRAG: A Knowledge Graph-Augmented Retrieval Framework for Intelligent Enterprise Compliance Workflows --- A HIPAA Case Study},
  author={Shaik, Mahaboob Johny},
  journal={Research Artifact & Prototype Release v0.1.0-pilot},
  year={2026}
}
```
