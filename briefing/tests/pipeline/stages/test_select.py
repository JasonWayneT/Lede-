"""Tests for select stage — Story 4.6.

Sections are now derived freely from content rather than classified against a
fixed taxonomy (see qa_gate fix for empty-section-on-a-given-day bug).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import AppConfig
from app.core.errors import PROVIDER_UNAVAILABLE, StageError
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import select


def _config():
    return AppConfig(llm_provider="ollama")


def _packet(n_clusters=2):
    clusters = [[{"text": f"cluster {i} text", "email_id": str(i)}] for i in range(n_clusters)]
    return HandoffPacket(run_id=1, clusters=clusters)


@pytest.mark.asyncio
async def test_select_classifies_each_cluster():
    packet = _packet(n_clusters=2)
    with patch("app.pipeline.stages.select.llm.complete", new=AsyncMock(return_value="AI")):
        result = await select.run(packet, _config())
    assert len(result.selected_clusters) == 2
    assert all(sc["section_name"] == "AI" for sc in result.selected_clusters)


@pytest.mark.asyncio
async def test_select_accepts_freeform_section_name():
    packet = _packet(n_clusters=1)
    with patch("app.pipeline.stages.select.llm.complete", new=AsyncMock(return_value="Climate Policy")):
        result = await select.run(packet, _config())
    assert result.selected_clusters[0]["section_name"] == "Climate Policy"


@pytest.mark.asyncio
async def test_select_explicit_other_passthrough():
    packet = _packet(n_clusters=1)
    with patch("app.pipeline.stages.select.llm.complete", new=AsyncMock(return_value="Other")):
        result = await select.run(packet, _config())
    assert result.selected_clusters[0]["section_name"] == "Other"


@pytest.mark.asyncio
async def test_select_falls_back_to_other_when_response_too_long():
    packet = _packet(n_clusters=1)
    rambling = "This is way too many words for a section name"
    with patch("app.pipeline.stages.select.llm.complete", new=AsyncMock(return_value=rambling)):
        result = await select.run(packet, _config())
    assert result.selected_clusters[0]["section_name"] == "Other"


@pytest.mark.asyncio
async def test_select_falls_back_to_other_when_response_empty():
    packet = _packet(n_clusters=1)
    with patch("app.pipeline.stages.select.llm.complete", new=AsyncMock(return_value="   ")):
        result = await select.run(packet, _config())
    assert result.selected_clusters[0]["section_name"] == "Other"


@pytest.mark.asyncio
async def test_select_one_section_per_cluster():
    packet = _packet(n_clusters=3)
    responses = ["Technology", "Finance", "AI"]
    with patch("app.pipeline.stages.select.llm.complete", new=AsyncMock(side_effect=responses)):
        result = await select.run(packet, _config())
    sections = [sc["section_name"] for sc in result.selected_clusters]
    assert sections == ["Technology", "Finance", "AI"]


@pytest.mark.asyncio
async def test_select_raises_stage_error_on_llm_failure():
    packet = _packet(n_clusters=1)
    with patch("app.pipeline.stages.select.llm.complete",
               new=AsyncMock(side_effect=StageError("llm", "fail", code=PROVIDER_UNAVAILABLE))):
        with pytest.raises(StageError):
            await select.run(packet, _config())
