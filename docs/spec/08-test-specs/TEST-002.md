# Test Spec: TEST-002 Story 1.2 AppConfig

## Metadata

- Test ID: `TEST-002`
- Type: unit
- Status: passing
- Related requirements: `ARCH-002`
- Related acceptance criteria: `AC-033`, `AC-034`, `AC-035`, `AC-036`, `AC-037`

## Purpose

Proves `AppConfig` loads defaults from `.env`/environment and validates constrained fields with clear errors.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run unit tests:
   - Command: `uv run pytest -q tests/test_config.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test file: `briefing/tests/test_config.py`
- Command: `uv run pytest -q tests/test_config.py`

