# Test Spec: TEST-007 Story 2.2 label-based fetch

## Metadata

- Test ID: `TEST-007`
- Type: unit
- Status: passing
- Related requirements: `FR-002`
- Related acceptance criteria: `AC-008`

## Purpose

Proves label-filtered Gmail fetch excludes processed email IDs and returns required email fields.

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

