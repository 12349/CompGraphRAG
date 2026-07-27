import unittest
import numpy as np
from retrieval.hybrid_scorer import HybridScorer

class TestHybridScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = HybridScorer(alpha=0.4, beta=0.5, gamma=0.1, decay_lambda=0.85)

    def test_weight_assertion(self):
        with self.assertRaises(AssertionError):
            HybridScorer(alpha=0.5, beta=0.5, gamma=0.5)

    def test_cosine_similarity(self):
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([1.0, 0.0, 0.0])
        v3 = np.array([0.0, 1.0, 0.0])
        
        self.assertAlmostEqual(self.scorer.cosine_similarity(v1, v2), 1.0)
        self.assertAlmostEqual(self.scorer.cosine_similarity(v1, v3), 0.0)

    def test_calculate_path_score(self):
        path = [
            {"relation_weight": 1.0, "confidence": 1.0, "hop": 1},
            {"relation_weight": 1.0, "confidence": 1.0, "hop": 2}
        ]
        # (1.0 + 0.85) / 2 = 0.925
        score = self.scorer.calculate_path_score(path)
        self.assertAlmostEqual(score, 0.925)

if __name__ == "__main__":
    unittest.main()
