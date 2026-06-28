# Story 9.2: Daemon Mode -- Background Process

Status: ready-for-dev

## Story

As a user who wants briefings even when the browser is closed,
I want to enable Daemon Mode so the scheduler runs as a background service,
so that my morning briefing is ready even if I have not opened the app.

## Acceptance Criteria

1. **Given** I enable Daemon Mode in Settings and save, **When** the setting is saved, **Then** a detached background subprocess is spawned and a PID file is written to `data/briefing.pid`

2. **Given** the daemon process running and the app's browser UI is closed, **When** the scheduled time arrives, **Then** the daemon fires the Run and completes it

3. **Given** the daemon process running, **When** I open the app's browser UI, **Then** the UI reads the PID file, confirms the daemon is alive, and shows "Daemon Mode: Running"

4. **Given** I disable Daemon Mode and save, **When** the save completes, **Then** the daemon process is terminated, the PID file is deleted, and Settings shows "Daemon Mode: Off"

5. **Given** the PID file existing but the process no longer running, **When** the app starts, **Then** it detects the stale PID, removes the file, and shows "Daemon Mode: Off (process not found)"

## Tasks / Subtasks

- [ ] Implement daemon spawn/kill in `app/core/scheduler.py` (AC: 1, 4, 5)
  - [ ] `def start_daemon(config: AppConfig) -> None`: spawn `subprocess.Popen(["uv", "run", "python", "-m", "app.daemon_runner"], detach=True)`; write PID to `data/briefing.pid`
  - [ ] `def stop_daemon(config: AppConfig) -> None`: read PID file; `os.kill(pid, signal.SIGTERM)`; delete PID file
  - [ ] `def check_daemon_alive() -> bool`: read PID file; `os.kill(pid, 0)` (signal 0 = existence check); return False if PID file missing or process dead; clean up stale PID file if dead

- [ ] Create `app/daemon_runner.py` — lightweight daemon entry point (AC: 2)
  - [ ] Separate from `main.py` and `mcp_server.py`
  - [ ] Initializes `AsyncIOScheduler` + DB (no web server)
  - [ ] Loads schedule settings from `data/settings.json`
  - [ ] Runs event loop indefinitely: `asyncio.run(daemon_main())`

- [ ] Integrate daemon status into settings GET (AC: 3, 5)
  - [ ] `GET /api/settings/schedule` includes `"daemon_alive": true|false`
  - [ ] On app startup (lifespan): call `check_daemon_alive()` — clean up stale PID file if needed

- [ ] Expose daemon start/stop via settings PUT (AC: 1, 4)
  - [ ] `PUT /api/settings/schedule` with `daemon_mode: true` → call `start_daemon(config)` after persisting
  - [ ] `PUT /api/settings/schedule` with `daemon_mode: false` → call `stop_daemon(config)`

- [ ] Write tests in `tests/api/test_settings.py` (AC: 5)
  - [ ] Mock PID file with non-existent PID; test `check_daemon_alive()` returns False and cleans file

## Dev Notes

### Detached subprocess (cross-platform)

```python
import subprocess, sys, os

kwargs = {"close_fds": True}
if sys.platform == "win32":
    kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
else:
    kwargs["start_new_session"] = True

proc = subprocess.Popen(["uv", "run", "python", "-m", "app.daemon_runner"], **kwargs)
with open(data_dir / "briefing.pid", "w") as f:
    f.write(str(proc.pid))
```

### PID liveness check

`os.kill(pid, 0)` raises `ProcessLookupError` if the PID doesn't exist. This is the standard cross-platform way to check if a process is alive. On Windows, use `psutil.pid_exists()` as a fallback if `os.kill` doesn't work reliably.

### daemon_runner.py is NOT an MCP server

`daemon_runner.py` is a third entry point (after `main.py` and `mcp_server.py`). It runs the scheduler only — no web server, no MCP tools. It follows the same entry point isolation rule.

### References

- [Source: docs/ARCHITECTURE.md § "Infrastructure & Deployment — Daemon mode"] — PID file + detached subprocess
- [Source: docs/epics-stories.md § "Story 9.2"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
