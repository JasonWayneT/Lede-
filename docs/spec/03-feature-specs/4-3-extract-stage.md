# Story 4.3: Extract Stage -- HTML to Text

Status: ready-for-dev

## Story

As a developer,
I want the extract stage to convert raw newsletter HTML into clean structured text chunks with metadata,
so that downstream embedding and synthesis stages work with readable normalized content.

## Acceptance Criteria

1. **Given** a HandoffPacket with raw HTML emails, **When** the extract stage runs, **Then** it returns the packet with `extracted_texts` populated — one entry per email

2. **Given** a newsletter email with HTML body, **When** extraction runs, **Then** the output contains clean readable text with no HTML tags, tracking pixels, navigation chrome, or footer unsubscribe blocks

3. **Given** each extracted text entry, **When** I inspect it, **Then** it contains: `email_id` (str), `text` (str), `title` (str), `sender_name` (str), `date` (datetime)

4. **Given** an email with a malformed or empty HTML body, **When** extraction runs on that email, **Then** the email is skipped with a WARNING log entry — it does not cause a `StageError` for the whole stage

5. **Given** the extract stage, **When** I inspect it, **Then** it imports no LLM services — extraction is pure Python text processing

6. **Given** the stage completing successfully, **When** the orchestrator processes the result, **Then** the HandoffPacket is written to `data/artifacts/{run_id}/stage_02_extract.json`

## Tasks / Subtasks

- [ ] Implement `app/pipeline/stages/extract.py` (AC: 1–6)
  - [ ] `async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket`
  - [ ] For each email in `packet.emails`: call `_extract_one(email)` — catch exceptions per-email, log WARNING, skip
  - [ ] `_extract_one(email) -> dict | None`: parse HTML → clean text, return structured dict or `None` on failure
  - [ ] Assign results to `packet.extracted_texts` (list of dicts, one per successfully extracted email)
  - [ ] No `StageError` raised unless ALL emails fail (zero extracted texts is a valid reason to halt)

- [ ] Implement `_extract_one` HTML cleaner (AC: 2, 3)
  - [ ] Use `html.parser` from stdlib or `beautifulsoup4` if available (bs4 is NOT in the dependency list — use stdlib `html.parser`)
  - [ ] Strip: `<script>`, `<style>`, `<img>`, `<a>` tags (keep text content of `<a>`), tracking pixel `<img>` (0x0 images)
  - [ ] Remove footer patterns: lines containing "unsubscribe", "view in browser", "manage preferences" (case-insensitive)
  - [ ] Normalize whitespace: collapse multiple newlines/spaces
  - [ ] Extract `title` from `<title>` tag or email `Subject` header
  - [ ] Copy `sender_name`, `date` from email metadata (already parsed in Story 2.2)

- [ ] Write tests in `tests/pipeline/stages/test_extract.py` (AC: 1–5)
  - [ ] Test HTML with tracking pixels and footer is cleaned
  - [ ] Test malformed HTML (empty body) is skipped with WARNING
  - [ ] Test extracted dict has all required fields
  - [ ] Confirm no import of `llm` or any LLM service

## Dev Notes

### No bs4 in dependencies

`beautifulsoup4` is NOT in the `uv add` command from Story 1.1. Use Python stdlib `html.parser` via `html.parser.HTMLParser` subclass, OR use Python's `html.unescape()` + regex for simpler extraction. Do NOT add `bs4` as a dependency without updating Story 1.1.

If the HTML parsing proves too complex with stdlib, consider adding `lxml` (`uv add lxml`) — but check with the project owner first.

### Per-email error isolation (AC: 4)

This is the only stage where per-item error handling is required rather than a stage-level `StageError`. Design the loop explicitly:

```python
results = []
for email in packet.emails:
    try:
        extracted = _extract_one(email)
        if extracted:
            results.append(extracted)
    except Exception as e:
        logger.warning(f"Extract skipped email {email.get('email_id')}: {e}")
packet.extracted_texts = results
```

### No LLM calls (AC: 5)

Extraction is deterministic text processing. No calls to `llm.complete()`. This is enforced by AC 5 — the stage must be importable without LLM dependencies being present.

### References

- [Source: docs/ARCHITECTURE.md § "Pipeline Stage Interface"] — stage signature
- [Source: docs/ARCHITECTURE.md § "Structure Patterns — Handoff Artifact Files"] — `stage_02_extract.json`
- [Source: docs/epics-stories.md § "Story 4.3"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
