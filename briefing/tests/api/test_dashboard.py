"""Tests for dashboard hold-state surfacing — BUG-006."""

from __future__ import annotations

import json

import pytest

from app.core.config import AppConfig
from app.db.database import get_session
from app.db.models import Run


def _onboard():
    config = AppConfig()
    settings_file = config.data_dir / "settings.json"
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings_file.write_text(json.dumps({"onboarding_complete": True}))


async def _insert_run(status: str, error: str | None = None) -> int:
    async with get_session() as session:
        async with session.begin():
            run = Run(status=status, depth="standard", section_config={}, error=error)
            session.add(run)
        await session.refresh(run)
        return run.id


@pytest.mark.asyncio
async def test_dashboard_shows_hold_banner_with_error(async_client):
    # AC-086
    _onboard()
    await _insert_run("hold", "[select] Ollama unreachable: All connection attempts failed")

    resp = await async_client.get("/", follow_redirects=True)

    assert resp.status_code == 200
    assert "Ollama unreachable" in resp.text
    assert "Needs attention" in resp.text
    assert "/retry" in resp.text


@pytest.mark.asyncio
async def test_dashboard_no_hold_banner_when_no_held_runs(async_client):
    _onboard()
    await _insert_run("complete", None)

    resp = await async_client.get("/", follow_redirects=True)

    assert resp.status_code == 200
    assert "hold-banner" not in resp.text
    assert "Needs attention" not in resp.text


@pytest.mark.asyncio
async def test_dashboard_shows_most_recent_hold_run(async_client):
    _onboard()
    await _insert_run("hold", "First failure")
    await _insert_run("hold", "Second, more recent failure")

    resp = await async_client.get("/", follow_redirects=True)

    assert "Second, more recent failure" in resp.text
