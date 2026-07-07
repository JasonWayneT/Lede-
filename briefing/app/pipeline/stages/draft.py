"""Draft stage — synthesize broadcast prose for each framed cluster."""

# Implements FR-006, ARCH-003, FR-029

from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.services import condense, llm, music

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "pipeline_prompts" / "stages" / "draft.md"


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    drafted: list[dict] = []
    music_assets = music.load_music_assets()

    for story in packet.framed_stories:
        cluster = story.get("cluster", [])
        section_name = story.get("section_name", "Other")
        depth_tier = story.get("depth_tier", config.briefing_depth)
        lead_angle = story.get("lead_angle", "")
        local_stakes = story.get("local_stakes", "")
        guardrails = story.get("guardrails", [])
        source_count = story.get("source_count", len(cluster))
        sensitivity = story.get("sensitivity", "normal")
        story_weight = story.get("story_weight", "medium")

        source_names = ", ".join(
            entry.get("sender_name", "") for entry in cluster if entry.get("sender_name")
        ) or "Unknown"

        # Implements FR-027, ARCH-006 — reuse frame's condensed source_texts; fall back for
        # older persisted handoff artifacts (partial rerun) that predate this field.
        source_texts = story.get("source_texts")
        if source_texts is None:
            source_texts = await condense.get_source_texts(cluster, config)
        snippets = "\n".join(f"- {t}" for t in source_texts)
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

        # Implements FR-029 — not yet consumed; Phase 5 (mixing) will read this field
        selected_music = music.select_music(
            segment_role="main_summary",
            section_name=section_name,
            sensitivity=sensitivity,
            assets=music_assets,
        )

        drafted.append({
            "section_name": section_name,
            "depth_tier": depth_tier,
            "prose": prose,
            "sources": [e.get("sender_name", "") for e in cluster if e.get("sender_name")],
            "source_count": source_count,
            "story_weight": story_weight,  # FR-028/FR-031 — threaded through for the mix profile
            "selected_music": selected_music,
        })

    packet.drafted_stories = drafted
    logger.info("Draft: drafted %d stories", len(drafted))
    return packet
