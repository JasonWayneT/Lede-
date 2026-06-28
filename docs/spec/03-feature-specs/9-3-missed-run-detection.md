# Story 9.3: Missed Run Detection and Auto-Retry

Status: ready-for-dev

## Story

As a user who does not use Daemon Mode,
I want the app to detect and retry any missed scheduled runs when I open it,
so that I still get my briefing even if the app was not running at the scheduled time.

## Acceptance Criteria

1. **Given** a scheduled run that fired at 7:00 AM while the app was closed, **When** I open the app at 9:00 AM, **Then** the app detects the missed run and displays: "Missed run at 7:00 AM -- retrying now"

2. **Given** the missed run detection firing, **When** the app initializes, **Then** a new Run starts automatically before the history list renders

3. **Given** multiple missed runs (app closed for 3 days with daily schedule), **When** the app opens, **Then** only one retry Run fires (the most recent missed run) — not multiple simultaneous runs

## Tasks / Subtasks

- [ ] Implement missed run detection in `app/core/scheduler.py` (AC: 1–3)
  - [ ] `async def check_missed_runs(config: AppConfig) -> datetime | None`: compares last successful Run's `created_at` against expected schedule time; returns missed run datetime if detected, else None
  - [ ] Logic: if `cadence != "off"` and the most recent completed Run was before the last scheduled fire time → missed run detected
  - [ ] Return only the most recent missed run (not all missed runs)

- [ ] Call on app startup in `app/main.py` lifespan (AC: 2)
  - [ ] After `init_db()` and scheduler start: `missed = await check_missed_runs(config)`
  - [ ] If missed: automatically call `await orchestrator.start_run(config)` in background

- [ ] Add missed run notification endpoint (AC: 1)
  - [ ] `GET /api/briefings/missed` → `{"data": {"missed_at": "ISO8601"|null, "retrying": true|false}}`
  - [ ] Dashboard loads this on page load; shows banner if `missed_at` is not null

- [ ] Write tests (AC: 1–3)
  - [ ] Mock DB with last Run from yesterday; schedule daily at 7am; detect missed run
  - [ ] Mock DB with last Run from 3 days ago; verify only one retry fired
  - [ ] Mock DB with last Run from today after scheduled time; verify no missed run detected

## Dev Notes

### Missed run detection logic

```python
from datetime import datetime, timedelta

async def check_missed_runs(config) -> datetime | None:
    if config.schedule_cadence == "off":
        return None
    
    # Get last successful run time
    async with get_session() as session:
        result = await session.execute(
            select(Run).where(Run.status == "complete").order_by(Run.created_at.desc()).limit(1)
        )
        last_run = result.scalar_one_or_none()
    
    now = datetime.utcnow()
    last_fire = _calc_last_fire_time(config.schedule_cadence, config.schedule_time, now)
    
    if last_run is None or last_run.created_at < last_fire:
        return last_fire  # missed run at this time
    return None
```

### _calc_last_fire_time

Calculate when the most recent scheduled fire should have occurred before now. For "daily" at "07:00": if now is 09:00, last fire = today at 07:00. If now is 06:00, last fire = yesterday at 07:00.

### Only one retry (AC: 3)

Even if the app was closed for a week, only one retry fires. This prevents a flood of pipeline runs on app open. The user can manually trigger additional runs.

### References

- [Source: docs/epics-stories.md § "Story 9.3"] — acceptance criteria
- [Source: docs/PRD.md § "UJ-2 — Edge case"] — "on next app open, the app detects the missed run and retries it automatically"

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
