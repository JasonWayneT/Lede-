"""Frame stage — assign depth tier, lead angle, and guardrails to each cluster."""

# Implements FR-005, ARCH-003

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.services import llm

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "pipeline_prompts" / "stages" / "frame.md"

_UPGRADE: dict[tuple[str, int], str] = {
    ("brief", 3): "standard",
    ("standard", 5): "deep",
}


def _depth_tier(baseline: str, source_count: int) -> str:
    for (base, threshold), upgraded in _UPGRADE.items():
        if baseline == base and source_count >= threshold:
            return upgraded
    return baseline


def _parse_frame_response(response: str) -> dict:
    import re
    text = response.strip()
    # Try direct parse first, then extract JSON block if LLM added preamble
    candidates = [text]
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        candidates.append(m.group(0))
    for candidate in candidates:
        try:
            data = json.loads(candidate)
            return {
                "lead_angle": str(data.get("lead_angle", "")),
                "local_stakes": str(data.get("local_stakes", "")),
                "guardrails": list(data.get("guardrails", [])),
            }
        except (json.JSONDecodeError, ValueError):
            continue
    logger.warning("Frame: could not parse LLM JSON response; using defaults")
    return {"lead_angle": "", "local_stakes": "", "guardrails": []}


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    framed: list[dict] = []

    for sc in packet.selected_clusters:
        cluster = sc.get("cluster", [])
        section_name = sc.get("section_name", "Other")
        source_count = len(cluster)
        depth_tier = _depth_tier(config.briefing_depth, source_count)

        snippets = "\n".join(f"- {entry.get('text', '')[:300]}" for entry in cluster)
        prompt = prompt_template.format(
            section=section_name,
            source_count=source_count,
            depth_tier=depth_tier,
            cluster_texts=snippets,
        )

        try:
            response = await llm.complete(prompt, config)
        except StageError:
            raise
        except Exception as e:
            raise StageError("frame", str(e), retryable=True) from e

        frame_data = _parse_frame_response(response)
        framed.append({
            **sc,
            "depth_tier": depth_tier,
            "source_count": source_count,
            **frame_data,
        })

    packet.framed_stories = framed
    logger.info("Frame: framed %d stories", len(framed))
    return packet
