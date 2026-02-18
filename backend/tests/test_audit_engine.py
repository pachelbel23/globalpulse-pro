"""Tests for the LLM-powered business model audit engine."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from models.audit import AuditRequest, SWOTReport
from services.audit_engine import AuditEngine


@pytest.fixture
def audit_request():
    return AuditRequest(
        model_description="SaaS platform for supply chain analytics",
        target_market="US manufacturing sector",
        industry="Technology",
    )


@pytest.fixture
def valid_swot_json():
    return json.dumps(
        {
            "strengths": ["Strong technology stack", "Scalable SaaS model"],
            "weaknesses": ["Limited brand recognition"],
            "opportunities": ["Growing demand for supply chain visibility"],
            "threats": ["Intense competition from incumbents"],
            "risk_summary": "Moderate risk due to competitive landscape but strong product-market fit.",
        }
    )


@pytest.mark.asyncio
async def test_audit_returns_swot(audit_request, valid_swot_json):
    """Mock _call_llm to return valid JSON, verify SWOTReport fields."""
    engine = AuditEngine(api_key="test-key")
    engine._call_llm = AsyncMock(return_value=valid_swot_json)

    report = await engine.analyze(audit_request)

    assert isinstance(report, SWOTReport)
    assert len(report.strengths) == 2
    assert len(report.weaknesses) == 1
    assert len(report.opportunities) == 1
    assert len(report.threats) == 1
    assert "Moderate risk" in report.risk_summary


@pytest.mark.asyncio
async def test_audit_handles_malformed_llm_response(audit_request):
    """Mock returns non-JSON string, expect ValueError with 'parse'."""
    engine = AuditEngine(api_key="test-key")
    engine._call_llm = AsyncMock(return_value="This is not JSON")

    with pytest.raises(ValueError, match="parse"):
        await engine.analyze(audit_request)
