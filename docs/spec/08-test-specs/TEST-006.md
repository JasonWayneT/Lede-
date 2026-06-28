# Test Spec: TEST-006 Story 2.1 Gmail OAuth

## Metadata

- Test ID: `TEST-006`
- Type: unit
- Status: passing
- Related requirements: `FR-001`
- Related acceptance criteria: `AC-007`

## Purpose

Proves Gmail OAuth authorization stores token in keyring (not filesystem) and invalid/revoked token results in `StageError(code=AUTH_ERROR, retryable=False)`.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/services/test_gmail.py`

## Expected result

- Tests pass (exit code 0)

## Automation notes

- Test file: `briefing/tests/services/test_gmail.py`
- Command: `uv run pytest -q tests/services/test_gmail.py`

