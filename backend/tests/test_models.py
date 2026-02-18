from models.indicators import IndicatorPoint, IndicatorSeries


def test_indicator_point_valid():
    point = IndicatorPoint(date="2024-01-01", value=3.5)
    assert point.date == "2024-01-01"
    assert point.value == 3.5


def test_indicator_point_null_value():
    point = IndicatorPoint(date="2024-01-01", value=None)
    assert point.value is None


def test_indicator_series_valid():
    series = IndicatorSeries(
        series_id="GDP",
        title="Gross Domestic Product",
        units="Billions of Dollars",
        frequency="Quarterly",
        data=[
            IndicatorPoint(date="2024-01-01", value=1.0),
            IndicatorPoint(date="2024-04-01", value=2.0),
        ],
    )
    assert series.series_id == "GDP"
    assert len(series.data) == 2


def test_indicator_series_empty_data():
    series = IndicatorSeries(
        series_id="GDP",
        title="Gross Domestic Product",
        units="Billions of Dollars",
        frequency="Quarterly",
        data=[],
    )
    assert series.data == []
