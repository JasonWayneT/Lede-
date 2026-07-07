"""Tests for dashboard hold-state surfacing — BUG-006 — and missed-run surfacing — BUG-011."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

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


# ── Missed-run banner (BUG-011, 9-3/AC-1) ───────────────────────────────────

@pytest.mark.asyncio
async def test_dashboard_shows_missed_run_banner(async_client):
    _onboard()
    fixed_time = datetime(2026, 7, 6, 7, 0, tzinfo=timezone.utc)
    with patch("app.core.scheduler.check_missed_runs", new=AsyncMock(return_value=fixed_time)):
        resp = await async_client.get("/", follow_redirects=True)

    assert resp.status_code == 200
    assert "Missed run" in resp.text
    assert "missed-run-banner" in resp.text


@pytest.mark.asyncio
async def test_dashboard_no_missed_run_banner_when_none_missed(async_client):
    _onboard()
    with patch("app.core.scheduler.check_missed_runs", new=AsyncMock(return_value=None)):
        resp = await async_client.get("/", follow_redirects=True)

    assert resp.status_code == 200
    assert "missed-run-banner" not in resp.text


@pytest.mark.asyncio
async def test_dashboard_missed_run_banner_shows_retrying_when_run_active(async_client):
    _onboard()
    await _insert_run("running", None)
    fixed_time = datetime(2026, 7, 6, 7, 0, tzinfo=timezone.utc)
    with patch("app.core.scheduler.check_missed_runs", new=AsyncMock(return_value=fixed_time)):
        resp = await async_client.get("/", follow_redirects=True)

    assert "retrying now" in resp.text
