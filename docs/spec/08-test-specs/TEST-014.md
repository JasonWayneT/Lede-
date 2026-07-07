# Test Spec: TEST-014 Frame stage sensitivity/story_weight classification

## Metadata

- Test ID: `TEST-014`
- Type: unit
- Status: passing
- Related requirements: `FR-028`
- Related acceptance criteria: `AC-067`, `AC-068`, `AC-069`

## Purpose

Proves the frame stage's structured-output parser extracts valid `sensitivity`/`story_weight`
values, defaults both to `normal`/`medium` when missing or outside the allowed enum, and still
produces both fields (at their defaults) when the LLM response fails to parse as JSON at all.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/pipeline/stages/test_frame.py`

## Expected result

- All tests pass (exit code 0), including the new classification-field tests

## Automation notes

- Test file: `briefing/tests/pipeline/stages/test_frame.py`
- Command: `uv run pytest -q tests/pipeline/stages/test_frame.py`
