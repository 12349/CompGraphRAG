import unittest
import os
from eval.eval_harness import CompGraphRAGEvaluator

class TestEvalHarness(unittest.TestCase):
    def setUp(self):
        self.dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datasets", "hipaa_gold_dataset.json")
        self.evaluator = CompGraphRAGEvaluator(self.dataset_path)

    def test_run_evaluation(self):
        results = self.evaluator.run_evaluation(run_stats=True)
        self.assertEqual(results["total_queries_evaluated"], 24)
        self.assertGreater(results["overall_compgraphrag_accuracy"], 0.80)
        self.assertIn("hop_marginal_benefit_h4_h8", results)
        self.assertIn("statistical_validation", results)

if __name__ == "__main__":
    unittest.main()
