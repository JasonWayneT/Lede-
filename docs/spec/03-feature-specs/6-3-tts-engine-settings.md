# Story 6.3: TTS Engine Configuration in Settings

Status: implemented

> **2026-07-06 note:** verified against code during an audit pass (this spec was previously
> unverified/flagged as an open item). `GET/PUT /api/settings/tts` and `POST
> /api/settings/tts/test` in `app/api/settings.py` match ACs 1–4 exactly, including the
> `BUG-002` form-encoding fix already documented in the Dev Notes below.

## Story

As a user,
I want to select and test my TTS engine from the Settings page,
so that I can verify audio output quality before running a full briefing.

## Acceptance Criteria

1. **Given** the Settings -- Audio section, **When** I view it, **Then** the current TTS engine is shown (Kokoro as default)

2. **Given** I click "Test Voice", **When** the action completes, **Then** a short sample sentence is synthesized and plays in the browser

3. **Given** I select Orpheus TTS when my machine has no GPU, **When** I attempt to save, **Then** a hardware requirement warning is shown: "Orpheus requires a CUDA-compatible GPU"

4. **Given** the TTS engine setting changed and saved, **When** the next Run starts, **Then** the newly configured engine is used

## Tasks / Subtasks

- [ ] Add TTS engine field to `AppConfig` (AC: 1, 4)
  - [ ] `tts_engine: str = "kokoro"` — accepts `"kokoro"`, `"orpheus"`
  - [ ] `orpheus_requires_gpu: bool` — detect CUDA availability at runtime (see dev notes)

- [ ] Add Settings -- Audio section to `app/templates/settings.html` (AC: 1–3)
  - [ ] Show current engine with radio buttons: Kokoro (default) / Orpheus
  - [ ] "Test Voice" button: HTMX POST to `/api/settings/tts/test`
  - [ ] Orpheus radio shows inline warning if CUDA not detected
  - [ ] Save button: HTMX PUT to `/api/settings/tts`

- [ ] Implement TTS settings endpoints in `app/api/settings.py` (AC: 1–4)
  - [ ] `GET /api/settings/tts` → current engine, CUDA status
  - [ ] `PUT /api/settings/tts` → accepts form-encoded fields `engine`, `tts_voice` (`Form(...)`
        params — matches the plain HTML `<form hx-put="...">` in `settings.html`; switched from a
        JSON body in `cfce0a9`, see `BUG-002`); validate engine choice; if Orpheus and no CUDA,
        return 400 with warning message
  - [ ] `POST /api/settings/tts/test` → synthesize sample text "Welcome to your morning briefing." → return audio file or inline `<audio>` tag for browser playback

- [ ] Write tests in `tests/api/test_settings.py` (AC: 3, 4)
  - [ ] Test PUT with Orpheus + no CUDA → 400 with warning message
  - [ ] Test PUT with Kokoro → 200, engine saved

## Dev Notes

### Orpheus is V2 scope

The architecture document notes: "Orpheus TTS integration (requires GPU; V2 upgrade path)." For V1, Orpheus can appear as an option in the UI with the GPU warning, but synthesis via Orpheus does not need to be implemented — just the warning gate. The TTS service in Story 6.2 only implements Kokoro.

### CUDA detection

```python
try:
    import torch
    cuda_available = torch.cuda.is_available()
except ImportError:
    cuda_available = False
```

Do NOT add `torch` as a dependency. Check if it's already available (it may be pulled in by Kokoro or sentence-transformers). If not available, CUDA = False.

### Test Voice audio response

For the test voice endpoint, synthesize a short sentence and return it as `audio/mpeg` binary response, or write to a temp file and return a URL to it. The browser's `<audio>` element can play the response directly if HTMX injects it.

### References

- [Source: docs/ARCHITECTURE.md § "Deferred Decisions"] — Orpheus is V2
- [Source: docs/epics-stories.md § "Story 6.3"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
