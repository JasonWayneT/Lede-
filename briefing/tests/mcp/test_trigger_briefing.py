"""Tests for MCP trigger_briefing and MCP sampling — Stories 11.1, 11.2."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.mcp_server import call_tool
from app.services import llm


@pytest.mark.asyncio
async def test_trigger_briefing_returns_run_id(mcp_db):
    with patch("app.mcp_server.orchestrator.start_run", new=AsyncMock(return_value=42)), \
         patch("app.mcp_server.orchestrator.run_pipeline", new=AsyncMock()), \
         patch("app.mcp_server.asyncio.create_task"):
        result = await call_tool("trigger_briefing", {"depth": "standard"})
    assert any("42" in r.text for r in result)


@pytest.mark.asyncio
async def test_trigger_briefing_default_depth(mcp_db):
    with patch("app.mcp_server.orchestrator.start_run", new=AsyncMock(return_value=1)) as mock_start, \
         patch("app.mcp_server.orchestrator.run_pipeline", new=AsyncMock()), \
         patch("app.mcp_server.asyncio.create_task"):
        await call_tool("trigger_briefing", {})
    mock_start.assert_called_once()


@pytest.mark.asyncio
async def test_mcp_sampling_calls_create_message(mcp_db):
    from app.core.config import AppConfig
    from app.mcp_server import server

    config = AppConfig.model_validate({
        "llm_provider": "mcp_sampling",
        "BRIEFING_DATA_DIR": str(mcp_db),
    })

    mock_server = AsyncMock()
    mock_server.create_message = AsyncMock(return_value=AsyncMock(content=AsyncMock(text="OK")))
    llm.set_mcp_server(mock_server)

    result = await llm.complete("Say OK", config)
    mock_server.create_message.assert_called_once()
    assert result == "OK"

    llm.set_mcp_server(None)


@pytest.mark.asyncio
async def test_mcp_sampling_fallback_when_no_context(mcp_db, caplog):
    import logging
    from app.core.config import AppConfig

    config = AppConfig.model_validate({
        "llm_provider": "mcp_sampling",
        "BRIEFING_DATA_DIR": str(mcp_db),
    })
    llm.set_mcp_server(None)

    with patch("app.services.llm._ollama_complete", new=AsyncMock(return_value="fallback")), \
         caplog.at_level(logging.WARNING):
        result = await llm.complete("Say OK", config)

    assert result == "fallback"
    assert any("falling back" in r.message.lower() for r in caplog.records)
