from fastapi import APIRouter

from core.config import settings
from core.exceptions import UpstreamError
from models.audit import AuditRequest, SWOTReport
from services.audit_engine import AuditEngine

router = APIRouter(tags=["audit"])


def get_audit_engine() -> AuditEngine:
    return AuditEngine(api_key=settings.GROQ_API_KEY)


@router.post("/api/audit", response_model=SWOTReport)
async def run_audit(request: AuditRequest):
    engine = get_audit_engine()
    try:
        return await engine.analyze(request)
    except ValueError as e:
        raise UpstreamError("LLM", str(e))
    except Exception as e:
        raise UpstreamError("LLM", str(e))
