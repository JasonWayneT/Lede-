# Story 12.2: API Route Tests

Status: ready-for-dev

## Story

As a developer,
I want tests for all FastAPI routes covering happy path and error cases,
so that any regression in the API layer is caught before it reaches users.

## Acceptance Criteria

1. **Given** `POST /api/briefings` called with a valid request, **When** the test runs, **Then** a 200 response is returned with `{"run_id": N, "status": "pending"}`

2. **Given** `GET /api/briefings` with completed Runs in the test DB, **When** the test runs, **Then** a 200 response is returned with a list of briefing entries sorted newest-first

3. **Given** `GET /api/briefings/{id}/download/markdown` for a completed Run, **When** the test runs, **Then** the markdown file is returned with `Content-Type: text/markdown`

4. **Given** `GET /api/briefings/{id}/download/markdown` for a non-existent Run, **When** the test runs, **Then** a 404 response is returned with the defined error envelope

5. **Given** `PUT /api/settings/{section}` with valid data, **When** the test runs, **Then** a 200 response confirms the settings are saved

## Tasks / Subtasks

- [ ] Write `tests/api/test_briefings.py` (AC: 1, 2)
  - [ ] Test `POST /api/briefings` → 200, run_id and status in response
  - [ ] Test `POST /api/briefings` when run already in progress → 409
  - [ ] Test `GET /api/briefings` with no runs → `{"data": []}`
  - [ ] Test `GET /api/briefings` with 3 runs → newest first
  - [ ] Mock `orchestrator.start_run` to return a fixed run_id

- [ ] Write `tests/api/test_downloads.py` (AC: 3, 4)
  - [ ] Create test markdown file in `tmp_path`; create `BriefingOutput` record pointing to it
  - [ ] Test download returns file with correct Content-Type
  - [ ] Test 404 for non-existent run_id
  - [ ] Test 404 for run with null audio_path

- [ ] Write `tests/api/test_settings.py` (AC: 5)
  - [ ] Test `PUT /api/settings/depth` with valid depth → 200
  - [ ] Test `PUT /api/settings/depth` with invalid depth → 422 (FastAPI validation error)
  - [ ] Test `PUT /api/settings/sections` with empty list → 400
  - [ ] Test `GET /api/settings/status` returns all required fields
  - [ ] Test `PUT /api/settings/llm` stores key via credentials (mocked)

- [ ] Write `tests/api/test_stream.py` (AC: SSE)
  - [ ] Test `GET /api/stream/{run_id}` streams events correctly
  - [ ] Test queue created and cleaned up

## Dev Notes

### Mocking orchestrator in API tests

`POST /api/briefings` adds `orchestrator.start_run` as a BackgroundTask. In tests, mock `orchestrator.start_run` to return immediately:

```python
async def mock_start_run(config): return 42

monkeypatch.setattr("app.pipeline.orchestrator.start_run", mock_start_run)
```

### Test file for download tests

Create a real temp file in `tmp_path`:
```python
briefing_md = tmp_path / "briefings" / "1" / "briefing.md"
briefing_md.parent.mkdir(parents=True)
briefing_md.write_text("# Test Briefing")
```

Then insert a `BriefingOutput` record pointing to it in the test DB.

### Error envelope format

404 response must match: `{"error": "...", "code": "NOT_FOUND"}`. Test with `response.json()["code"] == "NOT_FOUND"`.

### References

- [Source: docs/ARCHITECTURE.md § "Format Patterns — API Error Envelope"] — error response shape
- [Source: docs/ARCHITECTURE.md § "Format Patterns — API Success Response"] — success shape
- [Source: docs/epics-stories.md § "Story 12.2"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
