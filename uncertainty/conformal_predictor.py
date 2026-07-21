"""
Model-agnostic Split Conformal Prediction module for CompGraphRAG (Item 9 in Blueprint).
Guarantees calibrated confidence sets C(q) with coverage probability >= 1 - alpha.
Routes low-confidence determinations to REQUIRES-REVIEW category.
"""

import numpy as np
from typing import List, Dict, Any, Tuple

class ConformalPredictor:
    def __init__(self, alpha: float = 0.1):
        """
        alpha: significance level (e.g., 0.1 for 90% target coverage).
        """
        self.alpha = alpha
        self.q_hat = 0.5  # default non-conformity threshold
        self.classes = ["COMPLIANT", "NON-COMPLIANT", "REQUIRES-REVIEW"]

    def calibrate(self, val_scores: List[float], val_true_class_indices: List[int]):
        """
        Calibrates the non-conformity score quantile q_hat on a validation set.
        val_scores: array of predicted probabilities for true classes.
        """
        if not val_scores:
            return

        # Non-conformity score: s_i = 1 - P(y_i | x_i)
        non_conformity_scores = [1.0 - score for score in val_scores]
        n = len(non_conformity_scores)
        
        # Compute quantile level (n + 1) * (1 - alpha) / n
        q_level = np.ceil((n + 1) * (1.0 - self.alpha)) / n
        q_level = min(1.0, max(0.0, q_level))
        
        self.q_hat = float(np.quantile(non_conformity_scores, q_level))

    def predict_confidence_set(self, class_probabilities: Dict[str, float]) -> Dict[str, Any]:
        """
        Generates conformal prediction set C(q) = { y : 1 - P(y|q) <= q_hat }.
        """
        confidence_set = []
        for cls, prob in class_probabilities.items():
            non_conformity = 1.0 - prob
            if non_conformity <= self.q_hat:
                confidence_set.append(cls)

        if not confidence_set:
            # Fallback to highest probability class if empty
            highest_cls = max(class_probabilities, key=class_probabilities.get)
            confidence_set.append(highest_cls)

        # Routing decision logic
        is_unambiguous = (len(confidence_set) == 1 and "REQUIRES-REVIEW" not in confidence_set)
        routed_determination = confidence_set[0] if is_unambiguous else "REQUIRES-REVIEW"

        return {
            "confidence_set": confidence_set,
            "set_size": len(confidence_set),
            "calibrated_q_hat": self.q_hat,
            "routed_determination": routed_determination,
            "requires_human_review": not is_unambiguous
        }
