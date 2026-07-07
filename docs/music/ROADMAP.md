# Lede Music — Roadmap

Living tracking document for the music feature. This sits above the formal `docs/spec/` chain —
each phase below gets its own `CR-*` (and feature spec, ADR, tests) via the normal AGENTS.md
Change workflow when it's actually built, the same way `CR-001` covered the num_ctx/condense work.
This doc exists so the phase sequencing and V1/later split stay visible across sessions instead of
getting re-litigated each time.

## Status snapshot

- **Current phase:** 6 — Integration & verification (listening review)
- **Progress:** Phases 1-5 complete. Music is now mixed into the audio end to end.
- **Last updated:** 2026-07-04

## V1 scope, stated plainly

V1 is: intro/outro music, a background bed under narration, and section transition stingers —
selected deterministically from a small hand-curated library, driven by fields added to the
existing `frame.py` classification call. Nothing adaptive, no scoring engine, no per-clip variety
yet. The goal is one full, working pass end to end, not the complete system described in the
original policy report.

## Explicitly deferred to V2+

Naming these now so scope doesn't quietly creep back in mid-build:

- The full weighted scoring engine (section 15 of the original report) — V1 uses a deterministic lookup table (topic × tone → style) instead
- Rotation/seeding across multiple candidate clips per style — V1 ships one clip per style; add variety once repetition is actually noticeable
- The full 8-topic × 20-style taxonomy — V1 covers 6 styles, mapped to Lede's actual current sections (`AI, Technology, Finance, Politics, Other`) plus intro/outro/transition
- Numeric audio metadata (bpm, key, energy, seriousness, tension, warmth, brightness, rhythmic_density, melody_prominence) — only matters once the scoring engine exists
- Per-clip gain/fade/duck overrides — V1 uses mix-profile-level defaults (by segment role) only
- A dedicated classification LLM stage — V1 folds the needed fields into frame.py's existing call

## Phases

### Phase 1 — Asset library (done)
Build the 6 clips V1 needs. See checklist below. Each clip gets a real `ffprobe`-verified duration
and a hand-authored `music_bank/music_assets.json` record (category, style, allowed roles,
best_for/avoid_for, mood tags, voice_safe, loopable, license, source_prompt).

### Phase 2 — Classification (done)
Added `sensitivity` and `story_weight` to `frame.py`'s existing structured-output prompt
(`pipeline_prompts/stages/frame.md`) — not a new LLM call. Validated against fixed enums; falls
back to safe defaults (`normal`/`medium`) on missing/invalid values or full parse failure, same
pattern already used for `lead_angle`/`local_stakes`/`guardrails`. `emotional_tone` and
`music_intent`/`topic_category` were cut from this phase — no V1 consumer once style selection
keys off the existing `section_name` field instead of a separate topic axis. See `CR-003` and
`ADR-002` for the full rationale. Not yet consumed by anything — that's Phase 3/5.

### Phase 3 — Selection logic (done)
New `app/services/music.py`: deterministic section→style lookup (with fallback to
`warm_daily_briefing` for unmapped/custom sections), segment-role overrides (intro/outro →
`premium_newsletter_intro`, section_transition → `headline_transition`, checked before
sensitivity), and a sensitivity gate (`sensitive`/`crisis` → no music) for `main_summary` stories.
No scoring engine — a pure lookup function. Wired into `draft.py`: every drafted story now carries
a `selected_music` field (`{"asset_id", "style", "file"}` or `None`). Role overrides for
intro/outro/section_transition are implemented and tested in isolation but not yet exercised
end-to-end — no code calls them with those roles until Phase 4 creates discrete segments for them.
See `CR-004` and `ADR-003` for the three design decisions this required.

### Phase 4 — Audio pipeline restructuring (done)
`tts_prep.py` now builds an ordered **audio segment plan** (`packet.audio_segments`) from
`drafted_stories` — intro, per-story `main_summary` segments with `section_transition` stingers
between sections, outro. Each story segment carries its cleaned prose (Sources trailer stripped) +
`selected_music`; structural segments are music-only with role-selected music (finally exercising
Phase 3's role-override path end-to-end). `tts.synthesize_plan()` renders each narrated segment,
records `duration_seconds`, and concatenates into the same single `briefing.mp3` (contract
preserved, non-fatal). No mixing yet — `selected_music` + durations are threaded through for Phase 5.
This phase also fixed `BUG-005`: `tts_prep` was reading `assembled_markdown`, which the later
`assemble` stage populates, so narration had been generated from an empty string. Shared section
ordering was factored into `app/pipeline/ordering.py` (used by both `assemble` and `tts_prep`).
See `CR-005`, `ADR-004`, `BUG-005`.

**Known follow-up for listening review (Phase 6):** spoken section segues were dropped in favor of
Phase 5's musical stingers, and narration now rests entirely on draft prose (no LLM read-aloud
rewrite). Both are quality calls to confirm by ear once music is mixed in.

### Phase 5 — Mixing (done)
New `app/services/mixing.py` (pure numpy + `scipy.signal.resample_poly` + `soundfile`, **no new
dependency** — all three already present). `tts.synthesize_plan` now mixes each segment inline:
story segments get a ducked, looped, faded music bed under the narration (profile by `story_weight`,
which is now threaded draft → tts_prep → segment); intro/outro/section_transition render faded
music-only stingers. Output is 44.1 kHz stereo, clip-guarded, into the same single `briefing.mp3`.
No-music (sensitive/unmapped) and missing-file cases degrade to dry voice, non-fatally. Verified end
to end: a real Kokoro-narrated 3-segment plan produced a 44.1 kHz stereo mp3 whose length exactly
matched the recorded segment durations (intro 4.0s + story 7.55s + outro 5.0s = 16.55s). See
`CR-006`, `ADR-005`. Mix profiles (gain/duck/fade) are named constants in `mixing.py` — first-pass
values to tune by ear in Phase 6.

### Phase 6 — Integration & verification
Wire phases 2-5 together, generate a real briefing end to end, listen to it, verify sensitive/crisis
content correctly resolves to no music.

## Open decisions

- Music generation tool/workflow for remaining clips (currently: Gemini, one at a time, pasted description + file)
- Whether `music_bank/` config is versioned in git (current assumption: yes, like `pipeline_prompts/`) — confirmed by placing `music_assets.json` there in Phase 1
- Audio mixing library for Phase 5 — settled: numpy + scipy + soundfile, no new dependency
- **Open (BUG-007): should `duck_db` be deepened ~5-7dB across all `STORY_MIX_PROFILES` weights?**
  Measured: even after the new transient limiter, a `medium`-weight transient sits only ~0.8dB
  *below* real narration RMS, and `light` sits ~2.8dB *above* it. Fully guaranteeing transients stay
  under voice needs duck deepened that much, which would also make the already-approved quiet-bed
  level noticeably subtler (current ~12dB margin under voice would grow to ~17-19dB). This is a
  listening/taste call, not a code decision — needs Jason's ear.

## Phase 1 asset checklist

| Style | Covers | Status |
|---|---|---|
| `modern_tech_digest` | AI, Technology | done — `modern_tech_digest_01` |
| `premium_newsletter_intro` | intro + outro (every briefing) | done — `premium_newsletter_intro_01` |
| `headline_transition` | section transitions (every briefing) | done — `headline_transition_01` |
| `warm_daily_briefing` | Other / safe-default fallback | done — `warm_daily_briefing_01` |
| `business_briefing` | Finance | done — `business_briefing_01` |
| `civic_affairs` | Politics | done — `civic_affairs_01` |
