# Test Spec: TEST-003 Story 1.3 async DB initialization

## Metadata

- Test ID: `TEST-003`
- Type: integration
- Status: passing
- Related requirements: `ARCH-003`
- Related acceptance criteria: `AC-039`, `AC-043`, `AC-044`

## Purpose

Proves DB schema can be created asynchronously, is idempotent, and FastAPI lifespan initializes the DB file.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/test_db.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test file: `briefing/tests/test_db.py`
- Command: `uv run pytest -q tests/test_db.py`

