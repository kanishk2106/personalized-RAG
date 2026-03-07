import os
import json
import re
import logging
import boto3
from pdf_extractor.settings import Settings
from pdf_extractor.r2_store import R2Store

logger = logging.getLogger(__name__)

BATCH_SIZE = 50


def professional_cleaner(text: str) -> str:
    """Refines text specifically for CS678 assignment patterns."""
    if not text:
        return ""
    text = re.sub(r"HW\d+: .* CS\d+", "", text)
    text = re.sub(r"\d+of\d+", "", text)
    text = re.sub(r"\s+", " ", text)
    text = "".join(char for char in text if char.isprintable())
    return text.strip()


def clean_and_upload_batch(batch_keys: list, store: R2Store, s3_client, bucket_name: str, raw_dir: str):
    """Download a batch, clean only text + update char_count, upload to cleaned-json/, delete local."""
    total_pages_cleaned = 0
    local_files = []

    # --- STAGE: Download batch to local ---
    for i, obj_key in enumerate(batch_keys):
        filename = os.path.basename(obj_key)
        local_path = os.path.join(raw_dir, filename)
        logger.info(f"  [{i + 1}/{len(batch_keys)}] Downloading: {filename}")
        raw_bytes = store.get_bytes(obj_key)
        with open(local_path, "wb") as f:
            f.write(raw_bytes)
        local_files.append(local_path)

    # --- CLEAN + UPLOAD ---
    for local_path in local_files:
        filename = os.path.basename(local_path)
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Clean ONLY text field and update char_count per page
            pages = data.get("pages", [])
            total_new_chars = 0
            for page_entry in pages:
                cleaned_text = professional_cleaner(page_entry.get("text", ""))
                page_entry["text"] = cleaned_text
                page_entry["char_count"] = len(cleaned_text)
                total_new_chars += len(cleaned_text)
            total_pages_cleaned += len(pages)

            # Update top-level stats to reflect cleaned totals
            if "extraction" in data and "stats" in data["extraction"]:
                data["extraction"]["stats"]["total_chars"] = total_new_chars

            # Upload to cleaned-json/ with SAME filename
            cloud_key = f"cleaned-json/{filename}"
            s3_client.put_object(
                Bucket=bucket_name,
                Key=cloud_key,
                Body=json.dumps(data, indent=2).encode('utf-8'),
                ContentType='application/json'
            )
            logger.info(f"  Uploaded: {cloud_key} ({len(pages)} pages)")

        except Exception as e:
            logger.error(f"  Failed for {filename}: {str(e)}")

    # --- CLEANUP: Remove local files ---
    for local_path in local_files:
        try:
            os.remove(local_path)
        except OSError as e:
            logger.warning(f"  Could not delete {local_path}: {e}")

    return len(batch_keys), total_pages_cleaned


def run_batch_pipeline(store: R2Store, s: Settings):
    """Main pipeline: processes documents in batches of BATCH_SIZE."""
    raw_dir = os.path.join(os.getcwd(), "data", "raw_json")
    os.makedirs(raw_dir, exist_ok=True)

    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv("R2_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY")
    )
    bucket_name = os.getenv("R2_BUCKET_NAME")

    # Collect all .json keys from source prefix
    paginator = store.s3.get_paginator('list_objects_v2')
    all_keys = []
    for page in paginator.paginate(Bucket=store.bucket, Prefix=s.out_prefix):
        for obj in page.get('Contents', []):
            if obj['Key'].endswith('.json'):
                all_keys.append(obj['Key'])

    logger.info(f"Found {len(all_keys)} JSON files. Processing in batches of {BATCH_SIZE}")

    total_files = 0
    total_pages = 0
    batch_num = 0

    for i in range(0, len(all_keys), BATCH_SIZE):
        batch_keys = all_keys[i : i + BATCH_SIZE]
        batch_num += 1
        logger.info(f"--- Batch {batch_num}: docs {i+1}-{i+len(batch_keys)} ---")

        files_done, pages_done = clean_and_upload_batch(
            batch_keys, store, s3_client, bucket_name, raw_dir
        )
        total_files += files_done
        total_pages += pages_done

        logger.info(f"--- Batch {batch_num} done. Local cleaned up. ---")

    logger.info("=" * 50)
    logger.info(f"PIPELINE COMPLETE")
    logger.info(f"  Files Processed: {total_files}")
    logger.info(f"  Pages Cleaned:   {total_pages}")
    logger.info(f"  Batches:         {batch_num}")
    logger.info(f"  R2 Destination:  {bucket_name}/cleaned-json/")
    logger.info("=" * 50)