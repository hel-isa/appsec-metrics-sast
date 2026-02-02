# appsec-metrics-sast (demo)

Demo pipeline: AWS Lambda (scheduled) fetches data from GitHub public API and stores JSON in S3.

## Output
Writes one JSON file per run:
s3://<bucket>/<prefix>/dt=YYYY-MM-DD/run=YYYYMMDDTHHMMSSZ.json

Default prefix: raw/github_repos

## Local dev (tests only)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
Deploy (Terraform) - later
See infra/terraform
