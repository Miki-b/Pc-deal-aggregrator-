"""
Application configuration using Pydantic Settings
"""
from functools import cached_property
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "PC Deal Aggregator"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    DIRECT_DATABASE_URL: str | None = None

    # Telegram
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    TELEGRAM_SESSION_NAME: str = "session_name"
    # Live listener (halted while scraping) — comma-separated
    TELEGRAM_WATCHED_CHANNELS: str = "@pcagregator"
    # Historical scrape targets — comma-separated channel usernames
    TELEGRAM_SCRAPE_CHANNELS: str = "@pcagregator,@samcomptech,@sami_brand12"
    TELEGRAM_PHONE: str | None = None

    # Historical scrape settings
    SCRAPE_DAYS_BACK: int = 180
    SCRAPE_LIMIT_PER_CHANNEL: int = 10000
    SCRAPE_DOWNLOAD_IMAGES: bool = False
    # Only save posts that look like PC/laptop deals
    SCRAPE_REQUIRE_DEAL_SIGNAL: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS — comma-separated in .env
    CORS_ORIGINS: str = "*"

    @field_validator(
        "TELEGRAM_WATCHED_CHANNELS",
        "TELEGRAM_SCRAPE_CHANNELS",
        "CORS_ORIGINS",
        mode="before",
    )
    @classmethod
    def strip_env_string(cls, value: object) -> str:
        if isinstance(value, list):
            return ",".join(str(item) for item in value)
        return str(value).strip()

    @cached_property
    def watched_channels(self) -> List[str]:
        return [c.strip() for c in self.TELEGRAM_WATCHED_CHANNELS.split(",") if c.strip()]

    @cached_property
    def scrape_channels(self) -> List[str]:
        return [c.strip() for c in self.TELEGRAM_SCRAPE_CHANNELS.split(",") if c.strip()]

    @cached_property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


# Global settings instance
settings = Settings()
