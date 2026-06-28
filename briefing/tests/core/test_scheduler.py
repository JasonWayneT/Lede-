"""Tests for scheduler, daemon, and missed run detection — Stories 9.1–9.3."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core import scheduler as sched_mod
from app.core.config import AppConfig


def _config(tmp_path):
    return AppConfig.model_validate({
        "llm_provider": "ollama",
        "BRIEFING_DATA_DIR": str(tmp_path),
    })


# ---------------------------------------------------------------------------
# schedule_run tests
# ---------------------------------------------------------------------------

def test_schedule_run_daily_adds_job(tmp_path):
    config = _config(tmp_path)
    mock_scheduler = MagicMock()
    mock_scheduler.get_job.return_value = None
    with patch.object(sched_mod, "scheduler", mock_scheduler):
        sched_mod.schedule_run("daily", "07:00", config)
    mock_scheduler.add_job.assert_called_once()
    call_kwargs = mock_scheduler.add_job.call_args
    assert call_kwargs.args[1] == "cron"


def test_schedule_run_off_removes_job(tmp_path):
    config = _config(tmp_path)
    mock_job = MagicMock()
    mock_scheduler = MagicMock()
    mock_scheduler.get_job.return_value = mock_job
    with patch.object(sched_mod, "scheduler", mock_scheduler):
        sched_mod.schedule_run("off", "07:00", config)
    mock_scheduler.remove_job.assert_called_once_with(sched_mod._JOB_ID)
    mock_scheduler.add_job.assert_not_called()


# ---------------------------------------------------------------------------
# check_missed_runs tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_no_missed_run_when_cadence_off(tmp_path):
    config = _config(tmp_path)
    # Write settings.json with cadence=off
    settings_file = tmp_path / "settings.json"
    import json
    settings_file.write_text(json.dumps({"cadence": "off"}))
    result = await sched_mod.check_missed_runs(config)
    assert result is None


@pytest.mark.asyncio
async def test_missed_run_detected_no_previous_runs(tmp_path):
    config = _config(tmp_path)
    import json
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"cadence": "daily", "schedule_time": "07:00"}))

    from app.db.database import build_sqlite_db_url, init_db, init_engine
    init_engine(build_sqlite_db_url(tmp_path))
    await init_db()

    result = await sched_mod.check_missed_runs(config)
    # No runs in DB → missed run should be detected
    assert result is not None


@pytest.mark.asyncio
async def test_no_missed_run_when_recent_run_exists(tmp_path):
    config = _config(tmp_path)
    import json
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(json.dumps({"cadence": "daily", "schedule_time": "07:00"}))

    from app.db.database import build_sqlite_db_url, init_db, init_engine, get_session
    from app.db.models import Run
    init_engine(build_sqlite_db_url(tmp_path))
    await init_db()

    # Insert a run from today (after 7am)
    recent_dt = datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0)
    async with get_session() as session:
        async with session.begin():
            session.add(Run(status="complete", depth="standard", section_config={}, created_at=recent_dt))

    result = await sched_mod.check_missed_runs(config)
    # Recent run exists after scheduled time → no missed run
    assert result is None


# ---------------------------------------------------------------------------
# Daemon PID tests (Story 9.2)
# ---------------------------------------------------------------------------

def test_check_daemon_alive_no_pid_file(tmp_path):
    config = _config(tmp_path)
    assert sched_mod.check_daemon_alive(config) is False


def test_check_daemon_alive_stale_pid_cleans_up(tmp_path):
    config = _config(tmp_path)
    pid_file = tmp_path / "briefing.pid"
    pid_file.write_text("99999999")  # PID that certainly doesn't exist

    result = sched_mod.check_daemon_alive(config)
    assert result is False
    assert not pid_file.exists()  # stale file removed
