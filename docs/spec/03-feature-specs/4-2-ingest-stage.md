# Story 4.2: Ingest Stage -- Gmail Emails to HandoffPacket

Status: ready-for-dev

## Story

As a developer running the pipeline,
I want the ingest stage to fetch unprocessed emails and place them in the HandoffPacket,
so that all subsequent stages have the raw email data they need.

## Acceptance Criteria

1. **Given** a valid Gmail OAuth token and a configured label with unprocessed emails, **When** the ingest stage runs, **Then** it returns a HandoffPacket with the `emails` field populated with all unprocessed emails from the label

2. **Given** zero unprocessed emails in the label, **When** the ingest stage runs, **Then** it returns a HandoffPacket with `emails = []` and sets a flag that causes the orchestrator to halt the Run with status `"no_new_emails"`

3. **Given** a Gmail API failure during ingest, **When** the stage encounters the error, **Then** it raises `StageError("ingest", message, retryable=True)` — the HandoffPacket is not written to disk for this stage

4. **Given** the ingest stage completing successfully, **When** the orchestrator processes the result, **Then** the HandoffPacket is written to `data/artifacts/{run_id}/stage_01_ingest.json` before the next stage begins

5. **Given** the ingest stage function signature, **When** I inspect it, **Then** it matches: `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`

## Tasks / Subtasks

- [ ] Implement `app/pipeline/stages/ingest.py` (AC: 1–5)
  - [ ] Implement `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] Call `await gmail.fetch_unprocessed_emails(config, session)` — get session from `db.database.get_session()`
  - [ ] Assign result to `packet.emails`
  - [ ] If `len(packet.emails) == 0`: set `packet.early_halt = True`, `packet.halt_reason = "no_new_emails"`, return packet
  - [ ] Wrap all exceptions in `StageError("ingest", str(e), retryable=True)` except those already `StageError`

- [ ] Verify orchestrator handles `early_halt` (AC: 2, 4)
  - [ ] After ingest stage returns, orchestrator checks `packet.early_halt`
  - [ ] If true: set `Run.status = "no_new_emails"`, emit SSE status event, stop pipeline without error
  - [ ] Do NOT write artifact to disk for the early halt path (no partial packet to persist)
  - [ ] On success (emails found): write packet to disk before next stage

- [ ] Write tests in `tests/pipeline/stages/test_ingest.py` (AC: 1–5)
  - [ ] Mock `gmail.fetch_unprocessed_emails` returning a list of email dicts
  - [ ] Test `early_halt` flag set when empty list returned
  - [ ] Test `StageError` propagated on Gmail failure
  - [ ] Test function signature matches interface

## Dev Notes

### Stage interface (non-negotiable)

```python
async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
```

Every stage must match this exact signature. The orchestrator calls all stages uniformly.

### DB session in stage

The ingest stage is the only stage that needs a DB session (to query processed_emails). Pattern: inject session via `async with get_session() as session:` inside the stage's `run()` function. Do not accept session as a parameter — that would break the uniform stage interface.

### No direct Gmail API calls in stage

The stage calls `gmail.fetch_unprocessed_emails(config, session)` from `app.services.gmail`. It does not import `googleapiclient` directly.

### Logging

```python
logger = logging.getLogger(__name__)
logger.info(f"Ingest: fetched {len(packet.emails)} unprocessed emails", extra={"run_id": packet.run_id})
```

### References

- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — `async def run(packet, config) -> HandoffPacket`
- [Source: docs/ARCHITECTURE.md § "Structure Patterns — Handoff Artifact Files"] — `stage_01_ingest.json`
- [Source: docs/epics-stories.md § "Story 4.2"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
