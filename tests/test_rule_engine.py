"""
Unit tests for ComplianceRuleEngine component.
"""

import unittest
from reasoning.rule_engine import ComplianceRuleEngine

class TestComplianceRuleEngine(unittest.TestCase):
    def test_rule_engine_baa_lacking(self):
        engine = ComplianceRuleEngine()
        path = [
            {"source": "CoveredEntity_A", "relation": "disclosesPHITo", "target": "CloudVendor_B"},
            {"source": "CloudVendor_B", "relation": "lacksAgreement", "target": "BAA_Document"}
        ]
        res = engine.evaluate_subgraph(path)
        self.assertEqual(res["suggested_determination"], "NON-COMPLIANT")
        self.assertGreaterEqual(len(res["triggered_rules"]), 1)

    def test_rule_engine_tpo_exception(self):
        engine = ComplianceRuleEngine()
        path = [
            {"source": "PHI_Disclosure", "relation": "subjectToException", "target": "TPO_Exception"}
        ]
        res = engine.evaluate_subgraph(path)
        self.assertEqual(res["suggested_determination"], "COMPLIANT")

if __name__ == "__main__":
    unittest.main()
