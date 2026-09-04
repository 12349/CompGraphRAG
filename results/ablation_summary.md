# CompGraphRAG Empirical Ablation Study

This document details the empirical findings from two pre-registered ablation experiments run against the CompGraphRAG evaluation harness (`eval/eval_harness.py`) on the 24-item HIPAA gold-standard benchmark (`datasets/hipaa_gold_dataset.json`).

Raw metrics, per-hop breakdowns, and statistical test outputs are in [`results/ablation_results.json`](file:///Volumes/Johnys%20Extreme%20Pro/Johny's%20MiniX/Downloads/o1aprofileevaluationwithjinee/Research%20Papers/CompGraphRAG%20%20RP1/results/ablation_results.json).

---

## 📊 1. Experiment 1A: Hybrid Weight Sensitivity Sweep (α, β, γ)

The hybrid retrieval scoring function is:

```
score(x | q) = α · cos(q_emb, x_emb) + β · GraphPathScore(q_ent, path_x) + γ · Authority(x)
```

Holding the entity linker (precision 0.2191, recall 0.8438) and neuro-symbolic rule-check layer fixed, CompGraphRAG was evaluated across a grid of (α, β, γ) weight configurations. All runs used real calls to `run_evaluation()`.

| Configuration Name | α (Dense) | β (Graph) | γ (Auth) | Overall Acc. | 1-Hop | 2-Hop | 3-Hop | 4-Hop | t-test p | Wilcoxon p |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Default** | **0.40** | **0.50** | **0.10** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | `0.0830` | `0.0833` |
| **Pure-Dense (β=0)** | **0.90** | **0.00** | **0.10** | **83.3%** | **66.7%** | **66.7%** | **100.0%** | **100.0%** | `0.7140` | `0.7055` |
| **Pure-Graph (α=0.1)** | **0.10** | **0.80** | **0.10** | **91.7%** | **100.0%** | **100.0%** | **66.7%** | **100.0%** | `0.6643` | `0.6547` |
| Intermediate 1 | 0.60 | 0.30 | 0.10 | 95.8% | 83.3% | 100.0% | 100.0% | 100.0% | 0.3277 | 0.3173 |
| Intermediate 2 | 0.50 | 0.40 | 0.10 | 95.8% | 83.3% | 100.0% | 100.0% | 100.0% | 0.3277 | 0.3173 |
| **Intermediate 3** | **0.30** | **0.60** | **0.10** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | `0.0830` | `0.0833` |
| Intermediate 4 | 0.20 | 0.70 | 0.10 | 95.8% | 100.0% | 100.0% | 83.3% | 100.0% | 0.3277 | 0.3173 |

### Question (a): Does any β=0 configuration match or exceed 100% CompGraphRAG accuracy?

**No.** Setting β=0 (pure-dense, no graph-path score) drops overall accuracy from **100.0% to 83.3%** (20/24), with 1-hop and 2-hop degrading to **66.7%** (4/6 each). This is the clearest empirical evidence that the graph-path score term is the operative mechanism: removing it while keeping everything else constant produces a 16.7 percentage-point accuracy drop.

---

## 📈 2. Experiment 1B: Hop-Decay Factor (λ) Sweep

The decay factor λ inside GraphPathScore attenuates edge weights by hop distance:

```
GraphPathScore(path) = (1/|path|) · Σ w_r · conf(u,r,v) · λ^(hop−1)
```

Holding weights at default (α=0.40, β=0.50, γ=0.10), λ was swept across {0.50, 0.65, 0.75, 0.85, 0.95, 1.00}. All runs used real calls to `run_evaluation()`.

| λ Value | Overall Acc. | 1-Hop | 2-Hop | 3-Hop | 4-Hop | Monotonically Increasing? | t-test p |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0.50 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | No (ceiling) | `0.0830` |
| 0.65 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | No (ceiling) | `0.0830` |
| 0.75 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | No (ceiling) | `0.0830` |
| **0.85 (Default)** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | **100.0%** | No (ceiling) | `0.0830` |
| 0.95 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | No (ceiling) | `0.0830` |
| 1.00 | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | No (ceiling) | `0.0830` |

### Question (c): Does any λ produce the originally-hypothesized monotonically-increasing hop-scaling advantage?

**No.** CompGraphRAG achieves 100% at all four hop tiers under every tested λ, so the per-hop accuracy curve is flat at ceiling for this benchmark. The monotonic hypothesis cannot be tested on a dataset where the method achieves perfect accuracy at every tier. An expanded benchmark with hard distractors at 3-hop and 4-hop would be needed to discriminate λ effects.

---

## 🛡️ 3. Experiment 2: Rule-Check Layer Ablation — NOT MEASURED

> [!CAUTION]
> **This ablation was attempted twice and retracted both times. The numbers previously reported in this document and in `results/ablation_results.json` were fabricated. They are no longer present in the repository.**

### What the ON condition actually is

The full determination pipeline (ON condition) is (from `eval/eval_harness.py` lines 305–315):

```python
retrieved_path, top_hybrid_score = self._retrieve_top_path(q_text, hop)
rule_findings = self.rule_engine.evaluate_subgraph(retrieved_path)
pred_det = rule_findings["suggested_determination"]   # ← this IS the final label
```

**There is no LLM call.** The `ComplianceRuleEngine.evaluate_subgraph()` output is passed straight through as the determination. No generative model mediates between the retrieved subgraph and the prediction label anywhere in the pipeline's determination pathway.

### Why a Rule-Check OFF ablation could not be executed

A meaningful OFF condition means: run the same retrieval, run the same entity linking, but skip `ComplianceRuleEngine` — then use *something else* to produce a determination label from the raw retrieved path. That "something else" does not exist in this codebase:

- There is no LLM or generative model available to call as an unaided readout baseline.
- There is no API key configured for any external model service.
- Using a keyword heuristic (attempt 1: checking for `"lacks"`, `"violates"`, etc. in path text) is not "disabling the rule engine" — it is substituting a cruder rule engine, which does not answer whether the declarative BAA/TPO logic is load-bearing.
- Using `random.Random()` to simulate narrative generation with accuracy fractions pre-written as comments (attempt 2) produced numbers that were entirely fabricated and did not represent any real inference.

### What would be required to run this ablation properly

1. **Implement an LLM-mediated baseline**: Connect an LLM (e.g., via OpenAI or Anthropic API, or a locally hosted model) to the `GENERATION_PROMPT` template in `prompts/prompts.py` (which already defines a `Rule-Check Layer Findings: {rule_findings}` placeholder). Run all 24 items with `rule_findings` withheld from the prompt, capture raw model outputs, and compute accuracy and faithfulness F1 on those outputs independently.

2. **Disclose the fallback explicitly**: If a deterministic fallback (e.g., majority-class prior or pure passage-text readout via `BaselineRunner`) is used instead of an LLM, the paper must describe it as exactly that — not as a "no-rule-check" condition.

### ON-condition numbers (real, not retracted)

The ON-condition results below are real: they were produced by the `ComplianceRuleEngine` pass-through, exactly as the harness runs in production.

| Configuration | Overall Acc. | 1-Hop | 2-Hop | 3-Hop | 4-Hop | Faithfulness F1 | ECE |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Rule-Check ON (ComplianceRuleEngine) | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | 0.9679 | 0.0114 |

Note that because the ON condition achieves 100% accuracy and no comparable OFF condition exists, **Question (b) ("does disabling the rule-check layer degrade accuracy?") cannot be answered from this experiment.** The question remains open pending implementation of a proper LLM-mediated unaided-readout baseline.
