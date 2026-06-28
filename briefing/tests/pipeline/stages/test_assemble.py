"""Tests for assemble stage — Story 5.3."""

from __future__ import annotations

import pytest

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import assemble


def _config(data_dir=None, sections=None):
    kwargs = {"llm_provider": "ollama"}
    if data_dir is not None:
        kwargs["BRIEFING_DATA_DIR"] = str(data_dir)
    cfg = AppConfig.model_validate(kwargs)
    return cfg


def _drafted_stories():
    return [
        {"section_name": "Technology", "depth_tier": "brief", "prose": "Tech story A.", "sources": ["NL1"], "source_count": 3},
        {"section_name": "AI", "depth_tier": "standard", "prose": "AI story A.", "sources": ["NL2"], "source_count": 2},
        {"section_name": "AI", "depth_tier": "brief", "prose": "AI story B.", "sources": ["NL3"], "source_count": 1},
        {"section_name": "Other", "depth_tier": "brief", "prose": "Misc story.", "sources": ["NL4"], "source_count": 1},
    ]


@pytest.mark.asyncio
async def test_assemble_markdown_populated(tmp_path):
    packet = HandoffPacket(run_id=1, drafted_stories=_drafted_stories())
    cfg = _config(data_dir=tmp_path)
    result = await assemble.run(packet, cfg)
    assert result.assembled_markdown != ""
    assert "# Briefing" in result.assembled_markdown


@pytest.mark.asyncio
async def test_assemble_section_order(tmp_path):
    packet = HandoffPacket(run_id=1, drafted_stories=_drafted_stories())
    cfg = _config(data_dir=tmp_path)
    result = await assemble.run(packet, cfg)
    ai_pos = result.assembled_markdown.index("## AI")
    tech_pos = result.assembled_markdown.index("## Technology")
    other_pos = result.assembled_markdown.index("## Other")
    assert ai_pos < tech_pos < other_pos


@pytest.mark.asyncio
async def test_assemble_stories_sorted_by_source_count(tmp_path):
    packet = HandoffPacket(run_id=1, drafted_stories=_drafted_stories())
    cfg = _config(data_dir=tmp_path)
    result = await assemble.run(packet, cfg)
    pos_a = result.assembled_markdown.index("AI story A")
    pos_b = result.assembled_markdown.index("AI story B")
    assert pos_a < pos_b


@pytest.mark.asyncio
async def test_assemble_file_written(tmp_path):
    packet = HandoffPacket(run_id=99, drafted_stories=_drafted_stories())
    cfg = _config(data_dir=tmp_path)
    result = await assemble.run(packet, cfg)
    output = tmp_path / "briefings" / "99" / "briefing.md"
    assert output.exists()
    assert result.markdown_path == str(output)


@pytest.mark.asyncio
async def test_assemble_header_contains_metadata(tmp_path):
    packet = HandoffPacket(run_id=5, drafted_stories=_drafted_stories())
    cfg = _config(data_dir=tmp_path)
    result = await assemble.run(packet, cfg)
    assert "Run #5" in result.assembled_markdown
    assert "4 stories" in result.assembled_markdown
