import json
from typing import Any

import redis.asyncio as redis


class RedisCache:
    STALE_PREFIX = "stale:"
    STALE_TTL = 86400  # 24h stale backup

    def __init__(self, url: str):
        self.redis = redis.from_url(url, decode_responses=False)

    async def get(self, key: str) -> Any | None:
        """Get and JSON parse, return None on miss."""
        raw = await self.redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set(self, key: str, data: Any, ttl: int = 300) -> None:
        """JSON serialize, set with TTL, also set stale backup with STALE_TTL."""
        encoded = json.dumps(data).encode()
        await self.redis.set(key, encoded, ex=ttl)
        await self.redis.set(
            f"{self.STALE_PREFIX}{key}", encoded, ex=self.STALE_TTL
        )

    async def get_with_stale(self, key: str) -> tuple[Any | None, bool]:
        """Try primary first, then stale backup. Returns (data, is_stale)."""
        raw = await self.redis.get(key)
        if raw is not None:
            return json.loads(raw), False

        stale_raw = await self.redis.get(f"{self.STALE_PREFIX}{key}")
        if stale_raw is not None:
            return json.loads(stale_raw), True

        return None, False

    async def delete(self, key: str) -> None:
        """Delete both primary and stale keys."""
        await self.redis.delete(key, f"{self.STALE_PREFIX}{key}")

    async def close(self) -> None:
        """Close redis connection."""
        await self.redis.aclose()
