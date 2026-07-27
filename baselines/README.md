# CompGraphRAG Baseline Models Suite

This directory contains baseline wrappers and runners to benchmark CompGraphRAG against standard paradigms:

1. **Vector-RAG**: Dense bi-encoder passage retrieval only (Lewis et al., 2020).
2. **Naive-RAG**: Unranked top-k text chunk context window.
3. **GraphRAG**: Hierarchical community detection and summarization (Edge et al., Microsoft 2024).
4. **LightRAG**: Dual-level (low-level entity + high-level theme) graph indexing (Guo et al., 2024).
5. **HippoRAG**: Neurobiologically inspired PPR memory retrieval (Gutiérrez et al., NeurIPS 2024).

---

## Running Baseline Benchmarks
```bash
python3 run_demo.py --stats --baselines
```
