"""
Subgraph justification path extraction and audit trail walk generator.
Produces human-readable and machine-auditable JSON representations of justification subgraphs π.
"""

from typing import List, Dict, Any

class SubgraphExtractor:
    def format_subgraph_json(self, path_edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Formats traversed path edges into a formal subgraph π JSON structure.
        """
        nodes = set()
        edges = []
        
        for e in path_edges:
            src = e.get("source", "")
            tgt = e.get("target", "")
            rel = e.get("relation", "")
            conf = e.get("confidence", 1.0)
            
            nodes.add(src)
            nodes.add(tgt)
            edges.append({"source": src, "relation": rel, "target": tgt, "confidence": conf})

        return {
            "subgraph_pi": {
                "nodes": list(nodes),
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }

    def generate_natural_language_walk(self, path_edges: List[Dict[str, Any]]) -> str:
        """
        Converts path edges into a natural language walk sentence chain.
        """
        if not path_edges:
            return "No valid knowledge graph path traversed."

        walk_sentences = []
        for i, e in enumerate(path_edges, 1):
            sentence = f"Step {i}: [{e.get('source')}] --({e.get('relation')})--> [{e.get('target')}]."
            walk_sentences.append(sentence)

        return " ".join(walk_sentences)
