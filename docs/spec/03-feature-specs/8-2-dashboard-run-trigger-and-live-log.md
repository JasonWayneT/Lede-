# Story 8.2: Dashboard -- Run Trigger and Live Pipeline Log

Status: ready-for-dev

## Story

As a user,
I want to click a button to start a briefing run and watch real-time progress in my browser,
so that I know exactly what the pipeline is doing and can spot any issues immediately.

## Acceptance Criteria

1. **Given** the dashboard page loaded, **When** I view it, **Then** a "Run Briefing" button is visible and enabled

2. **Given** I click "Run Briefing", **When** the button is clicked, **Then** a `POST /api/briefings` request is sent, a `run_id` is returned, the button becomes disabled, and the live log panel appears

3. **Given** the live log panel active, **When** the pipeline progresses, **Then** each stage (ingest, extract, embed, cluster, select, frame, draft, tts_prep, assemble, qa_gate) appears in the log as it starts and completes via SSE

4. **Given** any stage error occurring, **When** the error event arrives, **Then** the error appears inline in the log with a plain-English description — the user does not need to check a terminal

5. **Given** the Run completing, **When** the `complete` event arrives, **Then** the new briefing entry appears in the history list without a page refresh and the "Run Briefing" button re-enables

6. **Given** a Run already in progress, **When** I view the dashboard, **Then** the "Run Briefing" button is disabled and the live log shows current progress

## Tasks / Subtasks

- [ ] Implement `POST /api/briefings` in `app/api/briefings.py` (AC: 2)
  - [ ] Accept optional `depth: str = "standard"` in request body
  - [ ] Call `await orchestrator.start_run(config)` as a `BackgroundTasks` task
  - [ ] Return `{"run_id": N, "status": "pending"}`
  - [ ] If a Run is already active (status = "running"), return 409 with message "A run is already in progress"

- [ ] Implement `app/templates/dashboard.html` (AC: 1–6)
  - [ ] "Run Briefing" button: `hx-post="/api/briefings"`, `hx-target="#log-panel"`, `hx-swap="innerHTML"`, disabled when run active
  - [ ] Live log panel `<div id="log-panel">`: initially hidden, shown after run starts
  - [ ] On success response from POST: use HTMX to connect to SSE: `<div hx-ext="sse" sse-connect="/api/stream/{run_id}" sse-swap="log">`
  - [ ] Stage log entries appended as they arrive
  - [ ] Error entries highlighted in red
  - [ ] On `complete` SSE event: re-enable button, trigger history list refresh via HTMX `hx-get="/history-partial"`

- [ ] Implement HTMX SSE connection (AC: 3–5)
  - [ ] Use `htmx.ext.sse` extension for SSE connection (included via CDN or separate script tag)
  - [ ] Each log event renders as `<div class="log-entry {level}">[{ts}] {stage}: {message}</div>`
  - [ ] Error events render with `class="log-entry error"`
  - [ ] Complete event: fire HTMX request to refresh history partial

- [ ] Write tests in `tests/api/test_briefings.py` (AC: 2)
  - [ ] Test `POST /api/briefings` returns `{"run_id": N, "status": "pending"}`
  - [ ] Test concurrent POST returns 409

## Dev Notes

### HTMX SSE extension

HTMX 2.x has SSE support via `htmx-ext-sse`. Add to base.html:
```html
<script src="https://unpkg.com/htmx-ext-sse@2.2.2/sse.js"></script>
```

Pattern for SSE in template:
```html
<div hx-ext="sse" sse-connect="/api/stream/{{run_id}}" sse-swap="message" hx-swap="beforeend">
```

### Active run detection

Check DB for a Run with `status = "running"` before creating a new one. Return 409 if found. The dashboard JS (minimal, via HTMX) should check this on page load to disable the button appropriately.

### Stage log format

```
[14:30:01] ingest: Fetched 23 unprocessed emails
[14:30:03] extract: Extracted text from 22 emails (1 skipped)
[14:30:08] embed: Generated 22 embeddings
```

Each line is a separate SSE event → separate `<div>` appended to the log panel.

### References

- [Source: docs/ARCHITECTURE.md § "Frontend Architecture"] — HTMX, Jinja2, SSE pattern
- [Source: docs/ARCHITECTURE.md § "API & Communication — REST conventions"] — `POST /api/briefings`
- [Source: docs/epics-stories.md § "Story 8.2"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
