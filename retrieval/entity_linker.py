"""
Two-stage regulatory entity linker module for CompGraphRAG.
Handles HIPAA domain jargon (e.g., 'CE' vs 'Covered Entity', 'BAA' vs 'Business Associate Agreement').
"""

from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple
import numpy as np

class EntityLinker:
    def __init__(self, knowledge_graph_nodes: List[Dict[str, Any]]):
        self.nodes = knowledge_graph_nodes
        self.synonym_map = {
            "ce": "Covered Entity",
            "covered entity": "Covered Entity",
            "baa": "Business Associate Agreement",
            "business associate": "Business Associate",
            "ba": "Business Associate",
            "phi": "Protected Health Information",
            "tpo": "Treatment, Payment, and Operations",
            "minimum necessary": "Minimum Necessary Standard"
        }

    def string_similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def link_entity(self, query_mention: str, mention_emb: np.ndarray = None, top_m: int = 3) -> List[Tuple[str, float]]:
        """
        Links a query mention to top-m graph nodes using fuzzy string match and domain synonym lookup.
        Returns list of (node_id, confidence_score).
        """
        clean_mention = query_mention.strip().lower()
        if clean_mention in self.synonym_map:
            target_canonical = self.synonym_map[clean_mention]
            for node in self.nodes:
                if node.get("label", "").lower() == target_canonical.lower():
                    return [(node["id"], 1.0)]

        scored_nodes = []
        for node in self.nodes:
            label_sim = self.string_similarity(query_mention, node.get("label", ""))
            
            # Embedding similarity if available
            emb_sim = 0.0
            if mention_emb is not None and "embedding" in node:
                norm_a = np.linalg.norm(mention_emb)
                norm_b = np.linalg.norm(node["embedding"])
                if norm_a > 0 and norm_b > 0:
                    emb_sim = max(0.0, float(np.dot(mention_emb, node["embedding"]) / (norm_a * norm_b)))
            
            combined_score = 0.6 * label_sim + 0.4 * emb_sim
            scored_nodes.append((node["id"], float(combined_score)))

        scored_nodes.sort(key=lambda x: x[1], reverse=True)
        return scored_nodes[:top_m]
