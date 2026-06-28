"""Kokoro TTS synthesis service."""

# Implements FR-009, ARCH-003

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from app.core.errors import StageError

logger = logging.getLogger(__name__)

_pipeline: Any = None


def _get_pipeline() -> Any:
    global _pipeline
    if _pipeline is None:
        from kokoro import KPipeline
        _pipeline = KPipeline(lang_code="a")
    return _pipeline


def _apply_pronunciation(script: str, guide: dict[str, str]) -> str:
    for term, pronunciation in guide.items():
        script = script.replace(term, pronunciation)
    return script


def _synthesize_sync(script: str, output_path: Path) -> None:
    import numpy as np
    import soundfile as sf

    pipeline = _get_pipeline()
    samples_list = []
    for _gs, _ps, audio in pipeline(script, voice="af_heart", speed=1.0):
        if hasattr(audio, "numpy"):
            audio = audio.numpy()
        samples_list.append(audio)

    if not samples_list:
        raise RuntimeError("Kokoro returned no audio samples")

    samples = np.concatenate(samples_list)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), samples, 24000, format="mp3")


async def synthesize(
    script: str,
    output_path: Path,
    pronunciation_guide: dict[str, str] | None = None,
) -> None:
    if pronunciation_guide:
        script = _apply_pronunciation(script, pronunciation_guide)

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, _synthesize_sync, script, output_path)
        logger.info("TTS: audio written to %s", output_path)
    except Exception as e:
        raise StageError("tts", str(e), retryable=False) from e


def cuda_available() -> bool:
    try:
        import torch
        return bool(torch.cuda.is_available())
    except ImportError:
        return False
