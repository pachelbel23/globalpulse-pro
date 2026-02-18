# Global Pulse Pro

Real-time global trade intelligence dashboard with 3D visualization.

## Commands

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pytest --cov=. --cov-report=term-missing
```

### Frontend

```bash
cd frontend
npm install
npm run dev
npm run build
npm run typecheck
```

### Docker

```bash
docker compose up -d
docker compose down
docker compose logs -f backend
```

## Architecture

```
backend/
  main.py          — FastAPI app entry point
  core/            — Config, shared utilities
  api/             — Route handlers (routers)
  services/        — Business logic layer
  storage/         — Database / cache access (InfluxDB, Redis)
  scrapers/        — Data ingestion from external sources

frontend/
  src/
    main.ts        — App entry point
    styles/        — CSS variables and global styles
    components/    — UI components
    services/      — API client, WebSocket
    layers/        — deck.gl map layers
    stores/        — State management
```

## Key Rules

1. **api/ never imports storage/ directly** — always go through services/ layer.
2. **TDD** — write tests before or alongside implementation. All new code needs tests.
3. **Pure TS classes on frontend** — no framework; use vanilla TypeScript with deck.gl and MapLibre GL.
4. **Type safety everywhere** — strict TypeScript on frontend, Pydantic models on backend.
5. **Environment variables** — never commit secrets. Use `.env` files (see `.env.example`).
