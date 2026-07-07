"""Tests for app/services/condense.py — CR-001, FR-027, ARCH-006."""

from __future__ import annotations

import re
from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import AppConfig
from app.services import condense


def _config():
    return AppConfig(llm_provider="ollama")


# ---------------------------------------------------------------------------
# AC-058 — under-budget passthrough
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_under_budget_passes_through_unchanged():
    text = "Short source text."
    with patch("app.services.condense.llm.complete", new=AsyncMock()) as mock_complete:
        result = await condense.condense(text, _config())
    assert result == text
    mock_complete.assert_not_called()


# ---------------------------------------------------------------------------
# AC-059 — sentence-boundary chunking, never mid-sentence
# ---------------------------------------------------------------------------


def test_split_into_chunks_never_splits_mid_sentence():
    sentence = "This is a sentence that repeats. "
    text = sentence * 400  # well over CONDENSE_CHUNK_CHARS
    chunks = condense._split_into_chunks(text)

    assert len(chunks) > 1
    for chunk in chunks:
        stripped = chunk.strip()
        assert stripped == "" or re.search(r"[.!?]$", stripped)


def test_split_into_chunks_handles_no_sentence_punctuation():
    text = "no punctuation just words " * 300
    chunks = condense._split_into_chunks(text)
    assert chunks  # falls back to a single chunk rather than raising


@pytest.mark.asyncio
async def test_over_budget_chunks_and_calls_llm_per_chunk():
    sentence = "This is a sentence that repeats. "
    text = sentence * 400  # over SOURCE_TEXT_BUDGET_CHARS

    with patch(
        "app.services.condense.llm.complete", new=AsyncMock(return_value="- fact one")
    ) as mock_complete:
        result = await condense.condense(text, _config())

    assert mock_complete.call_count > 1
    assert "fact one" in result


@pytest.mark.asyncio
async def test_condense_prompt_uses_condense_template():
    text = "Sentence one. " * 400
    captured_prompts = []

    async def capture(prompt, config, **kwargs):
        captured_prompts.append(prompt)
        return "extracted fact"

    with patch("app.services.condense.llm.complete", new=capture):
        await condense.condense(text, _config())

    assert captured_prompts
    assert "Extract only the facts" in captured_prompts[0]


# ---------------------------------------------------------------------------
# AC-060 — get_source_texts preserves cluster order, one call per entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_source_texts_preserves_order():
    cluster = [{"text": "first"}, {"text": "second"}, {"text": "third"}]
    result = await condense.get_source_texts(cluster, _config())
    assert result == ["first", "second", "third"]
