"""Tests for QA gate stage — Story 7.3."""

from __future__ import annotations

import pytest

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import qa_gate


def _config(sections=None):
    kw = {"llm_provider": "ollama"}
    if sections is not None:
        kw["BRIEFING_SECTIONS"] = ",".join(sections)
    return AppConfig.model_validate(kw)


def _story(section="AI", sources=("Axios",)):
    return {"section_name": section, "prose": "Some prose.", "sources": list(sources), "source_count": len(sources)}


def _packet_ok():
    packet = HandoffPacket(run_id=1)
    packet.drafted_stories = [_story("AI"), _story("Technology")]
    packet.tts_script = " ".join(["word"] * 300)
    return packet


@pytest.mark.asyncio
async def test_all_checks_pass():
    packet = _packet_ok()
    config = _config(sections=["AI", "Technology", "Other"])
    result = await qa_gate.run(packet, config)
    assert result.qa_passed is True


@pytest.mark.asyncio
async def test_uneven_section_coverage_does_not_raise():
    # Sections are derived from content per-run; a day with no Finance news
    # should not fail QA just because a configured section is empty.
    packet = _packet_ok()
    config = _config(sections=["AI", "Finance", "Other"])
    packet.drafted_stories = [_story("AI")]
    result = await qa_gate.run(packet, config)
    assert result.qa_passed is True


@pytest.mark.asyncio
async def test_no_stories_drafted_raises():
    packet = _packet_ok()
    config = _config(sections=["AI", "Finance", "Other"])
    packet.drafted_stories = []
    with pytest.raises(StageError) as exc_info:
        await qa_gate.run(packet, config)
    assert "no stories" in exc_info.value.message.lower()
    assert exc_info.value.retryable is True


@pytest.mark.asyncio
async def test_story_empty_sources_raises():
    packet = _packet_ok()
    config = _config(sections=["AI", "Other"])
    packet.drafted_stories = [_story("AI", sources=[])]
    with pytest.raises(StageError) as exc_info:
        await qa_gate.run(packet, config)
    assert "source" in exc_info.value.message.lower()


@pytest.mark.asyncio
async def test_tts_script_with_markdown_raises():
    packet = _packet_ok()
    config = _config(sections=["AI", "Technology", "Other"])
    packet.tts_script = " ".join(["word"] * 300) + " ## Header"
    with pytest.raises(StageError) as exc_info:
        await qa_gate.run(packet, config)
    assert "TTS" in exc_info.value.message or "markdown" in exc_info.value.message.lower()


@pytest.mark.asyncio
async def test_very_short_script_raises():
    packet = _packet_ok()
    config = _config(sections=["AI", "Technology", "Other"])
    packet.tts_script = " ".join(["word"] * 20)
    with pytest.raises(StageError) as exc_info:
        await qa_gate.run(packet, config)
    assert "runtime" in exc_info.value.message.lower() or "min" in exc_info.value.message


@pytest.mark.asyncio
async def test_other_section_skipped_in_section_check():
    packet = HandoffPacket(run_id=1)
    packet.drafted_stories = [_story("AI")]
    packet.tts_script = " ".join(["word"] * 300)
    config = _config(sections=["AI", "Other"])
    result = await qa_gate.run(packet, config)
    assert result.qa_passed is True
