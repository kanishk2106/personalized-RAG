from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

_INSERT_SQL = text(
    """
    INSERT INTO chat_logs (query, chunk_ids)
    VALUES (:query, :chunk_ids)
    """
)


async def log_chat(
    session: AsyncSession,
    query: str,
    chunk_ids: list[str],
) -> None:
    """Record the question and the chunk ids that reached the prompt.

    Never raises: a logging failure must not cost the visitor their answer.
    """
    try:
        await session.execute(_INSERT_SQL, {"query": query, "chunk_ids": chunk_ids})
        await session.commit()
    except Exception as log_err:
        print(f"chat_logs insert failed: {log_err}")
