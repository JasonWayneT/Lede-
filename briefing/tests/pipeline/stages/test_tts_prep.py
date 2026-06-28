"""Tests for TTS prep stage — Story 6.1."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import tts_prep


def _config():
    return AppConfig(llm_provider="ollama")


_VALID_RESP = json.dumps({"tts_script": "Welcome to your briefing.", "pronunciation_guide": {"AI": "A-I"}})


@pytest.mark.asyncio
async def test_tts_prep_populates_script():
    packet = HandoffPacket(run_id=1, assembled_markdown="# Briefing\n\nSome text.")
    with patch("app.pipeline.stages.tts_prep.llm.complete", new=AsyncMock(return_value=_VALID_RESP)):
        result = await tts_prep.run(packet, _config())
    assert result.tts_script == "Welcome to your briefing."


@pytest.mark.asyncio
async def test_tts_prep_pronunciation_guide():
    packet = HandoffPacket(run_id=1, assembled_markdown="# Briefing\n\nAI news.")
    with patch("app.pipeline.stages.tts_prep.llm.complete", new=AsyncMock(return_value=_VALID_RESP)):
        result = await tts_prep.run(packet, _config())
    assert isinstance(result.pronunciation_guide, dict)
    assert result.pronunciation_guide.get("AI") == "A-I"


@pytest.mark.asyncio
async def test_tts_prep_fallback_on_parse_failure(caplog):
    import logging
    packet = HandoffPacket(run_id=1, assembled_markdown="Some text.")
    with patch("app.pipeline.stages.tts_prep.llm.complete", new=AsyncMock(return_value="not json")):
        with caplog.at_level(logging.WARNING):
            result = await tts_prep.run(packet, _config())
    assert result.tts_script == "not json"
    assert result.pronunciation_guide == {}
    assert any("parse" in r.message.lower() for r in caplog.records)
