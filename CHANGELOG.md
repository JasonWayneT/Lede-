# Changelog — [Project Name]

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

> Entries accumulate here during active development. Move them into a versioned release when you ship.

[DRAFT] Fixes a bug where local (Ollama) briefings were silently limited to a tiny amount of
context regardless of the model in use, and replaces the fixed-length source-text truncation in
the frame/draft stages with content-aware condensation — so briefing stories read as real
explanations instead of headline-only summaries. Human reviews and finalizes before commit.

### Fixed
- BUG-001: Ollama requests never set the model's context window size, silently capping it at 2048 tokens no matter how large the configured model actually supports

### Changed
- Frame and draft stages now share one source-text budget instead of independently truncating each source to a small fixed length; sources that exceed the budget are condensed into their key facts (never cut mid-sentence) instead of chopped off

[DRAFT] Adds background music to the audio briefing. The briefing now opens and closes with a short
music theme, plays a stinger between sections, and runs a music bed under each story's narration —
with the style matched to the section (tech, business, politics, general) and music automatically
suppressed for sensitive or crisis stories. Human reviews and finalizes before commit.

### Added
- Background music in the audio briefing: intro/outro theme, section-transition stingers, and a ducked music bed under each story, selected by topic and muted for sensitive content

### Fixed
- BUG-005: the audio briefing was generated from an empty script because the narration step ran before the briefing text was assembled — narration is now built from the drafted stories, so the audio actually contains the briefing

---

## [0.1.0] — YYYY-MM-DD

### Added
- [New feature or capability visible to a user]

### Changed
- [Modification to existing behavior]

### Fixed
- [Bug that was corrected]

### Removed
- [Feature or behavior that was intentionally removed]

### Security
- [Vulnerability fixed or security improvement made]

---

<!--
INSTRUCTIONS FOR AGENTS AND CONTRIBUTORS

1. Add new entries under [Unreleased] as you work — not after the fact.
2. On release: rename [Unreleased] to the version + date, add a fresh [Unreleased] above it.
3. Use ISO dates: YYYY-MM-DD.
4. Omit empty sections — if nothing was Removed, skip the Removed header.
5. One entry per line. Start with a capital letter, no period at the end.
6. Focus on user-facing changes. Skip internal refactors unless they affect behavior.
-->
