"""Tests for TTS prep stage — Story 6.1 / 6.4 (CR-005, FR-030, BUG-005)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import tts_prep


def _config():
    return AppConfig(llm_provider="ollama")


def _drafted_stories():
    return [
        {
            "section_name": "AI", "source_count": 2, "sensitivity": "normal",
            "prose": "A-I story body.\n\n> Sources: NL1",
            "selected_music": {"asset_id": "modern_tech_digest_01", "style": "modern_tech_digest", "file": "x.mp3"},
        },
        {
            "section_name": "Finance", "source_count": 1, "sensitivity": "normal",
            "prose": "Finance story body.\n\n> Sources: NL2",
            "selected_music": {"asset_id": "business_briefing_01", "style": "business_briefing", "file": "y.mp3"},
        },
    ]


_PRON_RESP = json.dumps({"pronunciation_guide": {"AI": "A-I"}})


@pytest.mark.asyncio
async def test_plan_built_from_drafted_stories_not_markdown():
    # AC-074 (BUG-005) — assembled_markdown is empty; plan must still carry story prose.
    packet = HandoffPacket(run_id=1, drafted_stories=_drafted_stories(), assembled_markdown="")
    with patch("app.pipeline.stages.tts_prep.llm.complete", new=AsyncMock(return_value=_PRON_RESP)):
        result = await tts_prep.run(packet, _config())
    assert result.audio_segments
    narrated = [s for s in result.audio_segments if s["text"]]
    assert any("story body" in s["text"] for s in narrated)


@pytest.mark.asyncio
async def test_plan_order_intro_transitions_outro():
    # AC-075 — intro first, outro last, section_transition between the two sections.
    packet = HandoffPacket(run_id=1, drafted_stories=_drafted_stories())
    with patch("app.pipeline.stages.tts_prep.llm.complete", new=AsyncMock(return_value=_PRON_RESP)):
        result = await tts_prep.run(packet, _config())
    roles = [s["role"] for s in result.audio_segments]
    assert roles[0] == "intro"
    assert roles[-1] == "outro"
    assert roles.count("section_transition") == 1  # two sections -> one transition between
    assert roles.count("main_summary") == 2


@pytest.mark.asyncio
async def test_story_segment_strips_sources_and_carries_music():
    # AC-076
    packet = HandoffPacket(run_id=1, drafted_stories=_drafted_stories())
    with patch("app.pipeline.stages.tts_prep.llm.complete", new=AsyncMock(return_value=_PRON_RESP)):
        result = await tts_prep.run(packet, _config())
    story_seg = next(s for s in result.audio_segments if s["role"] == "main_summary")
    assert "Sources:" not in story_seg["text"]
    assert story_seg["selected_music"] is not None


@pytest.mark.asyncio
async def test_structural_segments_are_music_only():
    # AC-077 — intro/outro/transition have no narration text but do carry role-selected music.
    packet = HandoffPacket(run_id=1, drafted_stories=_drafted_stories())
    with patch("app.pipeline.stages.tts_prep.llm.complete", new=AsyncMock(return_value=_PRON_RESP)):
        result = await tts_prep.run(packet, _config())
    intro = next(s for s in result.audio_segments if s["role"] == "intro")
    outro = next(s for s in result.audio_segments if s["role"] == "outro")
    transition = next(s for s in result.audio_segments if s["role"] == "section_transition")
    assert intro["text"] == "" and outro["text"] == "" and transition["text"] == ""
    assert intro["selected_music"]["style"] == "premium_newsletter_intro"
    assert outro["selected_music"]["style"] == "premium_newsletter_intro"
    assert transition["selected_music"]["style"] == "headline_transition"


@pytest.mark.asyncio
async def test_tts_script_is_concatenated_narration():
    packet = HandoffPacket(run_id=1, drafted_stories=_drafted_stories())
    with patch("app.pipeline.stages.tts_prep.llm.complete", new=AsyncMock(return_value=_PRON_RESP)):
        result = await tts_prep.run(packet, _config())
    assert "A-I story body." in result.tts_script
    assert "Finance story body." in result.tts_script
    assert "Sources:" not in result.tts_script


@pytest.mark.asyncio
async def test_pronunciation_guide_non_fatal(caplog):
    # AC-079 — LLM failure must not fail the stage; guide is empty, plan still built.
    import logging
    packet = HandoffPacket(run_id=1, drafted_stories=_drafted_stories())
    with patch("app.pipeline.stages.tts_prep.llm.complete", new=AsyncMock(side_effect=RuntimeError("down"))):
        with caplog.at_level(logging.WARNING):
            result = await tts_prep.run(packet, _config())
    assert result.pronunciation_guide == {}
    assert result.audio_segments  # plan still built
