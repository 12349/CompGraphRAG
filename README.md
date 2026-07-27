# CompGraphRAG: Enterprise GraphRAG for Compliance Automation

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Domain](https://img.shields.io/badge/Domain-HIPAA%20%26%20Healthcare%20Compliance-green.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Neuro--Symbolic%20GraphRAG-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![CI Status](https://github.com/12349/CompGraphRAG/actions/workflows/ci.yml/badge.svg)](https://github.com/12349/CompGraphRAG/actions)

> **CompGraphRAG** is a Knowledge Graph-Augmented Retrieval-Augmented Generation (GraphRAG) framework specifically engineered for high-stakes enterprise regulatory and compliance determination workflows, validated through a comprehensive HIPAA compliance case study.

---

## 🌟 Key Features

* **🕸️ Multi-Hop Relational Retrieval**: Overcomes flat vector RAG limitations by indexing document entities, roles, policies, and regulatory constraints into a structured entity-relationship knowledge graph.
* **🧠 Neuro-Symbolic Rule Engine**: Combines deterministic compliance rule matching with LLM-based multi-hop graph traversal to guarantee auditable regulatory determinations.
* **📜 Subgraph Traversal Justification ($\pi$-Path)**: Generates human-auditable, step-by-step natural language path walks through knowledge subgraphs for every compliance determination.
* **📊 Conformal Uncertainty Quantification**: Provides calibrated uncertainty intervals $C(q)$ with Expected Calibration Error (ECE) monitoring to trigger human-in-the-loop audit flags when confidence falls below regulatory bounds.
* **⚡ Pre-Registered Statistical Validation Suite**: Includes paired t-test, Wilcoxon signed-rank test, Two One-Sided Tests (TOST) for equivalence, and Holm-Bonferroni p-value corrections across multi-hop stratifications.

---

## 📊 Benchmark Performance & Results

Running `python run_demo.py --stats` evaluates the 24-item gold dataset across 1-hop, 2-hop, 3-hop, and 4-hop queries (`results/eval_results_raw.json`):

| Metric | CompGraphRAG | Vector RAG Baseline | Delta / Benefit |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **100.0%** | 66.7% | **+33.3%** |
| **1-Hop Query Accuracy** | **100.0%** | 83.3% | **+16.7%** |
| **2-Hop Query Accuracy** | **100.0%** | 66.7% | **+33.3%** |
| **3-Hop Query Accuracy** | **100.0%** | 83.3% | **+16.7%** |
| **4-Hop Query Accuracy** | **100.0%** | 33.3% | **+66.7%** |
| **Explanation Faithfulness F1** | **1.0000** | N/A | — |
| **Expected Calibration Error (ECE)** | **0.0500** | N/A | — |
| **Paired t-Test (Statistical Significance)** | $t = 3.3912$ | $p = 0.002512$ ($p < 0.01$) | **Statistically Significant** |

---

## 🚀 Quick Start

### 1. Prerequisites & Installation

Clone the repository and install requirements:

```bash
git clone https://github.com/12349/CompGraphRAG.git
cd CompGraphRAG

pip install -r requirements.txt
```

### 2. Run Evaluation Benchmark & Pre-Registered Statistics

Execute the main system launcher with statistical validation:

```bash
python run_demo.py --stats
```

### 3. Run Unit Test Suite

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📂 Project Structure

```
├── run_demo.py                      # Main system entry point & benchmark harness
├── requirements.txt                 # Core dependencies
├── CITATION.cff                     # Citation metadata
├── CHANGELOG.md                     # Version history (v0.1.0-pilot)
├── datasets/                        # Gold-standard evaluation datasets
│   └── hipaa_gold_dataset.json      # 24 multi-hop HIPAA queries (1-4 hops)
├── results/                         # Automated raw evaluation outputs
│   └── eval_results_raw.json
├── docs/                            # Protocol & methodology documentation
│   └── annotation_protocol.md       # CUAD double-blind annotation & power analysis
├── baselines/                       # Baseline execution suite & wrappers
│   ├── runner.py
│   └── README.md
├── eval/                            # Evaluation harness & statistical validation
│   ├── eval_harness.py
│   └── stats_validation.py
├── retrieval/                       # Dense vector encoder & hybrid scorer
│   ├── hybrid_scorer.py
│   └── graph_retriever.py
├── reasoning/                       # Neuro-symbolic rule engine
│   └── rule_engine.py
├── uncertainty/                     # Split conformal predictor
│   └── conformal_predictor.py
└── tests/                           # Pytest & unittest test suite
```

---

## 📜 Code and Data Availability

The complete source code, baseline comparison suite, and 24-item HIPAA gold evaluation dataset for CompGraphRAG are open-source and publicly available at [https://github.com/12349/CompGraphRAG](https://github.com/12349/CompGraphRAG) under the MIT License (release tag `v0.1.0-pilot`).
