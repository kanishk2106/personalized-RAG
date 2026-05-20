import logging
import os
import re
from datetime import datetime

from sqlalchemy import (
    BigInteger, DateTime, ForeignKey, Integer, Text,
    UniqueConstraint, create_engine, delete, func, select,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker,
)

from .chunking import Chunk

logger = logging.getLogger(__name__)

def _get_database_url() -> str:
    raw = os.getenv("DATABASE_URL")
    if not raw:
        raise RuntimeError("DATABASE_URL not set in environment")
    return re.sub(r"^postgresql:", "postgresql+psycopg:", raw)


engine = create_engine(
    _get_database_url(),
    pool_pre_ping=True,
    pool_size=4,
    max_overflow=2,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    source_json_key: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    chunks: Mapped[list["DBChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DBChunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint(
            "document_id", "chunk_version", "chunk_index",
            name="uq_chunks_doc_version_index",
        ),
    )

    chunk_id: Mapped[str] = mapped_column(Text, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_version: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    document: Mapped[Document] = relationship(back_populates="chunks")


def get_existing_chunk_ids(doc_id: str) -> list[str]:
 
    with SessionLocal() as session:
        rows = session.execute(
            select(DBChunk.chunk_id)
            .join(Document, DBChunk.document_id == Document.id)
            .where(Document.doc_id == doc_id)
        ).all()
    return [r.chunk_id for r in rows]


def write_document(chunks: list[Chunk]) -> None:
  
    if not chunks:
        logger.warning("write_document called with 0 chunks; skipping")
        return

    doc_ids = {c.doc_id for c in chunks}
    if len(doc_ids) != 1:
        raise ValueError(f"Mixed doc_ids in chunk list: {doc_ids}")

    first = chunks[0]

    with SessionLocal() as session:
        with session.begin():
            upsert_stmt = (
                pg_insert(Document)
                .values(
                    doc_id=first.doc_id,
                    title=first.title,
                    source_json_key=first.source_json_key,
                )
                .on_conflict_do_update(
                    index_elements=["doc_id"],
                    set_={
                        "title": first.title,
                        "source_json_key": first.source_json_key,
                        "updated_at": func.now(),
                    },
                )
                .returning(Document.id)
            )
            document_pk = session.execute(upsert_stmt).scalar_one()

            session.execute(
                delete(DBChunk).where(DBChunk.document_id == document_pk)
            )

            session.execute(
                DBChunk.__table__.insert(),
                [
                    {
                        "chunk_id": c.chunk_id,
                        "document_id": document_pk,
                        "chunk_version": c.chunk_version,
                        "chunk_index": c.chunk_index,
                        "start_page": None if c.start_page == -1 else c.start_page,
                        "end_page": None if c.end_page == -1 else c.end_page,
                        "text": c.text.replace("\x00", ""),
                        "char_count": c.char_count,
                        "token_count": None,
                        "content_hash": c.content_hash,
                    }
                    for c in chunks
                ],
            )

    logger.info(
        "Wrote document doc_id=%s (pk=%d) with %d chunks",
        first.doc_id, document_pk, len(chunks),
    )