# Test Spec: TEST-008 Story 2.3 processed log management

## Metadata

- Test ID: `TEST-008`
- Type: integration
- Status: passing
- Related requirements: `FR-003`
- Related acceptance criteria: `AC-009`

## Purpose

Proves processed email IDs are written atomically with run completion and can be cleared via a Settings endpoint without calling Gmail.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/pipeline/test_processed_log.py tests/api/test_processed_log.py`

## Expected result

- Tests pass (exit code 0)

## Automation notes

- Test files:
  - `briefing/tests/pipeline/test_processed_log.py`
  - `briefing/tests/api/test_processed_log.py`
- Command: `uv run pytest -q tests/pipeline/test_processed_log.py tests/api/test_processed_log.py`

