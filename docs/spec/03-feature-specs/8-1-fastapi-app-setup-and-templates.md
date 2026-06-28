# Story 8.1: FastAPI App Setup and Base Templates

Status: ready-for-dev

## Story

As a developer,
I want the FastAPI app initialized with all routers registered and Jinja2 base templates rendering with Pico.css,
so that all UI stories have a working app shell to build on.

## Acceptance Criteria

1. **Given** running `uvicorn app.main:app --host 127.0.0.1 --port 8000`, **When** I open http://localhost:8000, **Then** the dashboard page renders with no 500 errors

2. **Given** the `base.html` template, **When** rendered, **Then** it includes Pico.css from CDN, dark mode (`data-theme="dark"`), and HTMX from CDN

3. **Given** all router modules (briefings, downloads, settings, stream), **When** the app starts, **Then** they are registered and their routes appear in FastAPI auto-docs at `/docs`

4. **Given** the FastAPI lifespan event, **When** the app starts, **Then** the database is initialized before any request is served

5. **Given** any unhandled `StageError` reaching the app level, **When** the exception handler fires, **Then** a JSON error response is returned: `{"error": "...", "code": "...", "retryable": bool}`

## Tasks / Subtasks

- [ ] Implement `app/main.py` (AC: 1, 3–5)
  - [ ] Create `FastAPI` app with `lifespan` context manager
  - [ ] `await init_db()` in lifespan startup
  - [ ] Register routers: `app.include_router(briefings.router, prefix="/api")`, same for downloads, settings, stream
  - [ ] Register Jinja2 templates: `templates = Jinja2Templates(directory="app/templates")`
  - [ ] Add `@app.exception_handler(StageError)` returning `JSONResponse(status_code=500, content={...})`
  - [ ] Mount static files if needed for audio playback
  - [ ] Root route `GET /` → render `dashboard.html`

- [ ] Implement `app/templates/base.html` (AC: 2)
  - [ ] `<!DOCTYPE html><html data-theme="dark" lang="en">`
  - [ ] `<head>`: Pico.css CDN link, HTMX CDN script, `{% block head %}{% endblock %}`
  - [ ] `<body>`: nav bar with links (Dashboard, History, Settings), `{% block content %}{% endblock %}`
  - [ ] Pico.css CDN: `https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css`
  - [ ] HTMX CDN: `https://unpkg.com/htmx.org@2.0.4`

- [ ] Implement stub templates (AC: 1)
  - [ ] `dashboard.html`: extends base, shows `<h1>Briefing</h1>` + placeholder "Run Briefing" section
  - [ ] `history.html`: extends base, shows `<h1>History</h1>` placeholder
  - [ ] `settings.html`: extends base, shows `<h1>Settings</h1>` placeholder

- [ ] Write tests in `tests/api/conftest.py` and `tests/api/test_briefings.py` (AC: 1, 3–5)
  - [ ] `async_client` fixture: `AsyncClient(app=app, base_url="http://test")`
  - [ ] Test `GET /` returns 200
  - [ ] Test `GET /docs` returns 200 (routes registered)
  - [ ] Test `StageError` handler returns JSON 500

## Dev Notes

### Jinja2 setup

```python
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
```

`request` must be passed in the context for Jinja2 templates to work with FastAPI.

### Pico.css classless mode

Pico v2 works classless — HTML semantic elements (`<nav>`, `<main>`, `<article>`, `<button>`) are styled automatically without adding CSS classes. Use native HTML elements.

### HTMX version

Use HTMX 2.0.4 (latest stable as of mid-2025). Pin the version in the CDN URL to avoid unexpected breaking changes.

### Router prefix

All API routes use `/api` prefix. Page routes (HTML templates) have no prefix: `GET /` (dashboard), `GET /history`, `GET /settings`.

### References

- [Source: docs/ARCHITECTURE.md § "Frontend Architecture"] — Pico.css classless, dark mode, HTMX + Jinja2
- [Source: docs/ARCHITECTURE.md § "API & Communication — REST conventions"] — `/api/` prefix
- [Source: docs/epics-stories.md § "Story 8.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
