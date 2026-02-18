from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from models.indicators import IndicatorPoint, IndicatorSeries


@pytest.mark.asyncio
async def test_get_fred_series():
    """Mock get_fred_client, verify 200 + correct JSON."""
    fake_series = IndicatorSeries(
        series_id="GDP",
        title="Gross Domestic Product",
        units="Billions of Dollars",
        frequency="Quarterly",
        data=[
            IndicatorPoint(date="2024-01-01", value=27000.0),
            IndicatorPoint(date="2024-04-01", value=27500.0),
        ],
    )

    mock_client = AsyncMock()
    mock_client.get_observations.return_value = fake_series

    with patch("api.indicators.get_fred_client", return_value=mock_client):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/indicators/fred/GDP")

    assert response.status_code == 200
    body = response.json()
    assert body["series_id"] == "GDP"
    assert body["title"] == "Gross Domestic Product"
    assert len(body["data"]) == 2
    assert body["data"][0]["date"] == "2024-01-01"
    assert body["data"][0]["value"] == 27000.0
    mock_client.get_observations.assert_awaited_once_with("GDP", None, None)


@pytest.mark.asyncio
async def test_get_fred_series_with_dates():
    """Verify start/end query params are forwarded to the client."""
    fake_series = IndicatorSeries(
        series_id="GDP",
        title="Gross Domestic Product",
        units="Billions of Dollars",
        frequency="Quarterly",
        data=[],
    )

    mock_client = AsyncMock()
    mock_client.get_observations.return_value = fake_series

    with patch("api.indicators.get_fred_client", return_value=mock_client):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get(
                "/api/indicators/fred/GDP",
                params={"start": "2024-01-01", "end": "2024-12-31"},
            )

    assert response.status_code == 200
    mock_client.get_observations.assert_awaited_once_with(
        "GDP", "2024-01-01", "2024-12-31"
    )


@pytest.mark.asyncio
async def test_get_fred_series_not_found():
    """Mock raises Exception, verify 502 upstream error."""
    mock_client = AsyncMock()
    mock_client.get_observations.side_effect = Exception("series not found")

    with patch("api.indicators.get_fred_client", return_value=mock_client):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/indicators/fred/INVALID")

    assert response.status_code == 502
    body = response.json()
    assert "FRED" in body["detail"]
    assert "series not found" in body["detail"]
