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
