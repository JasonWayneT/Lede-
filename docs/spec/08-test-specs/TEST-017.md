# Test Spec: TEST-017 Audio mixing

## Metadata

- Test ID: `TEST-017`
- Type: unit
- Status: passing
- Related requirements: `FR-031`
- Related acceptance criteria: `AC-080`, `AC-081`, `AC-082`, `AC-083`, `AC-084`, `AC-085`

## Purpose

Proves `app/services/mixing.py`: story segments mix a ducked/looped/faded bed under the voice;
structural segments render faded music-only stingers of the profile duration; no-music and
missing-file cases degrade to dry voice (non-fatal); output is 44.1 kHz stereo and clip-guarded;
and `story_weight` selects the mix profile. Includes one test that reads and mixes a real committed
MP3 clip (validates the soundfile MP3 read + scipy resample path), and confirms
`tts.synthesize_plan` writes a single mixed mp3 with per-segment durations.

## Preconditions

- Run from `briefing/` project root

## Steps

1. Run tests:
   - Command: `uv run pytest -q tests/services/test_mixing.py tests/services/test_tts.py`

## Expected result

- All tests pass (exit code 0)

## Automation notes

- Test files: `briefing/tests/services/test_mixing.py`, `briefing/tests/services/test_tts.py`
- Command: `uv run pytest -q tests/services/test_mixing.py tests/services/test_tts.py`
