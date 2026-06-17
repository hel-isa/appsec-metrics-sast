from dataclasses import dataclass

from src.app.ports.sarif_source import SarifSourcePort
from src.app.ports.storage import JsonStorePort
from src.app.metrics.sarif_metrics import compute_metrics
from src.utils.time import utc_date_str, utc_timestamp_str


@dataclass(frozen=True)
class MetricsResult:
    total_findings: int
    storage_key: str


def compute_and_store(
    source: SarifSourcePort,
    store: JsonStorePort,
    prefix: str,
    top_n: int = 10,
) -> MetricsResult:
    documents = source.load_documents()
    metrics = compute_metrics(documents, top_n=top_n)

    key = f"{prefix}/dt={utc_date_str()}/run={utc_timestamp_str()}.json"
    store.put_json(key=key, payload=metrics)

    return MetricsResult(
        total_findings=metrics["summary"]["total_findings"],
        storage_key=key,
    )
