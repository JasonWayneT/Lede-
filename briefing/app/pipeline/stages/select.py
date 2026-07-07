"""Select stage — assign each cluster a freeform section name using the LLM."""

# Implements FR-032 (see CR-007 — supersedes FR-006's fixed-taxonomy design)

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

    selected: list[dict] = []
    for cluster in packet.clusters:
        snippets = "\n".join(
            f"- {entry.get('text', '')[:300]}" for entry in cluster
        )
        prompt = prompt_template.format(cluster_texts=snippets)
        try:
            response = await llm.complete(prompt, config)
        except StageError:
            raise
        except Exception as e:
            raise StageError("select", str(e), retryable=True) from e

        section_name = _clean_section_name(response)
        selected.append({"cluster": cluster, "section_name": section_name})

    packet.selected_clusters = selected
    logger.info("Select: classified %d clusters", len(selected))
    return packet


def _clean_section_name(response: str) -> str:
    """Sanitize the LLM's freeform section name into a short Title Case label."""
    name = response.strip().strip(".\"'").split("\n")[0].strip()
    if not name:
        return "Other"
    words = name.split()
    if len(words) > 3:
        return "Other"
    return " ".join(w.capitalize() if w.islower() else w for w in words)
