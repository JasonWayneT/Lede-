"""Tests for app/services/music.py — CR-004, FR-029."""

from __future__ import annotations

from app.services import music


def _asset(id_, style, voice_safe=True):
    return {"id": id_, "style": style, "file": f"{style}/{id_}.mp3", "voice_safe": voice_safe}


# ---------------------------------------------------------------------------
# AC-070 — role override beats section/sensitivity
# ---------------------------------------------------------------------------


def test_role_override_beats_section_and_sensitivity():
    assert music.select_style("intro", "Politics", "crisis") == "premium_newsletter_intro"
    assert music.select_style("outro", "Finance", "sensitive") == "premium_newsletter_intro"
    assert music.select_style("section_transition", "AI", "crisis") == "headline_transition"


# ---------------------------------------------------------------------------
# AC-071 — sensitivity gate for main_summary
# ---------------------------------------------------------------------------


def test_sensitive_story_gets_no_music():
    assert music.select_style("main_summary", "AI", "sensitive") is None


def test_crisis_story_gets_no_music():
    assert music.select_style("main_summary", "Politics", "crisis") is None


def test_normal_and_serious_story_gets_music():
    assert music.select_style("main_summary", "AI", "normal") == "modern_tech_digest"
    assert music.select_style("main_summary", "Finance", "serious") == "business_briefing"


# ---------------------------------------------------------------------------
# AC-072 — section mapping + fallback
# ---------------------------------------------------------------------------


def test_known_sections_map_to_configured_style():
    assert music.select_style("main_summary", "AI", "normal") == "modern_tech_digest"
    assert music.select_style("main_summary", "Technology", "normal") == "modern_tech_digest"
    assert music.select_style("main_summary", "Finance", "normal") == "business_briefing"
    assert music.select_style("main_summary", "Politics", "normal") == "civic_affairs"
    assert music.select_style("main_summary", "Other", "normal") == "warm_daily_briefing"


def test_unmapped_section_falls_back_to_default_style():
    assert music.select_style("main_summary", "Sports", "normal") == music.DEFAULT_STYLE


# ---------------------------------------------------------------------------
# AC-073 — no voice-safe asset falls back to no music, not an error
# ---------------------------------------------------------------------------


def test_select_asset_returns_none_for_missing_style():
    assets = [_asset("a1", "business_briefing")]
    assert music.select_asset("civic_affairs", assets) is None


def test_select_asset_returns_none_when_not_voice_safe():
    assets = [_asset("a1", "civic_affairs", voice_safe=False)]
    assert music.select_asset("civic_affairs", assets) is None


def test_select_asset_returns_none_for_no_style():
    assert music.select_asset(None, [_asset("a1", "civic_affairs")]) is None


def test_select_asset_picks_deterministic_first_by_id():
    assets = [_asset("z_track", "civic_affairs"), _asset("a_track", "civic_affairs")]
    result = music.select_asset("civic_affairs", assets)
    assert result["id"] == "a_track"


# ---------------------------------------------------------------------------
# select_music — full pipeline, slimmed result shape
# ---------------------------------------------------------------------------


def test_select_music_returns_slimmed_record():
    assets = [_asset("modern_tech_digest_01", "modern_tech_digest")]
    result = music.select_music("main_summary", "AI", "normal", assets)
    assert result == {
        "asset_id": "modern_tech_digest_01",
        "style": "modern_tech_digest",
        "file": "modern_tech_digest/modern_tech_digest_01.mp3",
    }


def test_select_music_returns_none_for_sensitive_story():
    assets = [_asset("modern_tech_digest_01", "modern_tech_digest")]
    assert music.select_music("main_summary", "AI", "sensitive", assets) is None


def test_load_music_assets_reads_real_registry():
    # Sanity check against the actual committed registry, not just synthetic fixtures.
    assets = music.load_music_assets()
    assert len(assets) == 6
    ids = {a["id"] for a in assets}
    assert "modern_tech_digest_01" in ids
    assert "premium_newsletter_intro_01" in ids


# ── BUG-013: malformed music_assets.json degrades to no-music, not a crash ──

def test_load_music_assets_returns_empty_on_malformed_json(monkeypatch, tmp_path):
    bad_path = tmp_path / "music_assets.json"
    bad_path.write_text("{not valid json")
    monkeypatch.setattr(music, "MUSIC_ASSETS_PATH", bad_path)
    assert music.load_music_assets() == []


def test_load_music_assets_returns_empty_on_unreadable_file(monkeypatch, tmp_path):
    import os

    unreadable_path = tmp_path / "unreadable.json"
    unreadable_path.write_text("[]")

    def _raise_oserror(*args, **kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(music, "MUSIC_ASSETS_PATH", unreadable_path)
    monkeypatch.setattr(type(unreadable_path), "read_text", _raise_oserror)
    assert music.load_music_assets() == []
