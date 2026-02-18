from typing import Any

import httpx

from models.indicators import IndicatorPoint, IndicatorSeries

FRED_BASE_URL = "https://api.stlouisfed.org/fred"


class FredClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def _get(
        self, endpoint: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        url = f"{FRED_BASE_URL}/{endpoint}"
        request_params: dict[str, str] = {
            "api_key": self.api_key,
            "file_type": "json",
        }
        if params:
            request_params.update(params)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=request_params)
            response.raise_for_status()
            return response.json()

    async def get_series_info(self, series_id: str) -> dict[str, Any]:
        data = await self._get("series", {"series_id": series_id})
        return data["seriess"][0]

    async def get_observations(
        self,
        series_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> IndicatorSeries:
        info = await self.get_series_info(series_id)

        obs_params: dict[str, str] = {"series_id": series_id}
        if start_date:
            obs_params["observation_start"] = start_date
        if end_date:
            obs_params["observation_end"] = end_date

        obs_data = await self._get("series/observations", obs_params)

        points = [
            IndicatorPoint(date=obs["date"], value=float(obs["value"]))
            for obs in obs_data["observations"]
            if obs["value"] != "."
        ]

        return IndicatorSeries(
            series_id=info["id"],
            title=info["title"],
            units=info["units"],
            frequency=info["frequency"],
            data=points,
        )
