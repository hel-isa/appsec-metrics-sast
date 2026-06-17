import json
from pathlib import Path
from typing import Any


class LocalJsonStore:
    def __init__(self, out_dir: str = "out"):
        self.out_dir = Path(out_dir)

    def put_json(self, key: str, payload: Any) -> None:
        local_path = self.out_dir / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"[+] wrote metrics to {local_path}")
