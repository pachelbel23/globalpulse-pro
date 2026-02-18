from core.config import settings
from services.fred_client import FredClient


def get_fred_client() -> FredClient:
    return FredClient(api_key=settings.FRED_API_KEY)
