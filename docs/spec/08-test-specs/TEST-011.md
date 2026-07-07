# Test Spec: TEST-011 Frame/draft share one condensation pass via source_texts

## Metadata

- Test ID: `TEST-011`
- Type: unit
- Status: passing
- Related requirements: `FR-027`, `ARCH-006`
- Related acceptance criteria: `AC-057`, `AC-060`

## Purpose

Proves the frame stage computes `source_texts` once per cluster and stores it on the framed story
dict, that the draft stage builds its prompt from `story["source_texts"]` rather than re-deriving
text from the raw cluster, and that draft degrades gracefully (falls back to per-entry
condensation) when `source_texts` is absent — e.g. an older persisted handoff artifact replayed in
a partial rerun.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/pipeline/stages/test_frame.py tests/pipeline/stages/test_draft.py`

## Expected result

- All tests pass (exit code 0), including:
  - `test_frame.py::test_frame_populates_source_texts`
  - `test_draft.py::test_draft_uses_precomputed_source_texts`
  - `test_draft.py::test_draft_falls_back_when_source_texts_missing`

## Automation notes

- Test files: `briefing/tests/pipeline/stages/test_frame.py`, `briefing/tests/pipeline/stages/test_draft.py`
- Command: `uv run pytest -q tests/pipeline/stages/test_frame.py tests/pipeline/stages/test_draft.py`
