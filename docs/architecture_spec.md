# CompGraphRAG Architecture & Technical Specification

## 1. System Overview & Data Flow (Figure 1)
CompGraphRAG is a Knowledge Graph-Augmented hybrid retrieval framework engineered for regulated enterprise compliance workflows (with HIPAA as a case study). It unifies layout-aware document intelligence, formal TBox ontology modeling, neuro-symbolic pre-generation rule checking, and conformal uncertainty quantification.

```
+-----------------------------------------------------------------------------------+
|                        COMPGRAPHRAG SYSTEM ARCHITECTURE                           |
|                                                                                   |
|  Raw Docs D ──► DocIntel ──► De-ID Pass ──► TBox/ABox Graph G = (V, E, τ, λ)     |
|                                                     ▲                             |
|  Query q ────► Entity Linker ───────────────────────┼──► Graph Path Retrieval     |
|                                                     │                             |
|              Hybrid Retrieval Scorer:               │                             |
|  score(x|q) = α·cos(q,x) + β·GraphPathScore + γ·Auth│                             |
|                                                     ▼                             |
|                                       Neuro-Symbolic Rule Check                   |
|                                                     │                             |
|                                                     ▼                             |
|                                          LLM Generation & Subgraph π               |
|                                                     │                             |
|                                                     ▼                             |
|                                        Split Conformal UQ C(q)                    |
+-----------------------------------------------------------------------------------+
```

## 2. Formal Compliance Determination Function (Eq. 1)
$$\mathbf{f: \mathcal{Q} \times \mathcal{D} \times G \to (d, c, \pi)} \quad \text{--- (Eq. 1)}$$

Where $d \in \{\text{COMPLIANT}, \text{NON-COMPLIANT}, \text{REQUIRES-REVIEW}\}$, $c \in [0,1]$ is calibrated conformal confidence, and $\pi \subseteq G$ is a justification subgraph.

## 3. Mathematical Retrieval Scoring Engine (Eq. 2–4)
$$\mathbf{\text{score}(x|q) = \alpha \cdot \cos(q_{\text{emb}}, x_{\text{emb}}) + \beta \cdot \text{GraphPathScore}(q_{\text{ent}}, \text{path}_x) + \gamma \cdot \text{Authority}(x)} \quad \text{--- (Eq. 2)}$$

$$\mathbf{\cos(q_{\text{emb}}, x_{\text{emb}}) = \max\left(0, \frac{q_{\text{emb}} \cdot x_{\text{emb}}}{\|q_{\text{emb}}\| \|x_{\text{emb}}\|}\right)} \quad \text{--- (Eq. 3)}$$

$$\mathbf{\text{GraphPathScore}(q_{\text{ent}}, \text{path}_x) = \frac{1}{|\text{path}_x|} \sum_{(u,r,v) \in \text{path}_x} w_r \cdot \text{conf}(u,r,v) \cdot \lambda^{h-1}} \quad \text{--- (Eq. 4)}$$

Parameters: $\alpha = 0.40, \beta = 0.50, \gamma = 0.10, \lambda = 0.85$.

## 4. Neuro-Symbolic Compliance Engine (Eq. 5)
$$\mathbf{\text{RuleEval}(\pi) = \{ r \in \mathcal{R} \mid \text{Conditions}(r) \text{ satisfied in } \pi \}} \quad \text{--- (Eq. 5)}$$

- **Rule $R_1$ ($45\text{ C.F.R. } \S 164.502(\text{e})$ BAA Requirement)**: $(\text{Recipient} \in \text{BusinessAssociate}) \land (\text{BAA\_Document} \notin \pi) \implies \text{FLAG\_NON\_COMPLIANT}$.
- **Rule $R_2$ ($45\text{ C.F.R. } \S 164.506$ TPO Exception)**: $(\text{Purpose} \in \{\text{Treatment}, \text{Payment}, \text{Operations}\}) \land (\text{TPO\_Exception} \in \pi) \implies \text{FLAG\_COMPLIANT\_EXCEPTION}$.

## 5. Explanation Faithfulness Metrics (Eq. 6–7)
$$\mathbf{\text{Precision}_{\text{faith}} = \frac{|\mathcal{E} \cap \pi|}{|\mathcal{E}|}, \quad \text{Recall}_{\text{faith}} = \frac{|\mathcal{E} \cap \pi|}{|\pi|}} \quad \text{--- (Eq. 6)}$$

$$\mathbf{\text{F1}_{\text{faith}} = \frac{2 \cdot \text{Precision}_{\text{faith}} \cdot \text{Recall}_{\text{faith}}}{\text{Precision}_{\text{faith}} + \text{Recall}_{\text{faith}}}} \quad \text{--- (Eq. 7)}$$

## 6. Split Conformal Uncertainty Quantification (Eq. 8–11)
$$\mathbf{s_i = 1 - P(y_i \mid q_i)} \quad \text{--- (Eq. 8)}$$

$$\mathbf{\hat{q} = \text{Quantile}\left(\{s_1,\dots,s_n\}, \frac{\lceil(n+1)(1-\alpha_{\text{conf}})\rceil}{n}\right)} \quad \text{--- (Eq. 9)}$$

$$\mathbf{C(q) = \{ y \in \mathcal{Y} \mid 1 - P(y \mid q) \le \hat{q} \}} \quad \text{--- (Eq. 10)}$$

$$\mathbf{\text{FinalDetermination}(q) = \begin{cases} y, & \text{if } C(q) = \{y\} \text{ and } y \neq \text{REQUIRES-REVIEW} \\ \text{REQUIRES-REVIEW}, & \text{otherwise} \end{cases}} \quad \text{--- (Eq. 11)}$$
