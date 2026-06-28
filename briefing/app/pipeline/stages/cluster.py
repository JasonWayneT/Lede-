"""Cluster stage — group similar text embeddings into story clusters."""

# Implements ARCH-003

from __future__ import annotations

import logging

import numpy as np

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.services import embeddings as embeddings_svc

logger = logging.getLogger(__name__)


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    if not packet.embeddings:
        packet.clusters = []
        return packet

    try:
        vecs = packet.embeddings
        index = embeddings_svc.build_index(vecs)
        threshold = config.similarity_threshold
        n = len(vecs)
        assigned: set[int] = set()
        clusters: list[list[dict]] = []

        for i in range(n):
            if i in assigned:
                continue
            query_vec = vecs[i]
            indices, distances = embeddings_svc.search(index, query_vec, k=n)
            cluster = []
            for j, d in zip(indices, distances):
                if d >= threshold and j not in assigned:
                    cluster.append(packet.extracted_texts[j])
                    assigned.add(j)
            if cluster:
                clusters.append(cluster)

        packet.clusters = clusters
        logger.info("Cluster: %d clusters from %d texts", len(clusters), n)
    except Exception as e:
        raise StageError("cluster", str(e), retryable=True) from e

    return packet
