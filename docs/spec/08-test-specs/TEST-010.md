# Test Spec: TEST-010 Conditional source condensation

## Metadata

- Test ID: `TEST-010`
- Type: unit
- Status: passing
- Related requirements: `FR-027`, `ARCH-006`
- Related acceptance criteria: `AC-058`, `AC-059`, `AC-060`

## Purpose

Proves `app/services/condense.py` passes under-budget text through unchanged with no LLM call
(`AC-058`), splits over-budget text into chunks only on sentence boundaries — never mid-sentence,
including the no-punctuation edge case (`AC-059`) — and that `get_source_texts` preserves cluster
order (`AC-060`).

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/services/test_condense.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test file: `briefing/tests/services/test_condense.py`
- Command: `uv run pytest -q tests/services/test_condense.py`
