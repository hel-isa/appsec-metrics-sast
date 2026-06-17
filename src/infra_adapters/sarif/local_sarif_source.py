import json
from pathlib import Path
from typing import Any, Dict, List


class LocalSarifSource:
    """Loads every *.sarif / *.json SARIF document from a local directory."""

    def __init__(self, sarif_dir: str = "samples"):
        self.sarif_dir = Path(sarif_dir)

    def load_documents(self) -> List[Dict[str, Any]]:
        docs: List[Dict[str, Any]] = []
        paths = sorted(self.sarif_dir.glob("*.sarif")) + sorted(self.sarif_dir.glob("*.json"))
        for path in paths:
            with open(path, "r", encoding="utf-8") as f:
                docs.append(json.load(f))
        return docs
