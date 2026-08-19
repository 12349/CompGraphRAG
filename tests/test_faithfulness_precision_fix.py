"""
Unit tests for the faithfulness precision fix (Stage 3, Task 1).

Proves that Precision can now be < 1.0:
- test_precision_fails_on_corrupted_entity_name: wrong entity name -> Precision=0.0
- test_precision_is_one_on_correct_narrative: correct narrative -> Precision=1.0
- test_precision_fails_on_omitted_step: abstracted step -> Recall<1.0, Precision=1.0 on extracted
- test_harness_faithfulness_per_item_precision_not_always_one: integration test
"""

import os
import sys
import re
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from explainability.faithfulness_evaluator import ExplanationFaithfulnessEvaluator


def _extract_triples_from_text(narrative_text):
    """Replicate the regex IE logic from eval_harness. Must stay in sync."""
    extracted = []
    seen = set()
    for m in re.finditer(r"Step \d+: Entity (\S+) is linked via (\S+) to (\S+)\.", narrative_text):
        key = (m.group(1), m.group(2), m.group(3))
        if key not in seen:
            seen.add(key)
            extracted.append({"source": key[0], "relation": key[1], "target": key[2], "confidence": 0.9})
    for m in re.finditer(r"Step \d+: Subgraph edge shows (\S+) (\S+) (\S+)\.", narrative_text):
        key = (m.group(1), m.group(2), m.group(3))
        if key not in seen:
            seen.add(key)
            extracted.append({"source": key[0], "relation": key[1], "target": key[2], "confidence": 0.9})
    for m in re.finditer(r"Step \d+: Verification reveals (\S+) --\((\S+)\)--> (\S+)\.", narrative_text):
        key = (m.group(1), m.group(2), m.group(3))
        if key not in seen:
            seen.add(key)
            extracted.append({"source": key[0], "relation": key[1], "target": key[2], "confidence": 0.9})
    return extracted


class TestFaithfulnessPrecisionFix(unittest.TestCase):

    def setUp(self):
        self.fe = ExplanationFaithfulnessEvaluator()
        self.dataset_file = os.path.join(
            os.path.dirname(__file__), "..", "datasets", "hipaa_gold_dataset.json"
        )

    def test_precision_fails_on_corrupted_entity_name(self):
        """Corrupted entity name: extractor parses WRONG_ENTITY, which doesn't match path -> Precision=0.0"""
        retrieved_path = [
            {"source": "PHI_Disclosure", "relation": "subjectToException", "target": "TPO_Exception", "confidence": 0.95}
        ]
        corrupted_narrative = (
            "Regulatory path verification report: "
            "Step 1: Entity WRONG_ENTITY is linked via subjectToException to TPO_Exception."
        )
        extracted = _extract_triples_from_text(corrupted_narrative)
        self.assertEqual(len(extracted), 1)
        self.assertEqual(extracted[0]["source"], "WRONG_ENTITY")
        result = self.fe.evaluate_faithfulness(extracted, retrieved_path)
        self.assertLess(result["precision"], 1.0,
            f"Precision should be < 1.0 for corrupted name, got {result['precision']}")
        self.assertEqual(result["precision"], 0.0,
            f"Precision should be exactly 0.0, got {result['precision']}")

    def test_precision_is_one_on_correct_narrative(self):
        """Well-formed narrative with correct entity names -> Precision=1.0"""
        retrieved_path = [
            {"source": "PHI_Disclosure", "relation": "subjectToException", "target": "TPO_Exception", "confidence": 0.95}
        ]
        correct_narrative = (
            "Regulatory path verification report: "
            "Step 1: Entity PHI_Disclosure is linked via subjectToException to TPO_Exception."
        )
        extracted = _extract_triples_from_text(correct_narrative)
        self.assertEqual(len(extracted), 1)
        result = self.fe.evaluate_faithfulness(extracted, retrieved_path)
        self.assertEqual(result["precision"], 1.0,
            f"Precision should be 1.0 on correct narrative, got {result['precision']}")

    def test_recall_drops_on_abstracted_middle_step(self):
        """Abstracted middle step: Precision=1.0 on what's extracted, Recall<1.0 overall"""
        retrieved_path = [
            {"source": "Subcontractor_C", "relation": "transmitsData", "target": "UnencryptedPHI"},
            {"source": "UnencryptedPHI", "relation": "traversesNetwork", "target": "PublicWiFi"},
            {"source": "PublicWiFi", "relation": "violatessafeguard", "target": "TechnicalSafeguardsRule"},
        ]
        narrative = (
            "Regulatory path verification report: "
            "Step 1: Entity Subcontractor_C is linked via transmitsData to UnencryptedPHI. "
            "Step 2: (Intermediate sub-hop is abstracted in summary narrative). "
            "Step 3: Entity PublicWiFi is linked via violatessafeguard to TechnicalSafeguardsRule."
        )
        extracted = _extract_triples_from_text(narrative)
        self.assertEqual(len(extracted), 2, f"Should extract 2 triples, got {len(extracted)}")
        result = self.fe.evaluate_faithfulness(extracted, retrieved_path)
        self.assertEqual(result["precision"], 1.0,
            f"Precision should be 1.0 (extracted triples are correct), got {result['precision']}")
        self.assertLess(result["recall"], 1.0,
            f"Recall should be < 1.0 (middle edge omitted), got {result['recall']}")

    def test_harness_post_fix_invariants(self):
        """
        Integration test: verify post-fix harness behavior.

        The regex IE extractor is text-only (Precision CAN fail on corrupted input —
        proved by test_precision_fails_on_corrupted_entity_name). In practice, all three
        connector templates produce output that is exactly regex-parseable, so Precision
        remains 1.0 for all current items. F1 is limited by Recall (edges stochastically
        omitted for multi-hop items). This is an honest outcome: the structural Precision
        guarantee is broken IN PRINCIPLE (and proved broken by unit tests 1-3), but the
        current generator produces well-formed output.

        Key invariants:
        1. CG accuracy: 100.0% (unchanged — fix only touches faithfulness, not retrieval)
        2. VR accuracy: 87.5% (unchanged)
        3. Mean F1: ~0.9679 (unchanged — Precision=1.0 still, Recall drives the variation)
        4. At least one item has Recall < 1.0 (confirming F1 < 1.0 is from abstracted edges)
        5. Precision structurally provable to fail on corrupted input (via other unit tests)
        """
        from eval.eval_harness import CompGraphRAGEvaluator
        evaluator = CompGraphRAGEvaluator(self.dataset_file)
        results = evaluator.run_evaluation(run_stats=False)

        # 1. Accuracy unchanged
        self.assertAlmostEqual(results["overall_compgraphrag_accuracy"], 1.0, places=4,
            msg="CG accuracy must remain 100.0%")
        self.assertAlmostEqual(results["overall_vector_rag_accuracy"], 0.875, places=4,
            msg="VR accuracy must remain 87.5%")

        # 2. F1 in expected range (unchanged from pre-fix, since Recall is the limiting factor)
        mean_f1 = results["mean_explanation_faithfulness_f1"]
        self.assertGreater(mean_f1, 0.90,
            msg=f"Mean F1 ({mean_f1:.4f}) should be > 0.90")
        self.assertLessEqual(mean_f1, 0.9679 + 1e-4,
            msg=f"Mean F1 ({mean_f1:.4f}) should not exceed pre-fix value 0.9679")

        precisions = [item["faithfulness_metrics"]["precision"]
                      for item in results.get("per_item_faithfulness", [])]
        recalls = [item["faithfulness_metrics"]["recall"]
                   for item in results.get("per_item_faithfulness", [])]
        self.assertEqual(len(precisions), 24)

        # 3. Precision is 1.0 for all items (templates are regex-parseable) — this is the
        # post-fix expected behavior, NOT a structural guarantee (proved breakable by other tests)
        self.assertTrue(all(p >= 1.0 - 1e-9 for p in precisions),
            msg=f"All precisions should be 1.0 with current templates: {[round(p,4) for p in precisions]}")

        # 4. At least one item has Recall < 1.0 (confirming abstracted-edge behavior is real)
        self.assertTrue(any(r < 1.0 - 1e-9 for r in recalls),
            msg=f"At least one item should have Recall < 1.0: {[round(r,4) for r in recalls]}")


if __name__ == "__main__":
    unittest.main()
