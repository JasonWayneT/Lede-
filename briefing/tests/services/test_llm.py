"""Tests for app/services/llm.py — Stories 3.1, 3.2, 3.3."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import AppConfig
from app.core.errors import AUTH_ERROR, PROVIDER_UNAVAILABLE, StageError
from app.services import llm as llm_module


def _config(**kwargs) -> AppConfig:
    base = dict(
        llm_provider="ollama",
        ollama_model_name="llama3.2",
        ollama_base_url="http://localhost:11434",
        openai_model_name="gpt-4o-mini",
        anthropic_model_name="claude-haiku-4-5-20251001",
        gemini_model_name="gemini-1.5-flash",
    )
    base.update(kwargs)
    return AppConfig(**base)


# ---------------------------------------------------------------------------
# Story 3.1 — Ollama
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ollama_complete_success():
    cfg = _config(llm_provider="ollama")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": "hello from ollama"}
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client

        result = await llm_module.complete("say hello", cfg)

    assert result == "hello from ollama"


@pytest.mark.asyncio
async def test_ollama_uses_configured_model():
    cfg = _config(llm_provider="ollama", ollama_model_name="mistral")
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": "ok"}
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client

        await llm_module.complete("test", cfg)
        call_kwargs = mock_client.post.call_args
        body = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][1]
        assert body["model"] == "mistral"


@pytest.mark.asyncio
async def test_ollama_connect_error_raises_stage_error():
    import httpx

    cfg = _config(llm_provider="ollama")

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_client_cls.return_value = mock_client

        with pytest.raises(StageError) as exc_info:
            await llm_module.complete("test", cfg)

    assert exc_info.value.code == PROVIDER_UNAVAILABLE
    assert exc_info.value.retryable is True


# ---------------------------------------------------------------------------
# Story 3.2 — OpenAI
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_openai_complete_success():
    cfg = _config(llm_provider="openai")

    mock_choice = MagicMock()
    mock_choice.message.content = "openai says hello"
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]

    with patch("app.core.credentials.get", return_value="sk-test"), \
         patch("openai.AsyncOpenAI") as mock_cls:
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)

        result = await llm_module.complete("hello", cfg)

    assert result == "openai says hello"


@pytest.mark.asyncio
async def test_openai_auth_error():
    import openai

    cfg = _config(llm_provider="openai")

    with patch("app.core.credentials.get", return_value="bad-key"), \
         patch("openai.AsyncOpenAI") as mock_cls:
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            side_effect=openai.AuthenticationError("invalid", response=MagicMock(), body={})
        )

        with pytest.raises(StageError) as exc_info:
            await llm_module.complete("test", cfg)

    assert exc_info.value.code == AUTH_ERROR
    assert exc_info.value.retryable is False


@pytest.mark.asyncio
async def test_openai_missing_key_raises_auth_error():
    cfg = _config(llm_provider="openai")

    with patch("app.core.credentials.get", return_value=None):
        with pytest.raises(StageError) as exc_info:
            await llm_module.complete("test", cfg)

    assert exc_info.value.code == AUTH_ERROR


@pytest.mark.asyncio
async def test_anthropic_complete_success():
    cfg = _config(llm_provider="anthropic")

    mock_content = MagicMock()
    mock_content.text = "anthropic reply"
    mock_resp = MagicMock()
    mock_resp.content = [mock_content]

    with patch("app.core.credentials.get", return_value="test-key"), \
         patch("anthropic.AsyncAnthropic") as mock_cls:
        mock_client = AsyncMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_resp)

        result = await llm_module.complete("hello", cfg)

    assert result == "anthropic reply"


@pytest.mark.asyncio
async def test_gemini_complete_success():
    cfg = _config(llm_provider="gemini")

    mock_resp = MagicMock()
    mock_resp.text = "gemini reply"

    with patch("app.core.credentials.get", return_value="test-key"), \
         patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_model.generate_content_async = AsyncMock(return_value=mock_resp)

        result = await llm_module.complete("hello", cfg)

    assert result == "gemini reply"


# ---------------------------------------------------------------------------
# Story 3.3 — MCP sampling
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mcp_sampling_success():
    cfg = _config(llm_provider="mcp_sampling")

    mock_server = MagicMock()
    mock_result = MagicMock()
    mock_result.content.text = "mcp reply"
    mock_server.create_message = AsyncMock(return_value=mock_result)

    llm_module.set_mcp_server(mock_server)
    try:
        result = await llm_module.complete("hello", cfg)
    finally:
        llm_module.set_mcp_server(None)

    assert result == "mcp reply"


@pytest.mark.asyncio
async def test_mcp_sampling_fallback_to_ollama(caplog):
    cfg = _config(llm_provider="mcp_sampling")

    # Ensure no MCP context
    llm_module.set_mcp_server(None)

    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": "ollama fallback"}
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client

        import logging
        with caplog.at_level(logging.WARNING, logger="app.services.llm"):
            result = await llm_module.complete("test", cfg)

    assert result == "ollama fallback"
    assert any("falling back" in r.message.lower() for r in caplog.records)
