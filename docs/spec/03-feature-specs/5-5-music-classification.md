# Story 5.5: Music Sensitivity/Weight Classification

Status: done

## Story

As Lede's music selection logic (future phases),
I want each story classified by content sensitivity and editorial weight,
so that background music can be gated off for sensitive/crisis stories and tuned in intensity for
everything else — without a second LLM call per story.

Traces to `FR-028`. Design rationale (why two fields, not the original report's four) in
`docs/spec/07-decisions/ADR-002.md`. Part of Music Roadmap Phase 2 (`docs/music/ROADMAP.md`).

## Acceptance Criteria

1. **Given** the frame stage's LLM response includes a valid `sensitivity` value
   (`normal|serious|sensitive|crisis`), **When** the response is parsed, **Then** the framed story's
   `sensitivity` field matches that value (`AC-067`)

2. **Given** the frame stage's LLM response includes a valid `story_weight` value
   (`light|medium|heavy|sensitive`), **When** the response is parsed, **Then** the framed story's
   `story_weight` field matches that value (`AC-068`)

3. **Given** the LLM response omits `sensitivity`/`story_weight`, or returns a value outside the
   allowed enum, **When** the response is parsed, **Then** `sensitivity` defaults to `"normal"` and
   `story_weight` defaults to `"medium"` — the invalid value is never passed through (`AC-069`)

4. **Given** the LLM response fails to parse as JSON at all, **When** the full-fallback path runs,
   **Then** `sensitivity` and `story_weight` are still present on the framed story, at their
   defaults (`AC-069`)

## Tasks / Subtasks

- [x] Add `_ALLOWED_SENSITIVITY`, `_ALLOWED_STORY_WEIGHT`, and their defaults to `frame.py`
      (`TASK-019`)
- [x] Update `pipeline_prompts/stages/frame.md` to request both fields, with enum values and
      short guidance on when to use each spelled out for the LLM (`TASK-020`)
- [x] Extend `_parse_frame_response` to extract both fields and validate against the allowed
      enums, falling back to the default on any invalid/missing value — including in the
      full-JSON-parse-failure branch (`TASK-021`)
- [x] Tests: valid values pass through, missing fields default, invalid enum values default, full
      parse-failure fallback includes both fields (`TASK-022`)

## Dev Notes

### Why this doesn't need a new pipeline stage or a new LLM call

`frame.py` already makes one structured JSON call per cluster and already returns
`lead_angle`/`local_stakes`/`guardrails`. Adding two more fields to the same call and the same
parse function is strictly cheaper than a dedicated classification stage — see `ADR-002` and the
condensation work's own precedent (`CR-001`) of preferring "extend what exists" over "add a new
stage."

### Why not the original four fields

`emotional_tone` and `music_intent`/`topic_category` have no V1 consumer: style selection
(Phase 3) will key off the `section_name` field `frame.py` already produces (`FR-006`), since
Lede's 6 V1 music styles map 1:1 to its actual configured sections. Full rationale in `ADR-002`.

### Enum choice rationale

Values are taken directly from the original music policy report (`docs/music/ROADMAP.md`'s
source material) — not redesigned here, just narrowed to the two fields that have a V1 job.
`story_weight` and `sensitivity` both include an allowed value literally named `"sensitive"` for
two different axes (weight tier vs. content sensitivity) — inherited from the original report,
not renamed, per `ADR-002`'s negative consequences.

### References

- `docs/spec/07-decisions/ADR-002.md` — full rationale and alternatives considered
- `docs/spec/03-feature-specs/5-1-frame-stage.md` — the stage this amends
- `docs/music/ROADMAP.md` — Phase 2 of the music roadmap

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

### Completion Notes List

- Implemented as part of `CR-003`.

### File List

- `briefing/app/pipeline/stages/frame.py`
- `briefing/pipeline_prompts/stages/frame.md`
- `briefing/tests/pipeline/stages/test_frame.py`
