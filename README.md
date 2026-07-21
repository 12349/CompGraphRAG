# CompGraphRAG: Enterprise GraphRAG for Compliance Automation

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Domain](https://img.shields.io/badge/Domain-HIPAA%20%26%20Healthcare%20Compliance-green.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Neuro--Symbolic%20GraphRAG-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

> **CompGraphRAG** is a Knowledge Graph-Augmented Retrieval-Augmented Generation (GraphRAG) framework specifically engineered for high-stakes enterprise regulatory and compliance determination workflows, validated through a comprehensive HIPAA compliance case study.

---

## 🌟 Key Features

* **🕸️ Multi-Hop Relational Retrieval**: Overcomes flat vector RAG limitations by indexing document entities, roles, policies, and regulatory constraints into a structured entity-relationship knowledge graph.
* **🧠 Neuro-Symbolic Rule Engine**: Combines deterministic compliance rule matching with LLM-based multi-hop graph traversal to guarantee auditable regulatory determinations.
* **📜 Subgraph Traversal Justification ($\pi$-Path)**: Generates human-auditable, step-by-step natural language path walks through knowledge subgraphs for every compliance determination.
* **📊 Conformal Uncertainty Quantification**: Provides calibrated uncertainty intervals $C(q)$ with Expected Calibration Error (ECE) monitoring to trigger human-in-the-loop audit flags when confidence falls below regulatory bounds.
* **⚡ Benchmark Harness**: Pre-configured evaluation suite comparing CompGraphRAG directly against standard vector similarity RAG baselines.

---

## 📊 Benchmark Performance & Results

Running `run_demo.py` yields empirical verification on multi-hop HIPAA regulatory queries:

| Metric | CompGraphRAG | Vector RAG Baseline | Delta / Benefit |
| :--- | :---: | :---: | :---: |
| **Overall F1 / Accuracy** | **100.0%** | 66.7% | **+33.3%** |
| **1-Hop Query Accuracy** | **100.0%** | 100.0% | +0.0% |
| **2-Hop Query Accuracy** | **100.0%** | 50.0% | **+50.0%** |
| **3-Hop Query Accuracy** | **100.0%** | 50.0% | **+50.0%** |
| **Explanation Faithfulness F1** | **1.0000** | N/A | — |
| **Expected Calibration Error (ECE)** | **0.0800** | N/A | — |

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

```bash
git clone https://github.com/<your-username>/CompGraphRAG.git
cd CompGraphRAG

pip install -r requirements.txt
```

### 2. Run Evaluation Benchmark & Interactive Demos

Execute the main system launcher:

```bash
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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
