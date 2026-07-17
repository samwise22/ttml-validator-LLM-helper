import json
import threading
from datetime import datetime, timezone
from pathlib import Path


class JobStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def update(self, job_id: str, **values) -> dict:
        with self.lock:
            path = self.root / job_id / "job.json"
            current = json.loads(path.read_text()) if path.exists() else {"id": job_id}
            current.update(values)
            current["updatedAt"] = datetime.now(timezone.utc).isoformat()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(current, indent=2), encoding="utf-8")
            return current

    def get(self, job_id: str) -> dict | None:
        path = self.root / job_id / "job.json"
        return json.loads(path.read_text()) if path.exists() else None
