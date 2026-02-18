from models.risk import RegionRiskInput, RiskScore

WEIGHTS = {
    "inflation": 0.30,
    "unemployment": 0.25,
    "shipping": 0.25,
    "port_congestion": 0.20,
}


def _normalize(value: float, low: float, high: float) -> float:
    """Clamp value to [low, high] and scale to 0-100."""
    clamped = max(low, min(value, high))
    return ((clamped - low) / (high - low)) * 100.0


class RiskEngine:
    def calculate(self, inp: RegionRiskInput) -> RiskScore:
        inflation_risk = _normalize(inp.cpi_change, 0.0, 15.0)
        unemployment_risk = _normalize(inp.unemployment_rate, 0.0, 25.0)
        shipping_risk = _normalize(-inp.bdi_change, -20.0, 50.0)
        port_risk = _normalize(inp.port_congestion, 0.0, 1.0)

        breakdown = {
            k: round(v, 1)
            for k, v in [
                ("inflation", inflation_risk),
                ("unemployment", unemployment_risk),
                ("shipping", shipping_risk),
                ("port_congestion", port_risk),
            ]
        }

        overall = sum(breakdown[k] * WEIGHTS[k] for k in WEIGHTS)

        return RiskScore(
            region_code=inp.region_code,
            overall=round(overall, 1),
            breakdown=breakdown,
        )
