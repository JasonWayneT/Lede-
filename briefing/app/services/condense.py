"""Conditional source-text condensation — map-step extraction for sources too long to pass whole."""

# Implements ARCH-006, FR-027

from __future__ import annotations

import logging
import re
from pathlib import Path

from app.core.config import AppConfig
from app.core.errors import StageError
from app.services import llm

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent.parent / "pipeline_prompts" / "stages" / "condense.md"

# Shared by frame.py and draft.py so both stages see the same amount of each source — see ADR-001.
SOURCE_TEXT_BUDGET_CHARS = 4000
CONDENSE_CHUNK_CHARS = 3000

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


def _split_into_chunks(text: str, target_chars: int = CONDENSE_CHUNK_CHARS) -> list[str]:
    """Split text into chunks near target_chars, breaking only on sentence boundaries."""
    sentences = [s.strip() for s in _SENTENCE_BOUNDARY.split(text) if s.strip()]
    if not sentences:
        return [text] if text.strip() else []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for sentence in sentences:
        if current and current_len + len(sentence) > target_chars:
            chunks.append(" ".join(current))
            current = []
            current_len = 0
        current.append(sentence)
        current_len += len(sentence)
    if current:
        chunks.append(" ".join(current))
    return chunks


async def condense(text: str, config: AppConfig) -> str:
    """Return text unchanged if it fits the shared budget; otherwise extract facts chunk by chunk.

    Condensation is a single map pass with no separate reduce LLM call — the frame/draft stages
    that consume the result already synthesize across a cluster's sources.
    """
    if len(text) <= SOURCE_TEXT_BUDGET_CHARS:
        return text

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    facts: list[str] = []
    for chunk in _split_into_chunks(text):
        prompt = prompt_template.format(chunk_text=chunk)
        try:
            response = await llm.complete(prompt, config)
        except StageError:
            raise
        except Exception as e:
            raise StageError("condense", str(e), retryable=True) from e
        facts.append(response.strip())

    return "\n".join(facts)


async def get_source_texts(cluster: list[dict], config: AppConfig) -> list[str]:
    """Return the LLM-ready text for each entry in a cluster, in order, condensing as needed."""
    return [await condense(entry.get("text", ""), config) for entry in cluster]
