# Test Spec: TEST-016 Audio segment plan + segment-aware synthesis

## Metadata

- Test ID: `TEST-016`
- Type: unit
- Status: passing
- Related requirements: `FR-030`, `BUG-005`
- Related acceptance criteria: `AC-074`, `AC-075`, `AC-076`, `AC-077`, `AC-078`, `AC-079`

## Purpose

Proves `tts_prep` builds the audio segment plan from `drafted_stories` with the correct
intro/section-transition/story/outro ordering (fixing `BUG-005`), that story segments carry cleaned
prose + `selected_music` while structural segments are music-only with role-selected music, that the
pronunciation-guide LLM call is non-fatal, and that `tts.synthesize_plan` records per-segment
durations while writing a single `briefing.mp3`. Also covers `app/pipeline/ordering.py` and confirms
the refactored `assemble` still orders sections identically.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/pipeline/test_ordering.py tests/pipeline/stages/test_tts_prep.py tests/pipeline/stages/test_assemble.py tests/services/test_tts.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test files: `briefing/tests/pipeline/test_ordering.py`,
  `briefing/tests/pipeline/stages/test_tts_prep.py`,
  `briefing/tests/pipeline/stages/test_assemble.py`, `briefing/tests/services/test_tts.py`
- Command: `uv run pytest -q tests/pipeline tests/services/test_tts.py`
