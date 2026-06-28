"""TTS prep stage — rewrite assembled markdown into a spoken narration script."""

# Implements FR-008, ARCH-003

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.services import llm

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "pipeline_prompts" / "stages" / "tts_prep.md"


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = prompt_template.format(assembled_markdown=packet.assembled_markdown)

    try:
        response = await llm.complete(prompt, config)
    except StageError:
        raise
    except Exception as e:
        raise StageError("tts_prep", str(e), retryable=True) from e

    try:
        data = json.loads(response.strip())
        packet.tts_script = str(data.get("tts_script", ""))
        packet.pronunciation_guide = dict(data.get("pronunciation_guide", {}))
    except (json.JSONDecodeError, ValueError):
        logger.warning("TTS prep: could not parse LLM JSON; using raw response as script")
        packet.tts_script = response
        packet.pronunciation_guide = {}

    logger.info("TTS prep: script length %d chars", len(packet.tts_script))
    return packet
