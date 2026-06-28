"""Shared API test fixtures."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.database import build_sqlite_db_url, init_db, init_engine


@pytest_asyncio.fixture
async def async_client(tmp_path):
    db_url = build_sqlite_db_url(tmp_path)
    init_engine(db_url)
    await init_db()

    # Patch AppConfig so routes use tmp_path DB
    import app.api.settings as settings_mod
    settings_mod._config_singleton = None  # reset singleton

    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
