# Global Pulse Pro — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an enterprise global strategic intelligence dashboard with a TypeScript/deck.gl frontend and Python/FastAPI backend, serving real-time economic indicators, logistics data, and AI-powered business model auditing.

**Architecture:** Fully decoupled frontend (Vite + TypeScript + deck.gl + MapLibre) communicating via REST + WebSocket to a Python FastAPI backend. Backend uses InfluxDB for time-series storage, Redis for caching, APScheduler for data ingestion, and Groq LLM for AI analysis.

**Tech Stack:** Python 3.12, FastAPI, InfluxDB 2.7, Redis 7, APScheduler, httpx, Firecrawl, Groq SDK | TypeScript, Vite, deck.gl, MapLibre GL JS, D3.js

---

## Phase 1: Project Scaffolding & Infrastructure

### Task 1: Initialize monorepo structure

**Files:**
- Create: `backend/main.py`
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/core/__init__.py`
- Create: `backend/core/config.py`
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/vite-env.d.ts`
- Create: `docker-compose.yml`
- Create: `.gitignore`
- Create: `CLAUDE.md`

**Step 1: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
.env
*.egg-info/

# Node
node_modules/
dist/
.vite/

# IDE
.vscode/
.idea/

# Docker
influxdb-data/
redis-data/

# OS
.DS_Store
```

**Step 2: Create backend requirements.txt**

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.5
pydantic-settings==2.7.1
influxdb-client[async]==1.46.0
redis[hiredis]==5.2.1
apscheduler==3.10.4
httpx==0.28.1
firecrawl-py==1.10.2
groq==0.15.0
websockets==14.1
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-httpx==0.35.0
pytest-cov==6.0.0
```

**Step 3: Create backend/.env.example**

```bash
# Server
HOST=0.0.0.0
PORT=8000
ENV=development

# Storage
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=dev-token
INFLUXDB_ORG=global-pulse
INFLUXDB_BUCKET=trade-metrics
REDIS_URL=redis://localhost:6379

# External APIs
FRED_API_KEY=
FIRECRAWL_API_KEY=
GROQ_API_KEY=

# Scraper
SCRAPER_STORE_PATH=./data/scrapers.json
SCRAPER_MAX_CONCURRENT=3
```

**Step 4: Create backend/core/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    env: str = "development"

    influxdb_url: str = "http://localhost:8086"
    influxdb_token: str = ""
    influxdb_org: str = "global-pulse"
    influxdb_bucket: str = "trade-metrics"

    redis_url: str = "redis://localhost:6379"

    fred_api_key: str = ""
    firecrawl_api_key: str = ""
    groq_api_key: str = ""

    scraper_store_path: str = "./data/scrapers.json"
    scraper_max_concurrent: int = 3

    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

**Step 5: Create backend/core/__init__.py**

```python
```

**Step 6: Create backend/main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Global Pulse Pro",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}
```

**Step 7: Create frontend scaffolding**

`frontend/package.json`:
```json
{
  "name": "global-pulse-pro",
  "private": true,
  "version": "3.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "typecheck": "tsc --noEmit"
  },
  "devDependencies": {
    "typescript": "^5.7.0",
    "vite": "^6.1.0"
  },
  "dependencies": {
    "@deck.gl/core": "^9.1.0",
    "@deck.gl/layers": "^9.1.0",
    "@deck.gl/mapbox": "^9.1.0",
    "maplibre-gl": "^4.7.0",
    "d3": "^7.9.0"
  }
}
```

`frontend/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"]
}
```

`frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
});
```

`frontend/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Global Pulse Pro</title>
    <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.0/dist/maplibre-gl.css" />
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

`frontend/src/vite-env.d.ts`:
```typescript
/// <reference types="vite/client" />
```

`frontend/src/main.ts`:
```typescript
import './styles/main.css';

const app = document.getElementById('app');
if (app) {
  app.innerHTML = '<h1>Global Pulse Pro</h1><p>Loading...</p>';
}
```

Create `frontend/src/styles/main.css`:
```css
:root {
  --bg-primary: #0a0e17;
  --bg-secondary: #111827;
  --bg-panel: #1a2332;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --accent: #3b82f6;
  --danger: #ef4444;
  --success: #22c55e;
  --warning: #f59e0b;
  --border: #1e293b;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  overflow: hidden;
  height: 100vh;
  width: 100vw;
}

#app {
  height: 100%;
  width: 100%;
}
```

**Step 8: Create docker-compose.yml**

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
    environment:
      VITE_API_URL: http://localhost:8000

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    env_file:
      - ./backend/.env
    depends_on:
      - influxdb
      - redis

  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    volumes:
      - influxdb-data:/var/lib/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=admin12345
      - DOCKER_INFLUXDB_INIT_ORG=global-pulse
      - DOCKER_INFLUXDB_INIT_BUCKET=trade-metrics
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=dev-token

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  influxdb-data:
```

**Step 9: Create CLAUDE.md**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Global Pulse Pro — enterprise global strategic intelligence dashboard. TypeScript frontend + Python FastAPI backend, fully decoupled.

## Commands

### Backend
```bash
cd backend
pip install -r requirements.txt          # Install dependencies
uvicorn main:app --reload --port 8000    # Run dev server
pytest tests/ -v                         # Run all tests
pytest tests/test_risk_engine.py -v      # Run single test file
pytest tests/ -k "test_anomaly" -v       # Run tests by keyword
pytest tests/ --cov=services             # Coverage report
```

### Frontend
```bash
cd frontend
npm install                              # Install dependencies
npm run dev                              # Vite dev server on :5173
npm run build                            # Production build
npm run typecheck                        # TypeScript check
```

### Docker (full stack)
```bash
docker compose up -d                     # Start all services
docker compose down                      # Stop all services
docker compose logs -f backend           # Tail backend logs
```

## Architecture

- `backend/api/` — FastAPI route handlers (thin layer, validation + delegation to services)
- `backend/services/` — Business logic (FRED client, risk engine, anomaly detection, LLM)
- `backend/fetchers/` — Scheduled data ingestion tasks (called by APScheduler)
- `backend/models/` — Pydantic models shared by api/ and services/
- `backend/storage/` — InfluxDB and Redis abstraction layer
- `backend/core/` — Config, middleware, FastAPI dependency injection
- `frontend/src/components/` — TypeScript class-based UI components (no framework)
- `frontend/src/services/` — API client, WebSocket, data processing
- `frontend/src/config/` — Static data (regions, ports, indicators)

## Key Rules

- `api/` never imports from `storage/` directly — always through `services/`
- `fetchers/` are thin wrappers around `services/` functions, called by scheduler
- All economic calculation formulas (risk weights, Welford anomaly detection, z-score) MUST have unit tests
- TDD: write failing test first, then implement, then refactor
- Frontend uses pure TypeScript classes (no React/Vue/Angular)
```

**Step 10: Commit**

```bash
git add -A
git commit -m "chore: scaffold monorepo with backend, frontend, docker-compose"
```

---

### Task 2: Backend storage layer — InfluxDB client

**Files:**
- Create: `backend/storage/__init__.py`
- Create: `backend/storage/influxdb.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_influxdb_storage.py`
- Create: `backend/tests/conftest.py`

**Step 1: Write the failing test**

`backend/tests/conftest.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_influx_write_api():
    return MagicMock()


@pytest.fixture
def mock_influx_query_api():
    api = AsyncMock()
    api.query = AsyncMock(return_value=[])
    return api
```

`backend/tests/__init__.py`: empty file.

`backend/tests/test_influxdb_storage.py`:
```python
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from storage.influxdb import InfluxStorage


@pytest.fixture
def storage():
    with patch("storage.influxdb.InfluxDBClientAsync") as mock_cls:
        instance = AsyncMock()
        instance.write_api.return_value = AsyncMock()
        instance.query_api.return_value = AsyncMock()
        mock_cls.return_value = instance
        s = InfluxStorage(
            url="http://localhost:8086",
            token="test-token",
            org="test-org",
            bucket="test-bucket",
        )
        yield s


class TestInfluxStorage:
    @pytest.mark.asyncio
    async def test_write_metric(self, storage):
        await storage.write_metric(
            measurement="fred",
            tags={"series_id": "GDP"},
            fields={"value": 25000.5},
        )
        storage.client.write_api.return_value.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_returns_list(self, storage):
        storage.client.query_api.return_value.query.return_value = []
        result = await storage.query_metric("fred", "GDP", "-30d")
        assert isinstance(result, list)
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_influxdb_storage.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'storage'`

**Step 3: Write minimal implementation**

`backend/storage/__init__.py`: empty file.

`backend/storage/influxdb.py`:
```python
from datetime import datetime
from typing import Any

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point


class InfluxStorage:
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.org = org
        self.bucket = bucket
        self.client = InfluxDBClientAsync(url=url, token=token, org=org)

    async def write_metric(
        self,
        measurement: str,
        tags: dict[str, str],
        fields: dict[str, Any],
        timestamp: datetime | None = None,
    ) -> None:
        point = Point(measurement)
        for k, v in tags.items():
            point = point.tag(k, v)
        for k, v in fields.items():
            point = point.field(k, v)
        if timestamp:
            point = point.time(timestamp)

        write_api = self.client.write_api()
        await write_api.write(bucket=self.bucket, record=point)

    async def query_metric(
        self, measurement: str, series_id: str, range_str: str = "-30d"
    ) -> list[dict[str, Any]]:
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {range_str})
          |> filter(fn: (r) => r._measurement == "{measurement}")
          |> filter(fn: (r) => r.series_id == "{series_id}")
          |> sort(columns: ["_time"])
        '''
        query_api = self.client.query_api()
        tables = await query_api.query(query, org=self.org)

        results = []
        for table in tables:
            for record in table.records:
                results.append({
                    "time": record.get_time().isoformat(),
                    "value": record.get_value(),
                    "field": record.get_field(),
                })
        return results

    async def close(self) -> None:
        await self.client.close()
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_influxdb_storage.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/storage/ backend/tests/
git commit -m "feat(storage): add InfluxDB async client with write/query"
```

---

### Task 3: Backend storage layer — Redis cache with stale-on-error

**Files:**
- Create: `backend/storage/redis_cache.py`
- Create: `backend/tests/test_redis_cache.py`

**Step 1: Write the failing test**

`backend/tests/test_redis_cache.py`:
```python
import json
import pytest
from unittest.mock import AsyncMock, patch
from storage.redis_cache import RedisCache


@pytest.fixture
def cache():
    with patch("storage.redis_cache.redis.from_url") as mock_from_url:
        mock_redis = AsyncMock()
        mock_from_url.return_value = mock_redis
        c = RedisCache(url="redis://localhost:6379")
        c.redis = mock_redis
        yield c


class TestRedisCache:
    @pytest.mark.asyncio
    async def test_get_returns_none_on_miss(self, cache):
        cache.redis.get = AsyncMock(return_value=None)
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_roundtrip(self, cache):
        data = {"value": 42.0}
        cache.redis.set = AsyncMock()
        cache.redis.get = AsyncMock(return_value=json.dumps(data).encode())
        await cache.set("key", data, ttl=300)
        result = await cache.get("key")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_stale_returns_backup_on_miss(self, cache):
        stale_data = {"value": 99.0}
        # Primary miss, stale hit
        cache.redis.get = AsyncMock(
            side_effect=[None, json.dumps(stale_data).encode()]
        )
        result = await cache.get_with_stale("key")
        assert result == (stale_data, True)  # (data, is_stale)

    @pytest.mark.asyncio
    async def test_get_stale_returns_none_when_both_miss(self, cache):
        cache.redis.get = AsyncMock(return_value=None)
        result = await cache.get_with_stale("key")
        assert result == (None, False)
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_redis_cache.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'storage.redis_cache'`

**Step 3: Write minimal implementation**

`backend/storage/redis_cache.py`:
```python
import json
from typing import Any

import redis.asyncio as redis


class RedisCache:
    STALE_PREFIX = "stale:"
    STALE_TTL = 86400  # 24h stale backup

    def __init__(self, url: str):
        self.redis = redis.from_url(url, decode_responses=False)

    async def get(self, key: str) -> Any | None:
        raw = await self.redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set(self, key: str, data: Any, ttl: int = 300) -> None:
        serialized = json.dumps(data, default=str)
        await self.redis.set(key, serialized, ex=ttl)
        # Always update stale backup with longer TTL
        await self.redis.set(
            f"{self.STALE_PREFIX}{key}", serialized, ex=self.STALE_TTL
        )

    async def get_with_stale(self, key: str) -> tuple[Any | None, bool]:
        """Returns (data, is_stale). Tries primary key first, then stale backup."""
        primary = await self.get(key)
        if primary is not None:
            return (primary, False)

        stale_raw = await self.redis.get(f"{self.STALE_PREFIX}{key}")
        if stale_raw is not None:
            return (json.loads(stale_raw), True)

        return (None, False)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key, f"{self.STALE_PREFIX}{key}")

    async def close(self) -> None:
        await self.redis.aclose()
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_redis_cache.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/storage/redis_cache.py backend/tests/test_redis_cache.py
git commit -m "feat(storage): add Redis cache with stale-on-error fallback"
```

---

## Phase 2: Data Ingestion — FRED API

### Task 4: Pydantic models for indicators

**Files:**
- Create: `backend/models/__init__.py`
- Create: `backend/models/indicators.py`
- Create: `backend/tests/test_models.py`

**Step 1: Write the failing test**

`backend/tests/test_models.py`:
```python
import pytest
from pydantic import ValidationError
from models.indicators import IndicatorPoint, IndicatorSeries


class TestIndicatorModels:
    def test_indicator_point_valid(self):
        p = IndicatorPoint(date="2026-01-15", value=25000.5)
        assert p.value == 25000.5

    def test_indicator_point_null_value(self):
        p = IndicatorPoint(date="2026-01-15", value=None)
        assert p.value is None

    def test_indicator_series_valid(self):
        s = IndicatorSeries(
            series_id="GDP",
            title="Gross Domestic Product",
            units="Billions of Dollars",
            frequency="Quarterly",
            data=[
                IndicatorPoint(date="2025-10-01", value=23000.0),
                IndicatorPoint(date="2026-01-01", value=23500.0),
            ],
        )
        assert len(s.data) == 2
        assert s.series_id == "GDP"

    def test_indicator_series_empty_data(self):
        s = IndicatorSeries(
            series_id="GDP",
            title="GDP",
            units="USD",
            frequency="Q",
            data=[],
        )
        assert s.data == []
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_models.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`backend/models/__init__.py`: empty file.

`backend/models/indicators.py`:
```python
from pydantic import BaseModel


class IndicatorPoint(BaseModel):
    date: str
    value: float | None


class IndicatorSeries(BaseModel):
    series_id: str
    title: str
    units: str
    frequency: str
    data: list[IndicatorPoint]
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_models.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/models/ backend/tests/test_models.py
git commit -m "feat(models): add Pydantic models for FRED indicators"
```

---

### Task 5: FRED API client service

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/fred_client.py`
- Create: `backend/tests/test_fred_client.py`

**Step 1: Write the failing test**

`backend/tests/test_fred_client.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch
from services.fred_client import FredClient

MOCK_FRED_RESPONSE = {
    "seriess": [
        {
            "id": "GDP",
            "title": "Gross Domestic Product",
            "units": "Billions of Dollars",
            "frequency": "Quarterly",
        }
    ]
}

MOCK_FRED_OBSERVATIONS = {
    "observations": [
        {"date": "2025-10-01", "value": "23000.0"},
        {"date": "2026-01-01", "value": "23500.5"},
        {"date": "2026-01-15", "value": "."},  # FRED uses "." for missing
    ]
}


class TestFredClient:
    @pytest.mark.asyncio
    async def test_get_series_info(self):
        client = FredClient(api_key="test-key")
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MOCK_FRED_RESPONSE
            result = await client.get_series_info("GDP")
            assert result["id"] == "GDP"
            assert result["title"] == "Gross Domestic Product"

    @pytest.mark.asyncio
    async def test_get_observations_filters_missing(self):
        client = FredClient(api_key="test-key")
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = MOCK_FRED_OBSERVATIONS
            series = await client.get_observations("GDP")
            # "." values should be filtered out
            assert len(series.data) == 2
            assert series.data[0].value == 23000.0
            assert series.data[1].value == 23500.5

    @pytest.mark.asyncio
    async def test_get_observations_empty(self):
        client = FredClient(api_key="test-key")
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"observations": []}
            series = await client.get_observations("INVALID")
            assert series.data == []
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_fred_client.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`backend/services/__init__.py`: empty file.

`backend/services/fred_client.py`:
```python
from typing import Any

import httpx

from models.indicators import IndicatorPoint, IndicatorSeries


FRED_BASE_URL = "https://api.stlouisfed.org/fred"


class FredClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def _get(self, endpoint: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        all_params = {"api_key": self.api_key, "file_type": "json"}
        if params:
            all_params.update(params)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{FRED_BASE_URL}/{endpoint}", params=all_params)
            resp.raise_for_status()
            return resp.json()

    async def get_series_info(self, series_id: str) -> dict[str, Any]:
        data = await self._get("series", {"series_id": series_id})
        return data["seriess"][0]

    async def get_observations(
        self,
        series_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> IndicatorSeries:
        params: dict[str, str] = {"series_id": series_id}
        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date

        raw = await self._get("series/observations", params)
        info = await self.get_series_info(series_id)

        points = []
        for obs in raw.get("observations", []):
            if obs["value"] == ".":
                continue
            points.append(
                IndicatorPoint(date=obs["date"], value=float(obs["value"]))
            )

        return IndicatorSeries(
            series_id=series_id,
            title=info.get("title", series_id),
            units=info.get("units", ""),
            frequency=info.get("frequency", ""),
            data=points,
        )
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_fred_client.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/services/fred_client.py backend/tests/test_fred_client.py
git commit -m "feat(services): add FRED API client with observation filtering"
```

---

### Task 6: FRED API route

**Files:**
- Create: `backend/api/__init__.py`
- Create: `backend/api/router.py`
- Create: `backend/api/indicators.py`
- Create: `backend/core/dependencies.py`
- Create: `backend/core/exceptions.py`
- Create: `backend/tests/test_api/__init__.py`
- Create: `backend/tests/test_api/test_indicators.py`

**Step 1: Write the failing test**

`backend/tests/test_api/test_indicators.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from main import app
from models.indicators import IndicatorPoint, IndicatorSeries


@pytest.fixture
def mock_fred():
    series = IndicatorSeries(
        series_id="GDP",
        title="Gross Domestic Product",
        units="Billions of Dollars",
        frequency="Quarterly",
        data=[
            IndicatorPoint(date="2025-10-01", value=23000.0),
            IndicatorPoint(date="2026-01-01", value=23500.5),
        ],
    )
    with patch("api.indicators.get_fred_client") as mock:
        client = AsyncMock()
        client.get_observations = AsyncMock(return_value=series)
        mock.return_value = client
        yield client


@pytest.mark.asyncio
async def test_get_fred_series(mock_fred):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/indicators/fred/GDP")
    assert resp.status_code == 200
    body = resp.json()
    assert body["series_id"] == "GDP"
    assert len(body["data"]) == 2


@pytest.mark.asyncio
async def test_get_fred_series_not_found(mock_fred):
    mock_fred.get_observations.side_effect = Exception("Not found")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/indicators/fred/INVALID")
    assert resp.status_code == 502
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_api/test_indicators.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`backend/api/__init__.py`: empty file.

`backend/core/exceptions.py`:
```python
from fastapi import HTTPException


class UpstreamError(HTTPException):
    def __init__(self, source: str, detail: str = ""):
        super().__init__(
            status_code=502,
            detail=f"Upstream error from {source}: {detail}",
        )
```

`backend/core/dependencies.py`:
```python
from services.fred_client import FredClient
from core.config import settings


def get_fred_client() -> FredClient:
    return FredClient(api_key=settings.fred_api_key)
```

`backend/api/indicators.py`:
```python
from fastapi import APIRouter, Query

from core.dependencies import get_fred_client
from core.exceptions import UpstreamError
from models.indicators import IndicatorSeries

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("/fred/{series_id}", response_model=IndicatorSeries)
async def get_fred_series(
    series_id: str,
    start: str | None = Query(None, description="Start date YYYY-MM-DD"),
    end: str | None = Query(None, description="End date YYYY-MM-DD"),
):
    client = get_fred_client()
    try:
        return await client.get_observations(series_id, start, end)
    except Exception as e:
        raise UpstreamError("FRED", str(e))
```

`backend/api/router.py`:
```python
from fastapi import APIRouter
from api.indicators import router as indicators_router

api_router = APIRouter()
api_router.include_router(indicators_router)
```

Update `backend/main.py` — add after middleware:
```python
from api.router import api_router
app.include_router(api_router)
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_api/test_indicators.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/api/ backend/core/dependencies.py backend/core/exceptions.py backend/tests/test_api/ backend/main.py
git commit -m "feat(api): add FRED indicators REST endpoint"
```

---

### Task 7: FRED fetcher + scheduler integration

**Files:**
- Create: `backend/fetchers/__init__.py`
- Create: `backend/fetchers/fred_fetcher.py`
- Create: `backend/scheduler/__init__.py`
- Create: `backend/scheduler/jobs.py`
- Create: `backend/tests/test_fred_fetcher.py`

**Step 1: Write the failing test**

`backend/tests/test_fred_fetcher.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fetchers.fred_fetcher import fetch_fred_indicators

# Default FRED series to track
DEFAULT_SERIES = ["GDP", "CPIAUCSL", "UNRATE", "FEDFUNDS"]


class TestFredFetcher:
    @pytest.mark.asyncio
    async def test_fetches_all_default_series(self):
        mock_fred = AsyncMock()
        mock_influx = AsyncMock()
        mock_redis = AsyncMock()

        mock_fred.get_observations = AsyncMock(
            return_value=MagicMock(
                series_id="GDP",
                data=[MagicMock(date="2026-01-01", value=25000.0)],
                model_dump=lambda: {"series_id": "GDP", "data": []},
            )
        )

        await fetch_fred_indicators(
            fred=mock_fred,
            influx=mock_influx,
            cache=mock_redis,
        )

        assert mock_fred.get_observations.call_count == len(DEFAULT_SERIES)
        assert mock_influx.write_metric.call_count >= len(DEFAULT_SERIES)
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_fred_fetcher.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`backend/fetchers/__init__.py`: empty file.

`backend/fetchers/fred_fetcher.py`:
```python
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
    for series_id in DEFAULT_SERIES:
        try:
            series = await fred.get_observations(series_id)

            # Write latest point to InfluxDB
            if series.data:
                latest = series.data[-1]
                await influx.write_metric(
                    measurement="fred",
                    tags={"series_id": series_id},
                    fields={"value": latest.value},
                )

            # Cache full series in Redis (15min TTL)
            await cache.set(
                f"fred:{series_id}",
                series.model_dump(),
                ttl=900,
            )
            logger.info(f"FRED {series_id}: {len(series.data)} points fetched")

        except Exception:
            logger.exception(f"Failed to fetch FRED {series_id}")
```

`backend/scheduler/__init__.py`: empty file.

`backend/scheduler/jobs.py`:
```python
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
    """Wrapper to run async fetcher from sync APScheduler job."""
    loop = asyncio.get_event_loop()
    loop.create_task(coro_func(*args, **kwargs))


def register_jobs(influx: InfluxStorage, cache: RedisCache) -> None:
    fred = FredClient(api_key=settings.fred_api_key)

    scheduler.add_job(
        _run_async,
        "interval",
        minutes=15,
        args=[fetch_fred_indicators, fred, influx, cache],
        id="fred_fetcher",
        name="Fetch FRED indicators",
        replace_existing=True,
    )

    logger.info("Scheduled jobs registered")


def start_scheduler() -> None:
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_fred_fetcher.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/fetchers/ backend/scheduler/ backend/tests/test_fred_fetcher.py
git commit -m "feat(fetchers): add FRED scheduled data ingestion"
```

---

## Phase 3: Analytics Engine

### Task 8: Welford anomaly detector

**Files:**
- Create: `backend/services/anomaly_detector.py`
- Create: `backend/tests/test_anomaly_detector.py`

**Step 1: Write the failing test**

`backend/tests/test_anomaly_detector.py`:
```python
import pytest
from services.anomaly_detector import WelfordDetector


class TestWelfordDetector:
    def test_no_anomaly_with_stable_data(self):
        detector = WelfordDetector()
        # Feed 100 stable values
        for _ in range(100):
            result = detector.update("fred:GDP", 25000.0)
        assert result.is_anomaly is False

    def test_detects_spike(self):
        detector = WelfordDetector()
        # Establish baseline with 50 stable values
        for _ in range(50):
            detector.update("fred:GDP", 25000.0)
        # Inject a massive spike
        result = detector.update("fred:GDP", 50000.0)
        assert result.is_anomaly is True
        assert result.z_score >= 3.0
        assert result.severity == "critical"

    def test_needs_minimum_samples(self):
        detector = WelfordDetector(min_samples=10)
        result = detector.update("fred:GDP", 25000.0)
        assert result.is_anomaly is False
        assert result.z_score == 0.0

    def test_severity_levels(self):
        detector = WelfordDetector()
        # Establish baseline
        for _ in range(50):
            detector.update("test", 100.0)
        # z >= 1.5 but < 3.0 → low
        result = detector.update("test", 115.0)
        # Exact severity depends on stddev, but should not be critical
        assert result.severity in ("low", "medium", "none")

    def test_independent_streams(self):
        detector = WelfordDetector()
        for _ in range(50):
            detector.update("stream_a", 100.0)
            detector.update("stream_b", 1000.0)
        # Spike in A should not affect B
        result_a = detector.update("stream_a", 500.0)
        result_b = detector.update("stream_b", 1005.0)
        assert result_a.is_anomaly is True
        assert result_b.is_anomaly is False
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_anomaly_detector.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`backend/services/anomaly_detector.py`:
```python
import math
from dataclasses import dataclass, field


@dataclass
class AnomalyResult:
    key: str
    value: float
    mean: float
    stddev: float
    z_score: float
    is_anomaly: bool
    severity: str  # "none" | "low" | "medium" | "critical"


@dataclass
class _StreamState:
    count: int = 0
    mean: float = 0.0
    m2: float = 0.0

    @property
    def variance(self) -> float:
        if self.count < 2:
            return 0.0
        return self.m2 / self.count

    @property
    def stddev(self) -> float:
        return math.sqrt(self.variance)


class WelfordDetector:
    """Streaming anomaly detection using Welford's online algorithm."""

    def __init__(self, min_samples: int = 10):
        self.min_samples = min_samples
        self._streams: dict[str, _StreamState] = {}

    def update(self, key: str, value: float) -> AnomalyResult:
        if key not in self._streams:
            self._streams[key] = _StreamState()

        state = self._streams[key]

        # Welford update
        state.count += 1
        delta = value - state.mean
        state.mean += delta / state.count
        delta2 = value - state.mean
        state.m2 += delta * delta2

        # Not enough data yet
        if state.count < self.min_samples:
            return AnomalyResult(
                key=key, value=value,
                mean=state.mean, stddev=0.0, z_score=0.0,
                is_anomaly=False, severity="none",
            )

        stddev = state.stddev
        if stddev == 0:
            z_score = 0.0
        else:
            z_score = abs(value - state.mean) / stddev

        severity = "none"
        if z_score >= 3.0:
            severity = "critical"
        elif z_score >= 2.0:
            severity = "medium"
        elif z_score >= 1.5:
            severity = "low"

        return AnomalyResult(
            key=key, value=value,
            mean=state.mean, stddev=stddev, z_score=z_score,
            is_anomaly=z_score >= 1.5, severity=severity,
        )
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_anomaly_detector.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/services/anomaly_detector.py backend/tests/test_anomaly_detector.py
git commit -m "feat(services): add Welford streaming anomaly detector"
```

---

### Task 9: Risk scoring engine

**Files:**
- Create: `backend/services/risk_engine.py`
- Create: `backend/models/risk.py`
- Create: `backend/tests/test_risk_engine.py`

**Step 1: Write the failing test**

`backend/tests/test_risk_engine.py`:
```python
import pytest
from services.risk_engine import RiskEngine
from models.risk import RegionRiskInput


class TestRiskEngine:
    def test_score_within_bounds(self):
        engine = RiskEngine()
        inp = RegionRiskInput(
            region_code="apac",
            cpi_change=2.5,
            unemployment_rate=4.0,
            bdi_change=-10.0,
            port_congestion=0.3,
        )
        score = engine.calculate(inp)
        assert 0.0 <= score.overall <= 100.0

    def test_high_inflation_increases_risk(self):
        engine = RiskEngine()
        low = RegionRiskInput(
            region_code="apac",
            cpi_change=1.0,
            unemployment_rate=4.0,
            bdi_change=0.0,
            port_congestion=0.2,
        )
        high = RegionRiskInput(
            region_code="apac",
            cpi_change=8.0,
            unemployment_rate=4.0,
            bdi_change=0.0,
            port_congestion=0.2,
        )
        assert engine.calculate(high).overall > engine.calculate(low).overall

    def test_all_bad_signals_near_max(self):
        engine = RiskEngine()
        worst = RegionRiskInput(
            region_code="test",
            cpi_change=15.0,
            unemployment_rate=25.0,
            bdi_change=-50.0,
            port_congestion=1.0,
        )
        score = engine.calculate(worst)
        assert score.overall >= 70.0

    def test_all_good_signals_near_min(self):
        engine = RiskEngine()
        best = RegionRiskInput(
            region_code="test",
            cpi_change=1.5,
            unemployment_rate=3.0,
            bdi_change=10.0,
            port_congestion=0.05,
        )
        score = engine.calculate(best)
        assert score.overall <= 30.0
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_risk_engine.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`backend/models/risk.py`:
```python
from pydantic import BaseModel


class RegionRiskInput(BaseModel):
    region_code: str
    cpi_change: float        # YoY CPI % change
    unemployment_rate: float  # %
    bdi_change: float         # BDI % change (negative = bad)
    port_congestion: float    # 0.0 to 1.0


class RiskScore(BaseModel):
    region_code: str
    overall: float            # 0-100
    breakdown: dict[str, float]
```

`backend/services/risk_engine.py`:
```python
from models.risk import RegionRiskInput, RiskScore

# Weights must sum to 1.0
WEIGHTS = {
    "inflation": 0.30,
    "unemployment": 0.25,
    "shipping": 0.25,
    "port_congestion": 0.20,
}


def _normalize(value: float, low: float, high: float) -> float:
    """Clamp and normalize value to 0-100 scale."""
    clamped = max(low, min(value, high))
    return ((clamped - low) / (high - low)) * 100.0


class RiskEngine:
    def calculate(self, inp: RegionRiskInput) -> RiskScore:
        # Higher CPI change → higher risk (2% target, >10% extreme)
        inflation_risk = _normalize(inp.cpi_change, 0.0, 15.0)

        # Higher unemployment → higher risk
        unemployment_risk = _normalize(inp.unemployment_rate, 0.0, 25.0)

        # BDI drop → higher risk (invert: -50% = 100 risk, +20% = 0 risk)
        shipping_risk = _normalize(-inp.bdi_change, -20.0, 50.0)

        # Port congestion 0-1 → 0-100
        port_risk = inp.port_congestion * 100.0

        breakdown = {
            "inflation": round(inflation_risk, 1),
            "unemployment": round(unemployment_risk, 1),
            "shipping": round(shipping_risk, 1),
            "port_congestion": round(port_risk, 1),
        }

        overall = sum(
            breakdown[k] * WEIGHTS[k] for k in WEIGHTS
        )

        return RiskScore(
            region_code=inp.region_code,
            overall=round(overall, 1),
            breakdown=breakdown,
        )
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_risk_engine.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/services/risk_engine.py backend/models/risk.py backend/tests/test_risk_engine.py
git commit -m "feat(services): add multi-factor risk scoring engine"
```

---

## Phase 4: AI Integration

### Task 10: LLM client + Business Model Audit engine

**Files:**
- Create: `backend/services/llm_client.py`
- Create: `backend/services/audit_engine.py`
- Create: `backend/models/audit.py`
- Create: `backend/tests/test_audit_engine.py`

**Step 1: Write the failing test**

`backend/tests/test_audit_engine.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch
from services.audit_engine import AuditEngine
from models.audit import AuditRequest


MOCK_LLM_RESPONSE = """{
    "strengths": ["Strong brand recognition", "Low production costs"],
    "weaknesses": ["Single market dependency"],
    "opportunities": ["Southeast Asian expansion"],
    "threats": ["Rising tariffs", "Supply chain disruption"],
    "risk_summary": "Medium risk due to tariff exposure in target market."
}"""


class TestAuditEngine:
    @pytest.mark.asyncio
    async def test_audit_returns_swot(self):
        engine = AuditEngine(api_key="test")
        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = MOCK_LLM_RESPONSE
            request = AuditRequest(
                model_description="DTC footwear brand selling online",
                target_market="Vietnam",
                industry="Consumer Retail",
            )
            result = await engine.analyze(request)
            assert len(result.strengths) == 2
            assert len(result.threats) == 2
            assert "tariff" in result.risk_summary.lower()

    @pytest.mark.asyncio
    async def test_audit_handles_malformed_llm_response(self):
        engine = AuditEngine(api_key="test")
        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = "This is not JSON"
            request = AuditRequest(
                model_description="test",
                target_market="test",
                industry="test",
            )
            with pytest.raises(ValueError, match="parse"):
                await engine.analyze(request)
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_audit_engine.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`backend/models/audit.py`:
```python
from pydantic import BaseModel


class AuditRequest(BaseModel):
    model_description: str
    target_market: str
    industry: str


class SWOTReport(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    opportunities: list[str]
    threats: list[str]
    risk_summary: str
```

`backend/services/llm_client.py`:
```python
from groq import AsyncGroq


class LLMClient:
    def __init__(self, api_key: str):
        self.client = AsyncGroq(api_key=api_key)

    async def chat(self, system_prompt: str, user_prompt: str, model: str = "llama-3.1-70b-versatile") -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        return response.choices[0].message.content or ""
```

`backend/services/audit_engine.py`:
```python
import json

from models.audit import AuditRequest, SWOTReport
from services.llm_client import LLMClient

SYSTEM_PROMPT = """You are a global trade risk analyst. Given a business model description, target market, and industry, produce a SWOT analysis in JSON format.

Output ONLY valid JSON with these exact keys:
{
    "strengths": ["..."],
    "weaknesses": ["..."],
    "opportunities": ["..."],
    "threats": ["..."],
    "risk_summary": "One paragraph summary of key risks."
}

Consider: tariffs, supply chain logistics, local regulations, currency risk, labor costs, port congestion, and commodity price exposure."""


class AuditEngine:
    def __init__(self, api_key: str):
        self._llm = LLMClient(api_key=api_key)

    async def _call_llm(self, prompt: str) -> str:
        return await self._llm.chat(SYSTEM_PROMPT, prompt)

    async def analyze(self, request: AuditRequest) -> SWOTReport:
        prompt = (
            f"Business Model: {request.model_description}\n"
            f"Target Market: {request.target_market}\n"
            f"Industry: {request.industry}\n\n"
            f"Produce SWOT analysis."
        )

        raw = await self._call_llm(prompt)

        try:
            data = json.loads(raw)
            return SWOTReport(**data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ValueError(f"Failed to parse LLM response: {e}")
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_audit_engine.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/services/llm_client.py backend/services/audit_engine.py backend/models/audit.py backend/tests/test_audit_engine.py
git commit -m "feat(services): add LLM-powered business model audit engine"
```

---

### Task 11: Audit API route

**Files:**
- Create: `backend/api/audit.py`
- Modify: `backend/api/router.py`
- Create: `backend/tests/test_api/test_audit.py`

**Step 1: Write the failing test**

`backend/tests/test_api/test_audit.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from main import app
from models.audit import SWOTReport


@pytest.fixture
def mock_audit():
    report = SWOTReport(
        strengths=["Low cost"],
        weaknesses=["Small scale"],
        opportunities=["Expansion"],
        threats=["Tariffs"],
        risk_summary="Medium risk.",
    )
    with patch("api.audit.get_audit_engine") as mock:
        engine = AsyncMock()
        engine.analyze = AsyncMock(return_value=report)
        mock.return_value = engine
        yield engine


@pytest.mark.asyncio
async def test_post_audit(mock_audit):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/audit", json={
            "model_description": "DTC shoe brand",
            "target_market": "Vietnam",
            "industry": "Retail",
        })
    assert resp.status_code == 200
    body = resp.json()
    assert "strengths" in body
    assert "threats" in body


@pytest.mark.asyncio
async def test_post_audit_missing_field():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/audit", json={"model_description": "test"})
    assert resp.status_code == 422
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_api/test_audit.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`backend/api/audit.py`:
```python
from fastapi import APIRouter

from core.config import settings
from core.exceptions import UpstreamError
from models.audit import AuditRequest, SWOTReport
from services.audit_engine import AuditEngine

router = APIRouter(tags=["audit"])


def get_audit_engine() -> AuditEngine:
    return AuditEngine(api_key=settings.groq_api_key)


@router.post("/api/audit", response_model=SWOTReport)
async def run_audit(request: AuditRequest):
    engine = get_audit_engine()
    try:
        return await engine.analyze(request)
    except ValueError as e:
        raise UpstreamError("LLM", str(e))
    except Exception as e:
        raise UpstreamError("LLM", str(e))
```

Update `backend/api/router.py`:
```python
from fastapi import APIRouter
from api.indicators import router as indicators_router
from api.audit import router as audit_router

api_router = APIRouter()
api_router.include_router(indicators_router)
api_router.include_router(audit_router)
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_api/test_audit.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/api/audit.py backend/api/router.py backend/tests/test_api/test_audit.py
git commit -m "feat(api): add POST /api/audit endpoint for SWOT analysis"
```

---

## Phase 5: Custom Scraper

### Task 12: Custom scraper service + API

**Files:**
- Create: `backend/models/scraper.py`
- Create: `backend/services/custom_scraper.py`
- Create: `backend/storage/scraper_store.py`
- Create: `backend/api/scrapers.py`
- Modify: `backend/api/router.py`
- Create: `backend/tests/test_custom_scraper.py`

**Step 1: Write the failing test**

`backend/tests/test_custom_scraper.py`:
```python
import pytest
import json
import os
from storage.scraper_store import ScraperStore
from models.scraper import ScraperConfig


@pytest.fixture
def store(tmp_path):
    path = str(tmp_path / "scrapers.json")
    return ScraperStore(path)


class TestScraperStore:
    def test_create_and_list(self, store):
        config = ScraperConfig(
            name="test-scraper",
            url="https://example.com/data",
            selector="table.prices td",
            schedule_minutes=60,
        )
        created = store.create(config)
        assert created.id is not None

        all_scrapers = store.list_all()
        assert len(all_scrapers) == 1
        assert all_scrapers[0].name == "test-scraper"

    def test_delete(self, store):
        config = ScraperConfig(
            name="to-delete",
            url="https://example.com",
            selector=".data",
            schedule_minutes=30,
        )
        created = store.create(config)
        store.delete(created.id)
        assert len(store.list_all()) == 0

    def test_persistence(self, tmp_path):
        path = str(tmp_path / "scrapers.json")
        store1 = ScraperStore(path)
        store1.create(ScraperConfig(
            name="persist-test",
            url="https://example.com",
            selector=".x",
            schedule_minutes=15,
        ))
        # New instance reads from same file
        store2 = ScraperStore(path)
        assert len(store2.list_all()) == 1
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_custom_scraper.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`backend/models/scraper.py`:
```python
from pydantic import BaseModel


class ScraperConfig(BaseModel):
    id: str | None = None
    name: str
    url: str
    selector: str          # CSS selector or AI extraction prompt
    schedule_minutes: int
    active: bool = True


class ScraperResult(BaseModel):
    scraper_id: str
    timestamp: str
    data: list[str]
```

`backend/storage/scraper_store.py`:
```python
import json
import os
import uuid

from models.scraper import ScraperConfig


class ScraperStore:
    def __init__(self, path: str):
        self.path = path
        self._scrapers: dict[str, ScraperConfig] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                raw = json.load(f)
                for item in raw:
                    sc = ScraperConfig(**item)
                    self._scrapers[sc.id] = sc

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(
                [s.model_dump() for s in self._scrapers.values()],
                f, indent=2,
            )

    def create(self, config: ScraperConfig) -> ScraperConfig:
        config.id = uuid.uuid4().hex[:12]
        self._scrapers[config.id] = config
        self._save()
        return config

    def list_all(self) -> list[ScraperConfig]:
        return list(self._scrapers.values())

    def get(self, scraper_id: str) -> ScraperConfig | None:
        return self._scrapers.get(scraper_id)

    def delete(self, scraper_id: str) -> None:
        self._scrapers.pop(scraper_id, None)
        self._save()
```

`backend/api/scrapers.py`:
```python
from fastapi import APIRouter, HTTPException

from core.config import settings
from models.scraper import ScraperConfig
from storage.scraper_store import ScraperStore

router = APIRouter(prefix="/api/scrapers", tags=["scrapers"])

_store: ScraperStore | None = None


def get_store() -> ScraperStore:
    global _store
    if _store is None:
        _store = ScraperStore(settings.scraper_store_path)
    return _store


@router.get("", response_model=list[ScraperConfig])
async def list_scrapers():
    return get_store().list_all()


@router.post("", response_model=ScraperConfig, status_code=201)
async def create_scraper(config: ScraperConfig):
    return get_store().create(config)


@router.delete("/{scraper_id}", status_code=204)
async def delete_scraper(scraper_id: str):
    store = get_store()
    if store.get(scraper_id) is None:
        raise HTTPException(404, "Scraper not found")
    store.delete(scraper_id)
```

Update `backend/api/router.py` — add scraper router:
```python
from fastapi import APIRouter
from api.indicators import router as indicators_router
from api.audit import router as audit_router
from api.scrapers import router as scrapers_router

api_router = APIRouter()
api_router.include_router(indicators_router)
api_router.include_router(audit_router)
api_router.include_router(scrapers_router)
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_custom_scraper.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/models/scraper.py backend/storage/scraper_store.py backend/api/scrapers.py backend/api/router.py backend/tests/test_custom_scraper.py
git commit -m "feat(scrapers): add custom scraper CRUD with JSON persistence"
```

---

## Phase 6: Frontend — Map & Dashboard

### Task 13: Frontend API client + WebSocket service

**Files:**
- Create: `frontend/src/services/api-client.ts`
- Create: `frontend/src/services/ws-client.ts`
- Create: `frontend/src/types/api.ts`
- Create: `frontend/src/types/indicators.ts`
- Create: `frontend/src/types/risk.ts`

**Step 1: Create TypeScript types**

`frontend/src/types/api.ts`:
```typescript
export interface HealthResponse {
  status: string;
  version: string;
}

export interface WSMessage {
  channel: string;
  event: string;
  data: unknown;
  timestamp: string;
}

export interface WSSubscribe {
  action: 'subscribe' | 'unsubscribe';
  channels: string[];
}
```

`frontend/src/types/indicators.ts`:
```typescript
export interface IndicatorPoint {
  date: string;
  value: number | null;
}

export interface IndicatorSeries {
  series_id: string;
  title: string;
  units: string;
  frequency: string;
  data: IndicatorPoint[];
}
```

`frontend/src/types/risk.ts`:
```typescript
export interface RiskScore {
  region_code: string;
  overall: number;
  breakdown: Record<string, number>;
}
```

**Step 2: Create API client**

`frontend/src/services/api-client.ts`:
```typescript
import type { IndicatorSeries } from '@/types/indicators';
import type { HealthResponse } from '@/types/api';

const BASE_URL = import.meta.env.VITE_API_URL || '';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!resp.ok) {
    throw new Error(`API ${resp.status}: ${resp.statusText}`);
  }
  return resp.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>('/api/health'),

  getFredSeries: (seriesId: string, start?: string, end?: string) => {
    const params = new URLSearchParams();
    if (start) params.set('start', start);
    if (end) params.set('end', end);
    const qs = params.toString();
    return request<IndicatorSeries>(`/api/indicators/fred/${seriesId}${qs ? '?' + qs : ''}`);
  },

  postAudit: (body: { model_description: string; target_market: string; industry: string }) =>
    request<Record<string, unknown>>('/api/audit', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  getScrapers: () => request<unknown[]>('/api/scrapers'),
};
```

**Step 3: Create WebSocket client**

`frontend/src/services/ws-client.ts`:
```typescript
import type { WSMessage, WSSubscribe } from '@/types/api';

type MessageHandler = (msg: WSMessage) => void;

export class WSClient {
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private url: string;

  constructor(url: string = `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws/live`) {
    this.url = url;
  }

  connect(): void {
    this.ws = new WebSocket(this.url);

    this.ws.onmessage = (event) => {
      const msg: WSMessage = JSON.parse(event.data);
      const channelHandlers = this.handlers.get(msg.channel);
      if (channelHandlers) {
        channelHandlers.forEach((h) => h(msg));
      }
    };

    this.ws.onclose = () => {
      this.reconnectTimer = setTimeout(() => this.connect(), 5000);
    };
  }

  subscribe(channel: string, handler: MessageHandler): void {
    if (!this.handlers.has(channel)) {
      this.handlers.set(channel, new Set());
    }
    this.handlers.get(channel)!.add(handler);

    if (this.ws?.readyState === WebSocket.OPEN) {
      const msg: WSSubscribe = { action: 'subscribe', channels: [channel] };
      this.ws.send(JSON.stringify(msg));
    }
  }

  unsubscribe(channel: string, handler: MessageHandler): void {
    this.handlers.get(channel)?.delete(handler);
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
  }
}
```

**Step 4: Commit**

```bash
git add frontend/src/types/ frontend/src/services/
git commit -m "feat(frontend): add API client, WebSocket client, and TypeScript types"
```

---

### Task 14: Map container with deck.gl + MapLibre

**Files:**
- Create: `frontend/src/components/MapContainer.ts`
- Create: `frontend/src/config/regions.ts`
- Modify: `frontend/src/main.ts`

**Step 1: Create region presets**

`frontend/src/config/regions.ts`:
```typescript
export interface RegionPreset {
  center: [number, number];
  zoom: number;
  label: string;
}

export const REGIONS: Record<string, RegionPreset> = {
  global:   { center: [0, 20],      zoom: 1.5, label: '全球' },
  apac:     { center: [115, 25],    zoom: 3,   label: '亞太' },
  europe:   { center: [15, 50],     zoom: 3.5, label: '歐洲' },
  americas: { center: [-90, 25],    zoom: 2.5, label: '美洲' },
  mena:     { center: [45, 28],     zoom: 3.5, label: '中東北非' },
  africa:   { center: [20, 0],      zoom: 3,   label: '非洲' },
  seasia:   { center: [110, 5],     zoom: 4,   label: '東南亞' },
  latam:    { center: [-60, -15],   zoom: 3,   label: '拉丁美洲' },
};
```

**Step 2: Create MapContainer**

`frontend/src/components/MapContainer.ts`:
```typescript
import maplibregl from 'maplibre-gl';
import { Deck } from '@deck.gl/core';
import { ScatterplotLayer } from '@deck.gl/layers';
import { REGIONS, type RegionPreset } from '@/config/regions';

export class MapContainer {
  private map: maplibregl.Map | null = null;
  private deck: Deck | null = null;
  private container: HTMLElement;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container #${containerId} not found`);
    this.container = el;
  }

  init(): void {
    // MapLibre base map
    this.map = new maplibregl.Map({
      container: this.container,
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: REGIONS.global.center,
      zoom: REGIONS.global.zoom,
      pitch: 45,
      bearing: 0,
      antialias: true,
    });

    // deck.gl overlay
    this.deck = new Deck({
      parent: this.container,
      viewState: {
        longitude: REGIONS.global.center[0],
        latitude: REGIONS.global.center[1],
        zoom: REGIONS.global.zoom,
        pitch: 45,
        bearing: 0,
      },
      controller: true,
      layers: [],
      onViewStateChange: ({ viewState }) => {
        this.map?.jumpTo({
          center: [viewState.longitude, viewState.latitude],
          zoom: viewState.zoom,
          pitch: viewState.pitch,
          bearing: viewState.bearing,
        });
      },
    });
  }

  flyTo(regionKey: string): void {
    const region = REGIONS[regionKey];
    if (!region || !this.deck) return;

    this.deck.setProps({
      viewState: {
        longitude: region.center[0],
        latitude: region.center[1],
        zoom: region.zoom,
        pitch: 45,
        bearing: 0,
        transitionDuration: 2000,
      },
    });
  }

  updateLayers(layers: unknown[]): void {
    this.deck?.setProps({ layers });
  }

  destroy(): void {
    this.deck?.finalize();
    this.map?.remove();
  }
}
```

**Step 3: Update main.ts to render map**

`frontend/src/main.ts`:
```typescript
import './styles/main.css';
import { MapContainer } from '@/components/MapContainer';

// Create layout
const app = document.getElementById('app');
if (app) {
  app.innerHTML = `
    <div id="toolbar" class="toolbar">
      <span class="logo">Global Pulse Pro</span>
    </div>
    <div id="map-container" class="map-container"></div>
    <div id="side-panel" class="side-panel"></div>
  `;

  const map = new MapContainer('map-container');
  map.init();
}
```

Add to `frontend/src/styles/main.css`:
```css
.toolbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 48px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 16px;
  z-index: 100;
}

.logo {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.map-container {
  position: fixed;
  top: 48px;
  left: 0;
  right: 360px;
  bottom: 0;
}

.side-panel {
  position: fixed;
  top: 48px;
  right: 0;
  width: 360px;
  bottom: 0;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border);
  overflow-y: auto;
  padding: 16px;
}
```

**Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat(frontend): add deck.gl + MapLibre 3D map with region presets"
```

---

### Task 15: Economic Radar Panel

**Files:**
- Create: `frontend/src/components/Panel.ts`
- Create: `frontend/src/components/EconomicRadarPanel.ts`
- Create: `frontend/src/utils/format.ts`

**Step 1: Create Panel base class**

`frontend/src/components/Panel.ts`:
```typescript
export abstract class Panel {
  protected el: HTMLElement;
  protected collapsed = false;

  constructor(protected container: HTMLElement, protected title: string) {
    this.el = document.createElement('div');
    this.el.className = 'panel';
    this.el.innerHTML = `
      <div class="panel-header">
        <span class="panel-title">${title}</span>
        <button class="panel-toggle">−</button>
      </div>
      <div class="panel-body"></div>
    `;

    this.el.querySelector('.panel-toggle')!.addEventListener('click', () => {
      this.collapsed = !this.collapsed;
      this.el.querySelector('.panel-body')!.classList.toggle('hidden', this.collapsed);
      this.el.querySelector('.panel-toggle')!.textContent = this.collapsed ? '+' : '−';
    });

    this.container.appendChild(this.el);
  }

  protected get body(): HTMLElement {
    return this.el.querySelector('.panel-body')!;
  }

  abstract update(data: unknown): void;

  destroy(): void {
    this.el.remove();
  }
}
```

**Step 2: Create format utils**

`frontend/src/utils/format.ts`:
```typescript
export function formatNumber(n: number, decimals = 1): string {
  if (Math.abs(n) >= 1e12) return (n / 1e12).toFixed(decimals) + 'T';
  if (Math.abs(n) >= 1e9) return (n / 1e9).toFixed(decimals) + 'B';
  if (Math.abs(n) >= 1e6) return (n / 1e6).toFixed(decimals) + 'M';
  if (Math.abs(n) >= 1e3) return (n / 1e3).toFixed(decimals) + 'K';
  return n.toFixed(decimals);
}

export function formatPercent(n: number): string {
  const sign = n >= 0 ? '+' : '';
  return `${sign}${n.toFixed(2)}%`;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}
```

**Step 3: Create EconomicRadarPanel**

`frontend/src/components/EconomicRadarPanel.ts`:
```typescript
import { Panel } from './Panel';
import { api } from '@/services/api-client';
import { formatNumber, formatPercent } from '@/utils/format';
import type { IndicatorSeries } from '@/types/indicators';

const TRACKED_SERIES = [
  { id: 'GDP', label: 'GDP' },
  { id: 'CPIAUCSL', label: 'CPI' },
  { id: 'UNRATE', label: '失業率' },
  { id: 'FEDFUNDS', label: '聯邦基金利率' },
];

export class EconomicRadarPanel extends Panel {
  private refreshTimer: ReturnType<typeof setInterval> | null = null;

  constructor(container: HTMLElement) {
    super(container, '實體經濟雷達');
    this.loadData();
    this.refreshTimer = setInterval(() => this.loadData(), 15 * 60 * 1000);
  }

  private async loadData(): Promise<void> {
    this.body.innerHTML = '<div class="loading">Loading indicators...</div>';
    const rows: string[] = [];

    for (const { id, label } of TRACKED_SERIES) {
      try {
        const series = await api.getFredSeries(id);
        rows.push(this.renderRow(label, series));
      } catch {
        rows.push(`<div class="indicator-row error">${label}: unavailable</div>`);
      }
    }

    this.body.innerHTML = rows.join('');
  }

  private renderRow(label: string, series: IndicatorSeries): string {
    const latest = series.data[series.data.length - 1];
    const prev = series.data[series.data.length - 2];

    if (!latest) return `<div class="indicator-row">${label}: no data</div>`;

    let changeHtml = '';
    if (prev && latest.value != null && prev.value != null) {
      const change = ((latest.value - prev.value) / Math.abs(prev.value)) * 100;
      const cls = change >= 0 ? 'positive' : 'negative';
      changeHtml = `<span class="change ${cls}">${formatPercent(change)}</span>`;
    }

    return `
      <div class="indicator-row">
        <span class="indicator-label">${label}</span>
        <span class="indicator-value">${formatNumber(latest.value ?? 0)}</span>
        ${changeHtml}
      </div>
    `;
  }

  update(_data: unknown): void {
    this.loadData();
  }

  destroy(): void {
    if (this.refreshTimer) clearInterval(this.refreshTimer);
    super.destroy();
  }
}
```

**Step 4: Commit**

```bash
git add frontend/src/components/ frontend/src/utils/
git commit -m "feat(frontend): add Panel base class and Economic Radar panel"
```

---

### Task 16: Audit Panel (AI SWOT)

**Files:**
- Create: `frontend/src/components/AuditPanel.ts`

**Step 1: Create AuditPanel**

`frontend/src/components/AuditPanel.ts`:
```typescript
import { Panel } from './Panel';
import { api } from '@/services/api-client';

export class AuditPanel extends Panel {
  constructor(container: HTMLElement) {
    super(container, 'AI 商模審計器');
    this.renderForm();
  }

  private renderForm(): void {
    this.body.innerHTML = `
      <form class="audit-form">
        <label>商業模式描述
          <textarea name="model_description" rows="3" placeholder="例：DTC 運動鞋品牌，透過電商直銷..."></textarea>
        </label>
        <label>目標市場
          <input name="target_market" placeholder="例：越南" />
        </label>
        <label>產業
          <input name="industry" placeholder="例：消費零售" />
        </label>
        <button type="submit">分析 SWOT</button>
      </form>
      <div class="audit-result"></div>
    `;

    this.body.querySelector('form')!.addEventListener('submit', (e) => {
      e.preventDefault();
      this.runAudit();
    });
  }

  private async runAudit(): Promise<void> {
    const form = this.body.querySelector('form')! as HTMLFormElement;
    const fd = new FormData(form);
    const resultEl = this.body.querySelector('.audit-result')!;

    resultEl.innerHTML = '<div class="loading">AI 分析中...</div>';

    try {
      const report = await api.postAudit({
        model_description: fd.get('model_description') as string,
        target_market: fd.get('target_market') as string,
        industry: fd.get('industry') as string,
      });

      resultEl.innerHTML = this.renderSWOT(report);
    } catch (err) {
      resultEl.innerHTML = `<div class="error">分析失敗: ${err}</div>`;
    }
  }

  private renderSWOT(report: Record<string, unknown>): string {
    const sections = [
      { key: 'strengths', label: '優勢 (S)', cls: 'success' },
      { key: 'weaknesses', label: '劣勢 (W)', cls: 'warning' },
      { key: 'opportunities', label: '機會 (O)', cls: 'accent' },
      { key: 'threats', label: '威脅 (T)', cls: 'danger' },
    ];

    let html = '';
    for (const { key, label, cls } of sections) {
      const items = report[key] as string[] | undefined;
      if (!items) continue;
      html += `
        <div class="swot-section ${cls}">
          <h4>${label}</h4>
          <ul>${items.map((i) => `<li>${i}</li>`).join('')}</ul>
        </div>
      `;
    }

    if (report['risk_summary']) {
      html += `<div class="risk-summary"><strong>風險摘要:</strong> ${report['risk_summary']}</div>`;
    }

    return html;
  }

  update(_data: unknown): void {}
}
```

**Step 2: Commit**

```bash
git add frontend/src/components/AuditPanel.ts
git commit -m "feat(frontend): add AI SWOT Audit Panel with form and report rendering"
```

---

### Task 17: Wire up App.ts with all panels

**Files:**
- Create: `frontend/src/App.ts`
- Create: `frontend/src/services/timezone-focus.ts`
- Modify: `frontend/src/main.ts`

**Step 1: Create timezone focus service**

`frontend/src/services/timezone-focus.ts`:
```typescript
import type { RegionPreset } from '@/config/regions';
import { REGIONS } from '@/config/regions';

export function getActiveRegion(): string {
  const hour = new Date().getUTCHours();

  if (hour >= 0 && hour < 8) return 'apac';      // UTC+8~+12 trading
  if (hour >= 7 && hour < 16) return 'europe';    // UTC+0~+3 trading
  if (hour >= 13 && hour < 22) return 'americas'; // UTC-5~-8 trading
  return 'global';
}

export class TimezoneFocus {
  private timer: ReturnType<typeof setInterval> | null = null;
  private paused = false;
  private idleTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(private onFocus: (region: string) => void) {}

  start(): void {
    this.apply();
    this.timer = setInterval(() => {
      if (!this.paused) this.apply();
    }, 5 * 60 * 1000); // check every 5 min
  }

  pause(): void {
    this.paused = true;
    if (this.idleTimer) clearTimeout(this.idleTimer);
    this.idleTimer = setTimeout(() => {
      this.paused = false;
    }, 10 * 60 * 1000); // resume after 10min idle
  }

  private apply(): void {
    this.onFocus(getActiveRegion());
  }

  stop(): void {
    if (this.timer) clearInterval(this.timer);
    if (this.idleTimer) clearTimeout(this.idleTimer);
  }
}
```

**Step 2: Create App.ts**

`frontend/src/App.ts`:
```typescript
import { MapContainer } from '@/components/MapContainer';
import { EconomicRadarPanel } from '@/components/EconomicRadarPanel';
import { AuditPanel } from '@/components/AuditPanel';
import { TimezoneFocus } from '@/services/timezone-focus';

export class App {
  private map: MapContainer;
  private economicPanel: EconomicRadarPanel | null = null;
  private auditPanel: AuditPanel | null = null;
  private timezoneFocus: TimezoneFocus;

  constructor(private rootId: string) {
    this.map = new MapContainer('map-container');
    this.timezoneFocus = new TimezoneFocus((region) => this.map.flyTo(region));
  }

  init(): void {
    this.map.init();

    const sidePanel = document.getElementById('side-panel');
    if (sidePanel) {
      this.economicPanel = new EconomicRadarPanel(sidePanel);
      this.auditPanel = new AuditPanel(sidePanel);
    }

    this.timezoneFocus.start();

    // Pause auto-focus on manual map interaction
    document.getElementById('map-container')?.addEventListener('mousedown', () => {
      this.timezoneFocus.pause();
    });
  }

  destroy(): void {
    this.timezoneFocus.stop();
    this.economicPanel?.destroy();
    this.auditPanel?.destroy();
    this.map.destroy();
  }
}
```

**Step 3: Update main.ts**

`frontend/src/main.ts`:
```typescript
import './styles/main.css';
import { App } from '@/App';

const root = document.getElementById('app');
if (root) {
  root.innerHTML = `
    <div id="toolbar" class="toolbar">
      <span class="logo">Global Pulse Pro</span>
    </div>
    <div id="map-container" class="map-container"></div>
    <div id="side-panel" class="side-panel"></div>
  `;

  const app = new App('app');
  app.init();
}
```

**Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat(frontend): wire App controller with map, panels, and timezone focus"
```

---

## Phase 7: Integration & Docker

### Task 18: Backend lifespan — connect InfluxDB, Redis, scheduler

**Files:**
- Modify: `backend/main.py`

**Step 1: Update main.py with full lifespan**

`backend/main.py`:
```python
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from storage.influxdb import InfluxStorage
from storage.redis_cache import RedisCache
from scheduler.jobs import register_jobs, start_scheduler, stop_scheduler
from api.router import api_router

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
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}
```

**Step 2: Commit**

```bash
git add backend/main.py
git commit -m "feat(backend): connect InfluxDB, Redis, and scheduler in lifespan"
```

---

### Task 19: Dockerfiles

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`

**Step 1: Backend Dockerfile**

`backend/Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Step 2: Frontend Dockerfile**

`frontend/Dockerfile`:
```dockerfile
FROM node:20-slim

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**Step 3: Commit**

```bash
git add backend/Dockerfile frontend/Dockerfile
git commit -m "chore: add Dockerfiles for frontend and backend"
```

---

### Task 20: CI/CD Pipeline

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Create CI workflow**

`.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run tests
        run: cd backend && python -m pytest tests/ -v --cov=. --cov-fail-under=80
        env:
          REDIS_URL: redis://localhost:6379

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install and build
        run: cd frontend && npm ci && npm run build

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Python dependency audit
        run: pip install pip-audit && pip-audit -r backend/requirements.txt
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Node dependency audit
        run: cd frontend && npm ci && npm audit --audit-level=high
```

**Step 2: Commit**

```bash
git add .github/
git commit -m "ci: add GitHub Actions pipeline for tests, build, and security"
```

---

## Summary

| Phase | Tasks | What it delivers |
|-------|-------|-----------------|
| 1. Scaffolding | T1-T3 | Monorepo, Docker Compose, InfluxDB + Redis clients |
| 2. FRED Data | T4-T7 | Pydantic models, FRED client, API route, scheduled fetcher |
| 3. Analytics | T8-T9 | Welford anomaly detector, multi-factor risk engine |
| 4. AI | T10-T11 | LLM client, SWOT audit engine, audit API |
| 5. Scraper | T12 | Custom scraper CRUD with JSON persistence |
| 6. Frontend | T13-T17 | API client, 3D map, panels, timezone focus, App controller |
| 7. Integration | T18-T20 | Backend lifespan, Dockerfiles, CI/CD |

**Total: 20 tasks, ~60 TDD steps, ~7 phases.**

After all tasks: run `docker compose up -d` and access at `http://localhost:5173`.
