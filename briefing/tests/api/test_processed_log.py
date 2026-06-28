from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select


@pytest.mark.asyncio
async def test_clear_processed_log_endpoint_deletes_rows(tmp_path: Path):
    from app.core.config import AppConfig
    from app.db.database import get_session, init_db, init_engine
    from app.db.models import ProcessedEmail, Run

    # DB setup
    init_engine(f"sqlite+aiosqlite:///{tmp_path / 'briefing.db'}")
    await init_db()

    async with get_session() as session:
        run = Run(status="complete", depth="standard", section_config={}, error=None)
        session.add(run)
        await session.commit()
        await session.refresh(run)

        session.add_all(
            [
                ProcessedEmail(email_id="a", run_id=run.id),
                ProcessedEmail(email_id="b", run_id=run.id),
            ]
        )
        await session.commit()

    # Build a minimal app to host the route.
    from app.api.settings import router as settings_router

    app = FastAPI()
    app.include_router(settings_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.delete("/api/settings/processed-log")

    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["cleared"] is True
    assert data["rows_deleted"] == 2

    async with get_session() as session:
        result = await session.execute(select(ProcessedEmail.email_id))
        assert result.scalars().all() == []

