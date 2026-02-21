from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone


def get_env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise ValueError(f"Missing required env var: {name}")
    return v


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class Settings:
    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    bucket: str
    pdf_prefix: str
    out_prefix: str
    min_text_chars_per_page: int = 30
    ocr_dpi: int = 250
    ocr_lang: str = "eng"
    language_hint: str = "en"

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            r2_account_id=get_env("R2_ACCOUNT_ID"),
            r2_access_key_id=get_env("R2_ACCESS_KEY_ID"),
            r2_secret_access_key=get_env("R2_SECRET_ACCESS_KEY"),
            bucket=get_env("R2_BUCKET_NAME"),
            pdf_prefix=get_env("R2_PDF_PREFIX"),
            out_prefix=get_env("R2_EXTRACT_PREFIX"),
            min_text_chars_per_page=int(os.getenv("MIN_TEXT_CHARS_PER_PAGE", "30")),
            ocr_dpi=int(os.getenv("OCR_DPI", "250")),
            ocr_lang=os.getenv("OCR_LANG", "eng"),
            language_hint=os.getenv("LANGUAGE_HINT", "en"),
        )
