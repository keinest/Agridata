"""Configuration de l'application FastAPI AgriData."""
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_bool(value, default: bool = False) -> bool:
    """Accept common deployment values like 'release' without crashing."""
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}:
        return True
    if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
        return False
    return default


class Settings(BaseSettings):
    """Configuration globale de l'application"""

    model_config = SettingsConfigDict(
        env_file=("backend/.env", ".env"),
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "AgriData Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    API_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    DATA_DIR: str = "data"

    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://0.0.0.0:3000",
            "http://0.0.0.0:5173",
        ]
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    REDIS_URL: str = "redis://localhost:6379/0"

    WEATHER_API_KEY: Optional[str] = None

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100

    MAIL_ENABLED: bool = False
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = "noreply@agridata.app"
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: int = 587

    LOG_LEVEL: str = "INFO"

    @field_validator("DEBUG", "MAIL_ENABLED", mode="before")
    @classmethod
    def parse_bool_fields(cls, value):
        return _parse_bool(value)

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return value
        return [origin.strip() for origin in str(value).split(",") if origin.strip()]


settings = Settings()
