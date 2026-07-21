"""
Quantitative explanation-faithfulness metric for CompGraphRAG (Item 8 in Blueprint).
Computes Precision & Recall between generated natural-language explanations and retrieved subgraphs π.
"""

from typing import List, Dict, Any, Tuple

class ExplanationFaithfulnessEvaluator:
    def evaluate_faithfulness(self, 
                              extracted_explanation_triples: List[Dict[str, Any]], 
                              retrieved_subgraph_edges: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Computes precision, recall, and F1 between explanation assertions and true retrieved edges in π.
        Supports both ('subject', 'relation', 'object') and ('source', 'relation', 'target') key mappings.
        """
        if not retrieved_subgraph_edges:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        def get_triple(e: Dict[str, Any]) -> Tuple[str, str, str]:
            s = str(e.get("subject", e.get("source", ""))).strip().lower()
            r = str(e.get("relation", "")).strip().lower()
            o = str(e.get("object", e.get("target", ""))).strip().lower()
            return (s, r, o)

        true_triples = set(get_triple(edge) for edge in retrieved_subgraph_edges)
        exp_triples = set(get_triple(triple) for triple in extracted_explanation_triples)

        if not exp_triples:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        # True Positives: explanation assertions present in true subgraph π
        tp = len(exp_triples.intersection(true_triples))
        
        precision = tp / len(exp_triples) if len(exp_triples) > 0 else 0.0
        recall = tp / len(true_triples) if len(true_triples) > 0 else 0.0
        
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1)
        }
