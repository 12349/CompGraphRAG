"""
Evaluation package for CompGraphRAG.
"""
from .eval_harness import CompGraphRAGEvaluator
from .stats_validation import StatisticalValidator

__all__ = ["CompGraphRAGEvaluator", "StatisticalValidator"]
