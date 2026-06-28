# Story 11.1: MCP Server Entry Point and Tool Definitions

Status: ready-for-dev

## Story

As a developer or AI agent user,
I want a standalone MCP server exposing the four core briefing tools over stdio,
so that Claude Desktop or Hermes can control Briefing without launching the web UI.

## Acceptance Criteria

1. **Given** running `uv run python -m app.mcp_server`, **When** the process starts, **Then** it initializes the MCP server over stdio without starting FastAPI or a web server

2. **Given** the MCP server running, **When** a client calls `trigger_briefing` with optional `depth` argument, **Then** a Run is started via the pipeline orchestrator and the `run_id` is returned as a text response

3. **Given** the MCP server running, **When** a client calls `get_run_status` with a `run_id`, **Then** the current Run status (`pending`, `running`, `complete`, `failed`, `hold`) is returned

4. **Given** the MCP server running, **When** a client calls `list_briefings`, **Then** a list of past completed Runs is returned with date, story count, and section breakdown

5. **Given** the MCP server running, **When** a client calls `get_briefing_content` with a `run_id` and `content_type` (`"markdown"` or `"script"`), **Then** the requested file content is returned as text

6. **Given** `mcp_server.py`, **When** I inspect its imports, **Then** it imports from `pipeline/`, `core/`, `db/` only — no import of `api/`, `main.py`, or FastAPI

7. **Given** the Claude Desktop config from the architecture doc added to `claude_desktop_config.json`, **When** Claude Desktop loads, **Then** it can discover and call all four tools

## Tasks / Subtasks

- [ ] Implement `app/mcp_server.py` (AC: 1–7)
  - [ ] `from mcp.server import Server; from mcp.server.stdio import stdio_server`
  - [ ] `server = Server("briefing")`
  - [ ] Register `llm.set_mcp_server(server)` for MCP sampling support
  - [ ] Initialize DB: `asyncio.run(init_db())` before serving

- [ ] Implement `trigger_briefing` tool (AC: 2)
  - [ ] `@server.call_tool()` on `"trigger_briefing"`
  - [ ] Arguments: `{"depth": "standard"}` (optional)
  - [ ] Call `await orchestrator.start_run(config)` — returns `run_id`
  - [ ] Return `[TextContent(type="text", text=f"Run {run_id} started")]`

- [ ] Implement `get_run_status` tool (AC: 3)
  - [ ] Arguments: `{"run_id": int}`
  - [ ] Query `Run` table by ID; return status string

- [ ] Implement `list_briefings` tool (AC: 4)
  - [ ] No arguments
  - [ ] Query completed Runs (last 20); return JSON string

- [ ] Implement `get_briefing_content` tool (AC: 5)
  - [ ] Arguments: `{"run_id": int, "content_type": "markdown"|"script"}`
  - [ ] Read `data/briefings/{run_id}/briefing.md` or `briefing.mp3` path from `BriefingOutput`
  - [ ] Return file content as text (for markdown), or audio file path (for script/audio)

- [ ] Register tools using `@server.list_tools()` (AC: 7)
  - [ ] Return `Tool` objects for all four tools with descriptions and input schemas

- [ ] Write tests in `tests/mcp/` (AC: 2–5)
  - [ ] Use MCP test client or mock server to test each tool
  - [ ] Test `trigger_briefing` returns run_id
  - [ ] Test `get_run_status` with valid and invalid run_id
  - [ ] Test `get_briefing_content` returns file content

## Dev Notes

### MCP Python SDK pattern

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("briefing")

@server.list_tools()
async def list_tools():
    return [Tool(name="trigger_briefing", description="...", inputSchema={...}), ...]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "trigger_briefing":
        run_id = await orchestrator.start_run(config)
        return [TextContent(type="text", text=f"Run {run_id} started")]
    ...

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Claude Desktop config (for README/user docs)

```json
{
  "mcpServers": {
    "briefing": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp_server"],
      "cwd": "/path/to/briefing"
    }
  }
}
```

### Tool parameter naming

All tool names: `snake_case`. Parameter names: `snake_case`. These are the four defined tools — do not add new tools without updating the architecture doc.

### Entry point isolation

`mcp_server.py` does NOT import `fastapi`, `uvicorn`, or anything from `app/api/`. It imports `orchestrator`, `db`, `core` only.

### References

- [Source: docs/ARCHITECTURE.md § "MCP Architecture"] — tool names, stdio transport, entry point isolation
- [Source: docs/epics-stories.md § "Story 11.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
