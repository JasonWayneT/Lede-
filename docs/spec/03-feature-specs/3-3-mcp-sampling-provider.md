# Story 3.3: MCP Sampling Provider and Fallback

Status: ready-for-dev

## Story

As a user running Briefing via Claude Desktop or Hermes,
I want pipeline LLM calls to route through the host model's sampling capability,
so that I can use Claude quality without paying separate API token costs.

## Acceptance Criteria

1. **Given** `config.llm_provider = "mcp_sampling"` and an active MCP session with a host that supports sampling, **When** I call `llm.complete(prompt, config)`, **Then** the request is made via `server.create_message()` to the MCP host and the response text is returned

2. **Given** `config.llm_provider = "mcp_sampling"` but no active MCP sampling context is available, **When** I call `llm.complete(prompt, config)`, **Then** the call falls back to the Ollama provider and a WARNING log line is emitted noting the fallback

3. **Given** a pipeline stage making an LLM call, **When** `config.llm_provider = "mcp_sampling"`, **Then** the stage code is unchanged — it still calls `llm.complete(prompt, config)` with no awareness of the provider

## Tasks / Subtasks

- [ ] Add `mcp_sampling` branch to `llm.py` (AC: 1, 2, 3)
  - [ ] Add module-level `_mcp_server_context: Any = None` — set by `mcp_server.py` at startup, `None` when running in web UI mode
  - [ ] Add `def set_mcp_server(server) -> None` — called by `mcp_server.py` to register the active MCP server instance
  - [ ] In `mcp_sampling` branch: check if `_mcp_server_context` is not `None` and supports `create_message`
  - [ ] If available: call `await _mcp_server_context.create_message(messages=[{"role": "user", "content": {"type": "text", "text": prompt}}], max_tokens=2048)` and extract response text
  - [ ] If not available: log `logger.warning("MCP sampling not available, falling back to Ollama")` and call `_ollama_complete(prompt, config, system)`
  - [ ] Wrap errors in `StageError("llm", message, code=PROVIDER_UNAVAILABLE, retryable=True)`

- [ ] Register server in `app/mcp_server.py` (AC: 1)
  - [ ] After creating MCP `Server` instance, call `llm.set_mcp_server(server)`
  - [ ] This registers the context so `mcp_sampling` branches can find it

- [ ] Write tests in `tests/services/test_llm.py` (AC: 1, 2)
  - [ ] Mock `_mcp_server_context` with a mock object that has `create_message`
  - [ ] Test successful sampling call returns response text
  - [ ] Test fallback to Ollama when context is `None`, including WARNING log assertion

## Dev Notes

### MCP SDK create_message

The `mcp` Python SDK's server object exposes `create_message()` for sampling requests to the host. The exact API depends on the SDK version — check `mcp` package docs. Pattern:

```python
result = await server.create_message(
    messages=[SamplingMessage(role="user", content=TextContent(type="text", text=prompt))],
    max_tokens=2048
)
return result.content.text
```

### Why a module-level reference

`llm.py` cannot import from `mcp_server.py` (entry point isolation rule). The reverse is fine: `mcp_server.py` imports `llm` and calls `llm.set_mcp_server(server)`. This is the only clean pattern that avoids circular imports.

### Fallback is silent to stages

Stages never know which provider was used. The fallback is transparent: the stage calls `llm.complete()`, gets a string back, proceeds. The only indication of fallback is the WARNING log.

### `mcp_sampling` not selectable from web UI

In Settings, `mcp_sampling` appears as an option but shows a note: "Only available when running via Claude Desktop or Hermes MCP." If selected in web UI mode, all calls will fall back to Ollama.

### References

- [Source: docs/ARCHITECTURE.md § "MCP Architecture — MCP sampling as LLM provider"] — `server.create_message()`, falls back to Ollama
- [Source: docs/ARCHITECTURE.md § "Shared Core Rule"] — `pipeline/`, `services/`, `core/` never import from entry points
- [Source: docs/epics-stories.md § "Story 3.3"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
