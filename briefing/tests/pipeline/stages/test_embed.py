"""Tests for embed stage — Story 4.5."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import embed


def _config():
    return AppConfig(llm_provider="ollama")


@pytest.mark.asyncio
async def test_embed_one_vector_per_text():
    texts = [{"text": "hello"}, {"text": "world"}]
    packet = HandoffPacket(run_id=1, extracted_texts=texts)

    mock_vectors = [[0.1, 0.2], [0.3, 0.4]]
    with patch("app.pipeline.stages.embed.embeddings.encode", return_value=mock_vectors):
        result = await embed.run(packet, _config())

    assert len(result.embeddings) == 2
    assert result.embeddings[0] == [0.1, 0.2]


@pytest.mark.asyncio
async def test_embed_empty_texts():
    packet = HandoffPacket(run_id=1, extracted_texts=[])
    result = await embed.run(packet, _config())
    assert result.embeddings == []


@pytest.mark.asyncio
async def test_embed_preserves_order():
    texts = [{"text": f"text {i}"} for i in range(5)]
    packet = HandoffPacket(run_id=1, extracted_texts=texts)
    mock_vectors = [[float(i)] for i in range(5)]

    with patch("app.pipeline.stages.embed.embeddings.encode", return_value=mock_vectors):
        result = await embed.run(packet, _config())

    for i, vec in enumerate(result.embeddings):
        assert vec == [float(i)]
