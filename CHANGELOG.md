# Changelog — [Project Name]

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

> Entries accumulate here during active development. Move them into a versioned release when you ship.

[DRAFT] Production-readiness audit pass: fixes a real security gap in the on-demand link ingest
feature, a settings-saving bug on two Settings pages, and several places where the app could fail
silently or lose track of processed emails — plus brings the project's own spec documentation back
in sync with what the code actually does. Human reviews and finalizes before commit.

### Fixed
- BUG-008: on-demand article ingest could be tricked into fetching internal/private network addresses (a security hardening fix)
- BUG-009: Depth and AI Provider settings silently failed to save from the Settings page
- BUG-010: a corrupted lookback-window setting failed silently instead of logging a warning; a missing Gmail credentials file could crash instead of showing a clear message
- BUG-011: a missed scheduled run retried silently with no banner telling the user it happened
- BUG-012: a duplicate processed email could fail an entire briefing run
- BUG-013: a corrupted music-asset file crashed story writing instead of just skipping music
- BUG-014: one bad music clip could silence the entire briefing's audio instead of just that story
- BUG-015: two near-simultaneous run triggers could start two briefings at once
- BUG-016: Gemini errors were occasionally misclassified due to fragile text matching
- BUG-017: on-demand link ingest had no limit on how many links could be submitted at once
- BUG-018: a retried run could forget to mark its emails as processed, causing them to be reprocessed later

### Changed
- CR-007: documented that story topic sections are intentionally freeform for now (not yet matched to your configured topic list) — revisit once enough briefings exist to define a real topic list
- CR-008: documented the YouTube/article on-demand ingest feature properly (it worked already; the paperwork didn't exist)

### Developer
- All fixes above include regression tests; full test suite (287 tests) passes.
- Known, deliberately-deferred items: a retry-logic code duplication (low risk, one bug from it already fixed) and a rare daemon-process-identity edge case (would require adding a new dependency — flagged for a product decision rather than silently added).

---

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
