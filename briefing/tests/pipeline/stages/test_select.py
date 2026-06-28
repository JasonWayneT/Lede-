"""Tests for select stage — Story 4.6."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import AppConfig
from app.core.errors import PROVIDER_UNAVAILABLE, StageError
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import select


def _config():
    return AppConfig(llm_provider="ollama", sections=["AI", "Technology", "Finance", "Politics", "Other"])


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
async def test_select_fallback_to_other():
    packet = _packet(n_clusters=1)
    with patch("app.pipeline.stages.select.llm.complete", new=AsyncMock(return_value="UnknownSection")):
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
