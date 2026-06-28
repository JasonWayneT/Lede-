# Story 7.4: Three-Tier Retry and Hold State

Status: ready-for-dev

## Story

As a user,
I want the pipeline to automatically attempt recovery when a stage fails, and surface a clear Needs Review state when it cannot recover automatically,
so that I am never left with a silent failure and always have a manual option.

## Acceptance Criteria

1. **Given** a stage raising `StageError` with `retryable=True`, **When** the orchestrator catches it, **Then** Tier 1: the failing stage is retried once with a concise error message injected into the stage's context prompt

2. **Given** Tier 1 retry also failing, **When** the orchestrator handles the second failure, **Then** Tier 2: the stage is retried once more with expanded context and explicit correction guidance in the prompt

3. **Given** Tier 2 retry also failing, **When** the orchestrator handles the third failure, **Then** `Run.status` is set to `"hold"`, the briefing appears in history marked "Needs Review", and the error description is stored in `Run.error`

4. **Given** a Run in Hold state, **When** the user views it in history, **Then** they see: the stage that failed, a plain-English description of the issue, and a "Retry" button

5. **Given** the user clicking "Retry" on a held Run, **When** the retry is triggered, **Then** the pipeline resumes from the failed stage using the persisted HandoffPacket artifacts — it does not restart from ingest

6. **Given** a `StageError` with `retryable=False`, **When** the orchestrator catches it, **Then** it skips the retry tiers and immediately enters Hold state

7. **Given** any failure, **When** the orchestrator handles it, **Then** an error event is emitted to the SSE queue — the failure is always visible in the live log

## Tasks / Subtasks

- [ ] Implement `_retry` in `app/pipeline/orchestrator.py` (AC: 1–3, 6, 7)
  - [ ] `async def _retry(stage_module, stage_num: int, stage_name: str, packet: HandoffPacket, config: AppConfig, error: StageError) -> HandoffPacket`:
    - [ ] Emit SSE error event immediately (AC: 7)
    - [ ] If `not error.retryable`: goto Hold state immediately
    - [ ] **Tier 1:** inject `error.message` into `config._retry_context = {"tier": 1, "error": error.message}`; call `await stage_module.run(packet, config)`
    - [ ] If Tier 1 succeeds: return packet
    - [ ] **Tier 2:** set `config._retry_context = {"tier": 2, "error": error.message, "guidance": "Attempt with expanded context..."}`; call `await stage_module.run(packet, config)` again
    - [ ] If Tier 2 succeeds: return packet
    - [ ] **Hold:** set `Run.status = "hold"`, `Run.error = f"[{stage_name}] {error.message}"`, commit; emit SSE error event; raise `HoldException` to stop pipeline

- [ ] Implement retry context in stages (AC: 1, 2)
  - [ ] Add `_retry_context: dict = field(default_factory=dict)` to `AppConfig` (or pass as separate param)
  - [ ] LLM stages check for retry context and prepend error correction instruction to prompt if present

- [ ] Implement partial rerun from Hold state (AC: 5)
  - [ ] `POST /api/briefings/{run_id}/retry` endpoint in `api/briefings.py`
  - [ ] Load last successful artifact from `data/artifacts/{run_id}/stage_XX_*.json`
  - [ ] Reconstruct `HandoffPacket` from disk via `handoff.read_packet()`
  - [ ] Resume pipeline from the failed stage (find stage by `Run.error` field)
  - [ ] Set `Run.status = "running"` before resuming

- [ ] Write tests in `tests/pipeline/test_orchestrator.py` (AC: 1–7)
  - [ ] Test Tier 1 retry called on retryable error
  - [ ] Test Tier 2 retry called after Tier 1 failure
  - [ ] Test Hold state set after Tier 2 failure, `Run.error` populated
  - [ ] Test `retryable=False` skips to Hold immediately
  - [ ] Test SSE error event emitted on every failure

## Dev Notes

### Retry context injection

The cleanest approach is to add `_retry_context: dict = {}` as a mutable field on `AppConfig` (or a separate simple dict). Stages that call `llm.complete()` check this field and prepend a correction note if non-empty:

```python
if config._retry_context:
    tier = config._retry_context.get("tier", 1)
    prev_error = config._retry_context.get("error", "")
    correction = f"[Previous attempt failed: {prev_error}. Correct the issue.]\n\n"
    prompt = correction + prompt
```

### Hold state display

`Run.error` stores the failure description. In history (Story 8.3), runs with `status = "hold"` show a "Needs Review" badge and the content of `Run.error` as the description.

### Partial rerun (AC: 5)

Load the last written artifact before the failed stage. E.g. if stage 5 (select) failed: load `stage_04_cluster.json` → reconstruct packet → call stages 5–10. Do NOT reload from stage 1.

### Retry does NOT apply to TTS

TTS failure (Story 6.2) is non-fatal and bypasses the retry system entirely. Only `StageError` from the 10 numbered pipeline stages triggers retry.

### References

- [Source: docs/ARCHITECTURE.md § "Process Patterns — Retry Pattern"] — 3-tier retry, orchestrator only
- [Source: docs/ARCHITECTURE.md § "Data Architecture — Processed Log atomicity"] — do not write ProcessedEmail on failure
- [Source: docs/epics-stories.md § "Story 7.4"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
