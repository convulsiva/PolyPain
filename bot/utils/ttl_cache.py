import time
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl = ttl_seconds
        self._data: dict[Any, tuple[float, Any]] = {}

    def get(self, key: Any) -> Any | None:
        item = self._data.get(key)
        if not item:
            return None

        expires_at, value = item
        if time.time() > expires_at:
            self._data.pop(key, None)
            return None

        return value

    def set(self, key: Any, value: Any) -> None:
        self._data[key] = (time.time() + self.ttl, value)

    def clear(self) -> None:
        self._data.clear()
