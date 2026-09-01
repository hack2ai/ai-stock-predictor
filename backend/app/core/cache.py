from __future__ import annotations

import time
from threading import Lock
from typing import Any, Callable


class TTLCache:
    def __init__(self, ttl_seconds: int = 300, max_items: int = 256):
        self.ttl_seconds = ttl_seconds
        self.max_items = max_items
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = Lock()

    def get_or_set(self, key: str, factory: Callable[[], Any]) -> Any:
        now = time.monotonic()
        with self._lock:
            item = self._store.get(key)
            if item and now - item[0] < self.ttl_seconds:
                return item[1]
        value = factory()
        with self._lock:
            if len(self._store) >= self.max_items:
                oldest = min(self._store, key=lambda cache_key: self._store[cache_key][0])
                self._store.pop(oldest, None)
            self._store[key] = (time.monotonic(), value)
        return value


analysis_cache = TTLCache(ttl_seconds=300)
