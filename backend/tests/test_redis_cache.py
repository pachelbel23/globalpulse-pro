import json
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from storage.redis_cache import RedisCache


@pytest.fixture
def mock_redis():
    """Create a mock async Redis client."""
    mock = AsyncMock()
    return mock


@pytest.fixture
def cache(mock_redis):
    """Create a RedisCache instance with a mocked Redis client."""
    with patch("storage.redis_cache.redis.from_url", return_value=mock_redis):
        c = RedisCache("redis://localhost:6379")
    return c


@pytest.mark.asyncio
async def test_get_returns_none_on_miss(cache, mock_redis):
    mock_redis.get.return_value = None

    result = await cache.get("missing_key")

    assert result is None
    mock_redis.get.assert_awaited_once_with("missing_key")


@pytest.mark.asyncio
async def test_set_and_get_roundtrip(cache, mock_redis):
    data = {"price": 42.5, "currency": "USD"}

    await cache.set("trade:1", data, ttl=600)

    # Verify both primary and stale set calls were made
    assert mock_redis.set.await_count == 2
    mock_redis.set.assert_any_await(
        "trade:1", json.dumps(data).encode(), ex=600
    )
    mock_redis.set.assert_any_await(
        "stale:trade:1", json.dumps(data).encode(), ex=RedisCache.STALE_TTL
    )

    # Now simulate get returning the stored value
    mock_redis.get.return_value = json.dumps(data).encode()
    result = await cache.get("trade:1")

    assert result == data


@pytest.mark.asyncio
async def test_get_stale_returns_backup_on_miss(cache, mock_redis):
    data = {"price": 42.5}
    encoded = json.dumps(data).encode()

    # Primary miss, stale hit
    mock_redis.get.side_effect = [None, encoded]

    result, is_stale = await cache.get_with_stale("trade:1")

    assert result == data
    assert is_stale is True
    assert mock_redis.get.await_count == 2
    mock_redis.get.assert_any_await("trade:1")
    mock_redis.get.assert_any_await("stale:trade:1")


@pytest.mark.asyncio
async def test_get_stale_returns_none_when_both_miss(cache, mock_redis):
    # Both primary and stale miss
    mock_redis.get.side_effect = [None, None]

    result, is_stale = await cache.get_with_stale("trade:1")

    assert result is None
    assert is_stale is False
