from __future__ import annotations

import logging
from datetime import datetime, timezone
import pdfplumber
from botocore.exceptions import BotoCoreError, ClientError

from .extract import extract_text_with_fallback
from .r2_store import R2Store
from .schema import build_output_json, out_json_key
from .settings import Settings

logger = logging.getLogger(__name__)


def process_one_pdf(store: R2Store, s: Settings, pdf_key: str) -> None:
    logger.info("Processing PDF: s3://%s/%s", store.bucket, pdf_key)

    head = store.head(pdf_key)
    pdf_bytes = store.get_bytes(pdf_key)
    extracted_at = datetime.now(timezone.utc)

    result = extract_text_with_fallback(
        pdf_bytes=pdf_bytes,
        min_text_chars_per_page=s.min_text_chars_per_page,
        ocr_dpi=s.ocr_dpi,
        ocr_lang=s.ocr_lang,
    )

    out_json = build_output_json(
        schema_version=1,
        bucket=store.bucket,
        pdf_key=pdf_key,
        head_meta=head,
        extracted_at=extracted_at,
        method="pdfplumber+ocr_fallback",
        method_version=getattr(pdfplumber, "__version__", "unknown"),
        language_hint=s.language_hint,
        scanned_suspected=result.scanned_suspected,
        stats=result.stats,
        pages=result.pages,
    )

    out_key = out_json_key(s.out_prefix, pdf_key)
    store.put_json(out_key, out_json)

    logger.info(
        "Wrote JSON: s3://%s/%s (pages=%d, total_chars=%d, empty_pages=%d, scanned_suspected=%s)",
        store.bucket,
        out_key,
        out_json["extraction"]["stats"]["page_count"],
        out_json["extraction"]["stats"]["total_chars"],
        out_json["extraction"]["stats"]["empty_page_count"],
        out_json["extraction"]["scanned_suspected"],
    )


def run_batch() -> None:
    s = Settings.from_env()
    store = R2Store(s)

    pdf_keys = store.list_pdf_keys(pdf_prefix=s.pdf_prefix, extracted_prefix=s.out_prefix)
    if not pdf_keys:
        logger.warning("No new PDFs found under prefix=%r in bucket=%r", s.pdf_prefix, store.bucket)
        return

    logger.info("Found %d PDFs under prefix=%r", len(pdf_keys), s.pdf_prefix)

    for k in pdf_keys:
        try:
            process_one_pdf(store, s, k)
        except (ClientError, BotoCoreError) as e:
            logger.exception("S3/R2 SDK error for key=%s: %s", k, e)
        except Exception:
            logger.exception("Unexpected error for key=%s", k)
