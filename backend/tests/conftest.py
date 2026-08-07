"""
Shared test fixtures.

IMPORTANT: these tests run against a real PostgreSQL database, not SQLite.
Chunk.tsv is a Postgres-specific TSVECTOR type with a GENERATED ALWAYS AS
expression (see app/models/chunk.py) — SQLite has no equivalent, so an
in-memory SQLite test DB would either fail to create the table or silently
behave differently than production. This is a deliberate tradeoff: slightly
slower/heavier tests in exchange for tests that actually exercise the real
schema, including the generated column.

One-time setup before running tests:
    docker compose --env-file .env -f infra/docker-compose.yml exec db \
        psql -U postgres -c "CREATE DATABASE ai_support_system_test;"
"""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import (
    Base,
)  # noqa: F401 — importing app.models registers all models on Base.metadata

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_support_system_test",
)


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture()
def db_session(engine):
    """One connection + outer transaction per test, rolled back at the end.
    This is what gives each test a clean slate without recreating tables
    on every single test — much faster than drop/create per test."""
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
