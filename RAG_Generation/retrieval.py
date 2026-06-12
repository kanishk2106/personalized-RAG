
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class Candidate:
    chunk_id: str
    doc_id: str
    text: str
    dense_rank: int | None = None
    lexical_rank: int | None = None

def dense_search(
    pc_index,  
    query_vec: list[float],
    top_k: int,
) -> list[Candidate]:
    res = pc_index.query(
        vector=query_vec,
        top_k=top_k,
        include_metadata=True,
    )
    out: list[Candidate] = []
    for rank, match in enumerate(res.matches):
        md = match.metadata or {}
        out.append(
            Candidate(
                chunk_id=match.id,
                doc_id=str(md.get("doc_id", "")),
                text="",  
                dense_rank=rank,
            )
        )
    return out

_LEXICAL_SQL = text(
    """
    SELECT c.chunk_id,
           d.doc_id,
           c.text
    FROM chunks AS c
    JOIN documents AS d ON c.document_id = d.id
    WHERE to_tsvector('english', c.text) @@ plainto_tsquery('english', :q)
    ORDER BY ts_rank(to_tsvector('english', c.text),
                     plainto_tsquery('english', :q)) DESC
    LIMIT :k
    """
)


async def lexical_search(
    session: AsyncSession,
    query: str,
    top_k: int,
) -> list[Candidate]:
    rows = (await session.execute(_LEXICAL_SQL, {"q": query, "k": top_k})).all()
    return [
        Candidate(
            chunk_id=str(r.chunk_id),
            doc_id=str(r.doc_id),
            text=r.text,
            lexical_rank=rank,
        )
        for rank, r in enumerate(rows)
    ]

_HYDRATE_SQL = text(
    """
    SELECT c.chunk_id,
           d.doc_id,
           c.text
    FROM chunks AS c
    JOIN documents AS d ON c.document_id = d.id
    WHERE c.chunk_id = ANY(:ids)
    """
)


async def _hydrate_text(
    session: AsyncSession,
    candidates: list[Candidate],
) -> list[Candidate]:
    missing = [c for c in candidates if not c.text]
    if not missing:
        return candidates

    ids = [c.chunk_id for c in missing]
    rows = (await session.execute(_HYDRATE_SQL, {"ids": ids})).all()
    text_map = {r.chunk_id: r.text for r in rows}

    return [
        Candidate(
            chunk_id=c.chunk_id,
            doc_id=c.doc_id,
            text=text_map.get(c.chunk_id, ""),
            dense_rank=c.dense_rank,
            lexical_rank=c.lexical_rank,
        )
        if not c.text
        else c
        for c in candidates
    ]

def reciprocal_rank_fusion(
    dense: list[Candidate],
    lexical: list[Candidate],
    k: int = 60,
) -> list[Candidate]:
    scores: dict[str, float] = {}
    merged: dict[str, Candidate] = {}

    for lst in (dense, lexical):
        for rank, cand in enumerate(lst):
            scores[cand.chunk_id] = scores.get(cand.chunk_id, 0.0) + 1.0 / (k + rank)
            if cand.chunk_id not in merged or cand.text:
                merged[cand.chunk_id] = cand

    ordered = sorted(scores, key=lambda cid: scores[cid], reverse=True)
    return [merged[cid] for cid in ordered]


async def hybrid_retrieve(
    pc_index,  
    session: AsyncSession,
    query: str,
    query_vec: list[float],
    top_k: int = 20,
) -> list[Candidate]:
    dense, lexical = await asyncio.gather(
        asyncio.to_thread(dense_search, pc_index, query_vec, top_k),
        lexical_search(session, query, top_k),
    )
    fused = reciprocal_rank_fusion(dense, lexical)
    return await _hydrate_text(session, fused)
