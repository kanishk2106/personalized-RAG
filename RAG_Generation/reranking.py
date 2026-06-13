from __future__ import annotations

from functools import lru_cache

from sentence_transformers import CrossEncoder

from .retrieval import Candidate
_RERANKER_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
@lru_cache(maxsize=1)
def _load_reranker() -> CrossEncoder:
    return CrossEncoder(_RERANKER_NAME)
def rerank(
    query: str,
    candidates: list[Candidate],
    top_n: int = 2,
) -> list[Candidate]:
    if not candidates:
        return []

    model = _load_reranker()
    pairs = [(query, c.text) for c in candidates]
    scores = model.predict(pairs) 
    ranked = sorted(
        zip(candidates, scores),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return [cand for cand, _ in ranked[:top_n]]
