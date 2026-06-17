import os

from src.infra_adapters.sarif.local_sarif_source import LocalSarifSource
from src.infra_adapters.storage.local_json_store import LocalJsonStore
from src.app.use_cases.compute_sast_metrics import compute_and_store


if __name__ == "__main__":
    sarif_dir = os.getenv("SARIF_DIR", "samples")
    metrics_prefix = os.getenv("METRICS_PREFIX", "metrics/sast")

    source = LocalSarifSource(sarif_dir=sarif_dir)
    store = LocalJsonStore(out_dir="out")

    result = compute_and_store(source=source, store=store, prefix=metrics_prefix)
    print(f"[+] total findings: {result.total_findings}")
    print(f"[+] metrics key:    {result.storage_key}")
