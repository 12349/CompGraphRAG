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

## 📊 Verified Benchmark Results (N=24, hash-embedding encoder)

> Results from `python3 run_demo.py --stats --baselines` — three runs, identical output. See `docs/AUDIT_LOG_2026-08-18.md` for full audit details.

| Hop Tier | n | Vector-RAG Acc. | CompGraphRAG Acc. | Marginal Benefit |
|:---|:---:|:---:|:---:|:---:|
| 1-Hop | 6 | 66.7% | **83.3%** | +16.7% |
| 2-Hop | 6 | 66.7% | **50.0%** | −16.7% |
| 3-Hop | 6 | 83.3% | **66.7%** | −16.7% |
| 4-Hop | 6 | **100.0%** | 83.3% | −16.7% |
| **Overall** | **24** | **79.2%** | **70.8%** | **−8.3%** |

- **Naive-RAG**: 83.3% overall
- **Explanation Faithfulness F1**: 0.9798 (mean across 24 items; 19/24 = 1.0, 5 items < 1.0)
- **ECE**: 0.1469
- **Paired t-test**: mean diff = −0.0833, t = −0.6244, p = 0.5385 — **not significant**
- **Wilcoxon**: p = 0.5271 — **not significant**
- **H4/H8 (monotonically growing advantage)**: **NOT supported** on this dataset
- **GraphRAG / LightRAG / HippoRAG**: NOT MEASURED (not installed)

> **Note on N=6 pilot (paper)**: The canonical paper (`CompGraphRAG_Paper.docx` / `CompGraphRAG_Paper_extracted.txt`) describes a separate, earlier N=6 proof-of-concept pilot — not these N=24 results. The paper is explicit that those results are descriptive only and that statistical tests are a pre-registered plan.

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
