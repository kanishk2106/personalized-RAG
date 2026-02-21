from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from .settings import iso_z


def parse_doc_meta_from_basename(pdf_basename: str) -> Dict[str, Any]:
    base = os.path.splitext(pdf_basename)[0]
    m = re.match(r"^(doc_\d+)_([a-zA-Z]+\d+)_([A-Za-z]+)(\d+)?$", base)
    if not m:
        return {
            "doc_id": base,
            "course": None,
            "doc_type": "document",
            "sequence": None,
            "title": base.replace("_", " "),
            "tags": [],
            "source": "coursework",
        }

    doc_id, course, kind, seq = m.group(1), m.group(2).lower(), m.group(3).lower(), m.group(4)
    seq_i = int(seq) if seq else None

    if "lecture" in kind:
        doc_type = "lecture"
        title = f"{course.upper()} — Lecture {seq_i}" if seq_i else f"{course.upper()} — Lecture"
        tags = [course, "lecture"]
    elif "assignment" in kind:
        doc_type = "assignment"
        title = f"{course.upper()} — Assignment {seq_i}" if seq_i else f"{course.upper()} — Assignment"
        tags = [course, "assignment"]
    else:
        doc_type = kind
        title = f"{course.upper()} — {kind.title()} {seq_i}" if seq_i else f"{course.upper()} — {kind.title()}"
        tags = [course, kind]

    return {
        "doc_id": doc_id,
        "course": course,
        "doc_type": doc_type,
        "sequence": seq_i,
        "title": title,
        "tags": tags,
        "source": "coursework",
    }


def out_json_key(out_prefix: str, pdf_key: str) -> str:
    out_prefix = out_prefix if out_prefix.endswith("/") else out_prefix + "/"
    base = os.path.splitext(os.path.basename(pdf_key))[0]
    return f"{out_prefix}{base}.json"


def build_output_json(
    *,
    schema_version: int,
    bucket: str,
    pdf_key: str,
    head_meta: Dict[str, Any],
    extracted_at: datetime,
    method: str,
    method_version: str,
    language_hint: str,
    scanned_suspected: bool,
    stats: Dict[str, Any],
    pages: List[Dict[str, Any]],
) -> Dict[str, Any]:
    basename = os.path.basename(pdf_key)
    doc_meta = parse_doc_meta_from_basename(basename)

    content_type = head_meta.get("ContentType") or "application/pdf"
    size_bytes = head_meta.get("ContentLength")
    etag = (head_meta.get("ETag") or "").strip('"') or None

    uploaded_at = None
    lm = head_meta.get("LastModified")
    if lm:
        uploaded_at = iso_z(lm)

    return {
        "schema_version": schema_version,
        "doc": {
            "doc_id": doc_meta["doc_id"],
            "title": doc_meta["title"],
            "source": doc_meta["source"],
            "course": doc_meta["course"],
            "doc_type": doc_meta["doc_type"],
            "sequence": doc_meta["sequence"],
            "pdf": {
                "r2_bucket": bucket,
                "r2_key": pdf_key,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "etag": etag,
                "uploaded_at": uploaded_at,
            },
        },
        "extraction": {
            "extracted_at": iso_z(extracted_at),
            "method": method,
            "method_version": method_version,
            "language_hint": language_hint,
            "scanned_suspected": scanned_suspected,
            "stats": stats,
        },
        "pages": pages,
    }
