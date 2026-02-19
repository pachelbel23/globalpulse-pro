from fastapi import APIRouter

from api.audit import router as audit_router
from api.indicators import router as indicators_router
from api.scrapers import router as scrapers_router

api_router = APIRouter()
api_router.include_router(indicators_router)
api_router.include_router(audit_router)
api_router.include_router(scrapers_router)
