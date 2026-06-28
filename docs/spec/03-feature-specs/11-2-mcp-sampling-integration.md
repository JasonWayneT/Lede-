# Story 11.2: MCP Sampling Integration in llm.py

Status: ready-for-dev

## Story

As a user running Briefing via Claude Desktop with Sonnet,
I want pipeline LLM calls to use the host Claude model when MCP sampling is available,
so that I get Claude quality for synthesis without paying separate API token costs.

## Acceptance Criteria

1. **Given** the MCP server running inside a Claude Desktop session, **When** `config.llm_provider = "mcp_sampling"` and a stage calls `llm.complete(prompt, config)`, **Then** the call uses `server.create_message()` to route the prompt to the Claude host model

2. **Given** `config.llm_provider = "mcp_sampling"` but the server is running without a sampling-capable host, **When** `llm.complete()` is called, **Then** the call falls back silently to Ollama and logs a WARNING: `"MCP sampling not available, falling back to Ollama"`

3. **Given** switching the MCP host from Claude to a smaller model in Hermes, **When** the Hermes session uses a different model, **Then** pipeline calls automatically use the Hermes-configured model — no config change needed in Briefing

## Tasks / Subtasks

- [ ] Verify `llm.set_mcp_server()` and `_mcp_server_context` are implemented in Story 3.3 (AC: 1–3)
  - [ ] This story validates the end-to-end integration with a real MCP session context
  - [ ] Confirm `server.create_message()` call works with the actual `mcp` SDK

- [ ] Test with Claude Desktop (manual AC: 1)
  - [ ] Configure `claude_desktop_config.json` per architecture doc
  - [ ] Set `config.llm_provider = "mcp_sampling"` in `.env`
  - [ ] Trigger a Run from Claude Desktop and verify pipeline LLM calls route to Claude

- [ ] Write automated tests in `tests/mcp/test_trigger_briefing.py` (AC: 1, 2)
  - [ ] Mock `server.create_message()` returning a text response
  - [ ] Test that `llm.complete()` with `mcp_sampling` calls `create_message` when server context is set
  - [ ] Test fallback when context is None

## Dev Notes

### Primary implementation is in Story 3.3

This story is the integration verification for Story 3.3's MCP sampling implementation. If Story 3.3 is complete, Story 11.2 adds only the end-to-end test and any adjustments needed after actual SDK testing.

### create_message API (MCP SDK)

The exact API for `server.create_message()` depends on the `mcp` SDK version. Check the installed version with `uv run pip show mcp`. The general shape:

```python
from mcp.types import SamplingMessage, TextContent as MCPTextContent

result = await server.create_message(
    messages=[SamplingMessage(role="user", content=MCPTextContent(type="text", text=prompt))],
    max_tokens=2048
)
return result.content.text
```

### Host model transparency (AC: 3)

When running in Hermes, `server.create_message()` automatically uses whatever model Hermes is configured to provide. Briefing does not specify a model for sampling requests — it asks the host to respond. The host decides the model. This is the design intent.

### References

- [Source: docs/ARCHITECTURE.md § "MCP Architecture — MCP sampling as LLM provider"] — `server.create_message()`, fallback to Ollama
- [Source: docs/epics-stories.md § "Story 11.2"] — acceptance criteria
- [Source: story 3-3-mcp-sampling-provider.md] — primary implementation

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
