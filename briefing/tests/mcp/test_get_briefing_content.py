"""Tests for MCP get_briefing_content tool — Story 11.1."""

from __future__ import annotations

import pytest

from app.db.database import get_session
from app.db.models import BriefingOutput, Run
from app.mcp_server import call_tool


@pytest.mark.asyncio
async def test_get_briefing_content_markdown(mcp_db, tmp_path):
    md_file = tmp_path / "briefing.md"
    md_file.write_text("# Test Briefing\n\nHello world.")

    async with get_session() as session:
        async with session.begin():
            run = Run(status="complete", depth="standard", section_config={})
            session.add(run)
        await session.refresh(run)
        run_id = run.id

    async with get_session() as session:
        async with session.begin():
            session.add(BriefingOutput(run_id=run_id, markdown_path=str(md_file), audio_path=None))

    result = await call_tool("get_briefing_content", {"run_id": run_id, "content_type": "markdown"})
    assert "Hello world" in result[0].text


@pytest.mark.asyncio
async def test_get_briefing_content_no_output(mcp_db):
    result = await call_tool("get_briefing_content", {"run_id": 9999, "content_type": "markdown"})
    assert "no output" in result[0].text.lower() or "not found" in result[0].text.lower()


@pytest.mark.asyncio
async def test_get_briefing_content_audio_path(mcp_db):
    async with get_session() as session:
        async with session.begin():
            run = Run(status="complete", depth="standard", section_config={})
            session.add(run)
        await session.refresh(run)
        run_id = run.id

    async with get_session() as session:
        async with session.begin():
            session.add(BriefingOutput(run_id=run_id, markdown_path="/tmp/b.md", audio_path="/tmp/b.mp3"))

    result = await call_tool("get_briefing_content", {"run_id": run_id, "content_type": "audio"})
    assert "/tmp/b.mp3" in result[0].text
