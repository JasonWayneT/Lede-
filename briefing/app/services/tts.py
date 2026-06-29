"""Kokoro TTS synthesis service."""

# Implements FR-009, ARCH-003

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from app.core.errors import StageError

logger = logging.getLogger(__name__)

VOICES: dict[str, str] = {
    "af_heart":   "American Female — Heart (warm)",
    "af_bella":   "American Female — Bella (bright)",
    "af_nicole":  "American Female — Nicole (conversational)",
    "af_aoede":   "American Female — Aoede",
    "am_adam":    "American Male — Adam",
    "am_michael": "American Male — Michael",
    "bf_emma":    "British Female — Emma",
    "bf_isabella":"British Female — Isabella",
    "bm_george":  "British Male — George",
    "bm_lewis":   "British Male — Lewis",
}

_BRITISH = {"bf_emma", "bf_isabella", "bm_george", "bm_lewis"}

_pipeline: Any = None
_pipeline_lang: str | None = None


def _get_pipeline(lang_code: str) -> Any:
    global _pipeline, _pipeline_lang
    if _pipeline is None or _pipeline_lang != lang_code:
        from kokoro import KPipeline
        _pipeline = KPipeline(lang_code=lang_code)
        _pipeline_lang = lang_code
    return _pipeline


def _load_voice() -> str:
    settings_path = Path(__file__).parent.parent.parent / "data" / "settings.json"
    if settings_path.exists():
        try:
            return json.loads(settings_path.read_text()).get("tts_voice", "af_heart")
        except Exception:
            pass
    return "af_heart"


def _apply_pronunciation(script: str, guide: dict[str, str]) -> str:
    for term, pronunciation in guide.items():
        script = script.replace(term, pronunciation)
    return script


def _synthesize_sync(script: str, output_path: Path) -> None:
    import numpy as np
    import soundfile as sf

    voice = _load_voice()
    lang_code = "b" if voice in _BRITISH else "a"
    pipeline = _get_pipeline(lang_code)

    samples_list = []
    for _gs, _ps, audio in pipeline(script, voice=voice, speed=1.0):
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
