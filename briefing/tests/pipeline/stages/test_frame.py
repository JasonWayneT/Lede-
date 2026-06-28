"""Tests for frame stage — Story 5.1."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import frame


def _config(depth="standard"):
    return AppConfig(llm_provider="ollama", briefing_depth=depth)


def _cluster(n=1):
    return [{"text": f"text {i}", "sender_name": f"NL {i}", "email_id": str(i)} for i in range(n)]


def _selected(n_clusters=1, n_sources=1):
    return [{"cluster": _cluster(n_sources), "section_name": "AI"} for _ in range(n_clusters)]


_FRAME_RESP = json.dumps({"lead_angle": "Big news", "local_stakes": "Matters here", "guardrails": ["Check this"]})


@pytest.mark.asyncio
async def test_frame_populates_framed_stories():
    packet = HandoffPacket(run_id=1, selected_clusters=_selected(n_clusters=2))
    with patch("app.pipeline.stages.frame.llm.complete", new=AsyncMock(return_value=_FRAME_RESP)):
        result = await frame.run(packet, _config())
    assert len(result.framed_stories) == 2


@pytest.mark.asyncio
async def test_frame_fields_present():
    packet = HandoffPacket(run_id=1, selected_clusters=_selected())
    with patch("app.pipeline.stages.frame.llm.complete", new=AsyncMock(return_value=_FRAME_RESP)):
        result = await frame.run(packet, _config())
    story = result.framed_stories[0]
    assert "depth_tier" in story
    assert "lead_angle" in story
    assert "local_stakes" in story
    assert "guardrails" in story


@pytest.mark.asyncio
async def test_depth_upgrade_standard_to_deep():
    # 5 sources + standard baseline → deep
    packet = HandoffPacket(run_id=1, selected_clusters=_selected(n_sources=5))
    with patch("app.pipeline.stages.frame.llm.complete", new=AsyncMock(return_value=_FRAME_RESP)):
        result = await frame.run(packet, _config(depth="standard"))
    assert result.framed_stories[0]["depth_tier"] == "deep"


@pytest.mark.asyncio
async def test_depth_no_upgrade_below_threshold():
    # 2 sources + brief baseline → stays brief
    packet = HandoffPacket(run_id=1, selected_clusters=_selected(n_sources=2))
    with patch("app.pipeline.stages.frame.llm.complete", new=AsyncMock(return_value=_FRAME_RESP)):
        result = await frame.run(packet, _config(depth="brief"))
    assert result.framed_stories[0]["depth_tier"] == "brief"


@pytest.mark.asyncio
async def test_frame_guardrails_propagated():
    packet = HandoffPacket(run_id=1, selected_clusters=_selected())
    with patch("app.pipeline.stages.frame.llm.complete", new=AsyncMock(return_value=_FRAME_RESP)):
        result = await frame.run(packet, _config())
    assert result.framed_stories[0]["guardrails"] == ["Check this"]
