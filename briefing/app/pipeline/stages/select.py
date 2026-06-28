"""Select stage — assign each cluster to a section using LLM classification."""

# Implements FR-004, ARCH-003

from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.services import llm

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "pipeline_prompts" / "stages" / "select.md"


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    sections = config.sections
    if "Other" not in sections:
        sections = list(sections) + ["Other"]

    selected: list[dict] = []
    for cluster in packet.clusters:
        snippets = "\n".join(
            f"- {entry.get('text', '')[:300]}" for entry in cluster
        )
        prompt = prompt_template.format(
            sections=", ".join(sections),
            cluster_texts=snippets,
        )
        try:
            response = await llm.complete(prompt, config)
        except StageError:
            raise
        except Exception as e:
            raise StageError("select", str(e), retryable=True) from e

        section_name = _match_section(response.strip(), sections)
        selected.append({"cluster": cluster, "section_name": section_name})

    packet.selected_clusters = selected
    logger.info("Select: classified %d clusters", len(selected))
    return packet


def _match_section(response: str, sections: list[str]) -> str:
    normalized = response.strip().lower()
    for s in sections:
        if s.lower() == normalized:
            return s
    return "Other"
