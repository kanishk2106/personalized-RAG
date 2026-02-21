from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import pdfplumber
import pypdfium2 as pdfium
import pytesseract

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    pages: List[Dict[str, Any]]
    scanned_suspected: bool
    stats: Dict[str, Any]


def _normalize_text(t: str) -> str:
    t = t or ""
    return "\n".join(line.rstrip() for line in t.splitlines()).strip()


def extract_with_pdfplumber(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    pages: List[Dict[str, Any]] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = _normalize_text(page.extract_text() or "")
            pages.append({"page": i, "text": text, "char_count": len(text)})
    return pages


def ocr_page_text(pdf_bytes: bytes, page_index0: int, dpi: int, lang: str) -> str:
    doc = pdfium.PdfDocument(pdf_bytes)
    page = None
    try:
        page = doc.get_page(page_index0)
        scale = dpi / 72.0
        pil_image = page.render(scale=scale).to_pil()
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        text = pytesseract.image_to_string(pil_image, lang=lang)
        return _normalize_text(text)
    finally:
        if page is not None:
            try:
                page.close()
            except Exception:
                pass
        try:
            doc.close()
        except Exception:
            pass


def extract_text_with_fallback(
    pdf_bytes: bytes,
    min_text_chars_per_page: int,
    ocr_dpi: int,
    ocr_lang: str,
) -> ExtractionResult:
    pages = extract_with_pdfplumber(pdf_bytes)

    page_count = len(pages)
    empty_before = sum(1 for p in pages if p["char_count"] == 0)
    low_before = sum(1 for p in pages if p["char_count"] < min_text_chars_per_page)

    # Heuristic: mostly empty/low-text pages => likely scanned
    scanned_suspected = (empty_before / max(page_count, 1) >= 0.5) or (low_before / max(page_count, 1) >= 0.8)

    for p in pages:
        if p["char_count"] >= min_text_chars_per_page:
            continue
        try:
            ocr_text = ocr_page_text(pdf_bytes, p["page"] - 1, dpi=ocr_dpi, lang=ocr_lang)
            if len(ocr_text) > p["char_count"]:
                p["text"] = ocr_text
                p["char_count"] = len(ocr_text)
        except Exception:
            logger.exception("OCR failed for page=%d; leaving pdfplumber text as-is.", p["page"])

    stats = {
        "page_count": len(pages),
        "total_chars": sum(p["char_count"] for p in pages),
        "empty_page_count": sum(1 for p in pages if p["char_count"] == 0),
    }

    return ExtractionResult(pages=pages, scanned_suspected=scanned_suspected, stats=stats)
