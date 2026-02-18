from fastapi import APIRouter, Query

from core.dependencies import get_fred_client
from core.exceptions import UpstreamError
from models.indicators import IndicatorSeries

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("/fred/{series_id}", response_model=IndicatorSeries)
async def get_fred_series(
    series_id: str,
    start: str | None = Query(None),
    end: str | None = Query(None),
):
    client = get_fred_client()
    try:
        return await client.get_observations(series_id, start, end)
    except Exception as e:
        raise UpstreamError("FRED", str(e))
