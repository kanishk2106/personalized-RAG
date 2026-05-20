import json
import logging

from pdf_extractor.r2_store import R2Store
from pdf_extractor.settings import Settings

from .chunking import Chunk, build_page_aware_chunks
from .database import engine, get_existing_chunk_ids, write_document
from .embedding import sync_document_embeddings

logger = logging.getLogger(__name__)


def load_extracted_json(store: R2Store, json_key: str) -> dict:
    raw = store.get_bytes(json_key)
    return json.loads(raw.decode("utf-8"))
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
    logger.info("Finished chunking %s -> %d chunks", json_key, len(chunks))
    return chunks


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
                    doc_id = chunks[0].doc_id
                    old_chunk_ids = get_existing_chunk_ids(doc_id)
                    write_document(chunks)
                    sync_document_embeddings(doc_id, old_chunk_ids)
                    written += 1
                else:
                    logger.warning("No chunks for %s; skipping DB write", json_key)
            except Exception:
                failed += 1
                logger.exception("Unexpected error while chunking key=%s", json_key)
    finally:
        engine.dispose()

    logger.info("Batch complete: %d documents written, %d failed", written, failed)