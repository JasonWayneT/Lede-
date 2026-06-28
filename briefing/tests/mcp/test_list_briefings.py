"""Tests for MCP list_briefings tool — Story 11.1."""

from __future__ import annotations

import json

import pytest

from app.db.database import get_session
from app.db.models import Run
from app.mcp_server import call_tool


@pytest.mark.asyncio
async def test_list_briefings_empty(mcp_db):
    result = await call_tool("list_briefings", {})
    data = json.loads(result[0].text)
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_briefings_returns_completed_runs(mcp_db):
    async with get_session() as session:
        async with session.begin():
            session.add(Run(status="complete", depth="standard", section_config={}))
            session.add(Run(status="running", depth="standard", section_config={}))

    result = await call_tool("list_briefings", {})
    data = json.loads(result[0].text)
    assert len(data) == 1
    assert data[0]["status"] == "complete"
