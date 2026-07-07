"""LLM provider router — Ollama, OpenAI, Anthropic, Gemini, MCP sampling."""

# Implements ARCH-001, FR-010, FR-011, FR-012, FR-013, FR-014

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core import credentials
from app.core.config import AppConfig
from app.core.errors import AUTH_ERROR, PROVIDER_UNAVAILABLE, StageError

logger = logging.getLogger(__name__)

# Set by mcp_server.py at startup; None when running in web UI mode.
_mcp_server_context: Any = None


def set_mcp_server(server: Any) -> None:
    """Register the active MCP server instance so mcp_sampling can use it."""
    global _mcp_server_context
    _mcp_server_context = server


async def complete(prompt: str, config: AppConfig, system: str | None = None) -> str:
    """Route an LLM completion request to the configured provider."""
    provider = config.llm_provider
    if provider == "ollama":
        return await _ollama_complete(prompt, config, system)
    elif provider == "openai":
        return await _openai_complete(prompt, config, system)
    elif provider == "anthropic":
        return await _anthropic_complete(prompt, config, system)
    elif provider == "gemini":
        return await _gemini_complete(prompt, config, system)
    elif provider == "mcp_sampling":
        return await _mcp_complete(prompt, config, system)
    else:
        raise StageError("llm", f"Unknown provider: {provider}", retryable=False)


async def _ollama_complete(prompt: str, config: AppConfig, system: str | None) -> str:
    body: dict[str, Any] = {
        "model": config.ollama_model_name,
        "prompt": prompt,
        "stream": False,
        # Implements BUG-001, ARCH-006 — without this, Ollama silently defaults num_ctx to 2048
        # regardless of what the configured model actually supports.
        "options": {"num_ctx": config.ollama_num_ctx},
    }
    if system:
        body["system"] = system

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{config.ollama_base_url}/api/generate", json=body)
            resp.raise_for_status()
            return resp.json()["response"]
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        raise StageError("llm", f"Ollama unreachable: {e}", code=PROVIDER_UNAVAILABLE, retryable=True) from e
    except httpx.HTTPStatusError as e:
        raise StageError("llm", f"Ollama error {e.response.status_code}", code=PROVIDER_UNAVAILABLE, retryable=True) from e


async def _openai_complete(prompt: str, config: AppConfig, system: str | None) -> str:
    import openai

    key = credentials.get(credentials.OPENAI_KEY)
    if not key:
        raise StageError("llm", "OpenAI API key not configured.", code=AUTH_ERROR, retryable=False)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        client = openai.AsyncOpenAI(api_key=key)
        resp = await client.chat.completions.create(model=config.openai_model_name, messages=messages)
        return resp.choices[0].message.content or ""
    except openai.AuthenticationError as e:
        raise StageError("llm", "OpenAI API key invalid or expired.", code=AUTH_ERROR, retryable=False) from e
    except openai.APIConnectionError as e:
        raise StageError("llm", f"OpenAI unreachable: {e}", code=PROVIDER_UNAVAILABLE, retryable=True) from e


async def _anthropic_complete(prompt: str, config: AppConfig, system: str | None) -> str:
    import anthropic as anthropic_sdk

    key = credentials.get(credentials.ANTHROPIC_KEY)
    if not key:
        raise StageError("llm", "Anthropic API key not configured.", code=AUTH_ERROR, retryable=False)

    kwargs: dict[str, Any] = {
        "model": config.anthropic_model_name,
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    try:
        client = anthropic_sdk.AsyncAnthropic(api_key=key)
        resp = await client.messages.create(**kwargs)
        return resp.content[0].text if resp.content else ""
    except anthropic_sdk.AuthenticationError as e:
        raise StageError("llm", "Anthropic API key invalid or expired.", code=AUTH_ERROR, retryable=False) from e
    except anthropic_sdk.APIConnectionError as e:
        raise StageError("llm", f"Anthropic unreachable: {e}", code=PROVIDER_UNAVAILABLE, retryable=True) from e


async def _gemini_complete(prompt: str, config: AppConfig, system: str | None) -> str:
    import google.generativeai as genai

    key = credentials.get(credentials.GEMINI_KEY)
    if not key:
        raise StageError("llm", "Gemini API key not configured.", code=AUTH_ERROR, retryable=False)

    genai.configure(api_key=key)
    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    try:
        model = genai.GenerativeModel(config.gemini_model_name)
        resp = await model.generate_content_async(full_prompt)
        return resp.text or ""
    except Exception as e:
        err_str = str(e).lower()
        if "api key" in err_str or "permission" in err_str or "unauthenticated" in err_str:
            raise StageError("llm", "Gemini API key invalid or expired.", code=AUTH_ERROR, retryable=False) from e
        raise StageError("llm", f"Gemini error: {e}", code=PROVIDER_UNAVAILABLE, retryable=True) from e


async def _mcp_complete(prompt: str, config: AppConfig, system: str | None) -> str:
    if _mcp_server_context is None or not hasattr(_mcp_server_context, "create_message"):
        logger.warning("MCP sampling not available, falling back to Ollama")
        return await _ollama_complete(prompt, config, system)

    try:
        from mcp.types import SamplingMessage, TextContent

        messages = [SamplingMessage(role="user", content=TextContent(type="text", text=prompt))]
        result = await _mcp_server_context.create_message(messages=messages, max_tokens=2048)
        return result.content.text or ""
    except Exception as e:
        raise StageError("llm", f"MCP sampling error: {e}", code=PROVIDER_UNAVAILABLE, retryable=True) from e
