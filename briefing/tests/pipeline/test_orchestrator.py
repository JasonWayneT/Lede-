"""Tests for pipeline orchestrator — Stories 7.1 and 7.4."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api import stream as sse
from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline import orchestrator
from app.pipeline.handoff import HandoffPacket


def _config(tmp_path):
    return AppConfig.model_validate({
        "llm_provider": "ollama",
        "BRIEFING_DATA_DIR": str(tmp_path),
    })


@pytest.fixture(autouse=True)
def _clean_queues():
    sse._queues.clear()
    yield
    sse._queues.clear()


# ---------------------------------------------------------------------------
# Helper: build a minimal passing packet
# ---------------------------------------------------------------------------

def _good_packet(run_id=1):
    p = HandoffPacket(run_id=run_id)
    p.emails = [{"email_id": "msg-1", "text": "Hello", "title": "T", "sender_name": "S", "date": "2026-01-01"}]
    p.extracted_texts = [{"email_id": "msg-1", "text": "Hello", "title": "T", "sender_name": "S", "date": "2026-01-01"}]
    p.drafted_stories = [{"section_name": "AI", "prose": "Prose.", "sources": ["Axios"], "source_count": 1}]
    p.tts_script = " ".join(["word"] * 300)
    p.assembled_markdown = "# Briefing\n\nHello."
    p.markdown_path = "/tmp/briefing.md"
    p.qa_passed = True
    return p


# ---------------------------------------------------------------------------
# _retry tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_retry_tier1_succeeds_returns_packet(tmp_path):
    config = _config(tmp_path)
    packet = _good_packet()
    call_count = 0

    async def fake_run(pkt, cfg):
        nonlocal call_count
        call_count += 1
        return pkt

    stage_mod = MagicMock()
    stage_mod.run = fake_run
    error = StageError("select", "bad json", retryable=True)

    fake_session = AsyncMock()
    result = await orchestrator._retry(stage_mod, 5, "select", packet, config, error, fake_session)
    assert result is packet
    assert call_count == 1  # tier 1 only


@pytest.mark.asyncio
async def test_retry_tier2_after_tier1_fail(tmp_path):
    config = _config(tmp_path)
    packet = _good_packet()
    call_count = 0

    async def fake_run(pkt, cfg):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise StageError("select", "still bad", retryable=True)
        return pkt

    stage_mod = MagicMock()
    stage_mod.run = fake_run
    error = StageError("select", "initial fail", retryable=True)

    fake_session = AsyncMock()
    result = await orchestrator._retry(stage_mod, 5, "select", packet, config, error, fake_session)
    assert result is packet
    assert call_count == 2  # tier 1 + tier 2


@pytest.mark.asyncio
async def test_retry_hold_after_tier2_fail(tmp_path):
    config = _config(tmp_path)
    packet = _good_packet()

    async def always_fail(pkt, cfg):
        raise StageError("select", "always fails", retryable=True)

    stage_mod = MagicMock()
    stage_mod.run = always_fail
    error = StageError("select", "initial", retryable=True)

    # Mock DB interactions in _enter_hold
    fake_run_obj = MagicMock()
    fake_session = MagicMock()
    fake_session.begin = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=None), __aexit__=AsyncMock(return_value=None)))
    fake_session.get = AsyncMock(return_value=fake_run_obj)
    fake_session.add = MagicMock()

    with pytest.raises(orchestrator._HoldException):
        await orchestrator._retry(stage_mod, 5, "select", packet, config, error, fake_session)

    assert fake_run_obj.status == "hold"
    assert "select" in fake_run_obj.error


@pytest.mark.asyncio
async def test_non_retryable_skips_to_hold(tmp_path):
    config = _config(tmp_path)
    packet = _good_packet()

    stage_mod = MagicMock()
    stage_mod.run = AsyncMock()  # should never be called
    error = StageError("assemble", "disk full", retryable=False)

    fake_run_obj = MagicMock()
    fake_session = MagicMock()
    fake_session.begin = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=None), __aexit__=AsyncMock(return_value=None)))
    fake_session.get = AsyncMock(return_value=fake_run_obj)
    fake_session.add = MagicMock()

    with pytest.raises(orchestrator._HoldException):
        await orchestrator._retry(stage_mod, 9, "assemble", packet, config, error, fake_session)

    stage_mod.run.assert_not_called()
    assert fake_run_obj.status == "hold"


@pytest.mark.asyncio
async def test_sse_error_event_emitted_on_retry(tmp_path):
    config = _config(tmp_path)
    packet = _good_packet()

    sse.get_or_create_queue(1)

    async def ok_run(pkt, cfg):
        return pkt

    stage_mod = MagicMock()
    stage_mod.run = ok_run
    error = StageError("select", "bad", retryable=True)

    fake_session = AsyncMock()
    await orchestrator._retry(stage_mod, 5, "select", packet, config, error, fake_session)

    q = sse._queues.get(1)
    items = []
    while q and not q.empty():
        items.append(q.get_nowait())

    assert any(i.get("event") == "error" for i in items)
