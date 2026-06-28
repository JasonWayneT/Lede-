# Story 9.1: APScheduler Integration and Run Scheduling

Status: ready-for-dev

## Story

As a user who configured a daily schedule,
I want the app to automatically trigger a briefing run at my configured time when the app is open,
so that a fresh briefing is ready for me without manual action.

## Acceptance Criteria

1. **Given** a schedule configured to run daily at 7:00 AM and the app is open at 7:00 AM, **When** the scheduled time arrives, **Then** APScheduler fires and the orchestrator starts a Run exactly as if the user had clicked "Run Briefing"

2. **Given** a Run triggered by the scheduler, **When** it completes, **Then** it appears in the history list exactly like a manually triggered Run

3. **Given** the scheduler configuration changing in Settings, **When** the user saves a new cadence or time, **Then** APScheduler's job is updated in memory immediately — no restart required

4. **Given** cadence set to `"off"`, **When** the scheduler evaluates, **Then** no automatic Runs fire

5. **Given** a Run already in progress, **When** the scheduler fires for a new run, **Then** the new Run is queued and not started until the current Run completes

## Tasks / Subtasks

- [ ] Implement `app/core/scheduler.py` (AC: 1–5)
  - [ ] Use `apscheduler.schedulers.asyncio.AsyncIOScheduler`
  - [ ] Initialize scheduler in FastAPI lifespan: `scheduler.start()` on startup, `scheduler.shutdown()` on shutdown
  - [ ] `def schedule_run(cadence: str, time: str, config: AppConfig) -> None`: add or replace APScheduler job
  - [ ] Cadence → cron mapping: `"daily"` → `cron(hour=H, minute=M)`, `"every_other_day"` → `interval(days=2, start_date=...)`, `"weekly"` → `cron(day_of_week="mon", hour=H, minute=M)`, `"off"` → remove job
  - [ ] Job function: `lambda: asyncio.create_task(orchestrator.start_run(config))`
  - [ ] Check for active run before starting: if Run with `status="running"` exists in DB, queue the triggered run (see dev notes)

- [ ] Wire scheduler into lifespan in `app/main.py` (AC: 1, 4)
  - [ ] Import and start `scheduler` in lifespan alongside `init_db()`
  - [ ] On startup: load schedule settings from `data/settings.json` and call `schedule_run(...)` if cadence != "off"

- [ ] Expose scheduler reschedule to settings endpoint (AC: 3)
  - [ ] `PUT /api/settings/schedule` (Story 8.7) calls `scheduler.schedule_run(new_cadence, new_time, config)` after persisting

- [ ] Write tests in `tests/api/test_settings.py` (AC: 3, 4)
  - [ ] Mock APScheduler; test that PUT /settings/schedule calls reschedule
  - [ ] Test cadence "off" removes job

## Dev Notes

### APScheduler async

Use `AsyncIOScheduler` (not `BackgroundScheduler`) since the app is async. It integrates with FastAPI's event loop.

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()
```

### Queued run on concurrent fire (AC: 5)

APScheduler will fire the job even if a Run is in progress. The job function must check for active runs:

```python
async def _scheduled_run(config):
    async with get_session() as session:
        active = await session.execute(select(Run).where(Run.status == "running"))
        if active.scalar_one_or_none():
            logger.info("Scheduled run deferred — another run in progress")
            return
    await orchestrator.start_run(config)
```

A simple implementation skips the run if one is active. "Queuing" behavior (wait and run after) is complex and can be a V2 enhancement — for V1, skip with a log message.

### Scheduler as module singleton

```python
# app/core/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()
```

`main.py` imports this singleton and starts/stops it in the lifespan.

### References

- [Source: docs/ARCHITECTURE.md § "Infrastructure & Deployment — Scheduling"] — APScheduler, in-process
- [Source: docs/epics-stories.md § "Story 9.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
