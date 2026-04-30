"""Configuration de l'application Flask AgriData."""
import os
import secrets
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration globale de l'application"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "AgriData Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # Data storage
    DATA_DIR: str = "data"

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Optional integrations
    REDIS_URL: str = "redis://localhost:6379/0"
    WEATHER_API_KEY: Optional[str] = None

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60

    # Email
    MAIL_ENABLED: bool = False
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: str = "noreply@agridata.app"
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: int = 587

    # Logging
    LOG_LEVEL: str = "INFO"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_bool_fields(cls, value, default=False) -> bool:
        """Accept common deployment values like 'release' without crashing."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            return normalized in ("1", "true", "yes", "on")
        return bool(value)

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",")]
        return value

    def get_data_dir(self) -> str:
        """Return data directory, using /tmp on serverless (Vercel)."""
        if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
            return "/tmp/data"
        return self.DATA_DIR


settings = Settings()
