# CompGraphRAG Baseline Comparison Suite

This directory contains execution wrappers and instructions for comparing CompGraphRAG against original external baseline frameworks:

1. **Vector-RAG:** Dense semantic retrieval (sentence-transformers / OpenAI embeddings).
2. **Naive RAG:** BM25 keyword + dense hybrid vector search.
3. **GraphRAG:** Microsoft GraphRAG (global/local community summarization).
4. **LightRAG:** Dual-level graph retrieval.
5. **HippoRAG:** Personalized PageRank over Open IE subgraphs.

---

## Submodule Pinning & Reproduction Steps

To execute external baseline comparisons against official source implementations:

```bash
# Pin official baseline repositories as submodules
git submodule add https://github.com/microsoft/graphrag.git baselines/external/graphrag
git submodule add https://github.com/HKUDS/LightRAG.git baselines/external/lightrag
git submodule add https://github.com/osu-nlp/HippoRAG.git baselines/external/hipporag

# Execute comparative baseline evaluation suite
python3 baselines/runner.py
```
