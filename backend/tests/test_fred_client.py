from unittest.mock import AsyncMock, patch

import pytest

from services.fred_client import FredClient


@pytest.fixture
def client():
    return FredClient(api_key="test-key")


@pytest.mark.asyncio
async def test_get_series_info(client):
    mock_response = {
        "seriess": [
            {
                "id": "GDP",
                "title": "Gross Domestic Product",
                "units": "Billions of Dollars",
                "frequency": "Quarterly",
            }
        ]
    }
    client._get = AsyncMock(return_value=mock_response)

    result = await client.get_series_info("GDP")

    assert result["id"] == "GDP"
    assert result["title"] == "Gross Domestic Product"
    client._get.assert_called_once_with("series", {"series_id": "GDP"})


@pytest.mark.asyncio
async def test_get_observations_filters_missing(client):
    mock_series_response = {
        "seriess": [
            {
                "id": "GDP",
                "title": "Gross Domestic Product",
                "units": "Billions of Dollars",
                "frequency": "Quarterly",
            }
        ]
    }
    mock_obs_response = {
        "observations": [
            {"date": "2024-01-01", "value": "100.5"},
            {"date": "2024-04-01", "value": "."},
            {"date": "2024-07-01", "value": "102.3"},
        ]
    }

    async def mock_get(endpoint, params=None):
        if endpoint == "series":
            return mock_series_response
        return mock_obs_response

    client._get = AsyncMock(side_effect=mock_get)

    result = await client.get_observations("GDP")

    assert result.series_id == "GDP"
    assert result.title == "Gross Domestic Product"
    assert len(result.data) == 2
    assert result.data[0].date == "2024-01-01"
    assert result.data[0].value == 100.5
    assert result.data[1].date == "2024-07-01"
    assert result.data[1].value == 102.3


@pytest.mark.asyncio
async def test_get_observations_empty(client):
    mock_series_response = {
        "seriess": [
            {
                "id": "GDP",
                "title": "Gross Domestic Product",
                "units": "Billions of Dollars",
                "frequency": "Quarterly",
            }
        ]
    }
    mock_obs_response = {"observations": []}

    async def mock_get(endpoint, params=None):
        if endpoint == "series":
            return mock_series_response
        return mock_obs_response

    client._get = AsyncMock(side_effect=mock_get)

    result = await client.get_observations("GDP")

    assert result.series_id == "GDP"
    assert result.data == []
