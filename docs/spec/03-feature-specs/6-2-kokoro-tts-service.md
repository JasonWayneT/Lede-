# Story 6.2: Kokoro TTS Service and Audio Synthesis

Status: ready-for-dev

> **Amendment (CR-005 / FR-030).** In addition to `synthesize(script, output_path, guide)` (still
> present, used as the resume-path fallback), the service now exposes
> `synthesize_plan(segments, output_path, guide)`, which renders each narrated segment separately,
> records `duration_seconds` on it, and concatenates the narration into the same single
> `briefing.mp3`. Structural (music-only) segments produce no audio in Phase 4. See
> `docs/spec/03-feature-specs/6-4-audio-segment-plan.md` and `docs/spec/07-decisions/ADR-004.md`.
>
> **Amendment 2 (CR-006 / FR-031).** `synthesize_plan` now *mixes* each segment via
> `app/services/mixing.py` instead of concatenating dry narration: music beds ducked under story
> narration, music-only stingers for intro/outro/section_transition. Output is 44.1 kHz stereo.
> Structural segments are now audible. See `docs/spec/03-feature-specs/6-5-audio-mixing.md` and
> `docs/spec/07-decisions/ADR-005.md`.

## Story

As a developer,
I want a TTS service wrapper around Kokoro that synthesizes the narration script into an mp3 file,
so that users get a listenable audio briefing without needing GPU hardware.

## Acceptance Criteria

1. **Given** a TTS script string, **When** I call `tts.synthesize(script, output_path)`, **Then** an mp3 file is written to the specified path

2. **Given** Kokoro model weights not present in the local cache, **When** `tts.synthesize()` is called for the first time, **Then** the weights are downloaded automatically from HuggingFace before synthesis begins

3. **Given** the synthesized audio file, **When** I inspect the output path, **Then** it is saved to `data/briefings/{run_id}/briefing.mp3`

4. **Given** the TTS service, **When** synthesis fails (model unavailable, OOM, etc.), **Then** a `StageError` with `retryable=False` is raised — the orchestrator catches it, logs it, and continues the Run without audio (not a fatal Run failure)

5. **Given** a successful synthesis, **When** the orchestrator handles the result, **Then** the `BriefingOutput` DB record is updated with `audio_path` — `markdown_path` is always set regardless of audio success/failure

## Tasks / Subtasks

- [ ] Implement `app/services/tts.py` (AC: 1–4)
  - [ ] `_pipeline = None` — lazy singleton for the Kokoro pipeline
  - [ ] `def _get_pipeline()`: initialize `kokoro.KPipeline(lang_code="a")` (American English) if not cached; downloads weights on first call
  - [ ] `async def synthesize(script: str, output_path: Path) -> None`:
    - [ ] Apply pronunciation guide substitutions before synthesis (accept optional `pronunciation_guide: dict` param)
    - [ ] Call `_get_pipeline()` in executor (blocking): `loop.run_in_executor(None, _synthesize_sync, script, output_path)`
    - [ ] Wrap all exceptions in `StageError("tts", str(e), retryable=False)`
  - [ ] `def _synthesize_sync(script: str, output_path: Path) -> None`: call Kokoro, write mp3 to `output_path`

- [ ] Add TTS stage call in pipeline orchestrator (AC: 4, 5)
  - [ ] The assemble stage (Story 5.3) writes `briefing.md`; the orchestrator then calls `tts.synthesize()` as a separate step
  - [ ] If `StageError` from TTS: log error, continue to QA gate, set `audio_path = None` on `BriefingOutput`
  - [ ] If synthesis succeeds: set `audio_path = str(audio_file_path)` on `BriefingOutput`
  - [ ] `markdown_path` is always written regardless of audio outcome

- [ ] Write tests in `tests/services/test_tts.py` (AC: 1, 4)
  - [ ] Mock `_get_pipeline()` to avoid downloading model
  - [ ] Test synthesis writes file to output_path
  - [ ] Test exception from Kokoro raises `StageError(retryable=False)`

## Dev Notes

### Kokoro API

The `kokoro` package (Apache 2.0, 82M params) API:

```python
from kokoro import KPipeline
pipeline = KPipeline(lang_code="a")  # "a" = American English
generator = pipeline(script, voice="af_heart", speed=1.0)
for gs, ps, audio in generator:
    # audio is numpy array of samples
    ...
```

Write samples to mp3 using `soundfile` or `scipy.io.wavfile`. Check `kokoro` package for its preferred output method — it may include a helper. If kokoro doesn't export mp3 directly, write WAV first then convert (ffmpeg or pydub if available). Do NOT add heavy dependencies without checking.

### Audio failure isolation

Audio failure is the only stage in the entire pipeline that is non-fatal. The orchestrator must explicitly catch the `StageError` from TTS and continue. This is unique to this stage — all other `StageError`s trigger the retry sequence. TTS audio failure goes directly to "audio_path = None" with no retry.

### Output path

`data/briefings/{run_id}/briefing.mp3` — same directory as `briefing.md`. Directory already created by assemble stage.

### Pronunciation guide application

Before synthesizing, do simple string replacement: for each entry in `pronunciation_guide`, replace term with pronunciation in the script. E.g. replace "FAISS" with "fais" so Kokoro pronounces it correctly.

### References

- [Source: docs/ARCHITECTURE.md § "External Integrations — Kokoro TTS"] — `services/tts.py`, no auth needed
- [Source: docs/ARCHITECTURE.md § "Structure Patterns — Briefing Output Files"] — `data/briefings/{run_id}/briefing.mp3`
- [Source: docs/epics-stories.md § "Story 6.2"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
