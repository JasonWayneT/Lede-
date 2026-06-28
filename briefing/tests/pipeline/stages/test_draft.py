"""Tests for draft stage — Story 5.2."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import draft


def _config():
    return AppConfig(llm_provider="ollama")


def _framed_stories(n=2):
    return [
        {
            "cluster": [{"text": "content", "sender_name": f"NL {i}", "email_id": str(i)}],
            "section_name": "AI",
            "depth_tier": "standard",
            "lead_angle": "Lead",
            "local_stakes": "Stakes",
            "guardrails": ["Verify claim"],
            "source_count": 1,
        }
        for i in range(n)
    ]


@pytest.mark.asyncio
async def test_draft_one_per_framed_story():
    packet = HandoffPacket(run_id=1, framed_stories=_framed_stories(n=3))
    with patch("app.pipeline.stages.draft.llm.complete", new=AsyncMock(return_value="Prose text.")):
        result = await draft.run(packet, _config())
    assert len(result.drafted_stories) == 3


@pytest.mark.asyncio
async def test_draft_sources_populated():
    packet = HandoffPacket(run_id=1, framed_stories=_framed_stories(n=1))
    with patch("app.pipeline.stages.draft.llm.complete", new=AsyncMock(return_value="Story text.")):
        result = await draft.run(packet, _config())
    assert "NL 0" in result.drafted_stories[0]["sources"]


@pytest.mark.asyncio
async def test_draft_prompt_includes_guardrails():
    packet = HandoffPacket(run_id=1, framed_stories=_framed_stories(n=1))
    captured_prompts = []

    async def capture_prompt(prompt, config, **kwargs):
        captured_prompts.append(prompt)
        return "Story."

    with patch("app.pipeline.stages.draft.llm.complete", new=capture_prompt):
        await draft.run(packet, _config())

    assert "Verify claim" in captured_prompts[0]


@pytest.mark.asyncio
async def test_draft_prose_stored():
    packet = HandoffPacket(run_id=1, framed_stories=_framed_stories(n=1))
    with patch("app.pipeline.stages.draft.llm.complete", new=AsyncMock(return_value="Final prose.")):
        result = await draft.run(packet, _config())
    assert result.drafted_stories[0]["prose"] == "Final prose."
