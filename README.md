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
git clone https://github.com/compgraphrag/compgraphrag.git
cd compgraphrag
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

## 📜 Code & Data Availability Statement
- **Repository Access**: All software code, schemas, dataset benchmarks, evaluation scripts, and unit tests are publicly available under the Apache-2.0 license.
- **Raw Evaluation Artifacts**: Executed benchmark metrics are deterministically logged in `results/eval_results_raw.json`.
- **License**: Code is licensed under [Apache-2.0](LICENSE); annotations and dataset artifacts under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

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
