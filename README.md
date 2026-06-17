# appsec-metrics-sast

Turns raw SAST output (SARIF) into normalized **AppSec metrics** — findings by
severity, by rule, by file, and by tool — so security posture can be tracked
over time instead of read one scan at a time.

SARIF is the standard format emitted by CodeQL, Semgrep, and most modern SAST
tools, so this pipeline is tool-agnostic: point it at any SARIF and it produces
the same metrics shape.

## Why this exists

A single SAST scan tells you what is wrong today. It does not tell you whether
things are getting better, which rules generate the most noise, or which files
concentrate risk. This project answers those questions by normalizing SARIF into
a compact metrics document that can feed a dashboard or a trend store.

## What it computes

From one or more SARIF documents:

- total findings and unique rules
- findings by normalized severity (critical / high / medium / low / none)
- findings by tool (CodeQL, Semgrep, ...)
- top rules by frequency, with severity and description
- top files by finding count

Severity is normalized from each finding's `security-severity` score (CVSS-like,
using GitHub's banding) and falls back to the SARIF `level` when no score is
present.

## How it works (architecture)

The code follows a ports-and-adapters (hexagonal) layout so the metrics logic
stays pure and testable, independent of where SARIF comes from or where metrics
go.

```text
SARIF source (port)  ->  compute_metrics (pure domain)  ->  JSON store (port)
   |                          |                                 |
LocalSarifSource          severity mapping                 LocalJsonStore
S3SarifSource             aggregation                       S3JsonStore
```

- `src/app/ports/` - interfaces (`SarifSourcePort`, `JsonStorePort`)
- `src/app/metrics/` - pure severity mapping + aggregation (unit-tested)
- `src/app/use_cases/compute_sast_metrics.py` - orchestration
- `src/infra_adapters/sarif/` - local-directory and S3 SARIF sources
- `src/infra_adapters/storage/` - local-file and S3 JSON stores
- `src/handler.py` - AWS Lambda entry point (S3 SARIF -> S3 metrics)
- `scripts/local_run.py` - run locally against `samples/`

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# unit tests
PYTHONPATH=. python -m pytest -q

# compute metrics from the bundled sample SARIF
PYTHONPATH=. python scripts/local_run.py
# -> writes out/metrics/sast/dt=YYYY-MM-DD/run=...json
```

## Feeding it real scans

Any SAST tool that emits SARIF works. For example:

```bash
# Semgrep
semgrep --config auto --sarif --output samples/semgrep.sarif .

# CodeQL (via the CodeQL CLI or the github/codeql-action upload)
# drop the resulting .sarif into samples/ (local) or the S3 SARIF prefix (cloud)
```

Then re-run the pipeline to get updated metrics.

## AWS deployment (scheduled)

In the cloud the flow is: CI uploads SARIF to an S3 prefix, a scheduled Lambda
reads all SARIF under that prefix, computes metrics, and writes them back to a
metrics prefix partitioned by date and run.

`src/handler.py` expects:

- `DATA_BUCKET` - the S3 bucket
- `SARIF_PREFIX` - where CI uploads SARIF (e.g. `raw/sarif`)
- `METRICS_PREFIX` - where metrics are written (e.g. `metrics/sast`)

## Project structure

```text
src/
  app/
    ports/        # SarifSourcePort, JsonStorePort
    metrics/      # severity.py, sarif_metrics.py  (pure, tested)
    use_cases/    # compute_sast_metrics.py
  infra_adapters/
    sarif/        # local + S3 SARIF sources
    storage/      # local + S3 JSON stores
  handler.py      # AWS Lambda entry point
scripts/local_run.py
samples/          # example CodeQL + Semgrep SARIF
tests/
```

## Status and limitations

- Point-in-time metrics per run; trend aggregation across runs is not built yet
  (runs are partitioned by `dt`/`run` so they can be rolled up later).
- Severity normalization uses `security-severity` with a `level` fallback;
  tool-specific severity quirks are not individually tuned.
- The S3 adapters require AWS credentials/permissions at runtime.

## Roadmap

- Trend metrics and MTTR across partitioned runs
- Deduplication of the same finding reported by multiple tools
- Terraform module for the Lambda + schedule + bucket
- Direct feed into the executive Power BI dashboard (see `vuln-dashboard`)

## License

MIT
