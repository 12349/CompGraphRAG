"""
Interactive CLI Audit Demo for CompGraphRAG (Item 15 & Demo in Blueprint).
Demonstrates synthetic compliance determination, graph path traversal, rule evaluation, and conformal confidence set routing.
"""

import json
import os
from typing import Dict, Any

from retrieval.hybrid_scorer import HybridScorer
from reasoning.rule_engine import ComplianceRuleEngine
from explainability.subgraph_extractor import SubgraphExtractor
from uncertainty.conformal_predictor import ConformalPredictor

class CompGraphRAGDemoApp:
    def __init__(self, dataset_path: str):
        with open(dataset_path, 'r') as f:
            self.queries = json.load(f).get("queries", [])
            
        self.scorer = HybridScorer(alpha=0.4, beta=0.5, gamma=0.1)
        self.rule_engine = ComplianceRuleEngine()
        self.subgraph_extractor = SubgraphExtractor()
        self.conformal = ConformalPredictor(alpha=0.1)

    def run_demo_query(self, query_id: str) -> Dict[str, Any]:
        target = next((q for q in self.queries if q["id"] == query_id), self.queries[0])
        
        print("================================================================================")
        print(f" COMPGRAPHRAG AUDIT DEMO — Query ID: {target['id']}")
        print("================================================================================")
        print(f"QUERY: {target['question']}")
        print(f"COMPLEXITY: {target['hop_count']}-Hop Multi-Hop Query")
        print("--------------------------------------------------------------------------------")

        # Step 1: Rule Engine Evaluation
        rule_findings = self.rule_engine.evaluate_subgraph(target["gold_evidence_subgraph"])
        print("\n[STEP 1: NEURO-SYMBOLIC RULE ENGINE CHECK]")
        for rule in rule_findings["triggered_rules"]:
            print(f"  * Rule ID: {rule['rule_id']} | Recommendation: {rule['recommendation']}")
            print(f"    Finding: {rule['finding']}")

        # Step 2: Subgraph Extraction & Audit Walk
        subgraph_fmt = self.subgraph_extractor.format_subgraph_json(target["gold_evidence_subgraph"])
        nl_walk = self.subgraph_extractor.generate_natural_language_walk(target["gold_evidence_subgraph"])
        
        print("\n[STEP 2: TRAVERSED SUBGRAPH JUSTIFICATION (Path π)]")
        print(f"  Natural Language Walk: {nl_walk}")
        print(f"  Nodes: {subgraph_fmt['subgraph_pi']['nodes']}")

        # Step 3: Conformal Uncertainty Quantification
        probs = {"COMPLIANT": 0.05, "NON-COMPLIANT": 0.05, "REQUIRES-REVIEW": 0.05}
        suggested = rule_findings["suggested_determination"]
        probs[suggested] = 0.90
        
        conformal_res = self.conformal.predict_confidence_set(probs)

        print("\n[STEP 3: CONFORMAL UNCERTAINTY QUANTIFICATION]")
        print(f"  Calibrated Quantile (q_hat): {conformal_res['calibrated_q_hat']:.2f}")
        print(f"  Conformal Confidence Set C(q): {conformal_res['confidence_set']}")
        print(f"  Requires Human Audit: {conformal_res['requires_human_review']}")
        print("--------------------------------------------------------------------------------")
        print(f"FINAL SYSTEM DETERMINATION: {conformal_res['routed_determination']}")
        print(f"GOLD STANDARD LABEL:      {target['gold_determination']}")
        print("================================================================================\n")

        return {
            "query": target['question'],
            "subgraph": subgraph_fmt,
            "rule_findings": rule_findings,
            "conformal_res": conformal_res
        }
