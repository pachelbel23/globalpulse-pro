import pytest
from storage.scraper_store import ScraperStore
from models.scraper import ScraperConfig


@pytest.fixture
def store(tmp_path):
    path = str(tmp_path / "scrapers.json")
    return ScraperStore(path)


class TestScraperStore:
    def test_create_and_list(self, store):
        config = ScraperConfig(
            name="test-scraper",
            url="https://example.com/data",
            selector="table.prices td",
            schedule_minutes=60,
        )
        created = store.create(config)
        assert created.id is not None
        all_scrapers = store.list_all()
        assert len(all_scrapers) == 1
        assert all_scrapers[0].name == "test-scraper"

    def test_delete(self, store):
        config = ScraperConfig(
            name="to-delete",
            url="https://example.com",
            selector=".data",
            schedule_minutes=30,
        )
        created = store.create(config)
        store.delete(created.id)
        assert len(store.list_all()) == 0

    def test_persistence(self, tmp_path):
        path = str(tmp_path / "scrapers.json")
        store1 = ScraperStore(path)
        store1.create(
            ScraperConfig(
                name="persist-test",
                url="https://example.com",
                selector=".x",
                schedule_minutes=15,
            )
        )
        store2 = ScraperStore(path)
        assert len(store2.list_all()) == 1
