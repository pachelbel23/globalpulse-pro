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
