"""
CompGraphRAG Main System Launcher & Benchmark Execution Runner.
"""

import sys
import os
import argparse
import json

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eval.eval_harness import CompGraphRAGEvaluator
from demo.app import CompGraphRAGDemoApp

def main():
    parser = argparse.ArgumentParser(description="CompGraphRAG Benchmark Runner")
    parser.add_argument("--stats", action="store_true", help="Run pre-registered statistical validation tests")
    parser.add_argument("--baselines", action="store_true", help="Run comparative benchmark across all baselines")
    parser.add_argument("--force-hash-fallback", action="store_true", help="Force HybridScorer to use hash pseudo-embedding fallback for isolation testing")
    args = parser.parse_args()

    dataset_path = os.path.join(os.path.dirname(__file__), "datasets", "hipaa_gold_dataset.json")
    
    print("--------------------------------------------------------------------------------")
    print(" EXECUTING COMPGRAPHRAG BENCHMARK EVALUATION HARNESS")
    print("--------------------------------------------------------------------------------")
    evaluator = CompGraphRAGEvaluator(dataset_path=dataset_path, force_hash_fallback=args.force_hash_fallback)
    results = evaluator.run_evaluation(run_stats=args.stats)
    
    exec_meta = results.get("execution_metadata", {})
    print(f"Encoder Used: {exec_meta.get('encoder_used', 'unknown')}")
    print(f"Confidence Signal Source: {exec_meta.get('confidence_signal_source', 'unknown')}")
    print(f"Total Queries Evaluated: {results['total_queries_evaluated']} (Calibration: {exec_meta.get('calibration_split_size')}, Test: {exec_meta.get('test_split_size')})")
    print(f"Overall CompGraphRAG Accuracy: {results['overall_compgraphrag_accuracy']*100:.1f}%")
    print(f"Overall Vector RAG Baseline Accuracy: {results['overall_vector_rag_accuracy']*100:.1f}%")
    
    print(f"\nPer-Hop Absolute Accuracy & Marginal Benefit Breakdown:")
    cg_hops = results.get("compgraphrag_accuracy_by_hop", {})
    vec_hops = results.get("vector_rag_accuracy_by_hop", {})
    for hop in ["1", "2", "3", "4"]:
        cg_a = cg_hops.get(hop, 0.0) * 100
        v_a = vec_hops.get(hop, 0.0) * 100
        diff = cg_a - v_a
        print(f"  * {hop}-Hop Tier: CompGraphRAG = {cg_a:.1f}%, Vector-RAG = {v_a:.1f}% (Marginal Benefit = {diff:+.1f}%)")
    
    print(f"\nMean Explanation Faithfulness F1 Score: {results['mean_explanation_faithfulness_f1']:.4f}")
    print(f"Expected Calibration Error (ECE): {results['expected_calibration_error_ece']:.4f}")

    if "per_item_faithfulness" in results:
        print("\n--------------------------------------------------------------------------------")
        print(" PER-ITEM FAITHFULNESS METRICS (ALL EVALUATED QUERIES)")
        print("--------------------------------------------------------------------------------")
        for item_rec in results["per_item_faithfulness"]:
            fm = item_rec["faithfulness_metrics"]
            print(f"  * [{item_rec['id']}] ({item_rec['hop_count']}-Hop Tier): P = {fm['precision']:.4f}, R = {fm['recall']:.4f}, F1 = {fm['f1']:.4f}")

    if args.stats:
        print("\n--------------------------------------------------------------------------------")
        print(" PRE-REGISTERED STATISTICAL VALIDATION RESULTS")
        print("--------------------------------------------------------------------------------")
        stats = results["statistical_validation"]
        paired = stats["paired_difference"]
        print(f"Paired t-test Mean Diff: {paired['mean_diff']:+.4f} (t-statistic: {paired['t_statistic']:.4f}, p = {paired['t_p_value']:.4e})")
        print(f"Wilcoxon Signed-Rank p-value: {paired['wilcoxon_p_value']:.4e}")
        
        hb = stats.get("holm_bonferroni", {})
        print(f"Holm-Bonferroni Adjusted p-values (Hypotheses Tested: {hb.get('hypotheses_tested_count')}): {hb.get('adjusted_p_values')}")
        
        tost = stats.get("tost_equivalence", {})
        print(f"TOST Equivalence Status: {tost.get('status')} ({tost.get('reason')})")

    if args.baselines or args.stats:
        print("\n--------------------------------------------------------------------------------")
        print(" BASELINES COMPARATIVE SUMMARY")
        print("--------------------------------------------------------------------------------")
        for b_name, b_info in results["all_baselines_summary"].items():
            if b_info.get("status") == "EXECUTED":
                print(f"  * {b_name:15s} [EXECUTED]     Mean Acc: {b_info['mean_accuracy']*100:.1f}% (std: {b_info['std_accuracy']:.4f})")
            else:
                print(f"  * {b_name:15s} [NOT MEASURED] {b_info.get('reason')}")

    print("\n--------------------------------------------------------------------------------")
    print(" RUNNING INTERACTIVE SAMPLE AUDIT DEMOS")
    print("--------------------------------------------------------------------------------")
    demo_app = CompGraphRAGDemoApp(dataset_path=dataset_path)
    demo_app.run_demo_query("Q07-2HOP")
    demo_app.run_demo_query("Q13-3HOP")

    print(f"\n[INFO] Raw execution metrics saved to results/eval_results_raw.json")

if __name__ == "__main__":
    main()
