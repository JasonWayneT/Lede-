"""Tests for MCP get_run_status tool — Story 11.1."""

from __future__ import annotations

import pytest

from app.db.database import get_session
from app.db.models import Run
from app.mcp_server import call_tool


@pytest.mark.asyncio
async def test_get_run_status_returns_status(mcp_db):
    async with get_session() as session:
        async with session.begin():
            run = Run(status="running", depth="standard", section_config={})
            session.add(run)
        await session.refresh(run)
        run_id = run.id

    result = await call_tool("get_run_status", {"run_id": run_id})
    assert any("running" in r.text for r in result)


@pytest.mark.asyncio
async def test_get_run_status_not_found(mcp_db):
    result = await call_tool("get_run_status", {"run_id": 9999})
    assert any("not found" in r.text.lower() for r in result)
