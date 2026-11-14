
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Knowly API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Google Gemini AI configuration
    GEMINI_API_KEY: SecretStr
    GEMINI_GENERATION_MODEL: str = "gemini-3.5-flash-lite"

    # Private document storage
    DOCUMENT_STORAGE_PROVIDER: str = "local"
    DOCUMENT_STORAGE_DIR: Path = (
        BASE_DIR / "private_storage" / "documents"
    )
    MAX_UPLOAD_SIZE_BYTES: int = 20 * 1024 * 1024

    # Tigris S3-compatible object storage
    TIGRIS_ACCESS_KEY_ID: SecretStr | None = None
    TIGRIS_SECRET_ACCESS_KEY: SecretStr | None = None
    TIGRIS_BUCKET_NAME: str | None = None
    TIGRIS_ENDPOINT_URL: str = "https://t3.storage.dev"
    TIGRIS_REGION: str = "auto"

    # Frontend configuration
    FRONTEND_URL: str = "http://localhost:3000"

    # Authentication session configuration
    SESSION_COOKIE_NAME: str = "knowly_session"
    SESSION_TTL_SECONDS: int = 604800

    # CSRF protection configuration
    CSRF_COOKIE_NAME: str = "__Host-knowly_csrf"
    CSRF_SECRET_KEY: SecretStr

    # Google OAuth configuration
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: SecretStr
    GOOGLE_REDIRECT_URI: str
    OAUTH_STATE_SECRET: SecretStr

    # PostgreSQL database settings
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5433
    POSTGRES_SSLMODE: str = "prefer"

    @property
    def DATABASE_URL(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
            query={"sslmode": self.POSTGRES_SSLMODE},
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
