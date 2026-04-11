from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from hashlib import md5

from dotenv import load_dotenv
from sqlalchemy import (
    BigInteger, DateTime, ForeignKey, Integer, Text,
    UniqueConstraint, create_engine, delete, func,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker,
)
from wordsegment import load as ws_load, segment as ws_segment

from pdf_extractor.r2_store import R2Store
from pdf_extractor.settings import Settings

logger = logging.getLogger(__name__)
ws_load()
load_dotenv()
CHUNK_VERSION = "v1"


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    source_json_key: str
    chunk_version: str
    chunk_index: int
    start_page: int
    end_page: int
    text: str
    char_count: int
    content_hash: str


# ============ DATABASE: engine + ORM models ============

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


# ============ CHUNKING: all your existing code, unchanged ============

PROTECTED_PATTERNS = [
    re.compile(r'\b[\w.+-]+@[\w.-]+\.\w+\b'),
    re.compile(r'\b[A-Z]{2,6}\b'),
    re.compile(r'\b[A-Za-z]+[-_/.][\w\-_/.]{1,30}\b'),
    re.compile(r'\b[A-Za-z]*\d+[A-Za-z0-9]*\b'),
    re.compile(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+){1,3}[A-Z]{0,5}\b'),
    re.compile(r'\b[A-Z][a-z]{2,15}\b'),
]

_UNICODE_REPLACEMENTS = {
    "\u00a0": " ",
    "\ufeff": "",
    "\u2011": "-",
    "\u2012": "-",
    "\u2013": "-",
    "\u2014": "—",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2026": "...",
}


def normalize_unicode(text: str) -> str:
    for src, dst in _UNICODE_REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text


def remove_cid_artifacts(text: str) -> str:
    return re.sub(r"\(cid:\d+\)", "", text)


def remove_stray_digit_markers(text: str) -> str:
    return re.sub(r"(?<=[a-zA-Z])\s+\d{1,2}\s+(?=[a-zA-Z])", " ", text)


_MIN_GLUED_LEN = 10


def _segment_glued_run(match: re.Match) -> str:
    token = match.group(0)
    if len(token) < _MIN_GLUED_LEN:
        return token
    starts_upper = token[0].isupper()
    segmented = ws_segment(token.lower())
    if len(segmented) > 1:
        result = " ".join(segmented)
        if starts_upper:
            result = result[0].upper() + result[1:]
        logger.debug("Segmented glued run: %r -> %r", token, result)
        return result
    return token


def fix_concatenated_words(text: str) -> str:
    protected: list[str] = []

    def stash(match: re.Match) -> str:
        idx = len(protected)
        protected.append(match.group(0))
        return f"\ue000{idx}\ue001"

    combined = re.compile(
        "|".join(f"(?:{p.pattern})" for p in PROTECTED_PATTERNS)
    )
    text = combined.sub(stash, text)
    text = re.sub(r"([a-zA-Z])([,;:])([a-zA-Z])", r"\1\2 \3", text)
    text = re.sub(r"\b[a-zA-Z]{10,}\b", _segment_glued_run, text)
    for idx in range(len(protected) - 1, -1, -1):
        text = text.replace(f"\ue000{idx}\ue001", protected[idx])
    return text


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def detect_repeating_headers(pages_text: list[str], min_occurrences: int = 3) -> list[str]:
    from collections import Counter
    line_counts: Counter[str] = Counter()
    for page_text in pages_text:
        unique_lines = set()
        for line in page_text.splitlines():
            stripped = line.strip()
            if stripped and len(stripped) > 3:
                unique_lines.add(stripped)
        for line in unique_lines:
            line_counts[line] += 1
    headers = [line for line, count in line_counts.items() if count >= min_occurrences]
    return headers


def remove_page_artifacts(text: str, headers_to_strip: list[str] | None = None) -> str:
    lines = text.splitlines()
    cleaned_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.fullmatch(r"\d+\s*of\s*\d+", stripped, flags=re.IGNORECASE):
            continue
        if re.fullmatch(r"\d{1,3}", stripped):
            continue
        if headers_to_strip and stripped in headers_to_strip:
            continue
        cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)


def _collapse_newlines_smartly(text: str) -> str:
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"(\w)\n(\w)", r"\1 \2", text)
    text = re.sub(r"\n(?!\n)", " ", text)
    return text


def clean_page_text(text: str, headers_to_strip: list[str] | None = None) -> str:
    text = normalize_unicode(text)
    text = remove_cid_artifacts(text)
    text = remove_page_artifacts(text, headers_to_strip)
    text = _collapse_newlines_smartly(text)
    text = fix_concatenated_words(text)
    text = normalize_whitespace(text)
    return text


def is_garbage_chunk(text: str) -> bool:
    if len(text) < 50:
        return True
    total = len(text)
    alpha = sum(c.isalpha() for c in text)
    if alpha / total < 0.35:
        return True
    lone_digits = len(re.findall(r"(?<!\d)\d{1,2}(?!\d)", text))
    if lone_digits > 25:
        return True
    weird_symbols = sum(text.count(c) for c in "@£§¥°¦¬©®™")
    if weird_symbols > 8:
        return True
    word_count = len(re.findall(r"\b[a-zA-Z]{3,}\b", text))
    if word_count < 20:
        return True
    return False


def _snap_to_boundary(text: str, pos: int, search_window: int = 80) -> int:
    if pos >= len(text):
        return pos
    search_start = max(0, pos - search_window)
    window = text[search_start:pos]
    for marker in [". ", "? ", "! "]:
        idx = window.rfind(marker)
        if idx != -1:
            return search_start + idx + len(marker)
    idx = window.rfind(" ")
    if idx != -1:
        return search_start + idx + 1
    return pos


def _snap_forward_to_word(text: str, pos: int, search_window: int = 80) -> int:
    if pos <= 0 or pos >= len(text):
        return pos
    if text[pos - 1] == ' ' or text[pos - 1] == '\n':
        return pos
    search_end = min(len(text), pos + search_window)
    idx = text.find(' ', pos, search_end)
    return idx + 1 if idx != -1 else pos


QUESTION_BOUNDARY = re.compile(
    r'\n(?=Q\d+(?:\.\d+)?\s*\(\d+\s*points?\))',
    re.IGNORECASE,
)


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[tuple[str, int]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
    text = text.strip()
    if not text:
        return []
    chunks: list[tuple[str, int]] = []
    start = 0
    while start < len(text):
        raw_end = min(start + chunk_size, len(text))
        if raw_end < len(text):
            end = _snap_to_boundary(text, raw_end)
        else:
            end = raw_end
        chunk = text[start:end].strip()
        if chunk:
            leading_ws = len(text[start:end]) - len(text[start:end].lstrip())
            chunks.append((chunk, start + leading_ws))
        if end >= len(text):
            break
        next_start = max(start + 1, end - chunk_overlap)
        next_start = _snap_forward_to_word(text, next_start)
        start = next_start
    return chunks


def _split_by_question_boundaries(text: str) -> list[str]:
    sections = QUESTION_BOUNDARY.split(text)
    return [s for s in sections if s.strip()]


def build_page_aware_chunks(
    extracted_json: dict,
    source_json_key: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    drop_garbage: bool = True,
) -> list[Chunk]:
    doc = extracted_json.get("doc", {})
    pages = extracted_json.get("pages", [])
    doc_id = doc.get("doc_id", "unknown_doc")
    title = doc.get("title", "untitled")
    raw_page_texts = [p.get("text", "") for p in pages]
    headers_to_strip = detect_repeating_headers(raw_page_texts)
    if headers_to_strip:
        logger.info("Detected %d repeating header/footer lines to strip", len(headers_to_strip))
    page_units: list[tuple[int, str]] = []
    for page_obj in pages:
        page_num = page_obj.get("page")
        raw_text = page_obj.get("text", "")
        cleaned = clean_page_text(raw_text, headers_to_strip)
        if cleaned:
            page_units.append((page_num, cleaned))
    full_text = " ".join(text for _, text in page_units).strip()
    if not full_text:
        return []
    sections = _split_by_question_boundaries(full_text)
    raw_chunks: list[tuple[str, int]] = []
    if len(sections) > 1:
        logger.info("Detected Q&A document with %d question sections", len(sections))
        section_offset = 0
        for section in sections:
            section_pos = full_text.find(section, section_offset)
            if section_pos == -1:
                section_pos = section_offset
            if len(section) <= chunk_size:
                stripped = section.strip()
                if stripped:
                    raw_chunks.append((stripped, section_pos))
            else:
                sub_chunks = chunk_text(section, chunk_size, chunk_overlap)
                for chunk_str, local_offset in sub_chunks:
                    raw_chunks.append((chunk_str, section_pos + local_offset))
            section_offset = section_pos + len(section)
    else:
        raw_chunks = chunk_text(full_text, chunk_size, chunk_overlap)
    spans: list[tuple[int, int, int]] = []
    cursor = 0
    for page_num, text in page_units:
        start = cursor
        end = start + len(text)
        spans.append((page_num, start, end))
        cursor = end + 1
    chunks: list[Chunk] = []
    dropped = 0
    for idx, (chunk_text_value, chunk_start) in enumerate(raw_chunks):
        if drop_garbage and is_garbage_chunk(chunk_text_value):
            dropped += 1
            logger.debug("Dropped garbage chunk %d: %r", idx, chunk_text_value[:80])
            continue
        chunk_end = chunk_start + len(chunk_text_value)
        covered_pages = [
            page_num
            for page_num, start, end in spans
            if not (end < chunk_start or start > chunk_end)
        ]
        if covered_pages:
            start_page = min(covered_pages)
            end_page = max(covered_pages)
        else:
            start_page = -1
            end_page = -1
        chunk_index = idx
        content_hash = md5(chunk_text_value.encode("utf-8")).hexdigest()
        stable_id_input = f"{doc_id}|{source_json_key}|{CHUNK_VERSION}|{chunk_index}"
        chunk_id = md5(stable_id_input.encode("utf-8")).hexdigest()
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                title=title,
                source_json_key=source_json_key,
                chunk_version=CHUNK_VERSION,
                chunk_index=chunk_index,
                start_page=start_page,
                end_page=end_page,
                text=chunk_text_value,
                char_count=len(chunk_text_value),
                content_hash=content_hash,
            )
        )
    if dropped:
        logger.info("Dropped %d garbage chunks from %s", dropped, source_json_key)
    return chunks


def load_extracted_json(store: R2Store, json_key: str) -> dict:
    raw = store.get_bytes(json_key)
    return json.loads(raw.decode("utf-8"))


def print_chunks_for_file(json_key: str, chunks: list[Chunk]) -> None:
    print("\n" + "=" * 100)
    print(f"FILE: {json_key}")
    print(f"TOTAL CHUNKS: {len(chunks)}")
    print("=" * 100)
    for chunk in chunks:
        print(f"\n[Chunk {chunk.chunk_index}]")
        print(f"chunk_id   : {chunk.chunk_id}")
        print(f"doc_id     : {chunk.doc_id}")
        print(f"title      : {chunk.title}")
        print(f"pages      : {chunk.start_page} -> {chunk.end_page}")
        print(f"char_count : {chunk.char_count}")
        print("text:")
        print(chunk.text)
        print("-" * 100)


def process_one_json_for_chunking(
    store: R2Store,
    json_key: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Chunk]:
    logger.info("Chunking extracted JSON: s3://%s/%s", store.bucket, json_key)
    extracted_json = load_extracted_json(store, json_key)
    chunks = build_page_aware_chunks(
        extracted_json=extracted_json,
        source_json_key=json_key,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    print_chunks_for_file(json_key, chunks)
    logger.info("Finished chunking %s -> %d chunks", json_key, len(chunks))
    return chunks


# ============ DB WRITER ============

def write_document(chunks: list[Chunk]) -> None:
    """
    Idempotently write one document and all its chunks to Neon.
    UPSERTs the document row, deletes existing chunks, bulk inserts new ones.
    All in one transaction.
    """
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
                        "text": c.text,
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


# ============ BATCH RUNNER ============

def list_extracted_json_keys(store: R2Store, extracted_prefix: str) -> list[str]:
    keys: list[str] = []
    token: str | None = None
    while True:
        kwargs = {"Bucket": store.bucket, "Prefix": extracted_prefix, "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        resp = store.s3.list_objects_v2(**kwargs)
        for obj in resp.get("Contents", []):
            k = obj["Key"]
            if k.lower().endswith(".json"):
                keys.append(k)
        if resp.get("IsTruncated"):
            token = resp.get("NextContinuationToken")
        else:
            break
    return keys


def run_chunk_batch(
    json_filenames: list[str] | None = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> None:
    s = Settings.from_env()
    store = R2Store(s)

    if json_filenames:
        json_keys = json_filenames
        logger.info("Targeted chunking run for %d JSON files", len(json_keys))
    else:
        logger.info("Fetching extracted JSON keys from R2...")
        json_keys = list_extracted_json_keys(store, s.out_prefix)
        logger.info("Found %d extracted JSON files", len(json_keys))

    if not json_keys:
        logger.warning("No JSON files found to chunk.")
        return

    written = 0
    failed = 0
    try:
        for json_key in json_keys:
            try:
                chunks = process_one_json_for_chunking(
                    store=store,
                    json_key=json_key,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
                if chunks:
                    write_document(chunks)
                    written += 1
                else:
                    logger.warning("No chunks for %s; skipping DB write", json_key)
            except Exception:
                failed += 1
                logger.exception("Unexpected error while chunking key=%s", json_key)
    finally:
        engine.dispose()

    logger.info("Batch complete: %d documents written, %d failed", written, failed)


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
run_chunk_batch()