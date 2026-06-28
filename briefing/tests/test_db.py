from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import inspect, text


@pytest.mark.asyncio
async def test_init_db_creates_tables(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BRIEFING_DATA_DIR", str(tmp_path))

    from app.core.config import AppConfig
    from app.db.database import build_sqlite_db_url, get_engine, init_db, init_engine

    config = AppConfig()
    db_url = build_sqlite_db_url(config.data_dir)

    init_engine(db_url)
    await init_db()

    engine = get_engine()
    assert engine is not None

    async with engine.begin() as conn:
        table_names = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
    assert set(table_names) >= {"runs", "briefing_outputs", "processed_emails"}


@pytest.mark.asyncio
async def test_init_db_is_idempotent(tmp_path: Path):
    from app.db.database import init_db, init_engine

    db_url = f"sqlite+aiosqlite:///{tmp_path / 'briefing.db'}"
    init_engine(db_url)

    await init_db()
    await init_db()


@pytest.mark.asyncio
async def test_get_session_yields_async_session(tmp_path: Path):
    from app.db.database import get_session, init_db, init_engine

    db_url = f"sqlite+aiosqlite:///{tmp_path / 'briefing.db'}"
    init_engine(db_url)
    await init_db()

    async with get_session() as session:
        result = await session.execute(text("select 1"))
        assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_fastapi_lifespan_initializes_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("BRIEFING_DATA_DIR", str(tmp_path))

    from app.main import app

    async with app.router.lifespan_context(app):
        pass

    assert (tmp_path / "briefing.db").exists()

