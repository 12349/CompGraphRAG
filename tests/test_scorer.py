"""
Unit tests for HybridScorer retrieval component.
"""

import unittest
import numpy as np
from retrieval.hybrid_scorer import HybridScorer

class TestHybridScorer(unittest.TestCase):
    def test_hybrid_scorer_init(self):
        scorer = HybridScorer(alpha=0.4, beta=0.5, gamma=0.1)
        self.assertEqual(scorer.alpha, 0.4)
        self.assertEqual(scorer.beta, 0.5)
        self.assertEqual(scorer.gamma, 0.1)

    def test_cosine_similarity(self):
        scorer = HybridScorer(alpha=0.4, beta=0.5, gamma=0.1)
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        vec3 = np.array([0.0, 1.0, 0.0])
        
        self.assertAlmostEqual(scorer.cosine_similarity(vec1, vec2), 1.0, places=5)
        self.assertAlmostEqual(scorer.cosine_similarity(vec1, vec3), 0.0, places=5)

    def test_text_encoding(self):
        scorer = HybridScorer(alpha=0.4, beta=0.5, gamma=0.1)
        emb1 = scorer.encode_text("HIPAA Privacy Rule")
        emb2 = scorer.encode_text("HIPAA Privacy Rule")
        emb3 = scorer.encode_text("Unrelated Random String Query")
        
        self.assertIsInstance(emb1, np.ndarray)
        self.assertAlmostEqual(scorer.cosine_similarity(emb1, emb2), 1.0, places=5)
        self.assertLess(scorer.cosine_similarity(emb1, emb3), 0.99)

    def test_candidate_ranking(self):
        scorer = HybridScorer(alpha=0.4, beta=0.5, gamma=0.1)
        candidates = [
            {"q_emb": np.array([1.0, 0.0]), "x_emb": np.array([0.0, 1.0]), "path": []},
            {"q_emb": np.array([1.0, 0.0]), "x_emb": np.array([1.0, 0.0]), "path": [{"relation_weight": 1.0, "confidence": 1.0, "hop": 1}]}
        ]
        ranked = scorer.rank_candidates(candidates)
        self.assertEqual(len(ranked), 2)
        self.assertGreater(ranked[0]["hybrid_score"], ranked[1]["hybrid_score"])

if __name__ == "__main__":
    unittest.main()
