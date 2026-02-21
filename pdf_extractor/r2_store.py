from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
import os
import boto3
from botocore.config import Config

from .settings import Settings


class R2Store:
    def __init__(self, s: Settings):
        endpoint_url = f"https://{s.r2_account_id}.r2.cloudflarestorage.com"

        cfg = Config(
            signature_version="s3v4",
            retries={"max_attempts": 6, "mode": "standard"},
            connect_timeout=5,
            read_timeout=120,
        )

        self.bucket = s.bucket
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=s.r2_access_key_id,
            aws_secret_access_key=s.r2_secret_access_key,
            region_name="auto",
            config=cfg,
        )

    def list_pdf_keys(self, pdf_prefix: str, extracted_prefix: str) -> List[str]:
        extracted_map: Dict[str, bool] = {}
        token: Optional[str] = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": extracted_prefix, "MaxKeys": 1000}
            if token:
                kwargs["ContinuationToken"] = token
            resp = self.s3.list_objects_v2(**kwargs)
            for obj in resp.get("Contents", []):
                k = obj["Key"]
                if k.lower().endswith(".json"):
                    basename = os.path.splitext(os.path.basename(k))[0]
                    extracted_map[basename] = True
            if resp.get("IsTruncated"):
                token = resp.get("NextContinuationToken")
            else:
                break

        keys: List[str] = []
        token = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": pdf_prefix, "MaxKeys": 1000}
            if token:
                kwargs["ContinuationToken"] = token
            resp = self.s3.list_objects_v2(**kwargs)
            for obj in resp.get("Contents", []):
                k = obj["Key"]
                if k.lower().endswith(".pdf"):
                    basename = os.path.splitext(os.path.basename(k))[0]
                    if basename not in extracted_map:
                        keys.append(k)
            if resp.get("IsTruncated"):
                token = resp.get("NextContinuationToken")
            else:
                break
        return keys

    def head(self, key: str) -> Dict[str, Any]:
        return self.s3.head_object(Bucket=self.bucket, Key=key)

    def get_bytes(self, key: str) -> bytes:
        obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def put_json(self, key: str, data: Dict[str, Any]) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=body,
            ContentType="application/json; charset=utf-8",
        )
