# backend/app/core/config.py

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

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

    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    @property
    def database_url(self):
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
