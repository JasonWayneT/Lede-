# Story 2.3: Processed Log Management

Status: ready-for-dev

## Story

As a user,
I want the system to record which emails were processed after each successful Run and to be able to clear that log from Settings,
so that I am never shown the same newsletter content twice unless I choose to reprocess.

## Acceptance Criteria

1. **Given** a fully successful Run completing the QA gate, **When** the orchestrator finalizes the Run, **Then** all email IDs from that Run are written to the `processed_emails` table atomically in the same DB transaction as `Run.status = "complete"`

2. **Given** a Run that fails mid-pipeline, **When** I query the `processed_emails` table, **Then** no email IDs from the failed Run are present — the table is unchanged

3. **Given** the `processed_emails` table, **When** the ingest service queries for unprocessed emails, **Then** it issues a single query comparing fetched email IDs against the table

4. **Given** a user clicking "Clear Processed Log" in Settings, **When** the action completes, **Then** all rows are deleted from the `processed_emails` table; the next Run fetches all emails under the label regardless of previous runs

5. **Given** the clear log action, **When** it executes, **Then** no changes are made to Gmail — only the local `processed_emails` table is affected

## Tasks / Subtasks

- [ ] Implement atomic commit in `app/pipeline/orchestrator.py` (AC: 1, 2)
  - [ ] On Run completion (after QA gate passes): open a single DB transaction
  - [ ] Within the same transaction: set `Run.status = "complete"` AND insert all `ProcessedEmail` records for the run
  - [ ] If any DB write fails, rollback the entire transaction — email IDs are NOT committed on failure
  - [ ] On pipeline failure (any stage error reaching Hold): do NOT write `ProcessedEmail` records

- [ ] Implement dedup query in `app/services/gmail.py` (AC: 3)
  - [ ] Single query: `SELECT email_id FROM processed_emails WHERE email_id IN (:ids)` where `:ids` are the Gmail-fetched IDs
  - [ ] Filter fetched messages to exclude matching IDs before returning

- [ ] Implement clear log endpoint in `app/api/settings.py` (AC: 4, 5)
  - [ ] `DELETE /api/settings/processed-log` route
  - [ ] Execute: `DELETE FROM processed_emails` (all rows)
  - [ ] Return `{"data": {"cleared": true, "rows_deleted": N}}`
  - [ ] No Gmail API call — local DB only

- [ ] Write tests (AC: 1–5)
  - [ ] Test atomicity: simulate QA gate success → verify both `Run.status` and `ProcessedEmail` records committed together
  - [ ] Test atomicity: simulate mid-pipeline failure → verify `processed_emails` table unchanged
  - [ ] Test clear endpoint: verify all rows deleted, Gmail untouched (mocked)

## Dev Notes

### Transaction pattern (SQLAlchemy async)

```python
async with session.begin():
    run.status = "complete"
    session.add(run)
    for email_id in packet.email_ids:
        session.add(ProcessedEmail(email_id=email_id, run_id=run.id))
# commit happens automatically on context manager exit
```

If an exception occurs inside `begin()`, the context manager rolls back automatically.

### Atomicity is non-negotiable

The architecture explicitly states: "Processed Log atomicity: Written only after full Run success — partial run failures must not pollute the log." This is the core invariant of this story. The orchestrator must never write `ProcessedEmail` records in a separate transaction from `Run.status = "complete"`.

### No separate "log file"

Despite the epics file using "Processed Log" terminology, the implementation is the `processed_emails` SQLite table — not a JSON file or text file. Do not create a separate file-based log.

### References

- [Source: docs/ARCHITECTURE.md § "Data Architecture — Processed Log"] — SQLite table, atomic within same transaction as Run completion
- [Source: docs/ARCHITECTURE.md § "Cross-Cutting Concerns Identified — Processed Log atomicity"] — explicit atomicity requirement
- [Source: docs/epics-stories.md § "Story 2.3"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implemented atomic processed-log write on successful completion via `pipeline.orchestrator.finalize_run_success(...)` (single DB transaction sets run status + inserts ProcessedEmail rows).
- Implemented hold-state helper `pipeline.orchestrator.mark_run_hold(...)` that does not write ProcessedEmail rows.
- Implemented `DELETE /api/settings/processed-log` endpoint clearing all `processed_emails` rows (DB-only; no Gmail calls).
- Verification: `uv run pytest -q tests/pipeline/test_processed_log.py tests/api/test_processed_log.py` (PASS).

### File List

- `briefing/app/pipeline/orchestrator.py`
- `briefing/app/api/settings.py`
- `briefing/tests/pipeline/test_processed_log.py`
- `briefing/tests/api/test_processed_log.py`
