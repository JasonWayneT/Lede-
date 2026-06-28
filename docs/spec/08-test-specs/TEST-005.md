# Test Spec: TEST-005 Story 1.5 StageError + FastAPI envelope

## Metadata

- Test ID: `TEST-005`
- Type: integration
- Status: passing
- Related requirements: `ARCH-005`
- Related acceptance criteria: `AC-051`, `AC-052`, `AC-053`, `AC-054`

## Purpose

Proves StageError carries structured error information and FastAPI returns the standardized error envelope.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/test_errors.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test file: `briefing/tests/test_errors.py`
- Command: `uv run pytest -q tests/test_errors.py`

