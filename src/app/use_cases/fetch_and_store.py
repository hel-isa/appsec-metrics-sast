from dataclasses import dataclass
from src.app.ports.http_client import GitHubPort
from src.app.ports.storage import JsonStorePort
from src.utils.time import utc_date_str, utc_timestamp_str
@dataclass(frozen=True)
class FetchResult:
repo_count: int
s3_key: str
def fetch_repos_and_store(
github: GitHubPort,
store: JsonStorePort,
org: str,
prefix: str,
) -> FetchResult:
repos = github.list_org_repos(org)
rows = []
for r in repos:
    rows.append({
        "org": org,
        "repo_id": r["id"],
        "repo_name": r["name"],
        "full_name": r["full_name"],
        "is_private": r["private"],
        "stars": r["stargazers_count"],
        "forks": r["forks_count"],
        "open_issues": r["open_issues_count"],
        "updated_at": r["updated_at"],
    })

dt = utc_date_str()
run = utc_timestamp_str()
key = f"{prefix}/dt={dt}/run={run}.json"

store.put_json(key=key, payload=rows)

return FetchResult(repo_count=len(rows), s3_key=key)
