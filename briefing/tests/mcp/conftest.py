"""MCP test fixtures."""

from __future__ import annotations

import pytest_asyncio

from app.db.database import build_sqlite_db_url, init_db, init_engine


@pytest_asyncio.fixture
async def mcp_db(tmp_path):
    init_engine(build_sqlite_db_url(tmp_path))
    await init_db()
    return tmp_path
