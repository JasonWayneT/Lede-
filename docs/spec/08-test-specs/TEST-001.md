# Test Spec: TEST-001 Story 1.1 scaffold verification

## Metadata

- Test ID: `TEST-001`
- Type: manual
- Status: passing
- Related requirements: `ARCH-001`
- Related acceptance criteria: `AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`

## Purpose

Proves Story 1.1 completed: project scaffold exists, dependencies install via `uv`, and key imports succeed.

## Preconditions

- Python 3.11+
- `uv` installed
- Run from `briefing/` project root

## Steps

1. Verify required paths exist:

   - Confirm `pyproject.toml`, `.env.example`, `.gitignore`, `setup.py`, `briefing.sh`, `briefing.bat` exist
   - Confirm required directories exist: `app/…`, `tests/…`, `pipeline_prompts/…`, `data/…`

2. Verify dependency imports:

   - Run: `uv run python -c "import fastapi, sqlalchemy, mcp"`

## Expected result

- All required files/directories exist
- Import command exits 0 with no output/errors

## Regression coverage

- Related bug IDs: none
- Known failure modes prevented:
  - Missing scaffold files/dirs that block later stories
  - Missing critical dependencies (`fastapi`, `sqlalchemy`, `mcp`)

## Automation notes

- Test file: none (manual verification for scaffold story)
- Command: `uv run python -c "import fastapi, sqlalchemy, mcp"`
- Fixtures: none
- Mocking: none

