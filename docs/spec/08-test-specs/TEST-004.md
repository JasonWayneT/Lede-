# Test Spec: TEST-004 Story 1.4 keyring credentials wrapper

## Metadata

- Test ID: `TEST-004`
- Type: unit
- Status: passing
- Related requirements: `ARCH-004`
- Related acceptance criteria: `AC-045`, `AC-046`, `AC-047`, `AC-048`, `AC-049`

## Purpose

Proves credential wrapper uses the `"briefing"` service namespace and exposes standardized key constants, without touching real OS keychains in tests (keyring fully mocked).

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run unit tests:
   - Command: `uv run pytest -q tests/services/test_credentials.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test file: `briefing/tests/services/test_credentials.py`
- Command: `uv run pytest -q tests/services/test_credentials.py`

