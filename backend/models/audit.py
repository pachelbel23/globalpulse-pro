from pydantic import BaseModel


class AuditRequest(BaseModel):
    model_description: str
    target_market: str
    industry: str


class SWOTReport(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    opportunities: list[str]
    threats: list[str]
    risk_summary: str
