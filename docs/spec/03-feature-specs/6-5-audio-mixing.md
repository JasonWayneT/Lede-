# Story 6.5: Audio Mixing

Status: done

## Story

As a listener,
I want music under the narration and stingers between sections,
so that the briefing sounds like a produced show, not a raw text-to-speech read.

Traces to `FR-031`. Design rationale in `docs/spec/07-decisions/ADR-005.md`. Part of Music Roadmap
Phase 5 (`docs/music/ROADMAP.md`). This is the first phase whose output is audible.

## Acceptance Criteria

1. **Given** a narrated story segment with `selected_music` and a `story_weight`, **When**
   `mix_story()` runs, **Then** the music is ducked below the voice, looped to the narration length,
   faded in/out per the weight's profile, and summed with the voice (`AC-080`)

2. **Given** an intro/outro/section_transition segment with `selected_music`, **When**
   `mix_structural()` runs, **Then** a faded, music-only clip of the role profile's duration is
   produced (`AC-081`)

3. **Given** a story segment with `selected_music = None` (sensitive story, or unmapped section),
   **When** `mix_story()` runs, **Then** the output is the narration alone, resampled to the target
   format, with no bed (`AC-082`)

4. **Given** a `selected_music` whose file is missing on disk, **When** mixing tries to load it,
   **Then** it falls back to dry voice (story) or no segment (structural), logs a warning, and does
   not raise (`AC-083`)

5. **Given** any mixed segment, **When** mixing completes, **Then** the samples are 44.1 kHz stereo
   and the peak magnitude is clip-guarded to <= ~0.99 (`AC-084`)

6. **Given** a story segment carrying `story_weight`, **When** `mix_story()` runs, **Then** the mix
   profile matching that weight is applied (`AC-085`)

## Tasks / Subtasks

- [x] `music.MUSIC_BANK_DIR` constant (`TASK-034`)
- [x] Thread `story_weight`: `draft.py` copies it onto the drafted story, `tts_prep.py` copies it
      onto the story segment (`TASK-035`)
- [x] `app/services/mixing.py`: profiles + `_db_to_gain`, `_resample`, `_to_stereo`, `_apply_fade`,
      `_loop_to_length`, `_load_music`, `mix_story`, `mix_structural` (`TASK-036`)
- [x] Rewrite `tts._mix_plan_sync` / `synthesize_plan` to mix each segment inline and write one mp3
      (`TASK-037`)
- [x] Tests + `TEST-017` spec (`TASK-038`, `TASK-039`)
- [x] Roadmap update (`TASK-040`)

## Mix profiles

Adapted from the original music policy report (section 21). Named constants in `mixing.py` so they
can be tuned by ear in Phase 6 in one place.

Story segments (music ducked under voice), by `story_weight`:

| weight | duck_db | fade_in | fade_out |
|---|---|---|---|
| light | -22 | 2.0 | 3.0 |
| medium | -24 | 2.5 | 3.5 |
| heavy | -27 | 3.0 | 4.5 |
| sensitive | -30 | 3.5 | 5.0 (rarely reached — sensitive → no music) |

Structural segments (music-only), by role:

| role | gain_db | duration | fade_in | fade_out |
|---|---|---|---|---|
| intro | -14 | 4.0 | 1.0 | 2.0 |
| section_transition | -14 | 2.5 | 0.3 | 1.0 |
| outro | -14 | 5.0 | 1.0 | 4.0 |

## Dev Notes

### Toolkit and format

numpy + `scipy.signal.resample_poly` + `soundfile`, target 44.1 kHz stereo. No new dependency —
all three are already present (verified). See `ADR-005` for why not pydub/ffmpeg.

### Inline mixing

`tts.synthesize_plan` mixes each segment in its render loop (narration rendered via Kokoro for
story segments, music loaded + mixed by `mixing.py`), concatenates, and writes the single
`briefing.mp3`. No per-segment audio is persisted. `duration_seconds` is the mixed segment length.

### Non-fatal degradation

No-music and missing-file cases fall back to dry voice / omitted stinger. Consistent with `FR-011`.

## Amendment (BUG-007)

Real listening feedback: "loud drums under the words sometimes as it loops." Investigation
(measuring the actual committed clips, not assuming) found the 6 clips are already RMS-consistent
with each other (~-14.3 to -14.4 dBFS) but each has a ~15dB crest factor — transients sit far above
the level `duck_db` was tuned against. Added `_compress_transients()` (fast peak-capture envelope +
smoothed gain reduction, 10dB ceiling over the clip's own RMS) and replaced `_loop_to_length`'s hard
`np.tile` with a crossfaded loop unit (`_make_loopable_unit`). Also fixed an edge-padding artifact
in `_moving_average` found during this work. See `docs/spec/09-known-issues/BUG-007.md` for full
measurements, including the open, ear-judged question of whether `duck_db` should be deepened
further — not resolved by this fix alone.

### References

- `docs/spec/07-decisions/ADR-005.md` — toolkit, format, and profile-keying rationale
- `docs/spec/03-feature-specs/6-4-audio-segment-plan.md` — the segment plan consumed here
- `docs/spec/03-feature-specs/5-6-music-selection.md` — where `selected_music` comes from
- `docs/music/ROADMAP.md` — Phase 5

## Dev Agent Record

### Agent Model Used

claude-opus-4-8

### Completion Notes List

- Implemented as part of `CR-006`.

### File List

- `briefing/app/services/mixing.py` (new)
- `briefing/app/services/tts.py`
- `briefing/app/services/music.py`
- `briefing/app/pipeline/stages/draft.py`
- `briefing/app/pipeline/stages/tts_prep.py`
- `briefing/tests/services/test_mixing.py` (new)
- `briefing/tests/services/test_tts.py`
