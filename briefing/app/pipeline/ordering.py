"""Shared section-ordering for drafted stories.

Both the assemble stage (markdown) and the tts_prep stage (audio segment plan) must present
sections and stories in the same order, or the text briefing and the audio would disagree.
This is the single source of truth for that ordering.
"""

# Implements FR-030 (see ADR-004)

from __future__ import annotations

from collections import defaultdict

from app.core.config import AppConfig


def order_stories_by_section(
    drafted_stories: list[dict],
    config: AppConfig,
) -> list[tuple[str, list[dict]]]:
    """Return (section_name, stories) tuples in presentation order.

    Sections follow `config.sections` order with "Other" always last; any section present in the
    stories but absent from config is appended after. Within a section, stories are sorted by
    `source_count` descending.
    """
    stories_by_section: dict[str, list[dict]] = defaultdict(list)
    for story in drafted_stories:
        stories_by_section[story.get("section_name", "Other")].append(story)

    sections_order = [s for s in config.sections if s != "Other"] + ["Other"]
    ordered_sections = [s for s in sections_order if s in stories_by_section]
    for s in stories_by_section:
        if s not in ordered_sections:
            ordered_sections.append(s)

    return [
        (
            section,
            sorted(stories_by_section[section], key=lambda s: s.get("source_count", 0), reverse=True),
        )
        for section in ordered_sections
    ]
