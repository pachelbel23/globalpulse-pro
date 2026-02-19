import json
import os
import uuid

from models.scraper import ScraperConfig


class ScraperStore:
    def __init__(self, path: str):
        self.path = path
        self._scrapers: dict[str, ScraperConfig] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                raw = json.load(f)
                for item in raw:
                    sc = ScraperConfig(**item)
                    self._scrapers[sc.id] = sc

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(
                [s.model_dump() for s in self._scrapers.values()], f, indent=2
            )

    def create(self, config: ScraperConfig) -> ScraperConfig:
        config.id = uuid.uuid4().hex[:12]
        self._scrapers[config.id] = config
        self._save()
        return config

    def list_all(self) -> list[ScraperConfig]:
        return list(self._scrapers.values())

    def get(self, scraper_id: str) -> ScraperConfig | None:
        return self._scrapers.get(scraper_id)

    def delete(self, scraper_id: str) -> None:
        self._scrapers.pop(scraper_id, None)
        self._save()
