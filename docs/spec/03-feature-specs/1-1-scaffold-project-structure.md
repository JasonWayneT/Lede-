# Story 1.1: Scaffold Project Structure and Initialize uv Project

Status: ready-for-dev

## Story

As a developer,
I want the complete project directory structure scaffolded with all required files and uv dependencies installed,
so that I can begin implementing features immediately without spending time on project setup decisions.

## Acceptance Criteria

1. **Given** a machine with Python 3.11+ and uv installed, **When** I run the initialization command from the architecture doc, **Then** the `briefing/` root directory exists with `pyproject.toml`, `.env.example`, `.gitignore`, `setup.py`, `briefing.sh`, `briefing.bat`

2. **Given** the scaffolded project, **When** I inspect the directory tree, **Then** all directories exist: `app/core/`, `app/api/`, `app/pipeline/stages/`, `app/services/`, `app/db/`, `app/templates/`, `pipeline_prompts/stages/`, `data/briefings/`, `data/artifacts/`, `tests/api/`, `tests/pipeline/stages/`, `tests/services/`, `tests/mcp/`

3. **Given** the scaffolded project, **When** I run `uv run python -c "import fastapi, sqlalchemy, mcp"`, **Then** all packages import without error

4. **Given** the `.env.example` file, **When** I read it, **Then** it contains template entries for `BRIEFING_DATA_DIR` and `LOG_LEVEL` with example values

5. **Given** the `.gitignore` file, **When** I read it, **Then** it excludes: `data/`, `*.db`, `*.log`, `__pycache__/`, `.env`, `*.pyc`, `.venv/`

6. **Given** the `pipeline_prompts/` directory, **When** I inspect it, **Then** `handoff-schema.yaml` exists as an empty placeholder and `stages/` contains `select.md`, `frame.md`, `draft.md`, `tts_prep.md` as empty placeholders

## Tasks / Subtasks

- [ ] Initialize uv project and install all dependencies (AC: 1, 3)
  - [ ] Run `uv init briefing` (or create `pyproject.toml` manually if project root already exists)
  - [ ] Run the full `uv add` command from Architecture doc (see Dev Notes below) including `mcp` and `sse-starlette`
  - [ ] Confirm `uv run python -c "import fastapi, sqlalchemy, mcp"` exits 0

- [ ] Create all source directories with `__init__.py` stubs (AC: 2)
  - [ ] `app/`, `app/core/`, `app/api/`, `app/pipeline/`, `app/pipeline/stages/`, `app/services/`, `app/db/`, `app/templates/`
  - [ ] `tests/`, `tests/api/`, `tests/pipeline/`, `tests/pipeline/stages/`, `tests/services/`, `tests/mcp/`
  - [ ] Add empty `__init__.py` to every Python package directory (`app/` and all subdirs, `tests/` and all subdirs)

- [ ] Create runtime data directories (AC: 2)
  - [ ] `data/briefings/`, `data/artifacts/`
  - [ ] Add `.gitkeep` to each so they are tracked by git but their contents are not

- [ ] Create Python source file stubs (AC: 2)
  - [ ] `app/main.py` — empty FastAPI app with `app = FastAPI()` and `if __name__ == "__main__": import uvicorn; uvicorn.run(...)` stub
  - [ ] `app/mcp_server.py` — empty stub with module docstring: "MCP server entry point — standalone, no FastAPI dependency"
  - [ ] `app/core/config.py`, `app/core/credentials.py`, `app/core/scheduler.py`, `app/core/errors.py` — empty stubs (module docstring only)
  - [ ] `app/api/briefings.py`, `app/api/downloads.py`, `app/api/settings.py`, `app/api/stream.py` — empty stubs
  - [ ] `app/pipeline/orchestrator.py`, `app/pipeline/handoff.py` — empty stubs
  - [ ] `app/pipeline/stages/ingest.py`, `extract.py`, `embed.py`, `cluster.py`, `select.py`, `frame.py`, `draft.py`, `tts_prep.py`, `assemble.py`, `qa_gate.py` — empty stubs
  - [ ] `app/services/gmail.py`, `llm.py`, `tts.py`, `embeddings.py` — empty stubs
  - [ ] `app/db/database.py`, `app/db/models.py` — empty stubs
  - [ ] `tests/conftest.py` — empty stub
  - [ ] `tests/api/conftest.py`, `tests/pipeline/conftest.py`, `tests/services/conftest.py`, `tests/mcp/conftest.py` — empty stubs

- [ ] Create Jinja2 template stubs (AC: 2)
  - [ ] `app/templates/base.html`, `dashboard.html`, `history.html`, `settings.html` — minimal valid HTML stubs (can be a single `<h1>placeholder</h1>`)

- [ ] Create `pipeline_prompts/` directory and placeholder files (AC: 6)
  - [ ] `pipeline_prompts/handoff-schema.yaml` — empty file
  - [ ] `pipeline_prompts/style-guide.md` — empty file
  - [ ] `pipeline_prompts/stages/select.md`, `frame.md`, `draft.md`, `tts_prep.md` — empty files

- [ ] Create root config and script files (AC: 1, 4, 5)
  - [ ] `.env.example` — see exact contents in Dev Notes
  - [ ] `.gitignore` — see exact contents in Dev Notes
  - [ ] `briefing.sh` — single-line: `uvicorn app.main:app --host 127.0.0.1 --port 8000`
  - [ ] `briefing.bat` — Windows equivalent: `uvicorn app.main:app --host 127.0.0.1 --port 8000`
  - [ ] `setup.py` — stub with module docstring: "First-run onboarding wizard (OAuth + Kokoro download) — implemented in Epic 10"
  - [ ] `README.md` — minimal stub: project name + "Setup instructions coming in Epic 10"

## Dev Notes

### Exact uv add command (from Architecture doc)

```bash
uv add fastapi uvicorn[standard] sqlalchemy aiosqlite \
       google-auth google-auth-oauthlib google-api-python-client \
       sentence-transformers faiss-cpu kokoro \
       apscheduler keyring jinja2 python-multipart \
       sse-starlette httpx openai anthropic google-generativeai mcp
```

Note: `sse-starlette` is required for SSE support (confirmed in Architecture validation section). The Architecture doc's "First Implementation Priority" block lists it. Also add dev dependencies:

```bash
uv add --dev pytest pytest-asyncio
```

### Exact `.env.example` contents

```
# Briefing — environment configuration template
# Copy to .env and fill in values before running.

BRIEFING_DATA_DIR=./data
LOG_LEVEL=INFO
```

### Exact `.gitignore` contents

```
data/
*.db
*.log
__pycache__/
.env
*.pyc
.venv/
```

### Project structure (authoritative — from Architecture doc § "Complete Project Directory Structure")

Every directory and file in the tree below must exist after this story is complete. Stubs are acceptable for all Python source files and templates; they just need to be present and importable (no syntax errors).

```
briefing/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── setup.py
├── briefing.sh
├── briefing.bat
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── mcp_server.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── credentials.py
│   │   ├── scheduler.py
│   │   └── errors.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── briefings.py
│   │   ├── downloads.py
│   │   ├── settings.py
│   │   └── stream.py
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── handoff.py
│   │   └── stages/
│   │       ├── __init__.py
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
│   │   ├── __init__.py
│   │   ├── gmail.py
│   │   ├── llm.py
│   │   ├── tts.py
│   │   └── embeddings.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── history.html
│       └── settings.html
├── pipeline_prompts/
│   ├── style-guide.md
│   ├── handoff-schema.yaml
│   └── stages/
│       ├── select.md
│       ├── frame.md
│       ├── draft.md
│       └── tts_prep.md
├── data/
│   ├── briefings/.gitkeep
│   └── artifacts/.gitkeep
└── tests/
    ├── conftest.py
    ├── api/
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── test_briefings.py       ← empty stub for this story
    │   ├── test_downloads.py       ← empty stub
    │   ├── test_settings.py        ← empty stub
    │   └── test_stream.py          ← empty stub
    ├── pipeline/
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── test_orchestrator.py    ← empty stub
    │   ├── test_handoff.py         ← empty stub
    │   └── stages/
    │       ├── __init__.py
    │       ├── test_ingest.py      ← empty stub
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
    │   ├── __init__.py
    │   ├── test_llm.py
    │   ├── test_gmail.py
    │   ├── test_tts.py
    │   └── test_embeddings.py
    └── mcp/
        ├── __init__.py
        ├── conftest.py
        ├── test_trigger_briefing.py
        ├── test_get_run_status.py
        ├── test_list_briefings.py
        └── test_get_briefing_content.py
```

### Naming conventions (from Architecture doc § "Naming Patterns")

- Python files: `snake_case.py`
- Python packages: directory + `__init__.py`
- No test files co-located with source (`*.test.py` pattern is NOT used)
- Test files live exclusively under `tests/`

### What stubs must NOT do

- Stub Python files must not import anything that isn't already in the uv-managed venv — no cross-file imports yet
- Stub test files should contain only `# placeholder` or `pass` — no broken imports
- `app/main.py` stub is the one exception: it may import `fastapi` to confirm the package is available

### Entry point isolation rule (Architecture § "Entry Point Isolation")

Even in stubs, do not add any imports that would violate this rule:
- `main.py` must never import from `mcp_server.py`
- `mcp_server.py` must never import from `main.py` or `api/`
- `pipeline/`, `services/`, `core/`, `db/` must never import from `main.py` or `mcp_server.py`

### No story-specific tests required

This story creates structure, not logic. Test stubs are placeholders for future stories. The only verification needed is AC 3: `uv run python -c "import fastapi, sqlalchemy, mcp"` exits 0.

### Project Structure Notes

- Project root is `briefing/` — the uv project is initialized at this level
- `data/` is gitignored (per `.gitignore`) but `data/briefings/` and `data/artifacts/` need `.gitkeep` files so the directories are tracked
- `pipeline_prompts/` is NOT inside `app/` — it lives at the project root level alongside `app/`
- Architecture doc notes that `handoff-schema.yaml` field definitions are populated in Story 4.1, not here — the file is an empty placeholder only

### References

- [Source: docs/ARCHITECTURE.md § "Project Structure"] — authoritative directory tree
- [Source: docs/ARCHITECTURE.md § "First Implementation Priority"] — exact `uv add` command
- [Source: docs/ARCHITECTURE.md § "Naming Patterns"] — file and module naming conventions
- [Source: docs/ARCHITECTURE.md § "Entry Point Isolation"] — import boundary rules
- [Source: docs/ARCHITECTURE.md § "Gap Analysis Results"] — confirms `.gitignore` contents
- [Source: docs/epics-stories.md § "Story 1.1"] — acceptance criteria
- [Source: docs/epics-stories.md § "Additional Requirements"] — HandoffPacket schema deferred to Story 4.1

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Completed `uv init briefing` and installed runtime + dev dependencies with `uv add` / `uv add --dev` per Dev Notes.
- Created the full Story 1.1 directory tree and stubs (packages include `__init__.py`; tests contain `# placeholder`).
- Verified AC#3: `uv run python -c "import fastapi, sqlalchemy, mcp"` exits 0.
- Verified AC#1/#2/#6 via path existence checks from `briefing/` root.
- Note: `uv` created `.venv/` and `uv.lock` in `briefing/` (expected); `.venv/` is gitignored per `.gitignore`.

### File List

- `briefing/` scaffold and full tree per Story 1.1 (see “Project structure” section in this spec).
- Additional files created by `uv init` / dependency management: `briefing/uv.lock`, `briefing/.python-version`, `briefing/.venv/`.
