from fastapi import APIRouter, HTTPException

from core.config import settings
from models.scraper import ScraperConfig
from storage.scraper_store import ScraperStore

router = APIRouter(prefix="/api/scrapers", tags=["scrapers"])
_store: ScraperStore | None = None


def get_store() -> ScraperStore:
    global _store
    if _store is None:
        _store = ScraperStore(settings.SCRAPER_STORE_PATH)
    return _store


@router.get("", response_model=list[ScraperConfig])
async def list_scrapers():
    return get_store().list_all()


@router.post("", response_model=ScraperConfig, status_code=201)
async def create_scraper(config: ScraperConfig):
    return get_store().create(config)


@router.delete("/{scraper_id}", status_code=204)
async def delete_scraper(scraper_id: str):
    store = get_store()
    if store.get(scraper_id) is None:
        raise HTTPException(404, "Scraper not found")
    store.delete(scraper_id)
