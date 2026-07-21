# CompGraphRAG Architecture & Technical Specification

## 1. Overview
CompGraphRAG is a Knowledge Graph-Augmented hybrid retrieval framework engineered for regulated enterprise compliance workflows (with HIPAA as a case study). It unifies layout-aware document intelligence, formal TBox ontology modeling, neuro-symbolic pre-generation rule checking, and conformal uncertainty quantification.

```
Raw Documents ──► DocIntel ──► TBox/ABox Graph G=(V,E,λ,μ)
                                     ▲
Query q ────────► Entity Linker ─────┼──► Graph Path Retrieval (PPR)
                                     │
                             Hybrid Retrieval Scorer:
                       score(x|q) = α·cos(q,x) + β·PathScore + γ·Auth
                                     │
                                     ▼
                            Neuro-Symbolic Rule Engine
                                     │
                                     ▼
                          Generation & Subgraph π
                                     │
                                     ▼
                         Conformal Uncertainty C(q)
```

## 2. Mathematical Retrieval Scoring Function
$$\text{score}(x | q) = \alpha \cdot \cos(q_{\text{emb}}, x_{\text{emb}}) + \beta \cdot \text{GraphPathScore}(q_{\text{ent}}, \text{path}_x) + \gamma \cdot \text{Authority}(x)$$

Where:
- $\alpha + \beta + \gamma = 1.0, \quad \alpha, \beta, \gamma \ge 0$
- $\text{GraphPathScore}(q_{\text{ent}}, \text{path}) = \frac{1}{|\text{path}|} \sum_{(u,r,v) \in \text{path}} w_r \cdot \text{conf}(u,r,v) \cdot \lambda^{h-1}$
- $\lambda \in (0, 1]$ is the hop decay factor penalizing longer edge chains.

## 3. Neuro-Symbolic Compliance Engine
The rule-check layer acts as a gatekeeper between retrieval and generation:
1. Candidate subgraph edges are parsed into entity and relation sets.
2. Declarative rules (e.g., `45 CFR 164.502(e)` Business Associate Agreement requirement, `45 CFR 164.506` TPO exception) evaluate required node presences.
3. The rule-check output dictates whether generation proceeds or surfaces a flagged non-compliance / exception rationale.

## 4. Conformal Uncertainty Quantification
Conformal prediction guarantees distribution-free coverage:
- Non-conformity score $s_i = 1 - P(y_i | x_i)$.
- Quantile $\hat{q}$ computed at significance level $\alpha = 0.10$.
- Confidence set $C(q) = \{ y : 1 - P(y|q) \le \hat{q} \}$.
- If $|C(q)| > 1$ or includes `REQUIRES-REVIEW`, the system routes the decision to human audit.
