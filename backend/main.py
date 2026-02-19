import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from core.config import settings
from storage.influxdb import InfluxStorage
from storage.redis_cache import RedisCache
from scheduler.jobs import register_jobs, start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.influx = InfluxStorage(
        url=settings.influxdb_url,
        token=settings.influxdb_token,
        org=settings.influxdb_org,
        bucket=settings.influxdb_bucket,
    )
    app.state.cache = RedisCache(url=settings.redis_url)

    register_jobs(app.state.influx, app.state.cache)
    start_scheduler()
    logger.info("Global Pulse Pro backend started")

    yield

    # Shutdown
    stop_scheduler()
    await app.state.influx.close()
    await app.state.cache.close()
    logger.info("Global Pulse Pro backend stopped")


app = FastAPI(
    title="Global Pulse Pro",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}
