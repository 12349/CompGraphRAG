# CompGraphRAG Reproducibility Statement & Experimental Protocols

## 1. Experimental Settings
- **Seed Fixation**: All pseudo-random number generators in Python, NumPy, and NetworkX are fixed at `seed = 42`.
- **Temperature**: Generation LLM calls use `temperature = 0.0` to enforce deterministic outputs.

## 2. Hyperparameter Grid Search
- Hybrid Retrieval Weights ($\alpha, \beta, \gamma$):
  - Grid searched over $\alpha \in [0.1, 0.6]$, $\beta \in [0.1, 0.7]$, $\gamma \in [0.0, 0.3]$ subject to $\alpha + \beta + \gamma = 1.0$.
  - Optimal evaluated configuration: $\alpha = 0.40, \beta = 0.50, \gamma = 0.10$.
- Hop Decay Factor ($\lambda$):
  - Evaluated values: $\lambda \in \{0.70, 0.85, 0.95\}$. Default set to $\lambda = 0.85$.
- Conformal Prediction Significance ($\alpha_{\text{conf}}$):
  - Target coverage level set at $90\%$ ($\alpha_{\text{conf}} = 0.10$).

## 3. Baseline Commit Hashes
For comparative baseline runs:
- Microsoft GraphRAG: pinned to release commit `v0.3.0`
- LightRAG: pinned to main branch commit `c81f9a2`
- HippoRAG: pinned to NeurIPS 2024 submission release `v1.0.1`

## 4. Pre-Registration Statement
All eight hypotheses ($H1$ through $H8$) and statistical significance testing procedures (paired t-test, TOST equivalence test, Expected Calibration Error) were pre-registered in the project blueprint before executing full dataset benchmarking runs.
