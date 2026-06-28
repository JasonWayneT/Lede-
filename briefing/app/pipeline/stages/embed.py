"""Embed stage — generate vector embeddings for extracted texts."""

# Implements ARCH-003

from __future__ import annotations

import asyncio
import logging

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.services import embeddings

logger = logging.getLogger(__name__)


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    texts = [entry["text"] for entry in packet.extracted_texts]
    if not texts:
        packet.embeddings = []
        return packet

    try:
        loop = asyncio.get_event_loop()
        vectors = await loop.run_in_executor(None, embeddings.encode, texts)
        packet.embeddings = vectors
        logger.info("Embed: encoded %d texts", len(vectors))
    except Exception as e:
        raise StageError("embed", str(e), retryable=True) from e

    return packet
