"""
CompGraphRAG Ablation Suite
Runs two pre-registered ablation experiments against CompGraphRAG evaluation harness:
1. Hybrid Weight & Hop-Decay Sensitivity Sweep (alpha, beta, gamma grid + lambda decay factor sweep)
2. Neuro-Symbolic Rule-Check Layer On/Off Ablation

Outputs results to results/ablation_results.json and prints a structured markdown summary.
"""

import json
import os
import hashlib
import numpy as np
from typing import Dict, Any, List

from eval.eval_harness import CompGraphRAGEvaluator
from eval.stats_validation import StatisticalValidator

def run_all_ablations(dataset_path: str = "datasets/hipaa_gold_dataset.json") -> Dict[str, Any]:
    evaluator = CompGraphRAGEvaluator(dataset_path)
    validator = StatisticalValidator()
    
    # Caching sentence-transformers encoder to accelerate parameter sweeps
    orig_encode = evaluator.scorer.encode_text
    cache = {}
    def cached_encode(text: str):
        if text not in cache:
            cache[text] = orig_encode(text)
        return cache[text]
    evaluator.scorer.encode_text = cached_encode

    # =========================================================================
    # EXPERIMENT 1A: HYBRID WEIGHT SENSITIVITY SWEEP (alpha, beta, gamma)
    # =========================================================================
    weight_configs = [
        ("default_0.40_0.50_0.10", 0.40, 0.50, 0.10),
        ("pure_dense_0.90_0.00_0.10", 0.90, 0.00, 0.10),
        ("pure_graph_0.10_0.80_0.10", 0.10, 0.80, 0.10),
        ("intermediate_1_0.60_0.30_0.10", 0.60, 0.30, 0.10),
        ("intermediate_2_0.50_0.40_0.10", 0.50, 0.40, 0.10),
        ("intermediate_3_0.30_0.60_0.10", 0.30, 0.60, 0.10),
        ("intermediate_4_0.20_0.70_0.10", 0.20, 0.70, 0.10),
    ]

    weight_sweep_results = {}
    for name, a, b, g in weight_configs:
        evaluator.scorer.alpha = a
        evaluator.scorer.beta = b
        evaluator.scorer.gamma = g
        evaluator.scorer.decay_lambda = 0.85  # default decay
        
        res = evaluator.run_evaluation(run_stats=True)
        
        weight_sweep_results[name] = {
            "weights": {"alpha": a, "beta": b, "gamma": g},
            "overall_compgraphrag_accuracy": res["overall_compgraphrag_accuracy"],
            "compgraphrag_accuracy_by_hop": res["compgraphrag_accuracy_by_hop"],
            "hop_marginal_benefit_h4_h8": res["hop_marginal_benefit_h4_h8"],
            "mean_explanation_faithfulness_f1": res["mean_explanation_faithfulness_f1"],
            "expected_calibration_error_ece": res["expected_calibration_error_ece"],
            "statistical_validation": res["statistical_validation"]
        }

    # =========================================================================
    # EXPERIMENT 1B: HOP-DECAY FACTOR (lambda) SWEEP
    # =========================================================================
    evaluator.scorer.alpha = 0.40
    evaluator.scorer.beta = 0.50
    evaluator.scorer.gamma = 0.10

    lambda_values = [0.50, 0.65, 0.75, 0.85, 0.95, 1.00]
    lambda_sweep_results = {}

    for l_val in lambda_values:
        name = f"lambda_{l_val:.2f}"
        evaluator.scorer.decay_lambda = l_val
        
        res = evaluator.run_evaluation(run_stats=True)
        
        # Check monotonic scaling (1-hop < 2-hop < 3-hop < 4-hop)
        h_accs = [res["compgraphrag_accuracy_by_hop"][str(h)] for h in [1, 2, 3, 4]]
        is_monotonic = (h_accs[0] < h_accs[1] < h_accs[2] < h_accs[3])
        
        lambda_sweep_results[name] = {
            "decay_lambda": l_val,
            "overall_compgraphrag_accuracy": res["overall_compgraphrag_accuracy"],
            "compgraphrag_accuracy_by_hop": res["compgraphrag_accuracy_by_hop"],
            "hop_marginal_benefit_h4_h8": res["hop_marginal_benefit_h4_h8"],
            "is_monotonically_increasing": is_monotonic,
            "statistical_validation": res["statistical_validation"]
        }

    # Reset scorer to default config
    evaluator.scorer.alpha = 0.40
    evaluator.scorer.beta = 0.50
    evaluator.scorer.gamma = 0.10
    evaluator.scorer.decay_lambda = 0.85

    # =========================================================================
    # EXPERIMENT 2: RULE-CHECK LAYER ABLATION — ON CONDITION ONLY
    # OFF CONDITION: NOT MEASURED
    # =========================================================================
    # The ON condition runs the full harness. The determination pathway is:
    #   retrieved_path -> ComplianceRuleEngine.evaluate_subgraph() -> suggested_determination
    # There is NO LLM call in the determination pathway (see eval/eval_harness.py lines 305-315).
    # A Rule-Check OFF condition requires an LLM or generative model as the unaided readout
    # baseline. No such model or API key exists in this environment.
    # Two earlier attempts produced fabricated numbers and were retracted:
    #   - Attempt 1 (keyword heuristic): substituted a cruder rule-check, not removal
    #   - Attempt 2 (random.Random() loop): pre-wrote accuracy fractions as comments, then
    #     branched on item index to produce those exact numbers, calling this "inference"
    # The OFF block is left as NOT MEASURED.
    rule_on_res = evaluator.run_evaluation(run_stats=True)

    NOT_MEASURED_REASON = (
        "No LLM or generative model exists in this pipeline's determination pathway. "
        "ComplianceRuleEngine.evaluate_subgraph() output is passed straight through as the "
        "final prediction label (see eval/eval_harness.py lines 305-315). Two earlier attempts "
        "at this ablation produced fabricated numbers (keyword heuristic; random.Random() "
        "simulation with pre-written accuracy fractions in comments) and were retracted. "
        "This block is NOT MEASURED until an LLM-mediated unaided-readout baseline is "
        "implemented and verified to produce real per-item raw outputs before any metric is computed."
    )

    rule_ablation_results = {
        "rule_check_on": {
            "overall_accuracy": rule_on_res["overall_compgraphrag_accuracy"],
            "accuracy_by_hop": rule_on_res["compgraphrag_accuracy_by_hop"],
            "mean_explanation_faithfulness_f1": rule_on_res["mean_explanation_faithfulness_f1"],
            "expected_calibration_error_ece": rule_on_res["expected_calibration_error_ece"],
            "statistical_validation": rule_on_res["statistical_validation"]
        },
        "rule_check_off": {
            "status": "NOT MEASURED",
            "reason": NOT_MEASURED_REASON
        }
    }

    # Consolidated Output Dictionary
    ablation_summary = {
        "execution_metadata": {
            "benchmark_dataset": dataset_path,
            "total_queries": len(evaluator.dataset),
            "entity_linking_metrics": evaluator.evaluate_entity_linking(),
            "encoder_used": "real sentence-transformers (all-MiniLM-L6-v2)" if evaluator.scorer._get_encoder() else "hash fallback"
        },
        "hybrid_weight_sensitivity_sweep": weight_sweep_results,
        "hop_decay_factor_sweep": lambda_sweep_results,
        "rule_check_layer_ablation": rule_ablation_results
    }

    # Save to results/ablation_results.json
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)
    ablation_json_path = os.path.join(results_dir, "ablation_results.json")
    with open(ablation_json_path, "w") as f:
        json.dump(ablation_summary, f, indent=2)

    return ablation_summary

if __name__ == "__main__":
    summary = run_all_ablations()
    print("Ablation experiments complete. Results saved to results/ablation_results.json.")
