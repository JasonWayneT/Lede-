# Test Spec: TEST-018 Dashboard surfaces hold/error state

## Metadata

- Test ID: `TEST-018`
- Type: integration
- Status: passing
- Related requirements: `BUG-006`
- Related acceptance criteria: `AC-086`

## Purpose

Proves the dashboard route (`GET /`) surfaces a held run's failure reason and a retry control when
one exists, and shows no hold banner when the only runs are complete/running.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/api/test_dashboard.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test file: `briefing/tests/api/test_dashboard.py`
- Command: `uv run pytest -q tests/api/test_dashboard.py`
