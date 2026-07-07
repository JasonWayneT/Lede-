"""QA gate stage — deterministic pre-delivery validation."""

# Implements FR-013 (Check 1 revised per CR-007 — no longer requires per-section coverage)

from __future__ import annotations

import logging
import re

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket

logger = logging.getLogger(__name__)

_MARKDOWN_PATTERN = re.compile(r"##|(?<!\*)\*\*|(?<!\[)\[.+\]\(.+\)|https?://")


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    failures: list[str] = []

    # Check 1 — at least one story was selected overall.
    # Sections are now derived from content per-run, so an empty section on a
    # given day (e.g. no Politics news today) is expected, not a failure.
    if not packet.drafted_stories:
        failures.append("No stories were drafted for this briefing")

    # Check 2 — source attribution
    for story in packet.drafted_stories:
        if not story.get("sources"):
            failures.append("Story missing source attribution")
            break

    # Check 3 — TTS script cleanliness
    if packet.tts_script and _MARKDOWN_PATTERN.search(packet.tts_script):
        failures.append("TTS script contains unresolved markdown or URLs")

    # Check 4 — audio runtime estimate (~150 words/minute)
    if packet.tts_script:
        word_count = len(packet.tts_script.split())
        estimated_minutes = word_count / 150
        if estimated_minutes < 0.5 or estimated_minutes > 90:
            failures.append(
                f"Estimated audio runtime {estimated_minutes:.1f} min is outside acceptable range"
            )

    if failures:
        packet.qa_passed = False
        raise StageError("qa_gate", "; ".join(failures), retryable=True)

    packet.qa_passed = True
    logger.info("QA gate: all checks passed")
    return packet
