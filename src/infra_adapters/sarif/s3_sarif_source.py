import json
from typing import Any, Dict, List

import boto3


class S3SarifSource:
    """Loads SARIF documents uploaded by CI under an S3 prefix."""

    def __init__(self, bucket: str, prefix: str):
        self.bucket = bucket
        self.prefix = prefix.rstrip("/")
        self.s3 = boto3.client("s3")

    def load_documents(self) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
            for obj in page.get("Contents", []) or []:
                key = obj["Key"]
                if not key.endswith((".sarif", ".json")):
                    continue
                body = self.s3.get_object(Bucket=self.bucket, Key=key)["Body"].read()
                docs.append(json.loads(body.decode("utf-8")))
        return docs
