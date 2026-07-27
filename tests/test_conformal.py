"""
Unit tests for ConformalPredictor component.
"""

import unittest
from uncertainty.conformal_predictor import ConformalPredictor

class TestConformalPredictor(unittest.TestCase):
    def test_conformal_prediction_set(self):
        predictor = ConformalPredictor(alpha=0.1)
        predictor.calibrate([0.4, 0.45, 0.48], [0, 1, 0])
        
        # High confidence compliant query
        res_compliant = predictor.predict_confidence_set({"COMPLIANT": 0.95, "NON-COMPLIANT": 0.05})
        self.assertEqual(res_compliant["confidence_set"], ["COMPLIANT"])
        self.assertFalse(res_compliant["requires_human_review"])

        # Low confidence uncertain query
        res_uncertain = predictor.predict_confidence_set({"COMPLIANT": 0.42, "NON-COMPLIANT": 0.41})
        self.assertGreater(len(res_uncertain["confidence_set"]), 1)
        self.assertTrue(res_uncertain["requires_human_review"])

if __name__ == "__main__":
    unittest.main()
