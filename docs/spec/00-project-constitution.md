# Project Constitution

Use this file to preserve project intent across agents, sessions, rebuilds, and refactors.

## Project identity

- Project name: Briefing
- Product type: Local-first web app + background pipeline + MCP server
- Target users: Builders and PMs (single-user, technical)
- Primary problem: Too many newsletters; need cross-source synthesis into one daily briefing
- Primary value proposition: Local, self-hosted, story-centric briefing (markdown + optional audio) with dedup across sources
- Current stage: MVP

## Operating mode

- Spec mode: standard
- Required requirement categories:
  - Functional: yes
  - Non-functional: yes
  - UX/design: yes
  - Architecture: yes
  - Data: yes
  - Security/privacy: yes
  - Operations: yes
- Default priority scale: P0 | P1 | P2 | Won't have

## Technical defaults

- Frontend: Server-rendered Jinja2 templates + HTMX
- Backend: FastAPI (async)
- Database: SQLite via SQLAlchemy (async) + aiosqlite
- Authentication: None (localhost-only), OAuth2 for Gmail via Google Auth
- Hosting/deployment: Localhost only
- Testing framework: pytest (+ pytest-asyncio) + httpx AsyncClient
- Observability: Python logging + structured JSON log + SSE live log stream
- Package manager: uv
- Style system: Pico.css (CDN)

## Build target

> **Agent-completed during the Superpowers design phase.** The agent derives this from `docs/ARCHITECTURE.md` and `docs/PRD.md` and presents it for PM approval before writing any code. Do not proceed to implementation until this section is filled in and approved.

| Field | Value |
|---|---|
| **Deliverable type** | Local-first web app + pipeline runner + MCP (stdio) server |
| **Primary language(s)** | Python 3.11+ |
| **Runtime environment** | Local machine; browser UI at `http://127.0.0.1:8000` |
| **Entry point** | Web UI: `uvicorn app.main:app --host 127.0.0.1 --port 8000` (from `briefing/`); MCP: `uv run python -m app.mcp_server` |
| **Distribution method** | GitHub repository (clone + run locally) |
| **Install steps for a new user** | Install Python 3.11+ + `uv`; `uv sync` (or `uv add ...` per Story 1.1); run `briefing.bat`/`briefing.sh` |

**Approved for build:** [x] Yes — user approved build execution (2026-06-26)

## Product boundaries

### Goals

- `GOAL-001`:

### Non-goals

- `NG-001`:

## Global quality bar

- Performance:
- Accessibility:
- Security:
- Reliability:
- Maintainability:
- Documentation:

## Agent constraints

- Agents must update specs before code.
- Agents must cite requirement IDs in tasks and implementation summaries.
- Agents must preserve existing accepted behavior unless a change request says otherwise.
- Agents must record open questions instead of guessing when the decision changes product behavior.

