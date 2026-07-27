import unittest
from uncertainty.conformal_predictor import ConformalPredictor

class TestConformalPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = ConformalPredictor(alpha=0.1)

    def test_calibration(self):
        val_scores = [0.95, 0.92, 0.88, 0.90, 0.96, 0.91]
        self.predictor.calibrate(val_scores, [0]*len(val_scores))
        self.assertLessEqual(self.predictor.q_hat, 0.20)

    def test_unambiguous_prediction(self):
        probs = {"COMPLIANT": 0.92, "NON-COMPLIANT": 0.04, "REQUIRES-REVIEW": 0.04}
        res = self.predictor.predict_confidence_set(probs)
        self.assertEqual(res["routed_determination"], "COMPLIANT")
        self.assertFalse(res["requires_human_review"])

if __name__ == "__main__":
    unittest.main()
