"""
Pre-registered Statistical Validation Suite for CompGraphRAG (Items 9 & 10 in Blueprint).
Includes TOST equivalence testing, ECE calibration error calculation, and Holm-Bonferroni adjustment.
"""

import numpy as np
from scipy import stats
from typing import List, Dict, Any, Tuple

class StatisticalValidator:
    def compute_ece(self, confidences: List[float], accuracies: List[int], num_bins: int = 10) -> float:
        """
        Calculates Expected Calibration Error (ECE).
        """
        if not confidences:
            return 0.0

        bin_boundaries = np.linspace(0, 1, num_bins + 1)
        ece = 0.0
        n = len(confidences)

        for i in range(num_bins):
            bin_lower, bin_upper = bin_boundaries[i], bin_boundaries[i+1]
            in_bin = [(c, a) for c, a in zip(confidences, accuracies) if bin_lower <= c < bin_upper]
            
            if in_bin:
                bin_acc = np.mean([a for _, a in in_bin])
                bin_conf = np.mean([c for c, _ in in_bin])
                bin_weight = len(in_bin) / n
                ece += bin_weight * abs(bin_acc - bin_conf)

        return float(ece)

    def paired_difference_test(self, scores_a: List[float], scores_b: List[float]) -> Dict[str, float]:
        """
        Performs paired t-test and Wilcoxon signed-rank test.
        """
        diffs = np.array(scores_a) - np.array(scores_b)
        t_stat, t_p = stats.ttest_rel(scores_a, scores_b)
        
        try:
            w_stat, w_p = stats.wilcoxon(scores_a, scores_b)
        except Exception:
            w_stat, w_p = 0.0, 1.0

        return {
            "mean_diff": float(np.mean(diffs)),
            "std_diff": float(np.std(diffs)),
            "t_statistic": float(t_stat),
            "t_p_value": float(t_p),
            "wilcoxon_p_value": float(w_p)
        }

    def tost_equivalence_test(self, 
                              scores_a: List[float], 
                              scores_b: List[float], 
                              margin: float = 0.05) -> Dict[str, Any]:
        """
        Two One-Sided Tests (TOST) for equivalence (used for deployment constraint degradation testing).
        """
        diffs = np.array(scores_a) - np.array(scores_b)
        mean_d = np.mean(diffs)
        std_d = np.std(diffs, ddof=1)
        n = len(diffs)
        se = std_d / np.sqrt(n)

        # Lower boundary test: H01: mean_d <= -margin
        t1 = (mean_d - (-margin)) / se
        p1 = 1 - stats.t.cdf(t1, df=n-1)

        # Upper boundary test: H02: mean_d >= margin
        t2 = (mean_d - margin) / se
        p2 = stats.t.cdf(t2, df=n-1)

        tost_p = max(p1, p2)
        is_equivalent = tost_p < 0.05

        return {
            "margin": margin,
            "mean_difference": float(mean_d),
            "tost_p_value": float(tost_p),
            "is_statistically_equivalent": bool(is_equivalent)
        }

    def holm_bonferroni_adjustment(self, p_values: List[float]) -> List[float]:
        """
        Adjusts p-values for multiple comparisons across hypotheses.
        """
        m = len(p_values)
        indexed_p = sorted(enumerate(p_values), key=lambda x: x[1])
        adjusted = [0.0] * m

        for k, (orig_idx, p) in enumerate(indexed_p):
            adj_p = min(1.0, p * (m - k))
            adjusted[orig_idx] = float(adj_p)

        return adjusted
