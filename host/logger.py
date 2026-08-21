import json
import threading
from datetime import datetime, timezone


class JsonlLogger:
    """Append-only JSONL log of every MCP-relevant interaction."""

    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()

    def log(self, *, server: str, transport: str, direction: str, type_: str,
             id_, method: str, latency_ms: float) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "server": server,
            "transport": transport,
            "direction": direction,
            "type": type_,
            "id": id_,
            "method": method,
            "latency_ms": round(latency_ms, 2),
        }
        with self._lock, open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")
