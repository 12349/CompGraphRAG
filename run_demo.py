"""
CompGraphRAG Main System Launcher & Benchmark Execution Runner.
"""

import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eval.eval_harness import CompGraphRAGEvaluator
from demo.app import CompGraphRAGDemoApp

def main():
    dataset_path = os.path.join(os.path.dirname(__file__), "datasets", "hipaa_gold_dataset.json")
    
    print("--------------------------------------------------------------------------------")
    print(" EXECUTING COMPGRAPHRAG BENCHMARK EVALUATION HARNESS")
    print("--------------------------------------------------------------------------------")
    evaluator = CompGraphRAGEvaluator(dataset_path=dataset_path)
    results = evaluator.run_evaluation()
    
    print(f"Overall CompGraphRAG F1/Accuracy: {results['overall_compgraphrag_accuracy']*100:.1f}%")
    print(f"Overall Vector RAG Baseline Accuracy: {results['overall_vector_rag_accuracy']*100:.1f}%")
    print(f"Hop-Scaling Marginal Benefit (H4/H8):")
    for hop, benefit in results['hop_marginal_benefit_h4_h8'].items():
        print(f"  * {hop}-Hop Query Benefit over Vector Baseline: +{benefit*100:.1f}%")
    print(f"Mean Explanation Faithfulness F1 Score: {results['mean_explanation_faithfulness_f1']:.4f}")
    print(f"Expected Calibration Error (ECE): {results['expected_calibration_error_ece']:.4f}\n")

    print("--------------------------------------------------------------------------------")
    print(" RUNNING INTERACTIVE SAMPLE AUDIT DEMOS")
    print("--------------------------------------------------------------------------------")
    demo_app = CompGraphRAGDemoApp(dataset_path=dataset_path)
    demo_app.run_demo_query("Q2-HIPAA-2HOP")
    demo_app.run_demo_query("Q3-HIPAA-3HOP")

if __name__ == "__main__":
    main()
