# Test Spec: TEST-015 Deterministic music selection

## Metadata

- Test ID: `TEST-015`
- Type: unit
- Status: passing
- Related requirements: `FR-029`
- Related acceptance criteria: `AC-070`, `AC-071`, `AC-072`, `AC-073`

## Purpose

Proves `app/services/music.py`'s selection logic: segment-role override beats section/sensitivity;
sensitive/crisis stories get no music; known sections map to their configured style with a
fallback for unmapped sections; a style with no voice-safe asset resolves to no music rather than
raising. Also proves `draft.py` attaches a `selected_music` field to each drafted story.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/services/test_music.py tests/pipeline/stages/test_draft.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test files: `briefing/tests/services/test_music.py`, `briefing/tests/pipeline/stages/test_draft.py`
- Command: `uv run pytest -q tests/services/test_music.py tests/pipeline/stages/test_draft.py`
