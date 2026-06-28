# Story 12.4: Service and MCP Tests

Status: ready-for-dev

## Story

As a developer,
I want tests for the LLM provider router, Gmail service, TTS service, and MCP tools,
so that service integrations and tool contracts are verified.

## Acceptance Criteria

1. **Given** `llm.complete()` with `provider = "ollama"` and a mocked Ollama HTTP response, **When** the test runs, **Then** the mocked response text is returned

2. **Given** `llm.complete()` with `provider = "mcp_sampling"` and no active MCP context, **When** the test runs, **Then** the call falls back to Ollama (mocked) and a WARNING is logged

3. **Given** the Gmail service with a mocked Gmail API client, **When** fetching emails, **Then** only emails not in the Processed Log are returned

4. **Given** the MCP `trigger_briefing` tool called with a mock orchestrator, **When** the test runs, **Then** the mock orchestrator's `start_run()` is called and the `run_id` is returned in the response

5. **Given** the MCP `list_briefings` tool with test DB entries, **When** the test runs, **Then** the correct list of briefings is returned

## Tasks / Subtasks

- [ ] Write `tests/services/test_llm.py` (AC: 1, 2)
  - [ ] Mock `httpx.AsyncClient.post` to return Ollama response JSON
  - [ ] Test Ollama branch: response text returned
  - [ ] Test `ConnectError` → `StageError(PROVIDER_UNAVAILABLE, retryable=True)`
  - [ ] Test `mcp_sampling` with `_mcp_server_context = None` → fallback to Ollama, WARNING logged
  - [ ] Test `mcp_sampling` with mocked `server.create_message` → response text returned
  - [ ] Test BYOK: mock OpenAI SDK, verify `AUTH_ERROR` on auth failure

- [ ] Write `tests/services/test_gmail.py` (AC: 3)
  - [ ] Mock Gmail API client (`googleapiclient.discovery.build`)
  - [ ] Seed test DB with processed email IDs
  - [ ] Test: fetched emails minus processed IDs = result
  - [ ] Test: empty result returns `[]` without raising
  - [ ] Test: `HttpError` raises `StageError(retryable=True)`

- [ ] Write `tests/services/test_tts.py`
  - [ ] Mock Kokoro pipeline
  - [ ] Test `synthesize()` calls pipeline and writes output file
  - [ ] Test exception → `StageError(retryable=False)`

- [ ] Write `tests/mcp/conftest.py` and MCP tool tests (AC: 4, 5)
  - [ ] MCP test client fixture: use `mcp.client.stdio` or mock server
  - [ ] `tests/mcp/test_trigger_briefing.py`: mock `orchestrator.start_run`, verify run_id returned
  - [ ] `tests/mcp/test_get_run_status.py`: seed DB with Run, verify status string returned
  - [ ] `tests/mcp/test_list_briefings.py`: seed DB with completed Runs, verify list returned
  - [ ] `tests/mcp/test_get_briefing_content.py`: create temp briefing file, verify content returned

## Dev Notes

### MCP tool testing approach

The MCP SDK may not have a clean in-process test client. Options:
1. Call tool handler functions directly (bypass MCP protocol): `result = await call_tool("trigger_briefing", {"depth": "standard"})`
2. Use `mcp.client.stdio` to spawn the MCP server as a subprocess and communicate

For V1 tests, option 1 (direct function calls) is simpler and sufficient. The protocol framing is tested by the MCP SDK itself.

### LLM WARNING log assertion

```python
import logging
with caplog.at_level(logging.WARNING, logger="app.services.llm"):
    result = await llm.complete(prompt, config_with_mcp_sampling)
assert "MCP sampling not available" in caplog.text
```

### Gmail dedup test

```python
# Seed DB
session.add(ProcessedEmail(email_id="email-1", run_id=1, processed_at=datetime.utcnow()))
await session.commit()

# Mock Gmail to return email-1 and email-2
# Expect only email-2 in result
result = await gmail.fetch_unprocessed_emails(config, session)
assert len(result) == 1
assert result[0]["email_id"] == "email-2"
```

### References

- [Source: docs/ARCHITECTURE.md § "Testing Standards"] — pytest fixtures, mock HandoffPackets
- [Source: docs/epics-stories.md § "Story 12.4"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
