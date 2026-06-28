# Story 2.2: Label-Based Email Fetch Service

Status: ready-for-dev

## Story

As a user triggering a Run,
I want the system to fetch only newsletter emails from my configured Gmail label that have not been processed before,
so that each Run only processes new content.

## Acceptance Criteria

1. **Given** a configured Gmail label and a valid OAuth token, **When** the ingest service runs, **Then** only emails under that exact label are fetched

2. **Given** a Processed Log containing previously processed email IDs, **When** the ingest service fetches emails, **Then** emails whose IDs appear in the Processed Log are excluded from the fetched results

3. **Given** zero unprocessed emails exist under the label, **When** the ingest service runs, **Then** it returns an empty list and signals the orchestrator to halt the Run early with a "No new newsletters" status

4. **Given** a successful fetch, **When** I inspect the returned email objects, **Then** each contains: `email_id` (str), `subject` (str), `sender_name` (str), `sender_email` (str), `date` (datetime), `raw_html` (str)

5. **Given** the Gmail API call, **When** it fails due to a network error or quota limit, **Then** a `StageError` with `retryable=True` is raised — the Run does not crash silently

## Tasks / Subtasks

- [ ] Implement `gmail.fetch_unprocessed_emails(config, session)` in `app/services/gmail.py` (AC: 1–5)
  - [ ] Build Gmail service via `get_service()` (from Story 2.1)
  - [ ] List messages with label filter: `service.users().messages().list(userId="me", labelIds=[config.gmail_label]).execute()`
  - [ ] For each message ID, fetch full message: `service.users().messages().get(userId="me", id=msg_id, format="full").execute()`
  - [ ] Query `processed_emails` table: filter out IDs already present
  - [ ] Extract `email_id`, `subject`, `sender_name`, `sender_email`, `date`, `raw_html` from each unfiltered message
  - [ ] Return `[]` (empty list) if none remain after dedup — do NOT raise an error; the orchestrator handles the empty case
  - [ ] Wrap `googleapiclient.errors.HttpError` and network errors in `StageError("ingest", message, retryable=True)`

- [ ] Implement email field extraction helper (AC: 4)
  - [ ] Parse `From` header into `sender_name` and `sender_email` using `email.utils.parseaddr`
  - [ ] Parse `Date` header into `datetime` using `email.utils.parsedate_to_datetime`
  - [ ] Extract HTML body: walk MIME parts, prefer `text/html` over `text/plain`

- [ ] Write tests in `tests/services/test_gmail.py` (AC: 1–5)
  - [ ] Mock Gmail API client responses
  - [ ] Test dedup: emails with IDs in processed_emails table are excluded
  - [ ] Test empty result returns `[]` without raising
  - [ ] Test `HttpError` raises `StageError(retryable=True)`
  - [ ] Test extracted email object has all required fields

## Dev Notes

### Gmail API label filter

Gmail API `labelIds` filter accepts label names that match user-created labels exactly (case-sensitive). The `INBOX` system label is separate. If the user's label is `"Newsletters"`, pass `labelIds=["Newsletters"]`.

For user-created labels, you may need to first look up the label ID via `service.users().labels().list()` if `labelIds` with the display name does not filter correctly. Consider falling back to label ID lookup if display-name filtering returns unexpected results.

### Pagination

Gmail API `messages().list()` paginates (max 500 per page). Handle `nextPageToken` in a loop if needed. For typical newsletter volumes (< 100 emails), one page is sufficient — add pagination as a defensive check.

### HTML extraction

Use Python stdlib `email` package (already available) to decode MIME. No additional library needed. Decode base64 body parts with `base64.urlsafe_b64decode`.

### DB session dependency

`fetch_unprocessed_emails` needs a DB session to query `processed_emails`. Accept `session: AsyncSession` as a parameter — do NOT create a new session inside the service. The orchestrator provides the session.

### References

- [Source: docs/ARCHITECTURE.md § "External Integrations — Gmail API"] — auth via `core/credentials.py`
- [Source: docs/ARCHITECTURE.md § "Data Boundaries — Run state + history"] — ProcessedEmail in `db/models.py`
- [Source: docs/epics-stories.md § "Story 2.2"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implemented `gmail.fetch_unprocessed_emails(config, session)`:
  - Lists messages filtered by `config.gmail_label`
  - Dedups against `processed_emails` via a single DB query
  - Extracts required email fields including HTML body
- Verification: `uv run pytest -q tests/services/test_gmail.py` (PASS).

### File List

- `briefing/app/services/gmail.py`
- `briefing/tests/services/test_gmail.py`
