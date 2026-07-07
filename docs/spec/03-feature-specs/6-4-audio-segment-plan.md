# Story 6.4: Audio Segment Plan

Status: done

## Story

As the audio pipeline,
I want the briefing rendered as an ordered plan of discrete segments with known durations,
so that Phase 5 can lay music under each story and place stingers between sections — instead of one
opaque whole-briefing audio blob.

Traces to `FR-030` and `BUG-005`. Design rationale in `docs/spec/07-decisions/ADR-004.md`. Part of
Music Roadmap Phase 4 (`docs/music/ROADMAP.md`).

## Acceptance Criteria

1. **Given** a packet with `drafted_stories` populated and `assembled_markdown` empty, **When**
   `tts_prep.run()` executes, **Then** the segment plan / `tts_script` contains the story prose —
   not empty-input output (fixes `BUG-005`) (`AC-074`)

2. **Given** drafted stories spanning multiple sections, **When** the plan is built, **Then** its
   order is: one `intro` segment, then the sections (a `section_transition` segment before each
   section after the first), then one `outro` segment; sections are ordered per config with `Other`
   last, and stories within a section by `source_count` descending — matching `assemble` (`AC-075`)

3. **Given** a drafted story whose prose ends with a `> Sources: …` trailer and which carries a
   `selected_music` value, **When** the plan is built, **Then** its `main_summary` segment's `text`
   is the prose with the Sources trailer stripped, and the segment carries that `selected_music`
   (`AC-076`)

4. **Given** the `intro`, `outro`, and `section_transition` segments, **When** the plan is built,
   **Then** each has empty narration `text` and a `selected_music` resolved via
   `music.select_music(segment_role=…)` (role override) (`AC-077`)

5. **Given** a plan with narrated segments, **When** `synthesize_plan()` runs, **Then** each
   narrated segment is assigned a `duration_seconds`, and a single `briefing.mp3` is written to the
   same path as before (`AC-078`)

6. **Given** the pronunciation-guide LLM call raises or returns unparseable output, **When**
   `tts_prep.run()` executes, **Then** the guide is empty, the segment plan is still built, and the
   stage does not fail (`AC-079`)

## Tasks / Subtasks

- [x] `HandoffPacket.audio_segments: list[dict]` field (`TASK-027`)
- [x] `app/pipeline/ordering.py` with `order_stories_by_section()`; `assemble.py` refactored to use
      it (`TASK-028`)
- [x] Rewrite `tts_prep.py`: build the segment plan from `drafted_stories`, deterministic narration
      cleanup, non-fatal pronunciation LLM call, keep `tts_script` populated (`TASK-029`)
- [x] `tts.synthesize_plan(segments, output_path, pronunciation_guide)` — render each narrated
      segment, record `duration_seconds`, concatenate to single mp3 (`TASK-030`)
- [x] Wire main + on-demand orchestrator paths and briefings resume to `synthesize_plan` with
      `tts_script` fallback (`TASK-031`)
- [x] Tests + `TEST-016` spec (`TASK-032`, `TASK-033`)

## Segment shape

Each entry in `packet.audio_segments`:

```
{
  "role": "intro" | "main_summary" | "section_transition" | "outro",
  "section_name": str | None,      # the section this segment belongs to (None for intro/outro)
  "text": str,                      # narration; "" for structural (music-only) segments
  "selected_music": dict | None,    # {"asset_id","style","file"} or None
  "duration_seconds": float | None, # set by synthesize_plan for narrated segments; None until then
}
```

## Dev Notes

### Why the plan is built from `drafted_stories`

See `ADR-004` decision 1 + `BUG-005`: `assembled_markdown` isn't populated until the `assemble`
stage, which runs *after* `tts_prep`. `drafted_stories` (from `draft`, stage 7) is always available
and already carries prose + `section_name` + `selected_music` per story.

### Why structural segments are music-only

See `ADR-004` decision 3. V1 replaces spoken segues with musical stingers (the roadmap's intent).
In Phase 4, before mixing exists, structural segments produce no audio — the audible output is the
concatenated story narrations. They become audible in Phase 5.

### `tts_script` retained

`qa_gate` inspects `tts_script` (markdown/word-count checks) and the resume path guards on it. The
new `tts_prep` sets `tts_script` to the concatenated narration for compatibility, alongside the new
`audio_segments`. Noted as transitional redundancy in `ADR-004`.

### References

- `docs/spec/07-decisions/ADR-004.md` — full rationale and alternatives
- `docs/spec/09-known-issues/BUG-005.md` — the ordering bug fixed here
- `docs/spec/03-feature-specs/6-1-tts-prep-stage.md`, `6-2-kokoro-tts-service.md` — amended stages
- `docs/music/ROADMAP.md` — Phase 4

## Dev Agent Record

### Agent Model Used

claude-opus-4-8

### Completion Notes List

- Implemented as part of `CR-005`.

### File List

- `briefing/app/pipeline/handoff.py`
- `briefing/app/pipeline/ordering.py` (new)
- `briefing/app/pipeline/stages/assemble.py`
- `briefing/app/pipeline/stages/tts_prep.py`
- `briefing/pipeline_prompts/stages/tts_prep.md`
- `briefing/app/services/tts.py`
- `briefing/app/pipeline/orchestrator.py`
- `briefing/app/api/briefings.py`
- `briefing/tests/pipeline/test_ordering.py` (new)
- `briefing/tests/pipeline/stages/test_tts_prep.py`
- `briefing/tests/services/test_tts.py`
