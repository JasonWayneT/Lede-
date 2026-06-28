"""Daemon mode entry point — runs the scheduler without a web server."""

# Implements ARCH-005

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from app.core.config import AppConfig
from app.core.scheduler import check_missed_runs, schedule_run, scheduler
from app.db.database import build_sqlite_db_url, init_db, init_engine
from app.pipeline import orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def daemon_main() -> None:
    config = AppConfig()
    config.data_dir.mkdir(parents=True, exist_ok=True)

    init_engine(build_sqlite_db_url(config.data_dir))
    await init_db()

    settings_path = Path(config.data_dir) / "settings.json"
    stored: dict = {}
    if settings_path.exists():
        try:
            stored = json.loads(settings_path.read_text())
        except Exception:
            pass

    cadence = stored.get("cadence", "off")
    time_str = stored.get("schedule_time", "07:00")

    if cadence != "off":
        schedule_run(cadence, time_str, config)

    scheduler.start()
    logger.info("Briefing daemon started — cadence=%s time=%s", cadence, time_str)

    # Check for missed run on startup
    missed = await check_missed_runs(config)
    if missed:
        logger.info("Missed run detected at %s — starting now", missed.isoformat())
        run_id = await orchestrator.start_run(config)
        await orchestrator.run_pipeline(run_id, config)

    # Keep event loop alive
    try:
        while True:
            await asyncio.sleep(60)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(daemon_main())
