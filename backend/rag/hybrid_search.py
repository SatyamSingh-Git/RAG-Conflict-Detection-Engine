"""
Hybrid Search: BM25 (keyword) + Pinecone (vector) with Reciprocal Rank Fusion.

At query time:
  1. Pinecone returns top-K results via cosine similarity (semantic).
  2. BM25 scores ALL indexed chunks by keyword overlap (lexical).
  3. Reciprocal Rank Fusion (RRF) merges both ranked lists into a single fused ranking.

This ensures queries with exact keyword matches (e.g., "MRI machine") AND
semantically similar passages both contribute to the final retrieval.
"""
import os
import json
import re
from rank_bm25 import BM25Okapi
from rag.pinecone_utils import get_pinecone_index, search_pinecone
from rag.embeddings import get_embedding


# ─── BM25 Corpus Cache ───────────────────────────────────────────────────────
# We fetch all chunk texts from Pinecone once, then build the BM25 index.
_bm25_index = None
_bm25_corpus_ids = []
_bm25_corpus_meta = []


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer for BM25."""
    return re.findall(r"\w+", text.lower())


def _build_bm25_index():
    """Fetch all vectors/metadata from Pinecone and build BM25 index."""
    global _bm25_index, _bm25_corpus_ids, _bm25_corpus_meta

    index = get_pinecone_index()
    stats = index.describe_index_stats()
    total = stats.total_vector_count

    if total == 0:
        _bm25_index = None
        return

    # Fetch all IDs first, then fetch their metadata
    # Pinecone list() returns paginated IDs
    all_ids = []
    for ids_batch in index.list():
        all_ids.extend(ids_batch)

    # Fetch metadata in batches of 100
    all_docs = []
    batch_size = 100
    for i in range(0, len(all_ids), batch_size):
        batch_ids = all_ids[i:i + batch_size]
        fetch_result = index.fetch(ids=batch_ids)
        for vid, vec_data in fetch_result.vectors.items():
            all_docs.append({
                "id": vid,
                "metadata": vec_data.metadata
            })

    # Build the BM25 corpus
    tokenized_corpus = []
    _bm25_corpus_ids = []
    _bm25_corpus_meta = []

    for doc in all_docs:
        text = doc["metadata"].get("text", "")
        _bm25_corpus_ids.append(doc["id"])
        _bm25_corpus_meta.append(doc["metadata"])
        tokenized_corpus.append(_tokenize(text))

    _bm25_index = BM25Okapi(tokenized_corpus)


def get_bm25_index():
    """Return cached BM25 index, building it on first call."""
    global _bm25_index
    if _bm25_index is None:
        _build_bm25_index()
    return _bm25_index


def bm25_search(query: str, top_k: int = 10) -> list[dict]:
    """Run BM25 keyword search, returning ranked results."""
    bm25 = get_bm25_index()
    if bm25 is None:
        return []

    tokenized_query = _tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    # Get top-K indices sorted by score descending
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    results = []
    for rank, idx in enumerate(ranked_indices):
        if scores[idx] > 0:  # Only include matches with non-zero BM25 score
            results.append({
                "id": _bm25_corpus_ids[idx],
                "score": float(scores[idx]),
                "metadata": _bm25_corpus_meta[idx],
                "rank": rank + 1
            })
    return results


def reciprocal_rank_fusion(
    vector_results: list[dict],
    bm25_results: list[dict],
    k: int = 60,
    vector_weight: float = 0.7,
    bm25_weight: float = 0.3,
) -> list[dict]:
    """
    Reciprocal Rank Fusion (RRF) to merge two ranked lists.

    RRF score = Σ (weight / (k + rank_i))

    Parameters:
        k: smoothing constant (standard = 60)
        vector_weight: weight for semantic results (default 0.7)
        bm25_weight: weight for keyword results (default 0.3)
    """
    fused_scores: dict[str, float] = {}
    doc_data: dict[str, dict] = {}

    # Score vector results
    for rank, doc in enumerate(vector_results, 1):
        doc_id = doc["id"]
        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + vector_weight / (k + rank)
        doc_data[doc_id] = {
            "metadata": doc["metadata"],
            "vector_score": doc["score"],
            "vector_rank": rank,
        }

    # Score BM25 results
    for rank, doc in enumerate(bm25_results, 1):
        doc_id = doc["id"]
        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + bm25_weight / (k + rank)
        if doc_id not in doc_data:
            doc_data[doc_id] = {"metadata": doc["metadata"]}
        doc_data[doc_id]["bm25_score"] = doc["score"]
        doc_data[doc_id]["bm25_rank"] = rank

    # Sort by fused score
    ranked = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for doc_id, fused_score in ranked:
        data = doc_data[doc_id]
        results.append({
            "id": doc_id,
            "score": fused_score,
            "vector_score": data.get("vector_score", 0),
            "bm25_score": data.get("bm25_score", 0),
            "vector_rank": data.get("vector_rank"),
            "bm25_rank": data.get("bm25_rank"),
            "metadata": data["metadata"],
        })

    return results


def hybrid_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Full hybrid search pipeline:
      1. Pinecone vector search (semantic similarity)
      2. BM25 keyword search (lexical matching)
      3. Reciprocal Rank Fusion to merge both
    """
    # 1. Vector search via Pinecone
    query_vector = get_embedding(query)
    vector_results = search_pinecone(query_vector, top_k=top_k * 2)

    # 2. BM25 search
    bm25_results = bm25_search(query, top_k=top_k * 2)

    # 3. Fuse with RRF
    fused = reciprocal_rank_fusion(vector_results, bm25_results)

    return fused[:top_k]
