from typing import Protocol, List, Dict, Any

class GitHubPort(Protocol):
    def list_org_repos(self, org: str) -> List[Dict[str, Any]]: ...
