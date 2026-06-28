# Story 12.5: README and Google OAuth Setup Guide

Status: ready-for-dev

## Story

As a new technical user,
I want a README that guides me from clone to first briefing in under 15 minutes,
so that I can get value from Briefing without needing to read source code.

## Acceptance Criteria

1. **Given** the README, **When** I read it, **Then** it contains in order: what Briefing does (1 paragraph), prerequisites (Python, uv, Ollama, Google Cloud project), installation steps, Google OAuth setup guide, first run instructions, and a settings overview

2. **Given** the Google OAuth setup guide section, **When** I follow it, **Then** I can create a Google Cloud project, enable the Gmail API, download `credentials.json`, and complete OAuth authorization without external documentation

3. **Given** the README installation steps followed on a fresh machine, **When** I run `uv run python setup.py`, **Then** onboarding completes without errors

4. **Given** the README, **When** I read it, **Then** it includes a troubleshooting section covering: Ollama not running, OAuth token expired, Kokoro download failing, and first run producing no stories

## Tasks / Subtasks

- [ ] Write `README.md` (AC: 1–4)
  - [ ] **Section 1 — What is Briefing**: 1 paragraph description matching the PRD vision
  - [ ] **Section 2 — Prerequisites**: Python 3.11+, uv, Ollama (with install link), Google Cloud project
  - [ ] **Section 3 — Installation**: `git clone`, `uv sync`, copy `.env.example` to `.env`
  - [ ] **Section 4 — Google OAuth Setup Guide** (AC: 2): step-by-step
    - [ ] Step 1: Create Google Cloud project at console.cloud.google.com
    - [ ] Step 2: Enable Gmail API
    - [ ] Step 3: Create OAuth 2.0 Client ID (Desktop app type)
    - [ ] Step 4: Download `credentials.json` and place in project root
    - [ ] Note: the file is gitignored — never commit it
  - [ ] **Section 5 — First Run**: `uv run python setup.py` → browser OAuth → `./briefing.sh` or `briefing.bat` → open http://localhost:8000 → click "Run Briefing"
  - [ ] **Section 6 — Settings Overview**: brief description of each settings section
  - [ ] **Section 7 — Troubleshooting** (AC: 4):
    - [ ] Ollama not running: "Run `ollama serve` in a terminal"
    - [ ] OAuth token expired: "Go to Settings → Gmail → Re-authorize Gmail"
    - [ ] Kokoro download failing: "Check HuggingFace connectivity; model: hexgrad/Kokoro-82M"
    - [ ] First run no stories: "Verify Gmail label matches your label exactly (case-sensitive)"
  - [ ] **Section 8 — Claude Desktop / MCP**: include the `claude_desktop_config.json` snippet from architecture doc

- [ ] Populate `pipeline_prompts/style-guide.md` (editorial style)
  - [ ] Audience: busy professional, reads/listens in 10-15 minutes
  - [ ] Tone: authoritative but accessible; no jargon without context
  - [ ] Format: spoken broadcast prose; no markdown in stories; clear attribution
  - [ ] Length guidance per depth tier

- [ ] Write tests to verify setup (AC: 3)
  - [ ] `tests/test_setup.py`: test that `setup.py` is importable without errors
  - [ ] Test that `briefing.sh` and `briefing.bat` contain the correct uvicorn command

## Dev Notes

### README target: technical but not expert

The PRD target user is a PM or builder — someone who can clone a repo and set up a Google Cloud project but is not necessarily a Python developer. The README should not assume Python expertise. Commands should be copy-pasteable.

### OAuth guide specificity

The OAuth guide must be self-contained (AC: 2). Users should not need to visit other documentation. Include screenshots descriptions if helpful (e.g. "On the Credentials page, click 'Create credentials' → 'OAuth client ID'").

### style-guide.md is read by the draft stage

`pipeline_prompts/style-guide.md` is included in draft and tts_prep prompts. Keep it concise (< 300 words) and directive — LLMs perform better with specific instructions than general guidance.

### Under 15 minutes (NFR-7)

The section ordering matters. Users should be able to skim the README, run the commands, and get a briefing in < 15 minutes. Put commands before explanations. Use numbered steps, not paragraphs.

### References

- [Source: docs/PRD.md § "UJ-3"] — under 15 minutes from clone to first briefing
- [Source: docs/ARCHITECTURE.md § "MCP Architecture — Claude Desktop config"] — `claude_desktop_config.json`
- [Source: docs/epics-stories.md § "Story 12.5"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
