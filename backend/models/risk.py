from pydantic import BaseModel


class RegionRiskInput(BaseModel):
    region_code: str
    cpi_change: float        # YoY CPI % change
    unemployment_rate: float  # %
    bdi_change: float         # BDI % change (negative = bad)
    port_congestion: float    # 0.0 to 1.0


class RiskScore(BaseModel):
    region_code: str
    overall: float            # 0-100
    breakdown: dict[str, float]
