from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import select


@pytest.mark.asyncio
async def test_finalize_success_writes_processed_emails_and_status_atomically(tmp_path: Path):
    from app.db.database import get_session, init_db, init_engine
    from app.db.models import ProcessedEmail, Run
    from app.pipeline.orchestrator import finalize_run_success

    init_engine(f"sqlite+aiosqlite:///{tmp_path / 'briefing.db'}")
    await init_db()

    async with get_session() as session:
        run = Run(status="running", depth="standard", section_config={}, error=None)
        session.add(run)
        await session.commit()
        await session.refresh(run)
        run_id = run.id

    async with get_session() as session:
        await finalize_run_success(session=session, run_id=run_id, email_ids=["a", "b"])

        updated = await session.get(Run, run_id)
        assert updated is not None
        assert updated.status == "complete"

        result = await session.execute(select(ProcessedEmail.email_id))
        assert set(result.scalars().all()) == {"a", "b"}


@pytest.mark.asyncio
async def test_finalize_success_rolls_back_on_db_error(tmp_path: Path):
    from app.db.database import get_session, init_db, init_engine
    from app.db.models import ProcessedEmail, Run
    from app.pipeline.orchestrator import finalize_run_success

    init_engine(f"sqlite+aiosqlite:///{tmp_path / 'briefing.db'}")
    await init_db()

    async with get_session() as session:
        run = Run(status="running", depth="standard", section_config={}, error=None)
        session.add(run)
        await session.commit()
        await session.refresh(run)
        run_id = run.id

        # Pre-insert a processed email with unique email_id, so finalize attempts violate uniqueness.
        session.add(ProcessedEmail(email_id="dup", run_id=run_id))
        await session.commit()

    async with get_session() as session:
        with pytest.raises(Exception):
            await finalize_run_success(session=session, run_id=run_id, email_ids=["dup"])

    async with get_session() as session:
        updated = await session.get(Run, run_id)
        assert updated is not None
        assert updated.status == "running"


@pytest.mark.asyncio
async def test_mark_hold_does_not_write_processed_emails(tmp_path: Path):
    from app.db.database import get_session, init_db, init_engine
    from app.db.models import ProcessedEmail, Run
    from app.pipeline.orchestrator import mark_run_hold

    init_engine(f"sqlite+aiosqlite:///{tmp_path / 'briefing.db'}")
    await init_db()

    async with get_session() as session:
        run = Run(status="running", depth="standard", section_config={}, error=None)
        session.add(run)
        await session.commit()
        await session.refresh(run)
        run_id = run.id

    async with get_session() as session:
        await mark_run_hold(session=session, run_id=run_id, error="boom")

        updated = await session.get(Run, run_id)
        assert updated is not None
        assert updated.status == "hold"
        assert updated.error == "boom"

        result = await session.execute(select(ProcessedEmail.email_id))
        assert result.scalars().all() == []

