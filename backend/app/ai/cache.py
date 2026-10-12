import hashlib
import json
import time
from typing import Any, Optional, Dict

class AnalysisCache:
    """
    In-memory / persistent cache for AI outputs.
    Ensures multi-tenant isolation by incorporating workspace_id into cache keys,
    along with model identity, prompt version, and packet content hash.
    """
    _store: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def generate_key(
        cls,
        workspace_id: str,
        meeting_id: str,
        feature_name: str,
        input_hash: str,
        model_name: str,
        pipeline_version: str = "1.0.0"
    ) -> str:
        raw_key = f"{workspace_id}:{meeting_id}:{feature_name}:{model_name}:{pipeline_version}:{input_hash}"
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        entry = cls._store.get(key)
        if not entry:
            return None
        # Optional TTL check (default 7 days)
        if time.time() > entry.get("expires_at", float("inf")):
            del cls._store[key]
            return None
        return entry.get("data")

    @classmethod
    def set(cls, key: str, data: Any, ttl_seconds: int = 604800) -> None:
        cls._store[key] = {
            "data": data,
            "expires_at": time.time() + ttl_seconds,
            "created_at": time.time()
        }

    @classmethod
    def invalidate_meeting(cls, meeting_id: str) -> int:
        """Invalidates all cached features when a meeting is re-analyzed or corrected."""
        keys_to_remove = [k for k in cls._store.keys() if meeting_id in k]
        for k in keys_to_remove:
            del cls._store[k]
        return len(keys_to_remove)

    @classmethod
    def clear_all(cls):
        cls._store.clear()
