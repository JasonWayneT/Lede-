"""TTS prep stage — build the audio segment plan and pronunciation guide.

Rewritten for FR-030 / BUG-005 (see ADR-004): the plan is built from `drafted_stories` (available
from the draft stage), not from `assembled_markdown` (which the later assemble stage populates).
"""

# Implements FR-010, FR-030, BUG-005, ARCH-003

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from app.core.config import AppConfig
from app.core.errors import StageError
from app.pipeline.handoff import HandoffPacket
from app.pipeline.ordering import order_stories_by_section
from app.services import llm, music

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent.parent.parent / "pipeline_prompts" / "stages" / "tts_prep.md"

# draft.md appends a "> Sources: ..." attribution trailer; strip it (and any stray markdown) for speech.
_SOURCES_LINE = re.compile(r"^\s*>?\s*Sources:.*$", re.IGNORECASE | re.MULTILINE)
_MARKDOWN_CHARS = re.compile(r"[#*_`]+")
_BLANK_LINES = re.compile(r"\n{3,}")


def _clean_prose(prose: str) -> str:
    """Deterministically turn drafted prose into narration text (prose is already broadcast-ready)."""
    text = _SOURCES_LINE.sub("", prose)
    text = _MARKDOWN_CHARS.sub("", text)
    text = _BLANK_LINES.sub("\n\n", text)
    return text.strip()


def _build_segments(packet: HandoffPacket, config: AppConfig) -> list[dict]:
    """Build the ordered audio segment plan from drafted stories + structural segments."""
    assets = music.load_music_assets()
    ordered = order_stories_by_section(packet.drafted_stories, config)

    segments: list[dict] = [{
        "role": "intro",
        "section_name": None,
        "text": "",
        "selected_music": music.select_music("intro", "", "normal", assets),
        "duration_seconds": None,
    }]

    for idx, (section, section_stories) in enumerate(ordered):
        if idx > 0:  # transition between sections, not before the first
            segments.append({
                "role": "section_transition",
                "section_name": section,
                "text": "",
                "selected_music": music.select_music("section_transition", section, "normal", assets),
                "duration_seconds": None,
            })
        for story in section_stories:
            segments.append({
                "role": "main_summary",
                "section_name": section,
                "text": _clean_prose(story.get("prose", "")),
                "story_weight": story.get("story_weight", "medium"),  # FR-031 — mix profile key
                "selected_music": story.get("selected_music"),
                "duration_seconds": None,
            })

    segments.append({
        "role": "outro",
        "section_name": None,
        "text": "",
        "selected_music": music.select_music("outro", "", "normal", assets),
        "duration_seconds": None,
    })
    return segments


async def _pronunciation_guide(narration: str, config: AppConfig) -> dict:
    """Single non-fatal LLM call — a flat term->spelling dict. Empty on any failure."""
    if not narration.strip():
        return {}
    prompt = PROMPT_PATH.read_text(encoding="utf-8").format(narration=narration)
    try:
        response = await llm.complete(prompt, config)
        m = re.search(r"\{[\s\S]*\}", response.strip())
        data = json.loads(m.group(0) if m else response.strip())
        return dict(data.get("pronunciation_guide", {}))
    except Exception as e:
        logger.warning("TTS prep: pronunciation guide failed (non-fatal): %s", e)
        return {}


async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket:
    segments = _build_segments(packet, config)
    packet.audio_segments = segments

    # Concatenated narration: the audio source of truth, and kept for qa_gate / resume compat.
    narration = "\n\n".join(s["text"] for s in segments if s["text"])
    packet.tts_script = narration
    packet.pronunciation_guide = await _pronunciation_guide(narration, config)

    narrated = sum(1 for s in segments if s["text"])
    logger.info("TTS prep: %d segments (%d narrated), script %d chars", len(segments), narrated, len(narration))
    return packet
