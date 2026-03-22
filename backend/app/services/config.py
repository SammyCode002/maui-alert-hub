"""
Configuration service using Pydantic Settings.
Reads from .env file and environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    App configuration. Values come from .env file or environment variables.

    WHY Pydantic Settings?
    Instead of manually reading os.environ everywhere, Pydantic validates
    and types all your config in one place. If a required value is missing,
    you get a clear error at startup (not a random crash later).
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # NWS API config
    nws_user_agent: str = "MauiAlertHub/1.0 (contact@mauialerthub.com)"

    # Database
    database_url: str = "sqlite:///./maui_alert_hub.db"

    # Scraper settings
    scrape_interval_minutes: int = 5

    # Logging
    log_level: str = "DEBUG"

    # CORS
    cors_origins: str = "http://localhost:5173"

    # Environment
    environment: str = "development"


# Single global instance. Import this everywhere.
settings = Settings()
