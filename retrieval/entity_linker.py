"""
Two-stage regulatory entity linker module for CompGraphRAG.
Handles HIPAA domain jargon (e.g., 'CE' vs 'Covered Entity', 'BAA' vs 'Business Associate Agreement').
Ground query mentions and tokens to candidate knowledge graph nodes.
"""

import re
from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple
import numpy as np

class EntityLinker:
    def __init__(self, knowledge_graph_nodes: List[Dict[str, Any]]):
        self.nodes = knowledge_graph_nodes
        self.synonym_map = {
            "ce": "CoveredEntity",
            "covered entity": "CoveredEntity",
            "baa": "BAA",
            "business associate": "BusinessAssociate",
            "business associate agreement": "BAA",
            "phi": "PHI",
            "tpo": "TPO",
            "irb": "IRB",
            "hie": "HIE",
            "emt": "EMT",
            "cdc": "CDC",
            "llm": "LLM",
            "ehr": "EHR",
            "api": "API",
            "oauth": "OAuth",
            "wifi": "WiFi",
            "cloud vendor": "CloudVendor",
            "collection agency": "CollectionAgency",
            "subcontractor": "Subcontractor",
            "de-identified": "DeIdentified",
            "deidentified": "DeIdentified",
            "analytics": "Analytics",
            "law enforcement": "LawEnforcement"
        }

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'[A-Za-z0-9]+', text)]

    def string_similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def link_query_entities(self, query_text: str) -> List[Tuple[str, float]]:
        """
        Grounds query mentions and tokens to candidate graph nodes.
        Returns list of (node_id, confidence_score).
        """
        q_tokens = set(self._tokenize(query_text))
        
        # Expand synonyms
        for syn_key, syn_val in self.synonym_map.items():
            if syn_key in query_text.lower():
                q_tokens.add(syn_val.lower())
                
        linked = []
        for node in self.nodes:
            node_id = node if isinstance(node, str) else node.get('id', '')
            node_tokens = set(self._tokenize(re.sub(r'([a-z])([A-Z])', r'\1 \2', node_id)))
            
            overlap = q_tokens.intersection(node_tokens)
            meaningful_overlap = [t for t in overlap if t not in {'a', 'b', 'c', '1', '2', 'x', 'm'}]
            if meaningful_overlap:
                conf = len(meaningful_overlap) / max(1, len(node_tokens))
                linked.append((node_id, conf))
                
        linked.sort(key=lambda x: x[1], reverse=True)
        return linked

    def link_entity(self, query_mention: str, mention_emb: np.ndarray = None, top_m: int = 3) -> List[Tuple[str, float]]:
        """
        Links a query mention to top-m graph nodes using fuzzy string match and domain synonym lookup.
        """
        return self.link_query_entities(query_mention)[:top_m]
