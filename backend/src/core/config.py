from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit
from uuid import UUID

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEXORA_",
        env_file=REPOSITORY_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_environment: Literal["development", "test", "production"] = "development"
    app_origin: str = "http://localhost:8080"
    app_version: str = "0.1.0"
    database_url: str = Field(
        default="postgresql+asyncpg://nexora:local-only-change-me@127.0.0.1:5433/nexora"
    )
    tenant_id: UUID = UUID("00000000-0000-0000-0000-000000000001")
    tenant_name: str = "Nexora"
    session_cookie_name: str = "nexora_session"
    session_cookie_secure: bool = False

    @field_validator("app_origin")
    @classmethod
    def validate_app_origin(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("NEXORA_APP_ORIGIN must be an absolute HTTP(S) origin")
        if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
            raise ValueError("NEXORA_APP_ORIGIN must not include a path, query, or fragment")
        return f"{parsed.scheme}://{parsed.netloc}"

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.app_environment == "production":
            if not self.session_cookie_secure:
                raise ValueError("NEXORA_SESSION_COOKIE_SECURE must be true in production")
            if not self.app_origin.startswith("https://"):
                raise ValueError("NEXORA_APP_ORIGIN must use HTTPS in production")
            if not self.database_url.startswith("postgresql+"):
                raise ValueError("Production requires a PostgreSQL database URL")
        return self


settings = Settings()
