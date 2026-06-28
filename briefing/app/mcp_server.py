"""MCP server entry point — standalone, no FastAPI dependency."""

# Implements ARCH-001, FR-012

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from sqlalchemy import select

from app.core.config import AppConfig
from app.db.database import build_sqlite_db_url, get_session, init_db, init_engine
from app.db.models import BriefingOutput, Run
from app.pipeline import orchestrator
from app.services import llm

logger = logging.getLogger(__name__)

server = Server("briefing")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="trigger_briefing",
            description="Start a new briefing pipeline run. Returns the run_id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "depth": {
                        "type": "string",
                        "enum": ["brief", "standard", "deep"],
                        "description": "Briefing depth level",
                        "default": "standard",
                    }
                },
            },
        ),
        Tool(
            name="get_run_status",
            description="Get the current status of a briefing run.",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {"type": "integer", "description": "Run ID returned by trigger_briefing"}
                },
                "required": ["run_id"],
            },
        ),
        Tool(
            name="list_briefings",
            description="List the last 20 completed briefing runs.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_briefing_content",
            description="Get the content of a completed briefing (markdown or audio path).",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {"type": "integer", "description": "Run ID"},
                    "content_type": {
                        "type": "string",
                        "enum": ["markdown", "audio"],
                        "description": "Content type to retrieve",
                    },
                },
                "required": ["run_id", "content_type"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    config = AppConfig()

    if name == "trigger_briefing":
        depth = arguments.get("depth", "standard")
        config.briefing_depth = depth
        run_id = await orchestrator.start_run(config)
        asyncio.create_task(orchestrator.run_pipeline(run_id, config))
        return [TextContent(type="text", text=f"Run {run_id} started with depth={depth}")]

    elif name == "get_run_status":
        run_id = int(arguments["run_id"])
        async with get_session() as session:
            run = await session.get(Run, run_id)
        if not run:
            return [TextContent(type="text", text=f"Run {run_id} not found")]
        msg = f"Run {run_id}: status={run.status}"
        if run.error:
            msg += f" error={run.error}"
        return [TextContent(type="text", text=msg)]

    elif name == "list_briefings":
        async with get_session() as session:
            result = await session.execute(
                select(Run)
                .where(Run.status == "complete")
                .order_by(Run.created_at.desc())
                .limit(20)
            )
            runs = result.scalars().all()
        items = [
            {
                "run_id": r.id,
                "date": r.created_at.isoformat() if r.created_at else None,
                "status": r.status,
            }
            for r in runs
        ]
        return [TextContent(type="text", text=json.dumps(items, indent=2))]

    elif name == "get_briefing_content":
        run_id = int(arguments["run_id"])
        content_type = arguments.get("content_type", "markdown")
        async with get_session() as session:
            result = await session.execute(
                select(BriefingOutput).where(BriefingOutput.run_id == run_id)
            )
            output = result.scalar_one_or_none()
        if not output:
            return [TextContent(type="text", text=f"No output found for run {run_id}")]
        if content_type == "markdown":
            path = output.markdown_path
            if path and Path(path).exists():
                return [TextContent(type="text", text=Path(path).read_text(encoding="utf-8"))]
            return [TextContent(type="text", text="Markdown file not found")]
        else:
            return [TextContent(type="text", text=f"Audio path: {output.audio_path or 'not available'}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main() -> None:
    config = AppConfig()
    config.data_dir.mkdir(parents=True, exist_ok=True)
    init_engine(build_sqlite_db_url(config.data_dir))
    await init_db()

    # Register MCP server for sampling support
    llm.set_mcp_server(server)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
