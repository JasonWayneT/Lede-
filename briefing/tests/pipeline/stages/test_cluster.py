"""Tests for cluster stage — Story 4.5."""

from __future__ import annotations

import numpy as np
import pytest

from app.core.config import AppConfig
from app.pipeline.handoff import HandoffPacket
from app.pipeline.stages import cluster


def _config(threshold=0.75):
    return AppConfig(llm_provider="ollama", similarity_threshold=threshold)


def _unit(dim: int, idx: int, total: int) -> list[float]:
    """One-hot-ish vector for controlled similarity."""
    v = np.zeros(total, dtype=np.float32)
    v[idx] = 1.0
    return v.tolist()


@pytest.mark.asyncio
async def test_similar_texts_same_cluster():
    # Two nearly identical vectors → one cluster
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.99, 0.1, 0.0]
    texts = [{"text": "A", "email_id": "1"}, {"text": "B", "email_id": "2"}]
    packet = HandoffPacket(run_id=1, extracted_texts=texts, embeddings=[v1, v2])

    result = await cluster.run(packet, _config(threshold=0.9))
    flat = [item for c in result.clusters for item in c]
    assert len(flat) == 2


@pytest.mark.asyncio
async def test_distinct_texts_different_clusters():
    # Orthogonal vectors → separate clusters
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    texts = [{"text": "A", "email_id": "1"}, {"text": "B", "email_id": "2"}]
    packet = HandoffPacket(run_id=1, extracted_texts=texts, embeddings=[v1, v2])

    result = await cluster.run(packet, _config(threshold=0.9))
    assert len(result.clusters) == 2


@pytest.mark.asyncio
async def test_empty_embeddings():
    packet = HandoffPacket(run_id=1, extracted_texts=[], embeddings=[])
    result = await cluster.run(packet, _config())
    assert result.clusters == []
