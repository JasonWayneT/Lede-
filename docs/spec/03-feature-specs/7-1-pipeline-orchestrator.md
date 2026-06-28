# Story 7.1: Pipeline Orchestrator -- Stage Sequencing and DB Writes

Status: ready-for-dev

## Story

As a developer,
I want the pipeline orchestrator to execute all 9 stages in sequence, write HandoffPacket artifacts to disk after each stage, and write Run state to the database,
so that the pipeline is observable, recoverable, and produces durable artifacts.

## Acceptance Criteria

1. **Given** a Run is triggered, **When** the orchestrator starts, **Then** a Run record is created in the DB with `status="running"` before any stage executes

2. **Given** each stage completing successfully, **When** the orchestrator processes the result, **Then** the HandoffPacket is written to `data/artifacts/{run_id}/stage_{N:02d}_{name}.json` before the next stage starts

3. **Given** all stages completing successfully, **When** the orchestrator finalizes, **Then** `Run.status` is set to `"complete"` and `BriefingOutput` is written in the same DB transaction as `ProcessedEmail` records

4. **Given** a stage raising `StageError`, **When** the orchestrator catches it, **Then** it initiates the retry sequence from Story 7.4 before marking the Run failed or held

5. **Given** the orchestrator, **When** I inspect its imports, **Then** it imports from `pipeline/stages/*`, `pipeline/handoff.py`, `db/`, `core/errors.py`, and `api/stream.py` — it does not import from `main.py` or `mcp_server.py`

6. **Given** the orchestrator running as a FastAPI BackgroundTask, **When** the web server receives a new HTTP request during pipeline execution, **Then** the server remains responsive — the pipeline does not block the event loop

## Tasks / Subtasks

- [ ] Implement `app/pipeline/orchestrator.py` (AC: 1–6)
  - [ ] `async def run_pipeline(run_id: int, config: AppConfig) -> None` — called as BackgroundTask
  - [ ] Stage sequence: `[ingest, extract, embed, cluster, select, frame, draft, tts_prep, assemble, qa_gate]` with stage numbers 01–10
  - [ ] On start: open DB session, create `Run(status="running")`, commit, capture `run_id`
  - [ ] Loop through stages:
    - [ ] Emit SSE `status` event: `{"event": "status", "data": {"run_id": N, "status": "running", "current_stage": stage_name}}`
    - [ ] Call `await stage.run(packet, config)` inside `try/except StageError`
    - [ ] On success: write packet to disk via `handoff.write_packet(...)`; emit SSE `log` event
    - [ ] On `StageError`: call `_retry(stage, packet, config, error)` (from Story 7.4)
    - [ ] Check `packet.early_halt` after ingest — if True: set `Run.status = "no_new_emails"`, emit status event, return
  - [ ] On full success: atomic transaction — `Run.status = "complete"` + insert `ProcessedEmail` records + `BriefingOutput`
  - [ ] After assemble but before qa_gate: call `tts.synthesize()`, catch StageError gracefully (audio non-fatal)
  - [ ] Emit SSE `complete` event on success

- [ ] Add `start_run` entry point (AC: 1, 6)
  - [ ] `async def start_run(config: AppConfig) -> int` — creates Run record, enqueues BackgroundTask, returns `run_id`
  - [ ] Called by both `api/briefings.py` (web) and `mcp_server.py` (MCP)

- [ ] Write tests in `tests/pipeline/test_orchestrator.py` (AC: 1–5)
  - [ ] Mock all stages to return unchanged packets
  - [ ] Test `Run.status = "running"` set before stages execute
  - [ ] Test artifact written after each stage
  - [ ] Test atomic commit on success (Run + ProcessedEmail + BriefingOutput in same transaction)
  - [ ] Test `StageError` from a stage triggers retry call

## Dev Notes

### Stage list (exact order)

```python
STAGES = [
    (1, "ingest",   stages.ingest),
    (2, "extract",  stages.extract),
    (3, "embed",    stages.embed),
    (4, "cluster",  stages.cluster),
    (5, "select",   stages.select),
    (6, "frame",    stages.frame),
    (7, "draft",    stages.draft),
    (8, "tts_prep", stages.tts_prep),
    (9, "assemble", stages.assemble),
    (10, "qa_gate", stages.qa_gate),
]
```

TTS synthesis happens between assemble and qa_gate as a special non-stage call (audio failure is non-fatal).

### BackgroundTask isolation

The orchestrator runs in a `FastAPI BackgroundTask`. Do NOT `await` long-running operations on the web server's event loop without using an executor. sentence-transformers and FAISS are blocking — wrap in `run_in_executor`.

### DB session management

Open one session per pipeline run. Pass it to stages that need it (ingest) or manage it in the orchestrator for all DB writes. Do not open multiple sessions per run.

### References

- [Source: docs/ARCHITECTURE.md § "Layer Ownership — pipeline/orchestrator.py"] — owns stage sequencing, retry, DB writes, SSE emit
- [Source: docs/ARCHITECTURE.md § "Process Patterns — Retry Pattern"] — orchestrator owns retry, never stages
- [Source: docs/epics-stories.md § "Story 7.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
