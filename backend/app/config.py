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

    # Application
    APP_NAME: str = "AgriData Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    # Database
    DATABASE_URL: Optional[str] = None
    DB_DRIVER: str = "mysql+pymysql"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "agridata"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "agridata_db"

    # Database URL
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("mysql://"):
                return self.DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
            # PostgreSQL URLs are handled directly by SQLAlchemy with psycopg2
            return self.DATABASE_URL

        # Use SQLite for local development if DEBUG=True
        if self.DEBUG:
            return "sqlite:///./agridata.db"

        return (
            f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
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

    # Redis (Cache & Celery)
    REDIS_URL: str = "redis://localhost:6379/0"

    # External Services
    WEATHER_API_KEY: Optional[str] = None

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100

    # Email (Optional)
    MAIL_ENABLED: bool = False
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = "noreply@agridata.app"
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: int = 587

    # Logging
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


# Instance globale des settings
settings = Settings()
