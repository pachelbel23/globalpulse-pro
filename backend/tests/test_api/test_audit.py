"""Tests for POST /api/audit endpoint."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from models.audit import SWOTReport


@pytest.fixture
def valid_swot_report():
    return SWOTReport(
        strengths=["Strong technology stack", "Scalable SaaS model"],
        weaknesses=["Limited brand recognition"],
        opportunities=["Growing demand for supply chain visibility"],
        threats=["Intense competition from incumbents"],
        risk_summary="Moderate risk due to competitive landscape but strong product-market fit.",
    )


@pytest.mark.asyncio
async def test_post_audit(valid_swot_report):
    """Mock get_audit_engine, verify 200 + body has strengths/threats."""
    mock_engine = AsyncMock()
    mock_engine.analyze.return_value = valid_swot_report

    with patch("api.audit.get_audit_engine", return_value=mock_engine):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/audit",
                json={
                    "model_description": "SaaS platform for supply chain analytics",
                    "target_market": "US manufacturing sector",
                    "industry": "Technology",
                },
            )

    assert response.status_code == 200
    body = response.json()
    assert "strengths" in body
    assert len(body["strengths"]) == 2
    assert "threats" in body
    assert len(body["threats"]) == 1
    assert "risk_summary" in body
    mock_engine.analyze.assert_awaited_once()


@pytest.mark.asyncio
async def test_post_audit_missing_field():
    """POST with incomplete body, verify 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/audit",
            json={
                "model_description": "SaaS platform",
                # missing target_market and industry
            },
        )

    assert response.status_code == 422
