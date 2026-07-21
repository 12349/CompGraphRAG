"""
Graph-guided retriever module using NetworkX for CompGraphRAG.
Supports multi-hop path extraction and Personalized PageRank (PPR) sub-graph candidate generation.
"""

import networkx as nx
from typing import List, Dict, Any, Tuple

class GraphRetriever:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def retrieve_subgraph_paths(self, start_node_id: str, max_hops: int = 3) -> List[List[Dict[str, Any]]]:
        """
        Retrieves all path edge chains starting from start_node_id up to max_hops.
        Returns list of path list objects: [[edge1, edge2], ...]
        """
        if start_node_id not in self.graph:
            return []

        all_paths = []
        
        def dfs(current_node, current_path, current_hop):
            if current_hop >= max_hops:
                return
            
            for successor in self.graph.successors(current_node):
                edge_data = self.graph.get_edge_data(current_node, successor)
                edge_obj = {
                    "source": current_node,
                    "target": successor,
                    "relation": edge_data.get("relation", "relatedTo"),
                    "confidence": edge_data.get("confidence", 0.9),
                    "relation_weight": edge_data.get("relation_weight", 1.0),
                    "hop": current_hop + 1
                }
                new_path = current_path + [edge_obj]
                all_paths.append(new_path)
                dfs(successor, new_path, current_hop + 1)

        dfs(start_node_id, [], 0)
        return all_paths

    def personalized_pagerank(self, seed_nodes: List[str], alpha: float = 0.85) -> Dict[str, float]:
        """
        Calculates Personalized PageRank scores over the graph starting from seed_nodes.
        """
        valid_seeds = [n for n in seed_nodes if n in self.graph]
        if not valid_seeds:
            return {}
        
        personalization = {n: (1.0 / len(valid_seeds) if n in valid_seeds else 0.0) for n in self.graph.nodes()}
        return nx.pagerank(self.graph, alpha=alpha, personalization=personalization)
