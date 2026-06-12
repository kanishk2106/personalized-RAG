"""Cross-encoder reranking.

The hybrid retriever casts a wide net (recall); the cross-encoder re-scores
each (query, chunk) pair jointly for precision, then we keep the top N.
This is the quality step — bi-encoder retrieval can't model query-document
interaction, a cross-encoder can.
"""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import CrossEncoder

from .retrieval import Candidate

# Small, fast, strong reranker. Swap for bge-reranker-large if you want more
# quality at the cost of latency.
_RERANKER_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def _load_reranker() -> CrossEncoder:
    return CrossEncoder(_RERANKER_NAME)


def rerank(
    query: str,
    candidates: list[Candidate],
    top_n: int = 5,
) -> list[Candidate]:
    """Re-score candidates with the cross-encoder, return the top_n.

    No-op-safe: empty candidate list returns empty.
    """
    if not candidates:
        return []

    model = _load_reranker()
    pairs = [(query, c.text) for c in candidates]
    scores = model.predict(pairs)  # higher = more relevant

    ranked = sorted(
        zip(candidates, scores, strict=True),
        key=lambda pair: pair[1],
        reverse=True,
    )
    return [cand for cand, _ in ranked[:top_n]]
