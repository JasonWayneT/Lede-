# Story 8.7: Settings -- Schedule and Daemon Mode Display

Status: ready-for-dev

## Story

As a user,
I want to configure my briefing schedule and toggle daemon mode from Settings,
so that I can control when my briefings run and whether they run even when the browser is closed.

## Acceptance Criteria

1. **Given** the Settings -- Schedule section, **When** I view it, **Then** cadence options are shown: Off, Daily, Every Other Day, Weekly; plus a time picker

2. **Given** I set cadence to Daily at 7:00 AM and save, **When** I view Settings later, **Then** it shows "Next scheduled run: tomorrow at 7:00 AM"

3. **Given** the Daemon Mode toggle, **When** I view it, **Then** it shows current status (On/Off) and a description of what it does

4. **Given** a missed scheduled run, **When** I open the app after the missed time, **Then** a banner shows: "Missed run at [time] -- retrying now" and a retry Run appears in the live log

## Tasks / Subtasks

- [ ] Implement schedule settings endpoints in `app/api/settings.py` (AC: 1, 2)
  - [ ] `GET /api/settings/schedule` → `{"data": {"cadence": "daily"|"every_other_day"|"weekly"|"off", "time": "07:00", "next_run": "ISO8601"|null, "daemon_mode": false}}`
  - [ ] `PUT /api/settings/schedule` → accepts cadence, time, daemon_mode; persists to `data/settings.json`; updates APScheduler job (from Story 9.1)

- [ ] Implement "next run" calculation (AC: 2)
  - [ ] After PUT: calculate next run datetime from cadence + time
  - [ ] Return in response and show in GET

- [ ] Add Settings -- Schedule UI to `app/templates/settings.html` (AC: 1–3)
  - [ ] Cadence: radio buttons (Off / Daily / Every Other Day / Weekly)
  - [ ] Time picker: `<input type="time">` (HTML5 time input)
  - [ ] "Next scheduled run" display updated via HTMX after save
  - [ ] Daemon mode: toggle switch with description: "Run briefings automatically even when the browser is closed"
  - [ ] Save button: HTMX PUT

- [ ] Implement missed run banner in dashboard (AC: 4)
  - [ ] On page load: `GET /api/briefings/missed` → returns `{"missed_at": "ISO8601"|null}`
  - [ ] If missed run detected: show banner "Missed run at {time} — retrying now" and start retry run automatically
  - [ ] Missed run detection logic lives in `core/scheduler.py` or orchestrator (deferred to Story 9.3 for full implementation; this story implements the UI display only)

- [ ] Write tests in `tests/api/test_settings.py` (AC: 1, 2)
  - [ ] Test GET returns cadence, time, next_run
  - [ ] Test PUT validates cadence values
  - [ ] Test next_run calculated correctly for "daily" cadence

## Dev Notes

### APScheduler update

`PUT /api/settings/schedule` must update the APScheduler job immediately — not just persist to settings file. Import the scheduler from `core/scheduler.py` and call `scheduler.reschedule_job(...)` or `scheduler.add_job(...)`. APScheduler docs cover this pattern.

### Daemon mode toggle

The toggle in Settings calls `PUT /api/settings/schedule` with `daemon_mode: true/false`. The actual daemon process spawn/kill happens in Story 9.2. In this story, the toggle just persists the setting and shows current status.

### Missed run banner (AC: 4)

The missed run detection is implemented in Story 9.3. In this story: add the banner UI slot to `dashboard.html` and the API endpoint stub. The full logic (detect and auto-retry) is Story 9.3's responsibility.

### References

- [Source: docs/ARCHITECTURE.md § "Infrastructure & Deployment — Daemon mode"] — PID file + detached subprocess
- [Source: docs/epics-stories.md § "Story 8.7"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
