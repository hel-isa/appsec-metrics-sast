from src.utils.logging import configure_logging
from src.infra_adapters.http.github_client import GitHubClient
from src.infra_adapters.storage.s3_json_store import S3JsonStore
from src.app.use_cases.fetch_and_store import fetch_repos_and_store
def lambda_handler(event, context):
configure_logging()
gh_org = _env("GITHUB_ORG")
bucket = _env("DATA_BUCKET")
prefix = _env("PREFIX")

http = GitHubClient()
store = S3JsonStore(bucket=bucket)

result = fetch_repos_and_store(
    github=http,
    store=store,
    org=gh_org,
    prefix=prefix,
)

return {
    "status": "ok",
    "org": gh_org,
    "repo_count": result.repo_count,
    "s3_key": result.s3_key,
}
def _env(name: str) -> str:
import os
v = os.getenv(name)
if not v:
raise RuntimeError(f"Missing env var: {name}")
return v
