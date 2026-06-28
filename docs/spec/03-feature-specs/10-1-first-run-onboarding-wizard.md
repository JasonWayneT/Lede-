# Story 10.1: First-Run Onboarding Wizard

Status: ready-for-dev

## Story

As a new user setting up Briefing for the first time,
I want a guided setup wizard that walks me through authorization and configuration,
so that I can go from clone to first briefing in under 15 minutes.

## Acceptance Criteria

1. **Given** launching the app for the first time (no existing config or token), **When** I open http://localhost:8000, **Then** I am redirected to the onboarding wizard, not the dashboard

2. **Given** the wizard's first step, **When** I view it, **Then** it prompts me to authorize Gmail and explains the read-only access scope

3. **Given** completing OAuth authorization, **When** the token is stored, **Then** the wizard advances to the next step automatically

4. **Given** any step after OAuth, **When** I view it, **Then** a "Skip for now" button is visible and functional

5. **Given** the Kokoro model download step, **When** I reach it, **Then** the download starts automatically with a progress bar — no manual command needed

6. **Given** completing or skipping the wizard, **When** it closes, **Then** I land on the dashboard ready to click "Run Briefing"

7. **Given** reopening the app after completing onboarding, **When** the app initializes, **Then** the wizard does not appear — I go directly to the dashboard

8. **Given** the wizard completing with some steps skipped, **When** I view Settings, **Then** skipped items are shown as "Incomplete" with a prompt to configure them

## Tasks / Subtasks

- [ ] Implement onboarding state tracking (AC: 1, 7)
  - [ ] `data/settings.json`: add `"onboarding_complete": false` field (set to true when wizard completes or user explicitly closes it)
  - [ ] Middleware or route check in `main.py`: if `onboarding_complete == false` and request is not for `/setup/*`, redirect to `/setup`

- [ ] Implement wizard routes in `app/main.py` or new `app/api/setup.py` (AC: 1–8)
  - [ ] `GET /setup` → step 1 (Gmail OAuth)
  - [ ] `GET /setup/step/{N}` → specific step
  - [ ] `POST /setup/step/{N}/complete` → mark step done, advance to next
  - [ ] `POST /setup/step/{N}/skip` → skip step, advance to next
  - [ ] `POST /setup/complete` → set `onboarding_complete = true`, redirect to `/`

- [ ] Implement wizard steps (AC: 2–6)
  - [ ] Step 1 (required): Gmail OAuth — "Authorize Gmail" button triggers `POST /api/settings/gmail/reauthorize`; wizard polls for completion
  - [ ] Step 2 (auto): Kokoro download — download starts on page load, progress via SSE; "Skip" hides this step (Kokoro downloaded lazily on first TTS)
  - [ ] Step 3 (optional): Set Gmail label, sections, LLM provider (same forms as Settings)
  - [ ] Step 4 (optional): Schedule configuration
  - [ ] Final step: "You're all set!" → link to dashboard

- [ ] Create `app/templates/setup/` wizard templates (AC: 1–8)
  - [ ] `setup_base.html`: wizard layout with step progress indicator
  - [ ] `setup_step1.html`, `setup_step2.html`, etc.

- [ ] Write tests (AC: 1, 7)
  - [ ] Test redirect to `/setup` when `onboarding_complete = false`
  - [ ] Test no redirect when `onboarding_complete = true`

## Dev Notes

### Onboarding complete check

The most robust approach: on every `GET /` request, check `settings.onboarding_complete`. If false and no OAuth token stored, redirect to `/setup`. If false but OAuth is stored (user skipped wizard but has a token), let them through.

For V1: redirect if `onboarding_complete == false`. Simple and predictable.

### Kokoro download progress

Kokoro downloads via HuggingFace `huggingface_hub` library (transitive dependency of kokoro). Track download progress via a background task + SSE stream. Alternative: just show a spinner and let the download happen blocking in a thread — simpler and still acceptable UX.

### setup.py vs web wizard

The architecture references `setup.py` as a first-run onboarding script (CLI). The web wizard at `/setup` is the browser-based equivalent. Both exist: `setup.py` is the CLI path (for power users who want to configure before starting the server); the web wizard at `/setup` is the main path for browser users. This story implements the web wizard. `setup.py` may remain as a stub (Story 1.1 created it) and be fleshed out in this story or deferred.

### References

- [Source: docs/PRD.md § "UJ-3 — Builder sets up Briefing for the first time"] — under 15 minutes
- [Source: docs/ARCHITECTURE.md § "Requirements Overview — Onboarding"] — step-by-step wizard
- [Source: docs/epics-stories.md § "Story 10.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
