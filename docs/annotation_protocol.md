# CompGraphRAG Dataset Annotation Protocol & Power Analysis

## 1. Double-Blind Expert Annotation Protocol
Following the template established by the **Contract Understanding Atticus Dataset (CUAD)** [Hendrycks et al., 2021], the CompGraphRAG benchmark dataset construction protocol enforces strict double-blind annotation:

1. **Annotator Selection**: Annotations are produced independently by healthcare compliance officers and legal technology researchers.
2. **Task Definition**: For each query scenario $q$, annotators perform:
   - Categorical Determination Labeling: $d \in \{\text{COMPLIANT}, \text{NON-COMPLIANT}, \text{REQUIRES-REVIEW}\}$.
   - Subgraph Evidence Annotation: Edge-level extraction of supporting triples $\pi = \{(u,r,v)\}$.
3. **Adjudication**: Where annotator choices diverge, a third senior compliance arbitrator resolves the discrepancy.

---

## 2. Inter-Annotator Agreement Metrics

To ensure construct validity and annotation reliability:

- **Categorical Determination Labels**: Evaluated using **Cohen's Kappa ($\kappa$)**:
  $$\kappa = \frac{p_o - p_e}{1 - p_e}$$
  where $p_o$ is observed agreement and $p_e$ is expected chance agreement. Target threshold: $\kappa \ge 0.85$.

- **Graph Path Evidence Subgraphs ($\pi$)**: Evaluated using **Krippendorff's Alpha ($\alpha_{\text{krip}}$)** over set-valued edge overlap:
  $$\alpha_{\text{krip}} = 1 - \frac{D_o}{D_e}$$
  where $D_o$ is observed disagreement and $D_e$ is expected chance disagreement. Target threshold: $\alpha_{\text{krip}} \ge 0.80$.

---

## 3. Statistical Power Analysis
To size full-scale evaluation splits ($N \ge 100$) for detecting significant accuracy differences between CompGraphRAG and baseline models:

- **Effect Size**: Minimum detectable difference $\delta = 0.15$ ($15\%$ accuracy margin) at 3-hop query complexity.
- **Alpha Level**: $\alpha = 0.05$ (two-tailed).
- **Target Power**: $1 - \beta = 0.80$.
- **Sample Size Formula (Paired McNemar / $t$-test)**:
  $$N = \left( \frac{Z_{1-\alpha/2} + Z_{1-\beta}}{\delta} \right)^2 \cdot \sigma^2$$
  Yields a minimum required sample size of $N = 24$ per hop stratum ($N_{\text{total}} = 96$ queries).
