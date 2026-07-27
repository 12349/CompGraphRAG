import unittest
from reasoning.rule_engine import ComplianceRuleEngine

class TestComplianceRuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ComplianceRuleEngine()

    def test_baa_lacking_rule(self):
        path = [
            {"source": "CoveredEntity_A", "relation": "disclosesPHITo", "target": "CloudVendor_B"},
            {"source": "CloudVendor_B", "relation": "lacksAgreement", "target": "BAA_Document"}
        ]
        res = self.engine.evaluate_subgraph(path)
        self.assertEqual(res["suggested_determination"], "NON-COMPLIANT")
        self.assertEqual(len(res["triggered_rules"]), 1)
        self.assertEqual(res["triggered_rules"][0]["rule_id"], "RULE-HIPAA-BAA-REQUIRED")

    def test_tpo_exception_rule(self):
        path = [
            {"source": "PHI_Disclosure", "relation": "subjectToException", "target": "TPO_Exception"}
        ]
        res = self.engine.evaluate_subgraph(path)
        self.assertEqual(res["suggested_determination"], "COMPLIANT")

if __name__ == "__main__":
    unittest.main()
