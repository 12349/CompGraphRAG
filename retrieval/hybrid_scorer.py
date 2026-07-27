"""
Formal mathematical hybrid retrieval scoring engine for CompGraphRAG.
Score equation:
score(x | q) = α * cos(q_emb, x_emb) + β * GraphPathScore(q_ent, path_x) + γ * Authority(x)
where GraphPathScore(q_ent, path) = sum_{(u,r,v) in path} w_r * conf(u,r,v) * (lambda ^ hop_index)
"""

import numpy as np
from typing import List, Dict, Any, Tuple

class HybridScorer:
    def __init__(self, alpha: float = 0.4, beta: float = 0.5, gamma: float = 0.1, decay_lambda: float = 0.85):
        assert abs((alpha + beta + gamma) - 1.0) < 1e-4, "Weights alpha, beta, gamma must sum to 1.0"
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.decay_lambda = decay_lambda
        self._st_model = None

    def _get_encoder(self):
        if self._st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                self._st_model = False
        return self._st_model

    def encode_text(self, text: str) -> np.ndarray:
        encoder = self._get_encoder()
        if encoder:
            return encoder.encode(text)
        # Fallback deterministic pseudo-embedding for text
        words = text.lower().split()
        vec = np.zeros(64)
        for w in words:
            idx = sum(ord(c) for c in w) % 64
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

    def calculate_path_score(self, path: List[Dict[str, Any]]) -> float:
        if not path:
            return 0.0
        
        path_score = 0.0
        for edge in path:
            w_r = edge.get("relation_weight", 1.0)
            conf = edge.get("confidence", 0.9)
            hop = edge.get("hop", 1)
            decay = self.decay_lambda ** (hop - 1)
            path_score += w_r * conf * decay
            
        return float(path_score / len(path))

    def score_candidate(self, 
                        q_emb: np.ndarray, 
                        x_emb: np.ndarray, 
                        path: List[Dict[str, Any]], 
                        authority_score: float = 1.0) -> float:
        dense_score = max(0.0, self.cosine_similarity(q_emb, x_emb))
        graph_score = min(1.0, self.calculate_path_score(path))
        auth_score = min(1.0, max(0.0, authority_score))
        
        final_score = (self.alpha * dense_score) + (self.beta * graph_score) + (self.gamma * auth_score)
        return float(final_score)

    def rank_candidates(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for cand in candidates:
            cand["hybrid_score"] = self.score_candidate(
                q_emb=cand.get("q_emb", np.zeros(64)),
                x_emb=cand.get("x_emb", np.zeros(64)),
                path=cand.get("path", []),
                authority_score=cand.get("authority", 1.0)
            )
        return sorted(candidates, key=lambda c: c["hybrid_score"], reverse=True)
