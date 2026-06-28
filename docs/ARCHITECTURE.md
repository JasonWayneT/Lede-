---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-06-26'
inputDocuments:
  - 'prds/prd-briefing-2026-06-26/prd.md'
  - 'briefs/brief-newsletter-briefing-2026-06-26/brief.md'
  - 'C:/Users/Jason/Downloads/modular-news-production-report.md'
workflowType: 'architecture'
project_name: 'Briefing'
user_name: 'Jason'
date: '2026-06-26'
---

# Architecture Decision Document — Briefing

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

---

## Project Context Analysis

### Requirements Overview

**Functional Requirements (25 FRs across 7 groups):**

- **Gmail Ingest (FR-1–3):** OAuth 2.0 token management, label-based fetch, local Processed Log (atomic write on full run success only)
- **Modular Pipeline (FR-4–8, FR-7a):** 9 bounded stages with structured handoff packets — Extract → Embed → Cluster → Editorial Selection → Story Framing → Script Drafting → TTS Preparation → Assembly → QA Gate. Each stage receives minimum context only; no stage sees full pipeline history.
- **Audio/TTS (FR-9–11):** Two-stage audio production — TTS Script Preparation (spoken optimization) then Kokoro synthesis. Kokoro auto-downloaded during onboarding. Audio failure does not fail the whole Run.
- **QA Gate + Retry (FR-12–13):** Pre-delivery validation, 3-tier structured retry (same-module retry → expanded context retry → Hold state), manual remediation via UI. No silent failures.
- **LLM Provider (FR-14–15):** Ollama local default, BYOK for OpenAI/Anthropic/Gemini, encrypted local storage, runtime-switchable without restart.
- **Onboarding (FR-16–17):** First-run wizard — OAuth required, Kokoro auto-download, API keys/sections/schedule skippable; all revisitable in Settings.
- **Web UI (FR-18–25):** Trigger button, SSE/WebSocket live pipeline log, briefing history with downloads (markdown + audio), Settings (Gmail, sections, depth, LLM provider, schedule + daemon mode).

**Non-Functional Requirements:**

- **Async-first:** Pipeline runs take minutes. Web server must never block on pipeline execution.
- **Streaming:** Live log requires server-sent events (SSE) or WebSocket from worker to browser in real time.
- **Local-first security:** OAuth token and API keys encrypted at rest; never transmitted to any service beyond the configured provider's API.
- **Partial rerun support:** Handoff packet artifacts persisted to disk so failed pipeline stages can restart without replaying the full run.
- **Daemon mode:** Scheduler must be able to fire pipeline runs independently of the web server process (headless background service).
- **Self-contained install:** Dependencies (including Kokoro model weights) auto-downloaded during setup; no manual dependency hunting.

**Scale & Complexity:**

- Primary domain: full-stack local Python application (backend pipeline + web server + background scheduler)
- Complexity level: **Medium** — not trivial (async pipeline, SSE streaming, daemon mode, OAuth, encrypted storage) but well within a single-developer Python project
- Estimated architectural components: 6 (web server, pipeline orchestrator, pipeline worker, scheduler, credential store, data store)

### Technical Constraints & Dependencies

- **Python stack** — all components in Python
- **Google Cloud credentials.json** — prerequisite for OAuth; user provides it; setup script handles token exchange
- **Ollama** — must be running locally for default LLM mode; app detects and warns if unreachable
- **Kokoro** — 82M param model, Apache 2.0, auto-downloaded via HuggingFace on first setup
- **No external database required** — local file storage (JSON/SQLite) sufficient for V1 history, settings, processed log, and handoff artifacts
- **No cloud hosting** — runs entirely on user's machine; localhost only

---

## Starter Template Evaluation

### Primary Technology Domain

Python local application — async web server + modular pipeline worker + background scheduler. No JS framework. Server-rendered UI with HTMX for dynamic behavior and SSE for live log streaming.

### Selected Stack

| Concern | Choice | Rationale |
|---|---|---|
| Web framework | **FastAPI** | Async-native, SSE built-in, thin routers, auto-docs |
| Frontend | **HTMX + Jinja2** | No build step, no SPA complexity — server-rendered HTML with SSE for live log |
| Scheduling | **APScheduler** | No broker required, in-process or subprocess, daemon mode compatible |
| Embeddings | **sentence-transformers** | More stable than Ollama embeddings (known version mismatch issues in Ollama), fully local |
| Vector clustering | **FAISS (faiss-cpu)** | Industry standard for local similarity search; pairs with sentence-transformers |
| Pipeline execution | **asyncio + FastAPI BackgroundTasks** | Pipeline runs as async background task; no broker needed for V1 |
| Local data | **SQLite via SQLAlchemy (async)** | Briefing history needs querying; JSON files insufficient |
| Credential encryption | **keyring** | OS-native keychain (Windows Credential Manager / macOS Keychain / libsecret); no custom key management |
| Package management | **uv** | Fast, lockfile support, modern replacement for pip + venv |

### Project Structure

```
briefing/
├── README.md
├── pyproject.toml
├── .env.example
├── setup.py                  # first-run onboarding script
├── app/
│   ├── main.py               # FastAPI app, router registration
│   ├── core/
│   │   ├── config.py         # settings, env loading
│   │   ├── credentials.py    # keyring wrapper (OAuth token + API keys)
│   │   └── scheduler.py      # APScheduler setup + daemon mode
│   ├── api/
│   │   ├── briefings.py      # trigger, history, download routes
│   │   ├── settings.py       # settings CRUD routes
│   │   └── stream.py         # SSE endpoint for live pipeline log
│   ├── pipeline/
│   │   ├── orchestrator.py   # stage sequencing, handoff packet management
│   │   ├── handoff.py        # handoff packet schema + validation
│   │   └── stages/
│   │       ├── ingest.py
│   │       ├── extract.py
│   │       ├── embed.py
│   │       ├── cluster.py
│   │       ├── select.py
│   │       ├── frame.py
│   │       ├── draft.py
│   │       ├── tts_prep.py
│   │       ├── assemble.py
│   │       └── qa_gate.py
│   ├── services/
│   │   ├── gmail.py          # Gmail API wrapper
│   │   ├── llm.py            # Ollama + BYOK provider abstraction
│   │   ├── tts.py            # Kokoro wrapper
│   │   └── embeddings.py     # sentence-transformers + FAISS
│   ├── db/
│   │   ├── models.py         # SQLAlchemy models (Briefing, Run, ProcessedLog)
│   │   └── database.py       # async SQLite session
│   └── templates/            # Jinja2 HTML templates
│       ├── base.html
│       ├── dashboard.html
│       ├── history.html
│       └── settings.html
├── pipeline_prompts/         # per-module prompt files (modular research doc pattern)
│   ├── style-guide.md
│   ├── handoff-schema.yaml
│   └── stages/
│       ├── select.md
│       ├── frame.md
│       ├── draft.md
│       └── tts_prep.md
├── data/
│   ├── briefings/            # markdown + audio output per run
│   └── artifacts/            # handoff packet artifacts per run (supports partial rerun)
└── tests/
```

### Initialization Command

```bash
uv init briefing && cd briefing
uv add fastapi uvicorn[standard] sqlalchemy aiosqlite \
       google-auth google-auth-oauthlib google-api-python-client \
       sentence-transformers faiss-cpu kokoro \
       apscheduler keyring jinja2 python-multipart \
       httpx openai anthropic google-generativeai
```

**Note:** Project scaffolding using this structure is the first implementation story.

---

### Cross-Cutting Concerns Identified

- **Credential encryption:** Gmail OAuth token and BYOK API keys both need encrypted at-rest storage — centralized in a single credential store component
- **Handoff packet schema:** Shared contract between all 9 pipeline stages; must be defined once and validated at each stage boundary
- **Processed Log atomicity:** Written only after full Run success — partial run failures must not pollute the log
- **Error propagation:** Every stage failure must stream to the live log AND persist to the Run record for the Hold state; two consumers of the same error signal
- **Three runtime modes:** Normal (app open, user-triggered), Scheduled (app open, timer-triggered), Daemon (background service, no browser required) — architecture must cleanly separate these without code duplication

---

## Core Architectural Decisions

### Already Decided (from starter template + PRD)

FastAPI, HTMX + Jinja2, SQLite + SQLAlchemy async, APScheduler, sentence-transformers + FAISS, keyring, Ollama + BYOK, SSE for live log, uv.

### Data Architecture

| Decision | Choice | Rationale |
|---|---|---|
| DB migrations | `Base.metadata.create_all()` on startup — no Alembic | Local app, single user; schema changes ship with version updates |
| Handoff packet format | JSON files on disk: `data/artifacts/{run_id}/stage_N.json` | Enables partial reruns by reading from disk; survives process restarts |
| Processed Log | SQLite table in same DB as `Run` / `Briefing` | Single data store; queryable; atomic within same transaction as Run completion |
| SQLite models | Three tables: `Run` (id, status, created_at, depth, section_config, error), `BriefingOutput` (run_id, markdown_path, audio_path), `ProcessedEmail` (email_id, run_id, processed_at) | Covers history, downloads, and Processed Log in one schema |

### Authentication & Security

| Decision | Choice | Rationale |
|---|---|---|
| keyring namespace | Service: `briefing`; usernames: `gmail_oauth_token`, `openai_key`, `anthropic_key`, `gemini_key` | Predictable, no collisions |
| CSRF | None | Localhost-only, single-user — no cross-origin threat surface |
| OAuth token refresh | Auto-refresh via `google-auth` library on each Gmail API call | Library handles it natively; no custom refresh loop needed |

### API & Communication

| Decision | Choice | Rationale |
|---|---|---|
| Live log transport | **SSE** — `EventSourceResponse` via `sse-starlette` | Unidirectional server→browser, simpler than WebSocket, native FastAPI support |
| REST conventions | `/api/briefings` (POST trigger, GET history), `/api/briefings/{id}/download/{type}`, `/api/settings/{section}` (GET/PUT) | Clean resource-based paths |
| Error envelope | `{"error": "...", "code": "STAGE_FAILED", "stage": "cluster", "retryable": true}` | Consistent shape used by both SSE log events and REST error responses |

### Frontend Architecture

| Decision | Choice | Rationale |
|---|---|---|
| CSS | **Pico.css** (classless, CDN) | No build step, sensible defaults, dark mode built-in, pairs cleanly with HTMX + Jinja2 |
| Jinja2 patterns | Macros for reusable components (status badge, run card); `{% extends "base.html" %}` per page | Standard Jinja2; no extra tooling |
| Theme | Dark mode default (`data-theme="dark"`), user-toggleable in Settings | Appropriate for builder/PM audience |

### Infrastructure & Deployment

| Decision | Choice | Rationale |
|---|---|---|
| Run command | `uvicorn app.main:app --host 127.0.0.1 --port 8000` wrapped in `briefing.sh` / `briefing.bat` | Simple; README covers this; no launcher complexity in V1 |
| Daemon mode | PID file + detached subprocess spawned by `scheduler.py`; UI checks PID liveness | Cross-platform (Windows, Mac, Linux); no OS service dependencies |
| Testing | pytest + httpx AsyncClient for API tests; pytest fixtures with mock handoff packets for pipeline unit tests | Industry standard for FastAPI async testing |
| Logging | Python `logging` → structured JSON log file (`data/briefing.log`) + SSE queue — same log, two consumers via logging handlers | File and live stream share one source of truth |

### MCP Architecture

| Decision | Choice | Rationale |
|---|---|---|
| MCP server transport | **stdio** (subprocess) | Standard for local apps; Claude Desktop and Hermes spawn it as a child process; no port management |
| MCP server entry point | `app/mcp_server.py` — standalone, no FastAPI dependency | Users can run MCP-only without the web UI; shared core handles all logic |
| MCP tools exposed | `trigger_briefing`, `get_run_status`, `list_briefings`, `get_briefing_content` | Covers the full headless workflow |
| MCP sampling as LLM provider | Fourth option in `llm.py`: `mcp_sampling` — routes stage LLM calls to the host via `server.create_message()` | Lets Claude Desktop / Hermes supply the LLM; falls back to Ollama if no sampling context available |
| LLM provider options (updated) | `ollama` (default), `openai`, `anthropic`, `gemini`, `mcp_sampling` | Runtime-switchable; `mcp_sampling` only selectable when running inside MCP server entry point |
| MCP SDK | `mcp` (official Anthropic Python SDK) | Standard; supports both tool serving and sampling requests |
| Shared core rule | `pipeline/`, `services/`, `core/`, `db/` never import from `main.py` or `mcp_server.py` | Both entry points import shared internals; shared internals are entry-point agnostic |

**Updated `uv add` for MCP:**
```bash
uv add mcp
```

**Updated project structure additions:**
```
app/
├── main.py               # FastAPI web UI entry point (unchanged)
├── mcp_server.py         # MCP server entry point (standalone — no FastAPI)
```

**Claude Desktop config (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "briefing": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp_server"],
      "cwd": "/path/to/briefing"
    }
  }
}
```

---

### Deferred Decisions (Post-MVP)

- WebSocket upgrade (if SSE proves insufficient for bidirectional needs)
- Alembic migrations (when schema churn warrants it in V2+)
- Docker / packaged distribution (PyInstaller, etc.) — V2 distribution story
- Orpheus TTS integration (requires GPU; V2 upgrade path)


---

## Implementation Patterns & Consistency Rules

### Critical Conflict Points Identified

**7 areas where AI agents could diverge:**
1. Python naming (snake_case vs. camelCase vs. PascalCase across different elements)
2. API response shapes (error envelope decided; success envelope not previously defined)
3. SQLAlchemy model and column naming
4. Pipeline stage interface (what every stage must accept and return)
5. SSE event payload structure
6. File/directory naming for handoff artifacts and briefing outputs
7. LLM provider routing (stages must never call providers directly)

---

### Naming Patterns

**Python Code Conventions:**

| Element | Convention | Example |
|---|---|---|
| Files/modules | `snake_case.py` | `tts_prep.py`, `qa_gate.py` |
| Classes | `PascalCase` | `BriefingRun`, `HandoffPacket` |
| Functions/methods | `snake_case` | `run_pipeline()`, `get_briefing()` |
| Variables/params | `snake_case` | `run_id`, `email_id`, `audio_path` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`, `DEFAULT_DEPTH` |
| Private helpers | `_snake_case` (single underscore) | `_build_prompt()`, `_write_artifact()` |

**Database Column Naming:**
- All column names: `snake_case`
- Primary keys: `id` (integer autoincrement)
- Foreign keys: `{table_singular}_id` e.g. `run_id`, not `fk_run` or `runId`
- Timestamps: `created_at`, `updated_at`, `processed_at`
- Status field string enum values: `pending`, `running`, `complete`, `failed`, `hold`

**API Endpoint Naming:**
- Resource paths: plural noun, lowercase `/api/briefings`, `/api/settings`
- Path params: `{id}` format `/api/briefings/{id}/download/{type}`
- Query params: `snake_case` e.g. `?depth=standard&section=tech`
- No trailing slashes

**Keyring Naming:**
- Service name: always the string `"briefing"` (no variation)
- Username keys: `gmail_oauth_token`, `openai_key`, `anthropic_key`, `gemini_key` — no additions without updating `app/core/credentials.py`

**MCP Tool Naming:**
- Tool names: `snake_case` — `trigger_briefing`, `get_run_status`, `list_briefings`, `get_briefing_content`
- Tool parameter names: `snake_case` — `run_id`, `content_type`

---

### Structure Patterns

**Pipeline Stage Interface** (all 9 stages must conform):

```python
async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    ...
```

- Stages receive `HandoffPacket` and `AppConfig`; return a `HandoffPacket`
- Stages do NOT import from each other — only from `app/services/` and `app/core/`
- Stages do NOT write to the DB — the orchestrator owns all DB writes
- Stage failures raise `StageError(stage_name, message, retryable=True/False)` — no swallowed exceptions
- Stages do NOT call LLM providers directly — always via `app/services/llm.py`

**Entry Point Isolation Rule:**
- `pipeline/`, `services/`, `core/`, `db/` never import from `main.py` or `mcp_server.py`
- Both entry points import shared internals; shared internals are entry-point agnostic

**Test Organization:**

```
tests/
├── api/          # FastAPI route tests (httpx AsyncClient)
├── pipeline/     # Stage unit tests (mock HandoffPacket fixtures)
├── services/     # Service wrapper tests (llm, gmail, tts, embeddings)
└── mcp/          # MCP tool tests (mcp test client)
```

- No co-located test files (`*.test.py` pattern is NOT used)
- All fixtures in `tests/conftest.py` or `tests/{subdir}/conftest.py`

**Handoff Artifact Files:**
```
data/artifacts/{run_id}/stage_{N:02d}_{stage_name}.json
```
e.g. `data/artifacts/42/stage_03_embed.json`

**Briefing Output Files:**
```
data/briefings/{run_id}/briefing.md
data/briefings/{run_id}/briefing.mp3
```

---

### Format Patterns

**API Success Response:**
```json
{"data": {...}}
```
- All GET responses returning objects or lists wrap in `{"data": ...}`
- POST trigger returns `{"run_id": 42, "status": "pending"}`
- File downloads: raw binary response, no envelope

**API Error Envelope** (confirmed from step 4):
```json
{"error": "...", "code": "STAGE_FAILED", "stage": "cluster", "retryable": true}
```
- `code` values: `STAGE_FAILED`, `AUTH_ERROR`, `PROVIDER_UNAVAILABLE`, `VALIDATION_ERROR`, `NOT_FOUND`
- Always include `retryable` boolean on stage errors
- HTTP status codes: 200 success, 400 validation, 401 auth, 404 not found, 500 stage failure

**SSE Event Payload:**
```json
{"event": "log",      "data": {"level": "info", "stage": "embed", "message": "...", "ts": "ISO8601"}}
{"event": "complete", "data": {"run_id": 42, "audio_path": "...", "markdown_path": "..."}}
{"event": "error",    "data": {"code": "STAGE_FAILED", "stage": "cluster", "message": "...", "retryable": true}}
{"event": "status",   "data": {"run_id": 42, "status": "running", "current_stage": "embed"}}
```
- `event` always one of: `log`, `complete`, `error`, `status`
- `level` values: `info`, `warning`, `error`
- `ts` always ISO 8601 UTC

**MCP Tool Response Format:**
- MCP tools return plain text or JSON string — no custom envelope
- Errors surface as MCP error responses (SDK handles wrapping)

**JSON/Data Formats:**
- All JSON keys: `snake_case` (never camelCase)
- Dates/timestamps: ISO 8601 strings (`"2026-06-26T14:30:00Z"`) — never Unix timestamps
- Booleans: `true`/`false` — never `1`/`0`
- Empty collections: `[]` / `{}` — never `null` for missing lists or dicts

---

### Process Patterns

**LLM Provider Routing:**
- All LLM calls go through `app/services/llm.py` — stages never import `openai`, `anthropic`, `ollama`, or `mcp` directly
- `llm.py` resolves provider at call time from `AppConfig.llm_provider`
- Provider enum: `ollama` | `openai` | `anthropic` | `gemini` | `mcp_sampling`
- `mcp_sampling` falls back to `ollama` if no MCP sampling context is available at call time

**Error Handling:**
- Every pipeline stage wraps its body in `try/except` and raises `StageError` — raw exceptions never reach the orchestrator
- Orchestrator catches `StageError` and triggers 3-tier retry sequence
- Single `@app.exception_handler(StageError)` in `main.py` for REST responses
- User-facing messages: plain English in `message` field; technical detail in logs only

**Logging:**
```python
import logging
logger = logging.getLogger(__name__)  # always module-level, always __name__
```
- Log levels: `DEBUG` packet contents, `INFO` stage transitions, `WARNING` retries, `ERROR` failures
- Structured JSON format: `{"level": "info", "stage": "embed", "run_id": 42, "message": "..."}`
- Never `print()` — always `logger.*`
- Same logger used in both web UI and MCP server entry points

**Retry Pattern** (orchestrator only — never inside stages):
```
Tier 1: same-module retry (max 1 attempt)
Tier 2: expanded context retry (max 1 attempt)
Tier 3: Hold state — Run.status = "hold", stream error event, stop pipeline
```

---

### Enforcement Guidelines

**All AI agents MUST:**
- Use `snake_case` for all Python identifiers except class names (`PascalCase`) and constants (`UPPER_SNAKE_CASE`)
- Route all LLM calls through `app/services/llm.py` — never call providers directly from stages
- Implement `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket` for every pipeline stage
- Raise `StageError` (not generic exceptions) for all stage failures
- Use `logger = logging.getLogger(__name__)` — never `print()`
- Write tests under `tests/{api,pipeline,services,mcp}/` — never co-located with source
- Use the exact keyring service name `"briefing"` and exact key names defined in `credentials.py`
- Wrap REST responses in the defined success/error envelope formats
- Keep `main.py` and `mcp_server.py` import-free from each other — shared core only
- Name MCP tools in `snake_case` matching the four defined tool names exactly

**Pattern Enforcement:**
- PR checklist: "Does this stage implement the `run(packet, config)` interface?"
- PR checklist: "Are all LLM calls routed through `llm.py`?"
- PR checklist: "Are new keyring keys registered in `credentials.py`?"

---

### Pattern Examples

**Good — stage implementation:**
```python
# app/pipeline/stages/embed.py
async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    try:
        result = await services.embeddings.embed(packet.extracted_texts, config)
        return packet.with_embeddings(result)
    except Exception as e:
        raise StageError("embed", str(e), retryable=True)
```

**Anti-pattern — stage calling provider directly:**
```python
# WRONG
import openai
client = openai.AsyncOpenAI(api_key=...)  # use llm.py instead
```

**Good — MCP tool implementation:**
```python
# app/mcp_server.py
@server.call_tool()
async def trigger_briefing(arguments: dict) -> list[TextContent]:
    run_id = await orchestrator.start_run(arguments.get("depth", "standard"))
    return [TextContent(type="text", text=f"Run {run_id} started")]
```

**Anti-pattern — entry point coupling:**
```python
# WRONG
from app.main import app  # shared internals must not import entry points
```


---

## Project Structure & Boundaries

### Complete Project Directory Structure

```
briefing/
├── README.md
├── pyproject.toml                    # uv-managed deps, project metadata
├── .env.example                      # template: BRIEFING_DATA_DIR, LOG_LEVEL
├── .gitignore
├── setup.py                          # first-run onboarding wizard (OAuth + Kokoro download)
├── briefing.sh                       # launch web UI (Unix)
├── briefing.bat                      # launch web UI (Windows)
│
├── app/
│   ├── main.py                       # FastAPI entry point — router registration, lifespan
│   ├── mcp_server.py                 # MCP server entry point — standalone, no FastAPI
│   │
│   ├── core/
│   │   ├── config.py                 # AppConfig (settings, env loading, llm_provider enum)
│   │   ├── credentials.py            # keyring wrapper — gmail_oauth_token, *_key constants
│   │   ├── scheduler.py              # APScheduler setup + daemon mode + PID file
│   │   └── errors.py                 # StageError, error code constants
│   │
│   ├── api/
│   │   ├── briefings.py              # POST /api/briefings, GET /api/briefings, GET /api/briefings/{id}
│   │   ├── downloads.py              # GET /api/briefings/{id}/download/{type}
│   │   ├── settings.py               # GET/PUT /api/settings/{section}
│   │   └── stream.py                 # GET /api/stream/{run_id} — SSE endpoint
│   │
│   ├── pipeline/
│   │   ├── orchestrator.py           # stage sequencing, retry logic, DB writes, SSE event emit
│   │   ├── handoff.py                # HandoffPacket schema + disk read/write helpers
│   │   └── stages/
│   │       ├── ingest.py             # FR-1-3: Gmail fetch, label filter, dedup check
│   │       ├── extract.py            # FR-4: text extraction + normalization
│   │       ├── embed.py              # FR-5: sentence-transformers embeddings
│   │       ├── cluster.py            # FR-6: FAISS clustering
│   │       ├── select.py             # FR-7: editorial selection (LLM)
│   │       ├── frame.py              # FR-7a: story framing (LLM)
│   │       ├── draft.py              # FR-8: script drafting (LLM)
│   │       ├── tts_prep.py           # FR-9: spoken-form optimization (LLM)
│   │       ├── assemble.py           # FR-10: Kokoro TTS synthesis + file write
│   │       └── qa_gate.py            # FR-12: pre-delivery validation
│   │
│   ├── services/
│   │   ├── gmail.py                  # Gmail API wrapper (OAuth, label fetch, message parse)
│   │   ├── llm.py                    # Provider router: ollama|openai|anthropic|gemini|mcp_sampling
│   │   ├── tts.py                    # Kokoro wrapper (model load, synthesize, write mp3)
│   │   └── embeddings.py             # sentence-transformers + FAISS index helpers
│   │
│   ├── db/
│   │   ├── database.py               # async SQLite engine, session factory, create_all on startup
│   │   └── models.py                 # Run, BriefingOutput, ProcessedEmail SQLAlchemy models
│   │
│   └── templates/                    # Jinja2 HTML templates
│       ├── base.html                 # shared layout, Pico.css CDN, dark mode default
│       ├── dashboard.html            # trigger button, live SSE log panel
│       ├── history.html              # briefing history, download links
│       └── settings.html            # Gmail, sections, depth, LLM provider, schedule
│
├── pipeline_prompts/                 # prompt files — versioned alongside code
│   ├── style-guide.md                # tone, format, audience rules for all LLM stages
│   ├── handoff-schema.yaml           # canonical HandoffPacket field definitions
│   └── stages/
│       ├── select.md
│       ├── frame.md
│       ├── draft.md
│       └── tts_prep.md
│
├── data/                             # runtime data — gitignored
│   ├── briefings/                    # {run_id}/briefing.md + {run_id}/briefing.mp3
│   ├── artifacts/                    # {run_id}/stage_{N:02d}_{stage_name}.json
│   ├── briefing.db                   # SQLite database
│   └── briefing.log                  # structured JSON log
│
└── tests/
    ├── conftest.py                   # shared fixtures: test DB, AppConfig override
    ├── api/
    │   ├── conftest.py               # httpx AsyncClient fixture
    │   ├── test_briefings.py
    │   ├── test_downloads.py
    │   ├── test_settings.py
    │   └── test_stream.py
    ├── pipeline/
    │   ├── conftest.py               # mock HandoffPacket fixtures per stage
    │   ├── test_orchestrator.py
    │   ├── test_handoff.py
    │   └── stages/
    │       ├── test_ingest.py
    │       ├── test_extract.py
    │       ├── test_embed.py
    │       ├── test_cluster.py
    │       ├── test_select.py
    │       ├── test_frame.py
    │       ├── test_draft.py
    │       ├── test_tts_prep.py
    │       ├── test_assemble.py
    │       └── test_qa_gate.py
    ├── services/
    │   ├── test_llm.py               # provider routing, mcp_sampling fallback
    │   ├── test_gmail.py
    │   ├── test_tts.py
    │   └── test_embeddings.py
    └── mcp/
        ├── conftest.py               # mcp test client fixture
        ├── test_trigger_briefing.py
        ├── test_get_run_status.py
        ├── test_list_briefings.py
        └── test_get_briefing_content.py
```

---

### Architectural Boundaries

**Layer Ownership:**

| Layer | Owns | Does NOT own |
|---|---|---|
| `api/` routes | HTTP request/response, input validation, calling orchestrator | Pipeline logic, DB queries, LLM calls |
| `pipeline/orchestrator.py` | Stage sequencing, retry, DB writes, SSE event emit | HTTP concerns, credential management |
| `pipeline/stages/*` | Single-stage transformation, StageError raising | DB writes, retry logic, provider selection |
| `services/llm.py` | Provider routing, mcp_sampling fallback | Stage logic, prompt construction |
| `mcp_server.py` | MCP tool definitions, tool parameter parsing | Pipeline logic (delegates to orchestrator) |

**Data Boundaries:**

| Data type | Owner | Location |
|---|---|---|
| Run state + history | `db/models.py` via orchestrator | `data/briefing.db` |
| Handoff packets | `pipeline/handoff.py` | `data/artifacts/{run_id}/` |
| Briefing outputs | `pipeline/stages/assemble.py` | `data/briefings/{run_id}/` |
| Credentials | `core/credentials.py` via keyring | OS keychain |
| Prompts | stages read from `pipeline_prompts/stages/` | `pipeline_prompts/stages/` |
| Structured log | handlers registered in entry points only | `data/briefing.log` |

**Entry Point Isolation:**

```
main.py          imports  api/, core/, db/        (never pipeline directly)
mcp_server.py    imports  pipeline/, core/, db/   (never api/ or main.py)
api/briefings.py imports  pipeline/orchestrator   (never stages directly)
stages/*         imports  services/, core/         (never each other)
```

---

### Requirements to Structure Mapping

| FR Group | Files |
|---|---|
| Gmail Ingest (FR-1-3) | `services/gmail.py`, `pipeline/stages/ingest.py`, `db/models.py` (ProcessedEmail) |
| Modular Pipeline (FR-4-8, FR-7a) | `pipeline/orchestrator.py`, `pipeline/handoff.py`, `pipeline/stages/*` |
| Audio/TTS (FR-9-11) | `services/tts.py`, `pipeline/stages/tts_prep.py`, `pipeline/stages/assemble.py` |
| QA Gate + Retry (FR-12-13) | `pipeline/stages/qa_gate.py`, `pipeline/orchestrator.py`, `core/errors.py` |
| LLM Provider (FR-14-15) | `services/llm.py`, `core/config.py`, `core/credentials.py` |
| Onboarding (FR-16-17) | `setup.py`, `core/credentials.py`, `services/tts.py` (Kokoro download) |
| Web UI (FR-18-25) | `app/main.py`, `api/*`, `app/templates/*`, `api/stream.py` |
| MCP | `app/mcp_server.py`, `services/llm.py` (mcp_sampling provider) |

**Cross-Cutting Concerns:**

| Concern | Location |
|---|---|
| Error types | `core/errors.py` — imported by stages, orchestrator, API handlers |
| AppConfig | `core/config.py` — passed into every stage and service; env never read directly in stages |
| Logging | `logging.getLogger(__name__)` in every module; handlers registered in entry points only |
| Credential access | `core/credentials.py` only — no other module reads keyring |
| Scheduler + daemon | `core/scheduler.py` — PID file at `data/briefing.pid` |

---

### Integration Points

**Internal Communication:**
- `main.py` -> `api/` routers -> `pipeline/orchestrator.py` -> stages -> `services/`
- `mcp_server.py` -> `pipeline/orchestrator.py` (same path from orchestrator down)
- Orchestrator -> SSE queue -> `api/stream.py` -> browser (shared async queue object)

**External Integrations:**

| Integration | Service file | Auth |
|---|---|---|
| Gmail API | `services/gmail.py` | OAuth token via `core/credentials.py` |
| Ollama | `services/llm.py` | None (localhost HTTP) |
| OpenAI / Anthropic / Gemini | `services/llm.py` | BYOK via `core/credentials.py` |
| MCP host (sampling) | `services/llm.py` | MCP session context (no key needed) |
| Kokoro TTS | `services/tts.py` | None (local model) |
| HuggingFace (setup only) | `setup.py` | None (public model download) |

**Data Flow (single run):**

```
Gmail API -> ingest -> extract -> embed -> cluster -> select -> frame -> draft -> tts_prep -> assemble -> qa_gate
                                                                                       |
                                                              data/artifacts/{run_id}/stage_NN_name.json  (each stage)
                                                              data/briefings/{run_id}/briefing.md + .mp3  (assemble)
                                                              briefing.db Run + BriefingOutput            (orchestrator on completion)
```


---

## Architecture Validation Results

### Coherence Validation

**Decision Compatibility — PASS**

All technology choices are compatible:
- FastAPI + asyncio + SQLAlchemy async + aiosqlite — all async-native, no blocking conflicts
- APScheduler works in-process with FastAPI lifespan; daemon mode via detached subprocess is independent
- sentence-transformers + FAISS run synchronously in worker context — correct, embedding/clustering do not need async
- `mcp` SDK supports both stdio server and sampling client (`server.create_message()`) — single dependency covers both use cases
- `keyring` is sync — credential reads happen at startup and config load, not in async hot paths

**Pattern Consistency — PASS**

- `snake_case` convention aligns with Python stdlib, SQLAlchemy column names, JSON keys, and MCP tool names — no cross-layer friction
- `StageError` defined in `core/errors.py` flows cleanly: stage -> orchestrator -> API handler / MCP tool
- `logging.getLogger(__name__)` pattern is compatible with both entry points registering their own handlers

**Structure Alignment — PASS**

- Entry point isolation rule is supported by the directory structure — `api/` reachable from `main.py` only; `pipeline/` reachable from both entry points
- `data/` as a gitignored runtime directory is consistent with local-first, no-cloud-hosting NFR

---

### Requirements Coverage Validation

**Functional Requirements — PASS**

| FR Group | Coverage |
|---|---|
| Gmail Ingest (FR-1-3) | `services/gmail.py` + `stages/ingest.py` + `ProcessedEmail` model |
| Modular Pipeline (FR-4-8, FR-7a) | All 9 stages + `orchestrator.py` + `handoff.py` |
| Audio/TTS (FR-9-11) | `services/tts.py` + `stages/tts_prep.py` + `stages/assemble.py`; audio failure isolation at orchestrator level |
| QA Gate + Retry (FR-12-13) | `stages/qa_gate.py` + 3-tier retry in `orchestrator.py` + Hold state in `Run.status` |
| LLM Provider (FR-14-15) | `services/llm.py` with 5-provider enum; `core/credentials.py` for encrypted key storage |
| Onboarding (FR-16-17) | `setup.py` wizard; Kokoro auto-download in `services/tts.py` |
| Web UI (FR-18-25) | FastAPI routes in `api/` + Jinja2 templates + SSE in `api/stream.py` |
| MCP (added) | `app/mcp_server.py` + `mcp_sampling` provider in `llm.py` |

**Non-Functional Requirements — PASS**

| NFR | How addressed |
|---|---|
| Async-first | FastAPI BackgroundTasks; pipeline never blocks web server |
| Streaming | SSE via `sse-starlette`; shared async queue between orchestrator and `api/stream.py` |
| Local-first security | `keyring` for credentials; no external transmission beyond configured provider |
| Partial rerun | Handoff packets persisted to `data/artifacts/{run_id}/` after each stage |
| Daemon mode | PID file + detached subprocess in `core/scheduler.py` |
| Self-contained install | `setup.py` wizard + Kokoro auto-download; `uv` lockfile for reproducible deps |

---

### Gap Analysis Results

**Critical Gaps — None**

**Important Gaps:**

1. **SSE queue pattern not specified** — shared async queue between `orchestrator.py` and `api/stream.py` needs a defined pattern. Decision: `dict[int, asyncio.Queue]` module-level singleton in `api/stream.py`, keyed by `run_id`. Orchestrator imports and writes to it; SSE endpoint reads from it. Queue created when run starts, cleaned up on SSE disconnect or run completion.

2. **HandoffPacket field list not defined** — canonical fields for each stage's inputs/outputs not yet documented. To be populated in `handoff-schema.yaml` during the first implementation story, where stage-by-stage I/O gets specified.

**Nice-to-Have:**
- `.gitignore` contents not specified (should exclude `data/`, `*.db`, `*.log`, `__pycache__`, `.env`)
- `pyproject.toml` dev dependencies group not templated (pytest, httpx)

---

### Architecture Completeness Checklist

**Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

---

### Architecture Readiness Assessment

**Overall Status: READY FOR IMPLEMENTATION**

All 16 checklist items confirmed. No critical gaps. Two important gaps are non-blocking and resolved in the first implementation story.

**Confidence Level: High**

**Key Strengths:**
- Clean entry point isolation enables true MCP-only usage without web UI overhead
- Single `llm.py` abstraction makes provider switching (including MCP sampling fallback) transparent to all pipeline stages
- Handoff packet persistence to disk means partial reruns are structurally guaranteed, not an afterthought
- SSE + shared async queue keeps live log simple and avoids WebSocket complexity for a unidirectional use case

**Areas for Future Enhancement:**
- HandoffPacket field definitions (populated in story 1)
- `.gitignore` and `pyproject.toml` dev dep templates
- WebSocket upgrade path if SSE proves insufficient
- Alembic migrations when V2 schema churn warrants it

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently — especially the `run(packet, config)` stage interface and `llm.py` provider routing
- Respect entry point isolation: `main.py` and `mcp_server.py` never import each other
- Refer to this document for all architectural questions before making independent decisions

**First Implementation Priority:**
```bash
uv init briefing && cd briefing
uv add fastapi uvicorn[standard] sqlalchemy aiosqlite \
       google-auth google-auth-oauthlib google-api-python-client \
       sentence-transformers faiss-cpu kokoro \
       apscheduler keyring jinja2 python-multipart \
       sse-starlette httpx openai anthropic google-generativeai mcp
```
Then scaffold the full directory structure from the Project Structure section.
