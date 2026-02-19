from pydantic import BaseModel


class ScraperConfig(BaseModel):
    id: str | None = None
    name: str
    url: str
    selector: str  # CSS selector or AI extraction prompt
    schedule_minutes: int
    active: bool = True


class ScraperResult(BaseModel):
    scraper_id: str
    timestamp: str
    data: list[str]
