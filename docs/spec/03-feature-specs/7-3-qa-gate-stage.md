# Story 7.3: QA Gate Stage -- Pre-Delivery Validation

Status: implemented (Check 1 revised — see `CR-007`)

> **2026-07-06 update (`CR-007`):** Check 1 below originally required every *configured* section to
> have at least one story. Since `CR-007` (`select.py` now assigns freeform, LLM-generated section
> names instead of classifying against a fixed `config.sections` list — see `4-6-select-stage.md`),
> "every configured section has a story" is no longer a meaningful check: there is no longer a
> fixed, enumerable list of sections to check coverage against, and which topics show up is
> expected to vary run to run. Check 1 was rewritten to only require that *some* stories were
> drafted at all (a real regression signal — an empty briefing), and the code + existing tests
> already reflect this. This note brings the spec back in sync with that shipped behavior — see
> `AC-091`.

## Story

As a developer,
I want the QA gate stage to validate the assembled briefing before it is marked complete,
so that users never receive a silently broken or incomplete briefing.

## Acceptance Criteria

1. **Given** an assembled briefing, **When** the QA gate runs, **Then** it checks: at least one story was drafted overall (not per-section coverage — see update note above); every story has source attribution; the TTS script contains no unresolved markdown or raw URLs; estimated audio runtime is within a reasonable range (30 seconds to 90 minutes)

2. **Given** all QA checks passing, **When** the gate completes, **Then** `packet.qa_passed = True` and the orchestrator proceeds to finalize the Run

3. **Given** any QA check failing, **When** the gate completes, **Then** `packet.qa_passed = False` and a `StageError("qa_gate", description_of_failure, retryable=True)` is raised

4. **Given** the QA gate, **When** it runs, **Then** it makes no LLM calls — all checks are deterministic rule-based validations

## Tasks / Subtasks

- [ ] Implement `app/pipeline/stages/qa_gate.py` (AC: 1–4)
  - [ ] `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] Check 1 — section coverage: for each section in `config.sections`, verify at least one story in `packet.drafted_stories` has that `section_name`; failure message: "Section '{name}' has no stories"
  - [ ] Check 2 — source attribution: for each story in `packet.drafted_stories`, verify `story.get("sources")` is non-empty; failure message: "Story missing source attribution"
  - [ ] Check 3 — TTS script clean: verify `packet.tts_script` contains no `#`, `**`, `[`, `](`, or `http`; failure message: "TTS script contains unresolved markdown or URLs"
  - [ ] Check 4 — audio runtime estimate: estimate word count of `tts_script`, assume ~150 words/minute; check 0.5 min ≤ estimated_minutes ≤ 90 min; failure message: "Estimated audio runtime {N} min is outside acceptable range"
  - [ ] Collect all failures into a list before raising (check all, report all)
  - [ ] If any failures: `packet.qa_passed = False`; raise `StageError("qa_gate", "; ".join(failures), retryable=True)`
  - [ ] If no failures: `packet.qa_passed = True`; return packet
  - [ ] No `llm.complete()` calls — pure deterministic logic

- [ ] Write tests in `tests/pipeline/stages/test_qa_gate.py` (AC: 1–4)
  - [ ] Test all checks passing → `qa_passed = True`
  - [ ] Test missing section → `StageError` with descriptive message
  - [ ] Test story with empty sources → `StageError`
  - [ ] Test TTS script with `##` markdown → `StageError`
  - [ ] Test very short script (< 30 words) → `StageError`
  - [ ] Confirm no LLM import or call

## Dev Notes

### Check all before raising

Do not short-circuit on the first failure. Collect all failures and raise one `StageError` with all messages joined. This gives the retry system (Story 7.4) and the user a complete picture of what's wrong.

### Audio runtime estimation

At ~150 words/minute (typical broadcast pace), a 10-story standard briefing is roughly 10–15 minutes. The check prevents degenerate cases (empty script or infinite LLM loop output).

```python
word_count = len(packet.tts_script.split())
estimated_minutes = word_count / 150
```

### "Other" section in check 1

The "Other" section is the catch-all. Skip the "every configured section must have a story" check for "Other" — it may legitimately be empty if all clusters matched configured sections.

### QA gate is stage 10 (last)

Even though it's the last stage, it still follows the stage interface. The orchestrator writes its artifact to `stage_10_qa_gate.json` before finalization.

### References

- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — stage signature
- [Source: docs/epics-stories.md § "Story 7.3"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
