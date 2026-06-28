"""Assemble stage — organize drafted stories into a dated markdown briefing file."""

# Implements FR-007, ARCH-003, DATA-002

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket

logger = logging.getLogger(__name__)


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    try:
        stories_by_section: dict[str, list[dict]] = defaultdict(list)
        for story in packet.drafted_stories:
            stories_by_section[story.get("section_name", "Other")].append(story)

        # Order sections per config, Other always last
        sections_order = [s for s in config.sections if s != "Other"] + ["Other"]
        ordered_sections = [s for s in sections_order if s in stories_by_section]
        # Add any remaining sections not in config order
        for s in stories_by_section:
            if s not in ordered_sections:
                ordered_sections.append(s)

        # Build header
        total = len(packet.drafted_stories)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        breakdown_parts = []
        for sec in ordered_sections:
            count = len(stories_by_section[sec])
            word = "story" if count == 1 else "stories"
            breakdown_parts.append(f"{sec}: {count} {word}")
        breakdown = " | ".join(breakdown_parts)

        lines: list[str] = [
            f"# Briefing — {date_str}",
            "",
            f"Run #{packet.run_id} | {total} {'story' if total == 1 else 'stories'} | {breakdown}",
            "",
        ]

        for section in ordered_sections:
            section_stories = sorted(
                stories_by_section[section], key=lambda s: s.get("source_count", 0), reverse=True
            )
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
