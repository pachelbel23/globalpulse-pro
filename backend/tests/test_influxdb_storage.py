import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from storage.influxdb import InfluxStorage


@pytest.fixture
def storage(mock_influx_write_api, mock_influx_query_api):
    """Create an InfluxStorage instance with mocked APIs."""
    with patch(
        "storage.influxdb.InfluxDBClientAsync"
    ) as MockClient:
        instance = MockClient.return_value
        instance.write_api.return_value = mock_influx_write_api
        instance.query_api.return_value = mock_influx_query_api
        instance.close = AsyncMock()

        s = InfluxStorage(
            url="http://localhost:8086",
            token="test-token",
            org="test-org",
            bucket="test-bucket",
        )
        # Replace the internal APIs with our mocks for direct access
        s._write_api = mock_influx_write_api
        s._query_api = mock_influx_query_api
        yield s


@pytest.mark.asyncio
async def test_write_metric(storage, mock_influx_write_api):
    """write_metric should build a Point and call write on the write API."""
    mock_influx_write_api.write = AsyncMock()

    await storage.write_metric(
        measurement="trade_balance",
        tags={"country": "US"},
        fields={"value": 123.45},
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )

    mock_influx_write_api.write.assert_called_once()
    call_kwargs = mock_influx_write_api.write.call_args
    assert call_kwargs is not None


@pytest.mark.asyncio
async def test_query_returns_list(storage, mock_influx_query_api):
    """query_metric should return a list of dicts."""
    # Mock query to return a FluxTable-like structure
    mock_record = MagicMock()
    mock_record.get_time.return_value = datetime(2025, 1, 1, tzinfo=timezone.utc)
    mock_record.get_value.return_value = 42.0
    mock_record.get_field.return_value = "value"

    mock_table = MagicMock()
    mock_table.records = [mock_record]

    mock_influx_query_api.query.return_value = [mock_table]

    result = await storage.query_metric(
        measurement="trade_balance",
        series_id="US",
        range_str="-7d",
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["time"] == datetime(2025, 1, 1, tzinfo=timezone.utc)
    assert result[0]["value"] == 42.0
    assert result[0]["field"] == "value"
