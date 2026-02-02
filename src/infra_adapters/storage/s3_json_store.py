import json
import boto3
from typing import Any
class S3JsonStore:
def init(self, bucket: str):
self.bucket = bucket
self.s3 = boto3.client("s3")
def put_json(self, key: str, payload: Any) -> None:
    self.s3.put_object(
        Bucket=self.bucket,
        Key=key,
        Body=json.dumps(payload).encode("utf-8"),
        ContentType="application/json",
    )
