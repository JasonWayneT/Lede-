# Story 10.2: Onboarding Status and Revisit in Settings

Status: ready-for-dev

## Story

As a returning user who skipped steps during onboarding,
I want to complete or reconfigure any setup item from the Settings page,
so that I can set things up at my own pace without going through the full wizard again.

## Acceptance Criteria

1. **Given** the Settings page, **When** I view the Setup Status section, **Then** each item shows its status: Gmail (Authorized / Not authorized), Kokoro (Downloaded / Not downloaded), Sections (N configured), LLM Provider (configured provider), Schedule (cadence and time or Off)

2. **Given** a status item showing "Not configured", **When** I click it, **Then** I am taken directly to the relevant Settings section for that item

3. **Given** I complete a previously skipped item from Settings, **When** I save, **Then** its status in the Setup Status section updates to the configured state

## Tasks / Subtasks

- [ ] Implement `GET /api/settings/status` in `app/api/settings.py` (AC: 1)
  - [ ] Check each setup item:
    - [ ] `gmail`: `credentials.get(GMAIL_OAUTH_TOKEN)` → Authorized / Not authorized
    - [ ] `kokoro`: check if Kokoro model weights exist in local HF cache → Downloaded / Not downloaded
    - [ ] `sections`: `len(config.sections)` (excluding "Other") → "N configured"
    - [ ] `llm_provider`: `config.llm_provider` → provider name
    - [ ] `schedule`: `config.schedule_cadence` + `config.schedule_time` → "Daily at 7:00 AM" or "Off"
  - [ ] Return `{"data": {"gmail": {...}, "kokoro": {...}, "sections": {...}, "llm": {...}, "schedule": {...}}}`

- [ ] Add Setup Status panel to `app/templates/settings.html` (AC: 1–3)
  - [ ] At top of Settings page: "Setup Status" section
  - [ ] Each item as a row: icon (✓ / ✗), label, status text, link to relevant section
  - [ ] Clicking "Not authorized / Not configured" items → anchor link to the relevant section on the same page or HTMX scroll

- [ ] Update status dynamically after saves (AC: 3)
  - [ ] After each successful settings PUT, HTMX refreshes the Setup Status panel via `GET /api/settings/status`
  - [ ] Use `hx-trigger="every 0s"` after settings save or manual HTMX swap

- [ ] Kokoro download check (AC: 1)
  - [ ] Check if model cache directory exists: `~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M` (or equivalent)
  - [ ] If not found: show download link / button that triggers the onboarding Kokoro download step

- [ ] Write tests in `tests/api/test_settings.py` (AC: 1)
  - [ ] Test GET /api/settings/status returns all fields
  - [ ] Test gmail = "not_authorized" when no token stored
  - [ ] Test schedule = "Off" when cadence = "off"

## Dev Notes

### Kokoro cache path

The HuggingFace cache for Kokoro depends on the model ID used in `tts.py`. Check `os.environ.get("HF_HOME", "~/.cache/huggingface")` for the cache base. The model directory name is determined by the model ID.

As a simpler check: attempt to initialize the Kokoro pipeline (without synthesizing) — if it succeeds without downloading, model is present.

### No re-running the wizard

Settings should not redirect to the onboarding wizard. Each setting has its own page section that allows direct configuration. The Setup Status panel is informational — clicking items links to Settings sections, not back to the wizard.

### References

- [Source: docs/epics-stories.md § "Story 10.2"] — acceptance criteria
- [Source: docs/epics-stories.md § "FR-17"] — user can return to any onboarding configuration from Settings at any time

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
