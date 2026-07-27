"""
CompGraphRAG Main System Launcher & Benchmark Execution Runner.
"""

import sys
import os
import json
import argparse

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eval.eval_harness import CompGraphRAGEvaluator
from demo.app import CompGraphRAGDemoApp

def main():
    parser = argparse.ArgumentParser(description="CompGraphRAG System Launcher & Evaluation Runner")
    parser.add_argument("--stats", action="store_true", help="Include pre-registered statistical validation tests")
    args = parser.parse_args()

    dataset_path = os.path.join(os.path.dirname(__file__), "datasets", "hipaa_gold_dataset.json")
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    results_file = os.path.join(results_dir, "eval_results_raw.json")
    
    print("--------------------------------------------------------------------------------")
    print(" EXECUTING COMPGRAPHRAG BENCHMARK EVALUATION HARNESS")
    print("--------------------------------------------------------------------------------")
    evaluator = CompGraphRAGEvaluator(dataset_path=dataset_path)
    results = evaluator.run_evaluation(include_stats=args.stats)
    
    # Save raw results JSON to results/
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Dataset Size: {results['dataset_total_queries']} queries")
    print(f"Overall CompGraphRAG F1/Accuracy: {results['overall_compgraphrag_accuracy']*100:.1f}%")
    print(f"Overall Vector RAG Baseline Accuracy: {results['overall_vector_rag_accuracy']*100:.1f}%")
    print(f"Hop-Scaling Marginal Benefit (H1 - H4):")
    for hop, benefit in results['hop_marginal_benefit_h4_h8'].items():
        print(f"  * {hop}-Hop Query Benefit over Vector Baseline: +{benefit*100:.1f}%")
    print(f"Mean Explanation Faithfulness F1 Score: {results['mean_explanation_faithfulness_f1']:.4f}")
    print(f"Expected Calibration Error (ECE): {results['expected_calibration_error_ece']:.4f}\n")

    if args.stats and "statistical_validation" in results:
        stats = results["statistical_validation"]
        print("--------------------------------------------------------------------------------")
        print(" PRE-REGISTERED STATISTICAL VALIDATION REPORT")
        print("--------------------------------------------------------------------------------")
        print(f"  * Paired t-statistic: {stats['paired_difference']['t_statistic']:.4f} (p-value: {stats['paired_difference']['t_p_value']:.6f})")
        print(f"  * Wilcoxon signed-rank p-value: {stats['paired_difference']['wilcoxon_p_value']:.6f}")
        print(f"  * Holm-Bonferroni adjusted p-values: {stats['holm_bonferroni_adjusted_p_values']}")
        print(f"  * TOST Equivalence p-value: {stats['tost_equivalence']['tost_p_value']:.6f} (Statistically Equivalent: {stats['tost_equivalence']['is_statistically_equivalent']})\n")

    print(f"Raw evaluation metrics saved to: {results_file}\n")

    print("--------------------------------------------------------------------------------")
    print(" RUNNING INTERACTIVE SAMPLE AUDIT DEMOS")
    print("--------------------------------------------------------------------------------")
    demo_app = CompGraphRAGDemoApp(dataset_path=dataset_path)
    demo_app.run_demo_query("Q07-HIPAA-2HOP")
    demo_app.run_demo_query("Q13-HIPAA-3HOP")

if __name__ == "__main__":
    main()
