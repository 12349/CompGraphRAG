# CompGraphRAG Security, Privacy & Threat Model Specification

## 1. Threat Model & Boundaries
CompGraphRAG distinguishes between two distinct threat vectors:
1. **Infrastructure Confidentiality**: Protecting Protected Health Information (PHI) in transit and at rest during model execution.
2. **RAG Retrieval-Leakage Risk**: Preventing membership inference and differential privacy leaks where external queries deduce private individual records indexed in the graph.

```
+------------------------------------------------------------------------+
|                      COMPLIANCE SECURE BOUNDARY                        |
|                                                                        |
| Raw Enterprise Docs  ──► [De-Identification Pass]  ──► Knowledge Graph |
| (Policies, Logs)         (Presidio / Local NER)        (TBox / ABox)   |
|                                                            │           |
|                                                            ▼           |
| Hybrid Retrieval Engine  ◄──────────────────────────────────┘           |
|         │                                                              |
|         ▼                                                              |
| [Secured On-Prem / Private Azure LLM Boundary]                         |
|         │                                                              |
|         ▼                                                              |
| Determination & Subgraph π (De-identified Audit Trail)                 |
+------------------------------------------------------------------------+
```

## 2. Ingestion De-Identification Protocol
Before enterprise documents enter the Knowledge Graph construction module, they pass through a mandatory local PII/PHI de-identification pipeline:
- Direct Identifiers (Names, SSNs, Medical Record Numbers, Addresses) are replaced with synthetic canonical tokens (`[COVERED_ENTITY_A]`, `[WORKFORCE_MEMBER_1]`).
- Dates are normalized to relative temporal years or regulatory versions (`2026-v1`).

## 3. Retrieval Leakage Mitigations
- **Graph Anonymization**: ABox graph nodes represent role classes, obligation types, and policy clauses—never individual patient identity nodes.
- **Differential Privacy Scoping Disclaimer**: In the current evaluation release, the graph is constructed on synthetic and policy-level data. Production deployment on real PHI requires integrating local perturbation and differential privacy budgets before cross-department retrieval.

## 4. Scope Exclusions & Ethical Disclaimer
- **No Sole Basis for Legal Liability**: CompGraphRAG is an automated decision-support tool. System outputs MUST NOT serve as the sole legal basis for regulatory enforcement, penalties, or clinical liability without human reviewer verification.
