"""Centralized settings loaded from .env."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Postgres
    db_host:     str = Field("localhost",    alias="POSTGRES_HOST")
    db_port:     int = Field(5433,           alias="POSTGRES_PORT")
    db_name:     str = Field("finance_poc",  alias="POSTGRES_DB")
    db_user:     str = Field("postgres",     alias="POSTGRES_USER")
    db_password: str = Field("",             alias="POSTGRES_PASSWORD")

    # JWT
    jwt_secret_key:     str = "change-me"
    jwt_algorithm:      str = "HS256"
    jwt_expire_minutes: int = 60

    # CORS
    api_cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


settings = Settings()