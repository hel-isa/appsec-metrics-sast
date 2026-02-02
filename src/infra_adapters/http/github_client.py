import json
import time
import urllib.request
from typing import List, Dict, Any
class GitHubClient:
BASE = "https://api.github.com"
def list_org_repos(self, org: str) -> List[Dict[str, Any]]:
    all_items: List[Dict[str, Any]] = []
    page = 1
    while True:
        url = f"{self.BASE}/orgs/{org}/repos?per_page=100&page={page}"
        items = self._get_json(url)
        if not items:
            break
        all_items.extend(items)
        page += 1
    return all_items

def _get_json(self, url: str) -> Any:
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "appsec-metrics-sast-demo",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            if attempt == 3:
                raise
            time.sleep(0.5 * attempt)
