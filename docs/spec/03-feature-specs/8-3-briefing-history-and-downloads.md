# Story 8.3: Briefing History List and Download Endpoints

Status: implemented (renamed — see note)

> **2026-07-06 note (audit pass, doc drift D1):** this spec was written against a template named
> `history.html`; the actual page is `app/templates/archive.html`, with `/history` redirecting to
> `/archive` for backward compatibility (`main.py`). Cosmetic rename only — behavior matches this
> spec's ACs. The hold-state "Needs Review"/Retry indicator (`BUG-006`) actually lives on the
> dashboard, not this page — see `9-3-missed-run-detection.md`/`BUG-006`.

## Story

As a user,
I want to see a list of all my past briefings with download options,
so that I can access any previous briefing whenever I want.

## Acceptance Criteria

1. **Given** past completed Runs in the database, **When** I view the history page, **Then** each entry shows: date, story count, section breakdown, and status

2. **Given** a history entry, **When** I view it, **Then** it has separate download buttons for the markdown file and audio file

3. **Given** I click the markdown download button, **When** the request completes, **Then** the `briefing.md` file downloads with a filename matching the briefing date

4. **Given** a Run where audio generation failed, **When** I view its history entry, **Then** the audio download button is absent or disabled with a tooltip "Audio not available for this run"

5. **Given** the history list, **When** rendered, **Then** entries are sorted newest-first

6. **Given** a Run in Hold state, **When** it appears in history, **Then** it shows a distinct "Needs Review" indicator and a "Retry" button

## Tasks / Subtasks

- [ ] Implement `GET /api/briefings` in `app/api/briefings.py` (AC: 1, 5)
  - [ ] Query `Run` table joined with `BriefingOutput`; order by `created_at DESC`
  - [ ] Return `{"data": [{"run_id": N, "date": "ISO8601", "status": "...", "story_count": N, "section_breakdown": {...}, "markdown_path": "...", "audio_path": "..."|null}, ...]}`
  - [ ] `story_count` and `section_breakdown` read from `Run.section_config` JSON field (populated by orchestrator at run start)

- [ ] Implement download endpoints in `app/api/downloads.py` (AC: 3, 4)
  - [ ] `GET /api/briefings/{id}/download/markdown` → `FileResponse(path, filename=f"briefing-{date}.md", media_type="text/markdown")`
  - [ ] `GET /api/briefings/{id}/download/audio` → `FileResponse(path, filename=f"briefing-{date}.mp3", media_type="audio/mpeg")`
  - [ ] If file not found: 404 with error envelope
  - [ ] If `audio_path` is null: 404 with `{"error": "Audio not available for this run", "code": "NOT_FOUND"}`

- [ ] Implement `app/templates/history.html` (AC: 1–6)
  - [ ] Extends `base.html`
  - [ ] Jinja2 loop over briefings list
  - [ ] Each card: date, status badge, story count, section breakdown, download buttons
  - [ ] Status badges: "Complete" (green), "Hold / Needs Review" (red), "Running" (blue), "No New Emails" (gray)
  - [ ] Audio download button: disabled + tooltip when `audio_path` is null
  - [ ] "Retry" button for Hold runs: `hx-post="/api/briefings/{run_id}/retry"`

- [ ] Write tests in `tests/api/test_briefings.py` and `test_downloads.py` (AC: 1, 3, 4)
  - [ ] Test GET /api/briefings returns list sorted newest-first
  - [ ] Test download markdown returns file with correct filename
  - [ ] Test download audio when audio_path null returns 404

## Dev Notes

### section_breakdown storage

The orchestrator stores `section_breakdown` in `Run.section_config` as JSON at the end of the pipeline. Format: `{"AI": 3, "Technology": 2, "Other": 1}`. The history API returns this field directly.

### FileResponse

FastAPI's `FileResponse` handles Content-Disposition header for file download:
```python
from fastapi.responses import FileResponse
FileResponse(path=str(markdown_path), filename=f"briefing-{date_str}.md")
```

### History page loading

The history page at `GET /history` renders a Jinja2 template with briefings data from the DB. Alternatively, the page renders empty and HTMX loads the list via `GET /api/briefings` on page load. Either approach is fine.

### Retry button

The "Retry" button on a Hold run calls `POST /api/briefings/{run_id}/retry` — implemented in Story 7.4.

### References

- [Source: docs/ARCHITECTURE.md § "API & Communication — REST conventions"] — `/api/briefings/{id}/download/{type}`
- [Source: docs/ARCHITECTURE.md § "Format Patterns — API Success Response"] — `{"data": {...}}`
- [Source: docs/epics-stories.md § "Story 8.3"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
