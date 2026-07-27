"""
Unit tests for TBoxSchemaValidator component.
"""

import os
import unittest
from schema.schema_validator import TBoxSchemaValidator

class TestTBoxSchemaValidator(unittest.TestCase):
    def test_tbox_schema_validation(self):
        tbox_file = os.path.join(os.path.dirname(__file__), "..", "schema", "hipaa_tbox.json")
        validator = TBoxSchemaValidator(tbox_file)
        
        triples = [
            {"source": "CoveredEntity_A", "relation": "disclosesPHITo", "target": "CloudVendor_B"},
            {"source": "CloudVendor_B", "relation": "lacksAgreement", "target": "BAA_Document"}
        ]
        
        res = validator.validate_triples(triples)
        self.assertIn("schema_conformance_rate", res)
        self.assertEqual(res["schema_conformance_rate"], 100.0)

if __name__ == "__main__":
    unittest.main()
