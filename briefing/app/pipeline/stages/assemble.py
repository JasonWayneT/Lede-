"""Assemble stage — organize drafted stories into a dated markdown briefing file."""

# Implements FR-007, ARCH-003, DATA-002

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.pipeline.ordering import order_stories_by_section

logger = logging.getLogger(__name__)


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    try:
        # Shared ordering so the markdown and the audio segment plan (tts_prep) agree — FR-030
        ordered = order_stories_by_section(packet.drafted_stories, config)

        # Build header
        total = len(packet.drafted_stories)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        breakdown_parts = []
        for sec, section_stories in ordered:
            count = len(section_stories)
            word = "story" if count == 1 else "stories"
            breakdown_parts.append(f"{sec}: {count} {word}")
        breakdown = " | ".join(breakdown_parts)

        lines: list[str] = [
            f"# Briefing — {date_str}",
            "",
            f"Run #{packet.run_id} | {total} {'story' if total == 1 else 'stories'} | {breakdown}",
            "",
        ]

        for section, section_stories in ordered:
            lines.append(f"## {section}")
            lines.append("")
            for story in section_stories:
                lines.append(story.get("prose", "").strip())
                lines.append("")
                lines.append("---")
                lines.append("")

        markdown = "\n".join(lines)
        packet.assembled_markdown = markdown

        # Write to disk
        output_dir = Path(config.data_dir) / "briefings" / str(packet.run_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "briefing.md"
        output_path.write_text(markdown, encoding="utf-8")
        packet.markdown_path = str(output_path)

        logger.info("Assemble: wrote briefing to %s", output_path)
    except Exception as e:
        raise StageError("assemble", str(e), retryable=False) from e

    return packet
