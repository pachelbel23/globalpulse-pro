from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = "development"

    # InfluxDB
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = ""
    INFLUXDB_ORG: str = "globalpulsepro"
    INFLUXDB_BUCKET: str = "trade_data"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # API Keys
    FRED_API_KEY: str = ""
    FIRECRAWL_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # Scraper
    SCRAPER_STORE_PATH: str = "./data/scraper_store"
    SCRAPER_MAX_CONCURRENT: int = 5

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
