from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from hashlib import md5

from dotenv import load_dotenv

from wordsegment import load as ws_load, segment as ws_segment

from pdf_extractor.r2_store import R2Store
from pdf_extractor.settings import Settings

from .cleaning import clean_page_text, detect_repeating_headers

logger = logging.getLogger(__name__)

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




