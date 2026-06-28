"""Draft stage — synthesize broadcast prose for each framed cluster."""

# Implements FR-006, ARCH-003

from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.services import llm

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "pipeline_prompts" / "stages" / "draft.md"


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    drafted: list[dict] = []

    for story in packet.framed_stories:
        cluster = story.get("cluster", [])
        section_name = story.get("section_name", "Other")
        depth_tier = story.get("depth_tier", config.briefing_depth)
        lead_angle = story.get("lead_angle", "")
        local_stakes = story.get("local_stakes", "")
        guardrails = story.get("guardrails", [])
        source_count = story.get("source_count", len(cluster))

        source_names = ", ".join(
            entry.get("sender_name", "") for entry in cluster if entry.get("sender_name")
        ) or "Unknown"

        snippets = "\n".join(f"- {entry.get('text', '')[:500]}" for entry in cluster)
        guardrails_text = "\n".join(f"- {g}" for g in guardrails) if guardrails else "None"

        prompt = prompt_template.format(
            depth_tier=depth_tier,
            section_name=section_name,
            lead_angle=lead_angle,
            local_stakes=local_stakes,
            cluster_texts=snippets,
            guardrails=guardrails_text,
            source_names=source_names,
        )

        try:
            prose = await llm.complete(prompt, config)
        except StageError:
            raise
        except Exception as e:
            raise StageError("draft", str(e), retryable=True) from e

        drafted.append({
            "section_name": section_name,
            "depth_tier": depth_tier,
            "prose": prose,
            "sources": [e.get("sender_name", "") for e in cluster if e.get("sender_name")],
            "source_count": source_count,
        })

    packet.drafted_stories = drafted
    logger.info("Draft: drafted %d stories", len(drafted))
    return packet
