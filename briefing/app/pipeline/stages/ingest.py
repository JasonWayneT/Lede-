"""Ingest stage — fetch unprocessed emails into HandoffPacket."""

# Implements FR-001, ARCH-003

from __future__ import annotations

import logging

from app.core.config import AppConfig
from app.core.errors import StageError
from app.db.database import get_session
from app.pipeline.handoff import HandoffPacket
from app.services import gmail

logger = logging.getLogger(__name__)


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    try:
        async with get_session() as session:
            emails = await gmail.fetch_unprocessed_emails(config=config, session=session)
    except StageError:
        raise
    except Exception as e:
        raise StageError("ingest", str(e), retryable=True) from e

    packet.emails = emails
    logger.info("Ingest: fetched %d unprocessed emails", len(emails), extra={"run_id": packet.run_id})

    if not emails:
        packet.early_halt = True
        packet.halt_reason = "no_new_emails"

    return packet
