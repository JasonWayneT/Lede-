# Story 5.6: Deterministic Music Selection

Status: done

## Story

As a listener,
I want background music chosen consistently — the right style for the section, silence for
sensitive stories — so the briefing never feels tonally wrong or randomly different run to run.

Traces to `FR-029`. Design rationale in `docs/spec/07-decisions/ADR-003.md`. Part of Music Roadmap
Phase 3 (`docs/music/ROADMAP.md`).

## Acceptance Criteria

1. **Given** `segment_role` is `intro`, `outro`, or `section_transition`, **When**
   `select_style()` is called, **Then** it returns the fixed role style
   (`premium_newsletter_intro` or `headline_transition`) regardless of `section_name` or
   `sensitivity` (`AC-070`)

2. **Given** `segment_role="main_summary"` and `sensitivity` is `"sensitive"` or `"crisis"`,
   **When** `select_style()` is called, **Then** it returns `None` — no music — regardless of
   `section_name` (`AC-071`)

3. **Given** `segment_role="main_summary"`, `sensitivity="normal"`, and a `section_name` in the
   default set (`AI`, `Technology`, `Finance`, `Politics`, `Other`), **When** `select_style()` is
   called, **Then** it returns that section's configured style; **given** a `section_name` not in
   the map (a user-renamed/added section), **then** it returns `warm_daily_briefing` (`AC-072`)

4. **Given** a style with no matching asset, or none marked `voice_safe`, **When** `select_asset()`
   is called, **Then** it returns `None` and logs a warning — it does not raise (`AC-073`)

5. **Given** the draft stage processes a story, **When** it builds the drafted story dict,
   **Then** it includes a `selected_music` field — either `{"asset_id", "style", "file"}` or
   `None` — computed via `music.select_music(segment_role="main_summary", ...)`

## Tasks / Subtasks

- [x] New `app/services/music.py`: `MUSIC_ASSETS_PATH`, `ROLE_OVERRIDES`, `SECTION_STYLE_MAP`,
      `DEFAULT_STYLE`, `load_music_assets()`, `select_style()`, `select_asset()`, `select_music()`
      (`TASK-023`)
- [x] Wire `music.select_music(...)` into `draft.py`'s per-story loop, storing the result as
      `selected_music` on each drafted story (`TASK-024`)
- [x] Tests: role override precedence, sensitivity gate, section map + fallback, no-asset
      fallback, end-to-end via `draft.run()` (`TASK-025`)
- [x] `TEST-015` spec doc (`TASK-026`)

## Dev Notes

### Why this lives in `draft.py`, not `frame.py`

`frame.py` already computes and carries `section_name`/`sensitivity`; `draft.py` is where the
per-story loop already exists and where `source_texts`/prose get attached (`FR-027`/`FR-008`).
Selection needs both fields plus is naturally a "per drafted story" decision, so it's computed
there — same "compute where it's natural, consume later" pattern as `source_texts` (`CR-001`).

### Not yet wired: intro/outro/section_transition

`select_style()`/`select_music()` accept a `segment_role` parameter and already handle
`intro`/`outro`/`section_transition` correctly (tested in isolation), but nothing in the pipeline
calls them with those roles yet — Lede's `tts_prep.py`/`tts.py` don't produce discrete
intro/outro/transition segments (Phase 4). This is deliberate: the selection logic is ready, not
speculative-complexity-for-its-own-sake — see `ADR-003`.

### `music_bank/music_assets.json` location

`MUSIC_ASSETS_PATH` resolves relative to `app/services/music.py`'s own path
(`Path(__file__).parent.parent.parent / "music_bank" / "music_assets.json"`), same pattern as
`condense.py`'s `PROMPT_PATH`. `music_bank/` is committed config, not gitignored `data/`.

### References

- `docs/spec/07-decisions/ADR-003.md` — full rationale and alternatives considered
- `docs/spec/03-feature-specs/5-5-music-classification.md` — source of the `sensitivity` field this consumes
- `docs/music/ROADMAP.md` — Phase 3 of the music roadmap

## Dev Agent Record

### Agent Model Used

claude-sonnet-5

### Debug Log References

### Completion Notes List

- Implemented as part of `CR-004`.

### File List

- `briefing/app/services/music.py` (new)
- `briefing/app/pipeline/stages/draft.py`
- `briefing/tests/services/test_music.py` (new)
