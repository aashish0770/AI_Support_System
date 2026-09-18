# backend/app/core/config.py

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy import URL

# Anchored to this files locaton, not th caller's CWD same reasoning as alembic/env.py
# and the ingestion loaders path resolution.

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = _BACKEND_DIR.parent
load_dotenv(dotenv_path=_REPO_ROOT / ".env")


class Settings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ai_support_system"

    # LLM provider
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    @property
    # def database_url(self):
    #     return (
    #         f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
    #         f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    #     )
    def database_url(self) -> URL:
        return URL.create(
            "postgresql+psycopg2",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
