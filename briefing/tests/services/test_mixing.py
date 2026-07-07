"""Tests for app/services/mixing.py — CR-006, FR-031."""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest

from app.services import mixing


def _stereo(n, value=1.0):
    return np.full((n, 2), value, dtype=np.float32)


# ---------------------------------------------------------------------------
# DSP primitives
# ---------------------------------------------------------------------------


def test_db_to_gain():
    assert mixing._db_to_gain(0) == pytest.approx(1.0)
    assert mixing._db_to_gain(-6) == pytest.approx(0.501, abs=0.005)


def test_to_stereo_from_mono():
    out = mixing._to_stereo(np.zeros(100, dtype=np.float32))
    assert out.shape == (100, 2)


def test_resample_changes_length_24k_to_44k():
    out = mixing._resample(np.zeros(24000, dtype=np.float32), 24000, 44100)
    assert out.shape[0] == 44100  # 24000 * 147/80


def test_apply_fade_ramps_edges():
    buf = _stereo(mixing.TARGET_SR)  # 1 second of full-scale
    out = mixing._apply_fade(buf, fade_in_s=0.1, fade_out_s=0.1)
    assert out[0, 0] == pytest.approx(0.0, abs=1e-3)
    assert out[-1, 0] == pytest.approx(0.0, abs=1e-3)
    assert out[mixing.TARGET_SR // 2, 0] == pytest.approx(1.0)  # untouched middle


def test_loop_to_length_extends_and_trims():
    short = _stereo(100)
    assert mixing._loop_to_length(short, 250).shape[0] == 250   # tiled
    assert mixing._loop_to_length(short, 40).shape[0] == 40     # trimmed


def test_clip_guard_caps_peak():
    hot = _stereo(10, value=2.0)
    out = mixing._clip_guard(hot)
    assert float(np.max(np.abs(out))) <= mixing._PEAK_CEILING + 1e-6


# ---------------------------------------------------------------------------
# mix_story — AC-080, AC-082, AC-084, AC-085
# ---------------------------------------------------------------------------


def test_mix_story_no_music_returns_dry_voice():
    voice = np.zeros(44100, dtype=np.float32)
    out = mixing.mix_story(voice, 44100, None, "medium")
    assert out.shape == (44100, 2)  # stereo, same length, no bed


def test_mix_story_output_matches_narration_length():
    voice = np.zeros(44100 * 3, dtype=np.float32)  # 3 s
    with patch("app.services.mixing._load_music", return_value=_stereo(44100 * 40)):
        out = mixing.mix_story(voice, 44100, {"file": "x.mp3"}, "medium")
    assert out.shape[0] == 44100 * 3  # bed looped/trimmed to the voice length


def test_mix_story_weight_selects_profile():
    # Silent voice + constant full-scale music: output is the ducked bed; lighter weight = louder.
    voice = np.zeros(44100 * 10, dtype=np.float32)  # long enough that fades don't cover the middle
    with patch("app.services.mixing._load_music", return_value=_stereo(44100 * 40)):
        light = mixing.mix_story(voice, 44100, {"file": "x.mp3"}, "light")
        heavy = mixing.mix_story(voice, 44100, {"file": "x.mp3"}, "heavy")
    assert float(np.max(np.abs(light))) > float(np.max(np.abs(heavy)))


def test_mix_story_is_stereo_44k_and_clip_guarded():
    voice = np.ones(44100, dtype=np.float32)
    with patch("app.services.mixing._load_music", return_value=_stereo(44100)):
        out = mixing.mix_story(voice, 44100, {"file": "x.mp3"}, "medium")
    assert out.shape[1] == 2
    assert float(np.max(np.abs(out))) <= mixing._PEAK_CEILING + 1e-6


# ---------------------------------------------------------------------------
# mix_structural — AC-081
# ---------------------------------------------------------------------------


def test_mix_structural_returns_faded_stinger():
    with patch("app.services.mixing._load_music", return_value=_stereo(44100 * 40)):
        out = mixing.mix_structural("intro", {"file": "x.mp3"})
    expected = int(mixing.STRUCTURAL_MIX_PROFILES["intro"]["duration"] * mixing.TARGET_SR)
    assert out.shape[0] == expected
    assert out[0, 0] == pytest.approx(0.0, abs=1e-3)  # faded in


def test_mix_structural_no_music_returns_none():
    assert mixing.mix_structural("intro", None) is None


# ---------------------------------------------------------------------------
# AC-083 — missing file is non-fatal
# ---------------------------------------------------------------------------


def test_missing_file_story_falls_back_to_dry_voice():
    voice = np.zeros(44100, dtype=np.float32)
    out = mixing.mix_story(voice, 44100, {"file": "does/not/exist.mp3"}, "medium")
    assert out.shape == (44100, 2)


def test_missing_file_structural_returns_none():
    assert mixing.mix_structural("intro", {"file": "does/not/exist.mp3"}) is None


# ---------------------------------------------------------------------------
# Real committed clip — validates soundfile MP3 read + scipy resample path
# ---------------------------------------------------------------------------


def test_real_clip_reads_and_mixes():
    selected = {"file": "transitions_identity/premium_newsletter_intro_01.mp3", "style": "premium_newsletter_intro"}
    out = mixing.mix_structural("intro", selected)
    assert out is not None
    assert out.shape[1] == 2
    assert out.shape[0] == int(mixing.STRUCTURAL_MIX_PROFILES["intro"]["duration"] * mixing.TARGET_SR)


# ---------------------------------------------------------------------------
# BUG-007 — transient compression and seamless loop
# ---------------------------------------------------------------------------


def test_compress_transients_tames_a_spike_without_erasing_quiet_signal():
    # A bounded sine (fixed ~3dB crest factor) as the "quiet" bed, not noise — noise has its own
    # random peaks that can trip a limiter and would make this test flaky for the wrong reason.
    sr = mixing.TARGET_SR
    t = np.arange(sr) / sr
    tone = (0.05 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    quiet = np.stack([tone, tone], axis=1)
    spike = quiet.copy()
    spike[sr // 2 : sr // 2 + 200] = 1.0  # ~4.5ms transient far above the quiet floor

    out = mixing._compress_transients(spike)

    spike_peak = float(np.max(np.abs(spike)))
    out_peak = float(np.max(np.abs(out)))
    assert out_peak < spike_peak  # the transient was pulled down

    quiet_region_before = float(np.sqrt(np.mean(np.square(spike[:1000]))))
    quiet_region_after = float(np.sqrt(np.mean(np.square(out[:1000]))))
    assert quiet_region_after == pytest.approx(quiet_region_before, rel=0.05)  # far from the spike, untouched


def test_compress_transients_handles_silence():
    silence = np.zeros((1000, 2), dtype=np.float32)
    out = mixing._compress_transients(silence)
    assert np.max(np.abs(out)) == 0.0


def test_loopable_unit_shorter_than_original_by_crossfade_length():
    buf = _stereo(mixing.TARGET_SR * 5)  # 5 s
    unit = mixing._make_loopable_unit(buf)
    expected_cf = int(mixing._LOOP_CROSSFADE_S * mixing.TARGET_SR)
    assert unit.shape[0] == buf.shape[0] - expected_cf


def test_looped_seam_has_no_discontinuity():
    # Use a clip with real variation (not constant) so a hard-tile seam would be detectable.
    rng = np.random.default_rng(1)
    buf = rng.normal(0, 0.2, size=(mixing.TARGET_SR * 3, 2)).astype(np.float32)
    unit_len = mixing._make_loopable_unit(buf).shape[0]

    looped = mixing._loop_to_length(buf, buf.shape[0] * 3)
    seam_jump = np.max(np.abs(looped[unit_len] - looped[unit_len - 1]))
    typical_jump = np.max(np.abs(np.diff(looped[:5000], axis=0)))

    # The seam should not stand out from ordinary sample-to-sample variation in the signal.
    assert seam_jump <= typical_jump * 5
