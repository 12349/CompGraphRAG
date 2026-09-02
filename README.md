# CompGraphRAG: Enterprise GraphRAG for Compliance Automation

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/) [![Domain](https://img.shields.io/badge/Domain-HIPAA%20%26%20Healthcare%20Compliance-green.svg)](https://github.com/12349/CompGraphRAG/blob/main) [![Architecture](https://img.shields.io/badge/Architecture-Neuro--Symbol%20GraphRAG-orange.svg)](https://github.com/12349/CompGraphRAG/blob/main) [![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/12349/CompGraphRAG/blob/main/LICENSE)

> **CompGraphRAG** is a Knowledge Graph-Augmented Retrieval-Augmented Generation (GraphRAG) framework specifically engineered for high-stakes enterprise regulatory and compliance determination workflows, validated through a comprehensive HIPAA compliance case study.

---

## 🌟 Key Features

- **🕸️ Multi-Hop Relational Retrieval**: Overcomes flat vector RAG limitations by indexing document entities, roles, policies, and regulatory constraints into a structured entity-relationship knowledge graph.
- **🧠 Neuro-Symbolic Rule Engine**: Combines deterministic compliance rule matching with LLM-based multi-hop graph traversal to guarantee auditable regulatory determinations.
- **📜 Subgraph Traversal Justification (π-Path)**: Generates human-auditable, step-by-step natural language path walks through knowledge subgraphs for every compliance determination.
- **📊 Conformal Uncertainty Quantification**: Provides calibrated uncertainty intervals C(q) with Expected Calibration Error (ECE) monitoring to trigger human-in-the-loop audit flags when confidence falls below regulatory bounds.
- **⚡ Benchmark Harness**: Pre-configured evaluation suite comparing CompGraphRAG directly against two fairness-matched dense-retrieval baselines (Vector-RAG, Naive-RAG), both using the identical rule-based answer-readout step as CompGraphRAG.

---

## 📊 Benchmark Performance & Results

Running `run_demo.py` (via `eval/eval_harness.py`) on the 24-item `datasets/hipaa_gold_dataset.json` benchmark, with the real `sentence-transformers/all-MiniLM-L6-v2` encoder, yields:

| Metric | CompGraphRAG | Vector-RAG Baseline | Naive-RAG Baseline | Delta vs. best baseline |
| --- | --- | --- | --- | --- |
| **Overall Accuracy (N=24)** | **100.0%** | 87.5% | 87.5% | **+12.5%** |
| **1-Hop Query Accuracy (n=6)** | **100.0%** | 83.3% | 66.7% | **+16.7%** |
| **2-Hop Query Accuracy (n=6)** | **100.0%** | 66.7% | 83.3% | **+16.7%** |
| **3-Hop Query Accuracy (n=6)** | 100.0% | 100.0% | 100.0% | tie |
| **4-Hop Query Accuracy (n=6)** | 100.0% | 100.0% | 100.0% | tie |
| **Explanation Faithfulness F1** | **0.9679** | N/A | N/A | — |
| **Entity-Linking Precision / Recall** | **0.2191 / 0.8438** | N/A | N/A | — |
| **Expected Calibration Error (ECE)** | **0.0114** | N/A | N/A | — |
| **Paired t-test / Wilcoxon (p-value)** | 0.0830 / 0.0833 | — | — | not yet significant at N=24 |

Statistical note: the accuracy advantage is concentrated at 1- and 2-hop and ties at 3- and 4-hop; it does not clear the conventional p < 0.05 threshold at this sample size (Cohen's d ≈ 0.37, post-hoc power ≈ 40%). See the paper's Section VI-D and VII for the full statistical validation plan and the sample size needed to confirm this result. Entity-linking precision (21.9%) is notably low despite not degrading end-to-end accuracy — flagged in the paper (Section VII-E) as requiring the rule-check on/off ablation before that robustness can be trusted as a general property of the architecture rather than a benchmark-specific artifact.

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────┐
                                  │   Enterprise Corpos       │
                                  │ (Policies, BAA, IRB, etc) │
                                  └─────────────┬─────────────┘
                                                │
                                  ┌─────────────▼─────────────┐
                                  │   Schema-Guided Graph     │
                                  │   Indexing Engine         │
                                  └─────────────┬─────────────┘
                                                │
                                  ┌─────────────▼─────────────┐
                                  │ HIPAA Entity-Rel Graph    │
                                  └─────────────┬─────────────┘
                                                │
     ┌──────────────────────────────────────────┴──────────────────────────────────────────┐
     │                                                                                     │
┌────▼────────────────────────┐    ┌─────────────────────────────┐    ┌────────────────────▼──────────────────┐
│ Neuro-Symbolic Rule Check   │    │  Multi-Hop Subgraph Walk    │    │ Conformal Uncertainty Calibration    │
│ (Rule Matching & Violations)│    │  (Path Traversal & Context) │    │ (Quantile Risk & Audit Flagging)      │
└────┬────────────────────────┘    └─────────────┬───────────────┘    └────────────────────┬──────────────────┘
     │                                           │                                         │
     └───────────────────────────────────────────┼─────────────────────────────────────────┘
                                                 │
                                  ┌──────────────▼──────────────┐
                                  │ Auditable Compliance        │
                                  │ Determination & Path Walk   │
                                  └─────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites & Installation

Clone the repository and install requirements:

```
git clone https://github.com/<your-username>/CompGraphRAG.git
cd CompGraphRAG

pip install -r requirements.txt
```

### 2. Run Evaluation Benchmark & Interactive Demos

Execute the main system launcher:

```
python run_demo.py
```

---

## 📂 Project Structure

```
├── run_demo.py                      # Main system entry point & benchmark harness
├── requirements.txt                 # Core dependencies (rdflib, networkx, scikit-learn, etc.)
├── datasets/                        # HIPAA compliance gold-standard evaluation datasets
│   └── hipaa_gold_dataset.json
├── demo/                            # Interactive sample audit demonstration application
│   └── app.py
├── retrieval/                       # Knowledge graph retrieval & indexing engines
├── reasoning/                       # Neuro-symbolic rule execution engine
├── explainability/                  # Subgraph path walk & justification generator
├── uncertainty/                     # Conformal prediction & calibration module
├── eval/                            # System evaluation harness & metrics
├── schema/                          # Entity-relationship ontology definitions
└── docs/                            # Research specifications & technical documentation
```

---

## 📝 Citation & Research Foundation

CompGraphRAG builds upon established research in Knowledge Graph-Augmented LLMs, Neuro-Symbolic AI, and Conformal Prediction for Healthcare and Legal Compliance Automation.

---

## 🔓 Code & Data Availability Statement

The exact commit hash corresponding to this manuscript's final results and reproducibility reference is [`ddf7a99b36e70e236f7f65f9080ddcc8d16ff632`](https://github.com/12349/CompGraphRAG/commit/ddf7a99b36e70e236f7f65f9080ddcc8d16ff632) (tagged as [`v1.0-paper`](https://github.com/12349/CompGraphRAG/releases/tag/v1.0-paper)). All benchmark metrics reported in the paper can be regenerated using `python run_demo.py` via `eval/eval_harness.py`.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/12349/CompGraphRAG/blob/main/LICENSE) file for details.
