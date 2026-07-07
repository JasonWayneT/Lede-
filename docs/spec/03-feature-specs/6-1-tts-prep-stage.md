# Story 6.1: TTS Prep Stage -- Spoken-Form Optimization

Status: superseded-in-part by Story 6.4 (CR-005)

> **Amendment (CR-005 / FR-030 / BUG-005).** This story's original design — one LLM call rewriting
> `assembled_markdown` into a single narration script with spoken segues — has been restructured.
> `tts_prep` now builds an **audio segment plan** from `packet.drafted_stories` (not
> `assembled_markdown`, which was empty at this stage — `BUG-005`). Narration text is the drafted
> prose cleaned deterministically; the LLM call is retained only for the pronunciation guide
> (non-fatal). Spoken section segues (original AC 3) are dropped in favor of Phase 5 musical
> stingers. `tts_script` is still populated (concatenated narration) for `qa_gate`/resume
> compatibility. See `docs/spec/03-feature-specs/6-4-audio-segment-plan.md` and
> `docs/spec/07-decisions/ADR-004.md`. Original ACs 1, 2, 4, 5, 6 still hold in spirit; AC 3
> (spoken segues) is superseded.

## Story

As a developer,
I want the TTS prep stage to rewrite the assembled briefing prose into a narration-optimized script,
so that the audio output sounds like a real broadcast rather than a text document read aloud.

## Acceptance Criteria

1. **Given** a HandoffPacket with `assembled_markdown`, **When** the TTS prep stage runs, **Then** `packet.tts_script` is populated with a spoken-form version of the briefing

2. **Given** the TTS script, **When** I read it, **Then** it contains no markdown syntax (no `#`, `**`, `_`, `[]`, etc.), no raw URLs, and no attribution brackets

3. **Given** section transitions in the briefing, **When** they appear in the TTS script, **Then** they are natural spoken segues (e.g. "Turning now to technology..." not `## Technology`)

4. **Given** proper nouns and acronyms in the briefing, **When** the TTS script is generated, **Then** a pronunciation guide is produced as `packet.pronunciation_guide` (dict mapping term to pronunciation)

5. **Given** the TTS prep stage, **When** it generates the script, **Then** it calls `llm.complete()` with a prompt from `pipeline_prompts/stages/tts_prep.md`

6. **Given** the stage completing, **When** the orchestrator processes it, **Then** the HandoffPacket is written to `data/artifacts/{run_id}/stage_09_tts_prep.json`

## Tasks / Subtasks

- [ ] Implement `app/pipeline/stages/tts_prep.py` (AC: 1–6)
  - [ ] `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] Load `pipeline_prompts/stages/tts_prep.md`
  - [ ] Pass `packet.assembled_markdown` to LLM via prompt
  - [ ] Ask LLM to return JSON: `{"tts_script": "...", "pronunciation_guide": {"GPT-4": "G-P-T-4", ...}}`
  - [ ] Parse response; assign `packet.tts_script` and `packet.pronunciation_guide`
  - [ ] If JSON parsing fails: assign raw response to `packet.tts_script`, assign `{}` to `packet.pronunciation_guide`, log WARNING
  - [ ] Wrap LLM errors in `StageError("tts_prep", str(e), retryable=True)`

- [ ] Create initial `pipeline_prompts/stages/tts_prep.md` (AC: 2–4)
  - [ ] Instruct LLM: strip all markdown, replace `##` section headers with spoken segues, spell out acronyms, remove URLs
  - [ ] Instruct LLM to return JSON with `tts_script` and `pronunciation_guide`
  - [ ] Example segue rewrites in the prompt for few-shot guidance

- [ ] Write tests in `tests/pipeline/stages/test_tts_prep.py` (AC: 1–5)
  - [ ] Mock `llm.complete` returning JSON with script and pronunciation guide
  - [ ] Test tts_script has no markdown
  - [ ] Test pronunciation_guide is a dict
  - [ ] Test fallback on JSON parse failure

## Dev Notes

### Why a two-pass approach is not needed

The architecture calls for a single TTS prep stage that takes `assembled_markdown` and returns `tts_script`. Do not split into two LLM calls (one for stripping, one for segues) — one well-prompted call handles both transformations.

### Token length concern

`assembled_markdown` may be long (many stories). If the LLM has a context limit issue, split the markdown by section, call LLM per section, then concatenate. This is an implementation detail not specified in the ACs — use single call first, add section splitting as a fallback.

### pronunciation_guide format

```json
{"pronunciation_guide": {"AI": "A-I", "FAISS": "fais", "GPT-4": "G-P-T-4"}}
```

The TTS service (Story 6.2) reads this guide before synthesis to pre-process the script.

### References

- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — stage signature
- [Source: docs/ARCHITECTURE.md § "Structure Patterns — Handoff Artifact Files"] — `stage_09_tts_prep.json`
- [Source: docs/epics-stories.md § "Story 6.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
