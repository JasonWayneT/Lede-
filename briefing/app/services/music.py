"""Music selection — deterministic style + asset selection for background music beds."""

# Implements FR-029 (see ADR-003, Music Roadmap Phase 3)

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MUSIC_BANK_DIR = Path(__file__).parent.parent.parent / "music_bank"
MUSIC_ASSETS_PATH = MUSIC_BANK_DIR / "music_assets.json"

# Segment role beats everything else. Not yet exercised end-to-end — Phase 4 hasn't built
# discrete intro/outro/section_transition segments yet — but ready for when it does. See ADR-003.
ROLE_OVERRIDES: dict[str, str] = {
    "intro": "premium_newsletter_intro",
    "outro": "premium_newsletter_intro",
    "section_transition": "headline_transition",
}

# section_name -> style, for main_summary stories. Falls back to DEFAULT_STYLE for any section
# not listed here, including user-renamed/added sections (FR-023). See ADR-003.
SECTION_STYLE_MAP: dict[str, str] = {
    "AI": "modern_tech_digest",
    "Technology": "modern_tech_digest",
    "Finance": "business_briefing",
    "Politics": "civic_affairs",
    "Other": "warm_daily_briefing",
}
DEFAULT_STYLE = "warm_daily_briefing"

_SENSITIVE_GATE = {"sensitive", "crisis"}


def load_music_assets() -> list[dict]:
    if not MUSIC_ASSETS_PATH.exists():
        logger.warning("Music: %s not found; no music will be selected", MUSIC_ASSETS_PATH)
        return []
    return json.loads(MUSIC_ASSETS_PATH.read_text(encoding="utf-8"))


def select_style(segment_role: str, section_name: str, sensitivity: str) -> str | None:
    """Return the style name to use, or None for no music."""
    if segment_role in ROLE_OVERRIDES:
        return ROLE_OVERRIDES[segment_role]
    if sensitivity in _SENSITIVE_GATE:
        return None
    return SECTION_STYLE_MAP.get(section_name, DEFAULT_STYLE)


def select_asset(style: str | None, assets: list[dict]) -> dict | None:
    """Pick a voice-safe asset for the given style.

    Deterministic: sorted by id, first match. V1 has exactly one clip per style, so this never
    actually breaks a tie yet — it exists so V2's multi-candidate/rotation work has a stable,
    already-tested selection point to extend. See ADR-003.
    """
    if style is None:
        return None
    candidates = [a for a in assets if a.get("style") == style and a.get("voice_safe")]
    if not candidates:
        logger.warning("Music: no voice_safe asset found for style '%s'", style)
        return None
    return sorted(candidates, key=lambda a: a["id"])[0]


def select_music(
    segment_role: str,
    section_name: str,
    sensitivity: str,
    assets: list[dict],
) -> dict | None:
    """Full selection: style, then asset, slimmed to what downstream mixing needs."""
    style = select_style(segment_role, section_name, sensitivity)
    asset = select_asset(style, assets)
    if asset is None:
        return None
    return {"asset_id": asset["id"], "style": asset["style"], "file": asset["file"]}
