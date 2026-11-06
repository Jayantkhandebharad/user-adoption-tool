"""Tests run against a real Postgres: by default the dev emulator
(`scripts/dev-services.sh up`), in a separate `guide_test` database that is recreated and
migrated once per run. Override with TEST_DATABASE_URL."""

import os
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, make_url, text

from app.config import Settings
from app.main import create_app

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://guide:guide@localhost:55432/guide_test"
)
BACKEND_DIR = Path(__file__).resolve().parent.parent
STUDIO_ORIGIN = "http://testserver"


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    url = make_url(TEST_DATABASE_URL)
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{url.database}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    admin.dispose()

    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["database_url"] = TEST_DATABASE_URL
    command.upgrade(config, "head")
    yield TEST_DATABASE_URL


@pytest.fixture
def settings(database_url: str) -> Settings:
    return Settings(database_url=database_url, public_url=STUDIO_ORIGIN, _env_file=None)


@pytest.fixture
def make_client(settings: Settings) -> Iterator[Callable[..., TestClient]]:
    """Build a client for an app with some settings overridden. Tables are emptied afterwards."""
    apps: list[FastAPI] = []
    clients: list[TestClient] = []

    def make(**overrides: Any) -> TestClient:
        app = create_app(settings.model_copy(update=overrides))
        apps.append(app)
        clients.append(TestClient(app).__enter__())
        return clients[-1]

    yield make
    for test_client in clients:
        test_client.__exit__(None, None, None)
    for app in apps:
        with app.state.sessionmaker() as db:
            db.execute(text("TRUNCATE team_members, studio_sessions CASCADE"))
            db.commit()
        app.state.sessionmaker.kw["bind"].dispose()


@pytest.fixture
def client(make_client: Callable[..., TestClient]) -> TestClient:
    return make_client()
