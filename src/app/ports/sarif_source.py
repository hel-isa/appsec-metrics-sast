from typing import Protocol, List, Dict, Any


class SarifSourcePort(Protocol):
    """A source that yields parsed SARIF documents (already JSON-decoded)."""

    def load_documents(self) -> List[Dict[str, Any]]: ...
