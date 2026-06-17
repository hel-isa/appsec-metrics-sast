import os

from src.utils.logging import configure_logging
from src.infra_adapters.sarif.s3_sarif_source import S3SarifSource
from src.infra_adapters.storage.s3_json_store import S3JsonStore
from src.app.use_cases.compute_sast_metrics import compute_and_store


def _env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing env var: {name}")
    return value


def lambda_handler(event, context):
    configure_logging()

    bucket = _env("DATA_BUCKET")
    sarif_prefix = _env("SARIF_PREFIX")     # where CI uploads SARIF, e.g. raw/sarif
    metrics_prefix = _env("METRICS_PREFIX")  # where metrics land, e.g. metrics/sast

    source = S3SarifSource(bucket=bucket, prefix=sarif_prefix)
    store = S3JsonStore(bucket=bucket)

    result = compute_and_store(source=source, store=store, prefix=metrics_prefix)

    return {
        "status": "ok",
        "total_findings": result.total_findings,
        "metrics_key": result.storage_key,
    }
