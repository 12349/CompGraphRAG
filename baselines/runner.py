"""
Baseline Runner module for CompGraphRAG Comparative Analysis.
Executes real Vector-RAG and Naive-RAG baselines over candidate corpus text passages.
Marks uninstalled external systems (GraphRAG, LightRAG, HippoRAG) as 'NOT MEASURED'.
"""

import numpy as np
from typing import List, Dict, Any
from reasoning.rule_engine import ComplianceRuleEngine

class BaselineRunner:
    def __init__(self, hybrid_scorer=None):
        self.scorer = hybrid_scorer
        self.rule_engine = ComplianceRuleEngine()

    def _determine_from_passage(self, passage_text: str) -> str:
        """
        Predicts compliance determination from raw passage text using rule engine / statutory keyword parsing.
        """
        txt = passage_text.lower()
        if "without" in txt or "violates" in txt or "fails" in txt or "impermissible" in txt or "breach" in txt or "excluded" in txt or "lacks" in txt:
            return "NON-COMPLIANT"
        elif "permitted" in txt or "exempt" in txt or "satisfies" in txt or "qualify" in txt or "authorized" in txt or "compliant" in txt:
            return "COMPLIANT"
        return "REQUIRES-REVIEW"

    def run_vector_rag_query(self, query_text: str, candidate_passages: List[Dict[str, Any]], gold_det: str) -> Dict[str, Any]:
        """
        Real Vector-RAG baseline: Dense similarity retrieval over passage nodes without graph path traversal.
        """
        if not candidate_passages or self.scorer is None:
            return {"baseline": "Vector-RAG", "determination": "REQUIRES-REVIEW", "is_correct": False, "score": 0.0}

        q_emb = self.scorer.encode_text(query_text)
        scored = []
        for cand in candidate_passages:
            x_emb = cand.get("embedding", self.scorer.encode_text(cand.get("text", "")))
            sim = self.scorer.cosine_similarity(q_emb, x_emb)
            scored.append((cand, sim))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top_cand, top_score = scored[0]
        
        pred_det = self._determine_from_passage(top_cand.get("text", ""))
        return {
            "baseline": "Vector-RAG",
            "retrieved_passage": top_cand.get("text", ""),
            "determination": pred_det,
            "is_correct": (pred_det == gold_det),
            "score": float(top_score)
        }

    def run_naive_rag_query(self, query_text: str, candidate_passages: List[Dict[str, Any]], gold_det: str) -> Dict[str, Any]:
        """
        Real Naive-RAG baseline: BM25/keyword overlap + dense similarity without graph path traversal.
        """
        if not candidate_passages or self.scorer is None:
            return {"baseline": "Naive-RAG", "determination": "REQUIRES-REVIEW", "is_correct": False, "score": 0.0}

        q_words = set(query_text.lower().split())
        q_emb = self.scorer.encode_text(query_text)
        scored = []
        for cand in candidate_passages:
            p_words = set(cand.get("text", "").lower().split())
            keyword_overlap = len(q_words.intersection(p_words)) / max(1, len(q_words))
            x_emb = cand.get("embedding", self.scorer.encode_text(cand.get("text", "")))
            dense_sim = self.scorer.cosine_similarity(q_emb, x_emb)
            combined_score = 0.5 * keyword_overlap + 0.5 * dense_sim
            scored.append((cand, combined_score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top_cand, top_score = scored[0]
        pred_det = self._determine_from_passage(top_cand.get("text", ""))
        return {
            "baseline": "Naive-RAG",
            "retrieved_passage": top_cand.get("text", ""),
            "determination": pred_det,
            "is_correct": (pred_det == gold_det),
            "score": float(top_score)
        }

    def benchmark_all_baselines(self, queries: List[Dict[str, Any]], candidate_passages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes real Vector-RAG and Naive-RAG baselines; marks uninstalled external baselines as NOT MEASURED.
        """
        v_accs = []
        n_accs = []

        for q in queries:
            q_text = q.get("question", "")
            g_det = q.get("gold_determination", "")
            v_res = self.run_vector_rag_query(q_text, candidate_passages, g_det)
            n_res = self.run_naive_rag_query(q_text, candidate_passages, g_det)
            v_accs.append(1.0 if v_res["is_correct"] else 0.0)
            n_accs.append(1.0 if n_res["is_correct"] else 0.0)

        return {
            "Vector-RAG": {
                "status": "EXECUTED",
                "mean_accuracy": float(np.mean(v_accs)) if v_accs else 0.0,
                "std_accuracy": float(np.std(v_accs)) if v_accs else 0.0
            },
            "Naive-RAG": {
                "status": "EXECUTED",
                "mean_accuracy": float(np.mean(n_accs)) if n_accs else 0.0,
                "std_accuracy": float(np.std(n_accs)) if n_accs else 0.0
            },
            "GraphRAG": {
                "status": "NOT MEASURED",
                "reason": "Microsoft GraphRAG repository not installed in environment"
            },
            "LightRAG": {
                "status": "NOT MEASURED",
                "reason": "LightRAG repository not installed in environment"
            },
            "HippoRAG": {
                "status": "NOT MEASURED",
                "reason": "HippoRAG repository not installed in environment"
            }
        }
