"""Audio mixing — lay music beds under narration and render structural stingers.

Pure numpy / scipy / soundfile DSP, target 44.1 kHz stereo. No new dependency (see ADR-005).
"""

# Implements FR-031 (see ADR-005, Music Roadmap Phase 5)

from __future__ import annotations

import logging
from math import gcd

import numpy as np

from app.services import music

logger = logging.getLogger(__name__)

TARGET_SR = 44100
TARGET_CHANNELS = 2
_PEAK_CEILING = 0.99

# Implements BUG-007 — the AI-generated clips measured ~15dB crest factor (peak vs. RMS): quiet
# passages duck fine, but transients (drum hits) sit 15dB above the level the duck_db profiles were
# tuned against, so they can breach the voice regardless of where they land. Compress toward the
# clip's own RMS (measured consistent across all 6 clips at ~-14.3dBFS — no inter-clip level
# mismatch, so this does not change overall duck loudness) rather than a flat gain.
_TRANSIENT_CEILING_DB_OVER_RMS = 10.0
_ENVELOPE_ATTACK_MS = 8    # peak-capture window — must be short, or it averages the transient away
_GAIN_RELEASE_MS = 40      # smooths the resulting gain-reduction curve so it eases rather than snaps

# Loop seam crossfade — replaces a hard tile-and-cut with a blend of the clip's tail into its own
# head, so repeats (needed whenever a story runs longer than one ~25-30s clip) don't click/pop.
_LOOP_CROSSFADE_S = 1.0

# Story segments — music ducked under voice, keyed by story_weight. Values adapted from the
# original music policy report (section 21). Tunable by ear in Phase 6; edit here only.
STORY_MIX_PROFILES: dict[str, dict] = {
    "light":     {"duck_db": -22, "fade_in": 2.0, "fade_out": 3.0},
    "medium":    {"duck_db": -24, "fade_in": 2.5, "fade_out": 3.5},
    "heavy":     {"duck_db": -27, "fade_in": 3.0, "fade_out": 4.5},
    "sensitive": {"duck_db": -30, "fade_in": 3.5, "fade_out": 5.0},  # rarely reached (sensitive -> no music)
}
_DEFAULT_STORY_WEIGHT = "medium"

# Structural segments — music-only stingers, keyed by role.
STRUCTURAL_MIX_PROFILES: dict[str, dict] = {
    "intro":              {"gain_db": -14, "duration": 4.0, "fade_in": 1.0, "fade_out": 2.0},
    "outro":              {"gain_db": -14, "duration": 5.0, "fade_in": 1.0, "fade_out": 4.0},
    "section_transition": {"gain_db": -14, "duration": 2.5, "fade_in": 0.3, "fade_out": 1.0},
}


def _db_to_gain(db: float) -> float:
    return float(10.0 ** (db / 20.0))


def _to_stereo(samples: np.ndarray) -> np.ndarray:
    a = np.asarray(samples, dtype=np.float32)
    if a.ndim == 1:
        return np.stack([a, a], axis=1)
    if a.ndim == 2 and a.shape[1] == 1:
        return np.repeat(a, 2, axis=1)
    return a


def _resample(samples: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    if sr_in == sr_out:
        return np.asarray(samples, dtype=np.float32)
    from scipy.signal import resample_poly

    g = gcd(sr_out, sr_in)
    up, down = sr_out // g, sr_in // g
    return resample_poly(samples, up, down, axis=0).astype(np.float32)


def _apply_fade(buf: np.ndarray, fade_in_s: float, fade_out_s: float) -> np.ndarray:
    out = buf.copy()
    n = out.shape[0]
    fi = min(int(fade_in_s * TARGET_SR), n)
    fo = min(int(fade_out_s * TARGET_SR), n)
    if fi > 0:
        out[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    if fo > 0:
        out[n - fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    return out


def _moving_average(x: np.ndarray, window: int) -> np.ndarray:
    """Box-filter smoothing with edge-value padding.

    `np.convolve(..., mode="same")` implicitly zero-pads at the boundary, which falsely assumes
    silence just outside the buffer — for a gain-reduction curve that pulls gain toward 0 for the
    first/last `window/2` samples of every clip, an artifact unrelated to the actual signal.
    """
    if window <= 1:
        return x
    pad_before = window // 2
    pad_after = window - 1 - pad_before
    padded = np.pad(x, (pad_before, pad_after), mode="edge")
    kernel = np.ones(window, dtype=np.float32) / window
    return np.convolve(padded, kernel, mode="valid").astype(np.float32)


def _compress_transients(samples: np.ndarray, ceiling_db_over_rms: float = _TRANSIENT_CEILING_DB_OVER_RMS) -> np.ndarray:
    """Tame transient peaks relative to the clip's own RMS, without changing overall loudness.

    Peak-detect via a short max-filter (an average would dilute a brief drum hit rather than
    catch it), then smooth only the resulting gain-reduction curve so the correction eases in/out
    instead of snapping. Not a full attack/release compressor, but enough to stop drum hits from
    poking through a duck level tuned against the clip's quieter passages. See BUG-007.
    """
    if samples.size == 0:
        return samples
    mono_abs = np.mean(np.abs(samples), axis=-1)
    rms = float(np.sqrt(np.mean(np.square(mono_abs))))
    if rms <= 1e-9:
        return samples

    from scipy.ndimage import maximum_filter1d

    ceiling = rms * _db_to_gain(ceiling_db_over_rms)
    envelope = maximum_filter1d(mono_abs, size=max(1, int(TARGET_SR * _ENVELOPE_ATTACK_MS / 1000)))
    gain = np.minimum(1.0, ceiling / np.maximum(envelope, 1e-9))
    gain = _moving_average(gain, max(1, int(TARGET_SR * _GAIN_RELEASE_MS / 1000)))
    gain = np.clip(gain, 0.0, 1.0)
    return (samples * gain[:, None]).astype(np.float32)


def _make_loopable_unit(buf: np.ndarray, crossfade_s: float = _LOOP_CROSSFADE_S) -> np.ndarray:
    """Blend the clip's tail into its own head so tiling the result repeats with no hard seam."""
    n = buf.shape[0]
    cf = min(int(crossfade_s * TARGET_SR), n // 2)
    if cf <= 0:
        return buf
    fade_in = np.linspace(0.0, 1.0, cf, dtype=np.float32)[:, None]
    fade_out = np.linspace(1.0, 0.0, cf, dtype=np.float32)[:, None]
    blended_head = buf[:cf] * fade_in + buf[n - cf:] * fade_out
    return np.concatenate([blended_head, buf[cf:n - cf]], axis=0)


def _loop_to_length(buf: np.ndarray, n: int) -> np.ndarray:
    if buf.shape[0] >= n:
        return buf[:n]
    unit = _make_loopable_unit(buf)
    if unit.shape[0] == 0:
        return buf[:n]
    reps = int(np.ceil(n / unit.shape[0]))
    return np.tile(unit, (reps, 1))[:n]


def _clip_guard(buf: np.ndarray) -> np.ndarray:
    peak = float(np.max(np.abs(buf))) if buf.size else 0.0
    if peak > _PEAK_CEILING:
        buf = buf * (_PEAK_CEILING / peak)
    return buf.astype(np.float32)


def _load_music(selected_music: dict | None) -> np.ndarray | None:
    """Load a music clip as 44.1 kHz stereo float32, or None if missing/absent (non-fatal)."""
    if not selected_music:
        return None
    path = music.MUSIC_BANK_DIR / selected_music["file"]
    if not path.exists():
        logger.warning("Mixing: music file missing: %s (falling back to no music)", path)
        return None
    import soundfile as sf

    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    data = _resample(data, sr, TARGET_SR)
    data = _to_stereo(data)
    return _compress_transients(data)


def mix_story(narration: np.ndarray, sr_in: int, selected_music: dict | None, story_weight: str) -> np.ndarray:
    """Mix a music bed under a story's narration. No/absent music -> dry voice."""
    voice = _to_stereo(_resample(np.asarray(narration, dtype=np.float32), sr_in, TARGET_SR))
    bed_src = _load_music(selected_music)
    if bed_src is None:
        return _clip_guard(voice)

    profile = STORY_MIX_PROFILES.get(story_weight, STORY_MIX_PROFILES[_DEFAULT_STORY_WEIGHT])
    bed = _loop_to_length(bed_src, voice.shape[0]) * _db_to_gain(profile["duck_db"])
    bed = _apply_fade(bed, profile["fade_in"], profile["fade_out"])
    return _clip_guard(voice + bed)


def mix_structural(role: str, selected_music: dict | None) -> np.ndarray | None:
    """Render a music-only stinger for an intro/outro/section_transition. None if no music/profile."""
    bed_src = _load_music(selected_music)
    profile = STRUCTURAL_MIX_PROFILES.get(role)
    if bed_src is None or profile is None:
        return None

    n = int(profile["duration"] * TARGET_SR)
    bed = _loop_to_length(bed_src, n) * _db_to_gain(profile["gain_db"])
    bed = _apply_fade(bed, profile["fade_in"], profile["fade_out"])
    return _clip_guard(bed)
