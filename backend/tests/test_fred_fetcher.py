from unittest.mock import AsyncMock, MagicMock

import pytest

from models.indicators import IndicatorPoint, IndicatorSeries
from fetchers.fred_fetcher import fetch_fred_indicators, DEFAULT_SERIES


def _make_series(series_id: str) -> IndicatorSeries:
    return IndicatorSeries(
        series_id=series_id,
        title=f"{series_id} title",
        units="Units",
        frequency="Monthly",
        data=[
            IndicatorPoint(date="2024-01-01", value=100.0),
            IndicatorPoint(date="2024-02-01", value=101.0),
        ],
    )


@pytest.mark.asyncio
async def test_fetches_all_default_series():
    """fetch_fred_indicators should call get_observations for every DEFAULT_SERIES,
    write each latest value to InfluxDB, and cache each series in Redis."""
    fred = AsyncMock()
    influx = AsyncMock()
    cache = AsyncMock()

    fred.get_observations = AsyncMock(
        side_effect=lambda sid: _make_series(sid)
    )

    await fetch_fred_indicators(fred, influx, cache)

    # get_observations called once per default series
    assert fred.get_observations.call_count == len(DEFAULT_SERIES)
    for sid in DEFAULT_SERIES:
        fred.get_observations.assert_any_call(sid)

    # write_metric called at least once per series (all have data)
    assert influx.write_metric.call_count >= len(DEFAULT_SERIES)

    # cache.set called once per series
    assert cache.set.call_count == len(DEFAULT_SERIES)
    for sid in DEFAULT_SERIES:
        cache.set.assert_any_call(
            f"fred:{sid}",
            _make_series(sid).model_dump(),
            ttl=900,
        )


@pytest.mark.asyncio
async def test_continues_on_single_series_failure():
    """If one series fails, the fetcher should continue with the remaining series."""
    fred = AsyncMock()
    influx = AsyncMock()
    cache = AsyncMock()

    call_count = 0

    async def side_effect(sid):
        nonlocal call_count
        call_count += 1
        if sid == "GDP":
            raise RuntimeError("FRED API error")
        return _make_series(sid)

    fred.get_observations = AsyncMock(side_effect=side_effect)

    await fetch_fred_indicators(fred, influx, cache)

    # All series attempted
    assert fred.get_observations.call_count == len(DEFAULT_SERIES)
    # Only non-failing series written (len - 1)
    assert influx.write_metric.call_count == len(DEFAULT_SERIES) - 1


@pytest.mark.asyncio
async def test_skips_write_when_no_data():
    """If a series returns empty data, write_metric should not be called for it."""
    fred = AsyncMock()
    influx = AsyncMock()
    cache = AsyncMock()

    empty_series = IndicatorSeries(
        series_id="GDP",
        title="GDP title",
        units="Units",
        frequency="Quarterly",
        data=[],
    )

    async def side_effect(sid):
        if sid == "GDP":
            return empty_series
        return _make_series(sid)

    fred.get_observations = AsyncMock(side_effect=side_effect)

    await fetch_fred_indicators(fred, influx, cache)

    # write_metric should only be called for series with data (all except GDP)
    assert influx.write_metric.call_count == len(DEFAULT_SERIES) - 1
    # cache.set still called for all series (even empty ones)
    assert cache.set.call_count == len(DEFAULT_SERIES)
