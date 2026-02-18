import pytest
from models.risk import RegionRiskInput, RiskScore
from services.risk_engine import RiskEngine


@pytest.fixture
def engine():
    return RiskEngine()


def _make_input(**overrides) -> RegionRiskInput:
    defaults = {
        "region_code": "US",
        "cpi_change": 3.0,
        "unemployment_rate": 5.0,
        "bdi_change": 5.0,
        "port_congestion": 0.3,
    }
    defaults.update(overrides)
    return RegionRiskInput(**defaults)


def test_score_within_bounds(engine):
    """Any input produces 0 <= overall <= 100."""
    test_cases = [
        _make_input(cpi_change=0.0, unemployment_rate=0.0, bdi_change=20.0, port_congestion=0.0),
        _make_input(cpi_change=15.0, unemployment_rate=25.0, bdi_change=-50.0, port_congestion=1.0),
        _make_input(cpi_change=50.0, unemployment_rate=100.0, bdi_change=-200.0, port_congestion=5.0),
        _make_input(cpi_change=-10.0, unemployment_rate=-5.0, bdi_change=100.0, port_congestion=-1.0),
    ]
    for inp in test_cases:
        result = engine.calculate(inp)
        assert 0 <= result.overall <= 100, f"overall {result.overall} out of bounds for {inp}"


def test_high_inflation_increases_risk(engine):
    """CPI 8% should produce higher risk than CPI 1%."""
    low_inflation = engine.calculate(_make_input(cpi_change=1.0))
    high_inflation = engine.calculate(_make_input(cpi_change=8.0))
    assert high_inflation.overall > low_inflation.overall
    assert high_inflation.breakdown["inflation"] > low_inflation.breakdown["inflation"]


def test_all_bad_signals_near_max(engine):
    """Extreme bad values should produce overall >= 70."""
    inp = _make_input(
        cpi_change=14.0,
        unemployment_rate=22.0,
        bdi_change=-40.0,
        port_congestion=0.95,
    )
    result = engine.calculate(inp)
    assert result.overall >= 70, f"Expected >= 70 for bad signals, got {result.overall}"


def test_all_good_signals_near_min(engine):
    """Healthy values should produce overall <= 30."""
    inp = _make_input(
        cpi_change=1.0,
        unemployment_rate=3.0,
        bdi_change=10.0,
        port_congestion=0.05,
    )
    result = engine.calculate(inp)
    assert result.overall <= 30, f"Expected <= 30 for good signals, got {result.overall}"
