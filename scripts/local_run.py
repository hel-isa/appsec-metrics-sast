import os
import json
from pathlib import Path

from src.infra_adapters.http.github_client import GitHubClient
from src.app.use_cases.fetch_and_store import fetch_repos_and_store

class LocalJsonStore:
    def __init__(self, out_dir: str = "out"):
        self.out_dir = Path(out_dir)

    def put_json(self, key: str, payload):
        # Key looks like: raw/github_repos/dt=YYYY-MM-DD/run=...json
        local_path = self.out_dir / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print("WROTE:", local_path)

if __name__ == "__main__":
    org = os.getenv("GITHUB_ORG", "aws")
    prefix = os.getenv("PREFIX", "raw/github_repos")

    gh = GitHubClient()
    store = LocalJsonStore(out_dir="out")

    result = fetch_repos_and_store(
        github=gh,
        store=store,
        org=org,
        prefix=prefix,
    )
    print("RESULT:", result)
