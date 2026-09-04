"""
Neuro-symbolic compliance rule check engine for CompGraphRAG.
Evaluates graph path entities against declarative HIPAA exception/obligation rules to produce the final compliance determination.
"""

import json
from typing import List, Dict, Any

class ComplianceRuleEngine:
    def __init__(self, rules_file_path: str = None):
        self.rules = []
        if rules_file_path:
            with open(rules_file_path, 'r') as f:
                self.rules = json.load(f).get("rules", [])

    def evaluate_subgraph(self, path_edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates a candidate retrieved subgraph path.
        Returns rule findings dictionary: {"triggered_rules": [...], "suggested_determination": "..."}
        """
        triggered_rules = []
        node_labels = set()
        relations = set()

        for edge in path_edges:
            s = str(edge.get("source", edge.get("subject", ""))).lower()
            t = str(edge.get("target", edge.get("object", ""))).lower()
            r = str(edge.get("relation", "")).lower()
            node_labels.add(s)
            node_labels.add(t)
            relations.add(r)

        suggested = "REQUIRES-REVIEW"

        # Rule 1: BAA Lacking / Breach
        if "lacksagreement" in relations or any("lacks" in r for r in relations):
            triggered_rules.append({
                "rule_id": "RULE-HIPAA-BAA-REQUIRED",
                "finding": "PHI disclosed to entity without executed Business Associate Agreement.",
                "recommendation": "NON-COMPLIANT"
            })
            suggested = "NON-COMPLIANT"
        # Rule 2: Psychotherapy / Safeguard Violation
        elif "excludedfrom" in relations or "violatessafeguard" in relations:
            triggered_rules.append({
                "rule_id": "RULE-HIPAA-MIN-NECESSARY",
                "finding": "Action violates minimum necessary standard or security safeguard rule.",
                "recommendation": "NON-COMPLIANT"
            })
            suggested = "NON-COMPLIANT"
        # Rule 3: TPO Exception / IRB Waiver / Treatment
        elif "subjecttoexception" in relations or "satisfiesstandard" in relations or "qualifiesas" in relations:
            triggered_rules.append({
                "rule_id": "RULE-HIPAA-TPO-EXCEPTION",
                "finding": "Disclosure satisfies statutory exception or regulatory waiver requirements.",
                "recommendation": "COMPLIANT"
            })
            suggested = "COMPLIANT"

        return {
            "triggered_rules": triggered_rules,
            "suggested_determination": suggested,
            "rule_count": len(triggered_rules)
        }
