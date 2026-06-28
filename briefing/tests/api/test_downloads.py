"""Tests for download endpoints — Story 8.3."""

from __future__ import annotations

import pytest

from app.db.database import get_session
from app.db.models import BriefingOutput, Run


async def _create_run_with_output(audio_path=None, markdown_path="/tmp/b.md"):
    async with get_session() as session:
        async with session.begin():
            run = Run(status="complete", depth="standard", section_config={})
            session.add(run)
        await session.refresh(run)
        run_id = run.id

    async with get_session() as session:
        async with session.begin():
            session.add(BriefingOutput(run_id=run_id, markdown_path=markdown_path, audio_path=audio_path))

    return run_id


@pytest.mark.asyncio
async def test_download_markdown_not_found(async_client):
    resp = await async_client.get("/api/briefings/999/download/markdown")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_download_audio_null_path_returns_404(async_client):
    run_id = await _create_run_with_output(audio_path=None)
    resp = await async_client.get(f"/api/briefings/{run_id}/download/audio")
    assert resp.status_code == 404
    assert "Audio not available" in resp.json()["error"]


@pytest.mark.asyncio
async def test_download_markdown_file_not_on_disk(async_client):
    run_id = await _create_run_with_output(markdown_path="/nonexistent/path.md")
    resp = await async_client.get(f"/api/briefings/{run_id}/download/markdown")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_download_markdown_returns_correct_content_type(async_client, tmp_path):
    md_file = tmp_path / "briefing.md"
    md_file.write_text("# Test Briefing\n\nHello world.")
    run_id = await _create_run_with_output(markdown_path=str(md_file))
    resp = await async_client.get(f"/api/briefings/{run_id}/download/markdown")
    assert resp.status_code == 200
    assert "text/markdown" in resp.headers["content-type"] or "text/plain" in resp.headers["content-type"]
