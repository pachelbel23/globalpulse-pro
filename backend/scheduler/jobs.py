import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import settings
from services.fred_client import FredClient
from storage.influxdb import InfluxStorage
from storage.redis_cache import RedisCache
from fetchers.fred_fetcher import fetch_fred_indicators

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def _run_async(coro_func, *args, **kwargs):
    """Schedule an async coroutine as a task on the running event loop."""
    loop = asyncio.get_event_loop()
    loop.create_task(coro_func(*args, **kwargs))


def register_jobs(influx: InfluxStorage, cache: RedisCache) -> None:
    """Register all periodic fetcher jobs on the scheduler."""
    fred = FredClient(api_key=settings.FRED_API_KEY)
    scheduler.add_job(
        _run_async,
        "interval",
        minutes=15,
        args=[fetch_fred_indicators, fred, influx, cache],
        id="fred_fetcher",
        name="Fetch FRED indicators",
        replace_existing=True,
    )


def start_scheduler() -> None:
    """Start the APScheduler event loop."""
    scheduler.start()


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    scheduler.shutdown(wait=False)
