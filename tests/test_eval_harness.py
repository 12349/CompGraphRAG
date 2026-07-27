"""
Unit tests for CompGraphRAGEvaluator.
"""

import os
import unittest
from eval.eval_harness import CompGraphRAGEvaluator

class TestEvalHarness(unittest.TestCase):
    def test_eval_harness_run(self):
        dataset_file = os.path.join(os.path.dirname(__file__), "..", "datasets", "hipaa_gold_dataset.json")
        evaluator = CompGraphRAGEvaluator(dataset_file)
        results = evaluator.run_evaluation(include_stats=True)
        
        self.assertEqual(results["dataset_total_queries"], 24)
        self.assertEqual(results["overall_compgraphrag_accuracy"], 1.0)
        self.assertIn("statistical_validation", results)
        self.assertIn("t_statistic", results["statistical_validation"]["paired_difference"])

if __name__ == "__main__":
    unittest.main()
