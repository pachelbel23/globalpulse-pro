import logging

from services.fred_client import FredClient
from storage.influxdb import InfluxStorage
from storage.redis_cache import RedisCache

logger = logging.getLogger(__name__)

DEFAULT_SERIES = ["GDP", "CPIAUCSL", "UNRATE", "FEDFUNDS"]


async def fetch_fred_indicators(
    fred: FredClient,
    influx: InfluxStorage,
    cache: RedisCache,
) -> None:
    """Fetch the latest observations for each default FRED series,
    write the most recent value to InfluxDB, and cache the full series in Redis."""
    for series_id in DEFAULT_SERIES:
        try:
            series = await fred.get_observations(series_id)
            if series.data:
                latest = series.data[-1]
                await influx.write_metric(
                    measurement="fred",
                    tags={"series_id": series_id},
                    fields={"value": latest.value},
                )
            await cache.set(f"fred:{series_id}", series.model_dump(), ttl=900)
            logger.info(f"FRED {series_id}: {len(series.data)} points fetched")
        except Exception:
            logger.exception(f"Failed to fetch FRED {series_id}")
