from datetime import datetime
from typing import Any

from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client import Point


class InfluxStorage:
    """Async wrapper around the InfluxDB client for writing and querying metrics."""

    def __init__(self, url: str, token: str, org: str, bucket: str):
        self._org = org
        self._bucket = bucket
        self._client = InfluxDBClientAsync(url=url, token=token, org=org)
        self._write_api = self._client.write_api()
        self._query_api = self._client.query_api()

    async def write_metric(
        self,
        measurement: str,
        tags: dict[str, str],
        fields: dict[str, Any],
        timestamp: datetime | None = None,
    ) -> None:
        """Build an InfluxDB Point and write it to the configured bucket."""
        point = Point(measurement)
        for key, value in tags.items():
            point = point.tag(key, value)
        for key, value in fields.items():
            point = point.field(key, value)
        if timestamp is not None:
            point = point.time(timestamp)

        await self._write_api.write(bucket=self._bucket, org=self._org, record=point)

    async def query_metric(
        self,
        measurement: str,
        series_id: str,
        range_str: str = "-30d",
    ) -> list[dict[str, Any]]:
        """Execute a Flux query and return results as a list of dicts."""
        query = (
            f'from(bucket: "{self._bucket}")'
            f" |> range(start: {range_str})"
            f' |> filter(fn: (r) => r._measurement == "{measurement}")'
            f' |> filter(fn: (r) => r.series_id == "{series_id}")'
        )

        tables = await self._query_api.query(query, org=self._org)

        results: list[dict[str, Any]] = []
        for table in tables:
            for record in table.records:
                results.append(
                    {
                        "time": record.get_time(),
                        "value": record.get_value(),
                        "field": record.get_field(),
                    }
                )
        return results

    async def close(self) -> None:
        """Close the underlying InfluxDB client."""
        await self._client.close()
