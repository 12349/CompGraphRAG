"""
TBox Schema Conformance Rate Validator for CompGraphRAG Knowledge Graph Extraction.
Validates extracted knowledge graph triples against formal HIPAA TBox ontology definitions.
"""

import json
from typing import List, Dict, Any

class TBoxSchemaValidator:
    def __init__(self, tbox_path: str):
        with open(tbox_path, 'r') as f:
            tbox = json.load(f)
            self.classes = set(tbox.get("classes", []))
            self.relation_domain = tbox.get("relation_domain", {})
            self.relation_range = tbox.get("relation_range", {})

    def validate_triples(self, triples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates TBox Schema Conformance Rate (SCR).
        SCR = (valid_triples / total_triples) * 100
        """
        if not triples:
            return {"conformance_rate": 100.0, "total_triples": 0, "valid_triples": 0}

        valid_count = 0
        violations = []

        for t in triples:
            rel = t.get("relation", "")
            domain_ok = True
            range_ok = True

            # Domain check if specified
            if rel in self.relation_domain:
                expected_dom = self.relation_domain[rel]
                actual_dom = t.get("source_type", expected_dom)
                if actual_dom != expected_dom:
                    domain_ok = False

            # Range check if specified
            if rel in self.relation_range:
                expected_rng = self.relation_range[rel]
                actual_rng = t.get("target_type", expected_rng)
                if actual_rng != expected_rng:
                    range_ok = False

            if domain_ok and range_ok:
                valid_count += 1
            else:
                violations.append({"triple": t, "domain_valid": domain_ok, "range_valid": range_ok})

        scr = (valid_count / len(triples)) * 100.0
        return {
            "schema_conformance_rate": float(scr),
            "total_triples": len(triples),
            "valid_triples": valid_count,
            "violations_count": len(violations),
            "violations": violations
        }
