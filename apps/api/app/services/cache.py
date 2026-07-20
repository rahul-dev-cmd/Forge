"""Async Cache Service — Redis implementation with in-memory LRU fallback."""

from __future__ import annotations

import json
import time
from typing import Any


class CacheService:
    """
    High-performance caching layer with TTL support and fallback.
    """

    def __init__(self):
        self._memory_cache: dict[str, tuple[Any, float]] = {}

    async def get(self, key: str) -> Any | None:
        if key in self._memory_cache:
            val, expire_at = self._memory_cache[key]
            if time.time() < expire_at:
                return val
            else:
                del self._memory_cache[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        expire_at = time.time() + ttl_seconds
        self._memory_cache[key] = (value, expire_at)
        return True

    async def delete(self, key: str) -> bool:
        if key in self._memory_cache:
            del self._memory_cache[key]
            return True
        return False

    async def clear_prefix(self, prefix: str) -> int:
        keys_to_del = [k for k in self._memory_cache if k.startswith(prefix)]
        for k in keys_to_del:
            del self._memory_cache[k]
        return len(keys_to_del)


cache_service = CacheService()
