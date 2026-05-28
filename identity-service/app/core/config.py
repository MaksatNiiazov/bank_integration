from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Turkuaz Identity"
    environment: str = "development"
    database_url: str = "sqlite:///./data/identity.db"
    secret_key: str = "dev-change-me-32-byte-secret-key-for-turkuaz-identity"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    auto_create_schema: bool = True
    auto_create_admin: bool = True
    default_admin_email: str = "admin@example.com"
    default_admin_password: str = "admin123"
    default_admin_full_name: str = "Platform Admin"
    backend_cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:6750",
            "http://127.0.0.1:6750",
        ]
    )
    backend_cors_origin_regex: str | None = r"https://.*\.ngrok-free\.dev"


settings = Settings()
