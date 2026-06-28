"""APScheduler integration, daemon spawn/kill, and missed run detection."""

# Implements ARCH-005

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.core.config import AppConfig
from app.db.database import get_session
from app.db.models import Run

logger = logging.getLogger(__name__)

_JOB_ID = "briefing_scheduled_run"

scheduler = AsyncIOScheduler()


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------

def schedule_run(cadence: str, time_str: str, config: AppConfig) -> None:
    if scheduler.get_job(_JOB_ID):
        scheduler.remove_job(_JOB_ID)

    if cadence == "off":
        logger.info("Scheduler: cadence off — no job scheduled")
        return

    h, m = (int(x) for x in time_str.split(":"))

    if cadence == "daily":
        scheduler.add_job(_run_if_idle, "cron", hour=h, minute=m,
                          id=_JOB_ID, args=[config], replace_existing=True)
    elif cadence == "every_other_day":
        scheduler.add_job(_run_if_idle, "interval", days=2,
                          start_date=datetime.now().replace(hour=h, minute=m, second=0),
                          id=_JOB_ID, args=[config], replace_existing=True)
    elif cadence == "weekly":
        scheduler.add_job(_run_if_idle, "cron", day_of_week="mon", hour=h, minute=m,
                          id=_JOB_ID, args=[config], replace_existing=True)
    logger.info("Scheduler: job set — cadence=%s time=%02d:%02d", cadence, h, m)


async def _run_if_idle(config: AppConfig) -> None:
    from app.pipeline import orchestrator

    async with get_session() as session:
        result = await session.execute(select(Run).where(Run.status == "running"))
        if result.scalars().first():
            logger.info("Scheduled run deferred — another run already in progress")
            return

    run_id = await orchestrator.start_run(config)
    asyncio.create_task(orchestrator.run_pipeline(run_id, config))


# ---------------------------------------------------------------------------
# Missed run detection (Story 9.3)
# ---------------------------------------------------------------------------

def _calc_last_fire_time(cadence: str, time_str: str, now: datetime) -> datetime | None:
    if cadence == "off":
        return None
    h, m = (int(x) for x in time_str.split(":"))
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if cadence == "daily":
        if target > now:
            target -= timedelta(days=1)
        return target
    elif cadence == "every_other_day":
        if target > now:
            target -= timedelta(days=2)
        return target
    elif cadence == "weekly":
        days_since_monday = now.weekday()
        candidate = target - timedelta(days=days_since_monday)
        if candidate > now:
            candidate -= timedelta(weeks=1)
        return candidate
    return None


async def check_missed_runs(config: AppConfig) -> datetime | None:
    settings_path = Path(config.data_dir) / "settings.json"
    stored: dict = {}
    if settings_path.exists():
        try:
            stored = json.loads(settings_path.read_text())
        except Exception:
            pass

    cadence = stored.get("cadence", "off")
    time_str = stored.get("schedule_time", "07:00")

    if cadence == "off":
        return None

    now = datetime.utcnow()
    last_fire = _calc_last_fire_time(cadence, time_str, now)
    if last_fire is None:
        return None

    async with get_session() as session:
        result = await session.execute(
            select(Run).where(Run.status == "complete").order_by(Run.created_at.desc()).limit(1)
        )
        last_run = result.scalar_one_or_none()

    if last_run is None or last_run.created_at < last_fire:
        return last_fire
    return None


# ---------------------------------------------------------------------------
# Daemon spawn / kill (Story 9.2)
# ---------------------------------------------------------------------------

def _pid_file(config: AppConfig) -> Path:
    return Path(config.data_dir) / "briefing.pid"


def start_daemon(config: AppConfig) -> None:
    pid_path = _pid_file(config)
    kwargs: dict = {"close_fds": True}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    proc = subprocess.Popen(
        [sys.executable, "-m", "app.daemon_runner"],
        **kwargs,
    )
    pid_path.write_text(str(proc.pid))
    logger.info("Daemon started — PID %d", proc.pid)


def stop_daemon(config: AppConfig) -> None:
    pid_path = _pid_file(config)
    if not pid_path.exists():
        return
    try:
        pid = int(pid_path.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        logger.info("Daemon stopped — PID %d", pid)
    except (ProcessLookupError, ValueError):
        pass
    pid_path.unlink(missing_ok=True)


def check_daemon_alive(config: AppConfig) -> bool:
    pid_path = _pid_file(config)
    if not pid_path.exists():
        return False
    try:
        pid = int(pid_path.read_text().strip())
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError, ValueError, OSError):
        pid_path.unlink(missing_ok=True)
        return False
