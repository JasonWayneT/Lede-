---
title: "Briefing: AI Newsletter Aggregator"
status: final
created: 2026-06-26
updated: 2026-06-26
---

# Product Brief: Briefing

## Executive Summary

Briefing is an open-source, self-hostable tool that converts a cluttered newsletter inbox into a single structured intelligence briefing — readable or listenable. It connects to Gmail via OAuth, pulls everything under a chosen label, and uses an LLM to synthesize stories across sources into topic sections like AI, Technology, Finance, and Politics. The unit of value is the story, not the email: if five newsletters covered the same Fed announcement, Briefing collapses them into one entry with attribution.

The output is a clean editorial document — repackaged as if written by a single editor who read everything so you didn't have to. From there, users can paste it into NotebookLM for an audio deep dive, or run the built-in TTS mode for a single-voice NPR-style briefing.

Built for builders and PMs, Briefing is designed to be cloned, configured, and run locally. It defaults to a local LLM via Ollama and supports BYOK for OpenAI, Anthropic, or Gemini. The author dogfoods it as the primary user while the codebase is polished for public distribution.

## The Problem

Knowledge workers who subscribe to multiple newsletters face a version of the same problem every day: the information they want exists in their inbox, distributed across a dozen emails from a dozen sources, often covering the same stories from different angles. Reading all of it is too slow. Skimming loses context. Ignoring it creates guilt.

Existing tools summarize emails — they don't synthesize them. The result is a shorter pile of the same pile. What's missing is an editorial layer: something that reads across sources, recognizes when three newsletters are covering the same story, and produces one coherent briefing organized by what matters, not by who sent it.

The audio gap is equally real. Most people have more commute time than reading time. There's no good path from "inbox full of newsletters" to "something I can listen to on the way to work" that doesn't require manual copy-pasting into other tools.

## The Solution

Briefing is a pipeline with a clear job at each stage:

1. **Ingest** — OAuth login with Google; pulls all emails under a configured Gmail label
2. **Extract** — strips HTML, pulls article text, title, sender, date, and links
3. **Cluster** — LLM identifies when multiple emails are covering the same story and groups them
4. **Classify** — assigns each story cluster to a user-configured topic section
5. **Synthesize** — writes one editorial summary per cluster: what happened, why it matters, which sources covered it
6. **Assemble** — produces a final briefing document ordered by section
7. **Deliver** — markdown, PDF, or audio (NotebookLM paste or local TTS)

The user triggers a run on demand. The briefing reflects the newsletters that arrived since the last run.

## What Makes This Different

| Capability | Typical digest tools | Briefing |
|---|---|---|
| Summarize each email | Standard | Intermediate step only |
| Cross-source story clustering | Rare | Core behavior |
| Deduplicate repeated stories | Rarely | Core behavior |
| Topic-organized editorial output | Weak | Primary output |
| Audio delivery | Absent | V1 via NotebookLM; V2 native TTS |
| Local LLM support | No | Default (Ollama) |
| BYOK API keys | No | Supported |
| Self-hostable | No | Yes — designed for it |

The honest moat here is execution and taste. The architecture is not novel; the editorial quality of the synthesis and the clean self-hosted developer experience are what will make this stand out as a portfolio piece and a usable tool.

## Who This Serves

**Primary: Builders and PMs** — technical users who subscribe to newsletters in their domain (AI, product, finance, tech) and want to replace inbox-scanning with a structured briefing they can read or listen to. Comfortable with a CLI setup, running Ollama, and configuring OAuth. Would share or star a well-built open-source tool.

**Secondary (future): Non-technical knowledge workers** — once a hosted version exists. [ASSUMPTION: not a V1 concern]

## Success Criteria

- Author uses it as the primary way to consume newsletters within 2 weeks of first run
- Setup time for a new technical user under 15 minutes
- Briefing quality: stories from the same event collapsed into one entry, not duplicated
- Audio output usable during a commute without re-listening to understand context
- GitHub stars / forks as a proxy for builder adoption post-launch

## Scope

**V1 — In:**
- Gmail OAuth (read-only scope)
- Single label ingest, configurable
- Local LLM via Ollama (default model: `[ASSUMPTION: llama3 or mistral — confirm based on quality testing]`)
- BYOK config for OpenAI, Anthropic, Gemini
- Story clustering and deduplication
- User-configurable topic sections
- Markdown briefing output
- NotebookLM audio path (export-ready doc, manual paste)
- On-demand CLI trigger
- Clean README, setup guide, example config

**V1 — Out:**
- Scheduled runs
- Native TTS / audio generation
- Web UI
- Hosted / multi-user version
- Email delivery of the briefing
- Non-Gmail sources (RSS, Substack API, etc.)

**V2 additions:**
- Scheduled runs (cron or background service)
- Native single-voice TTS (open-source, NPR style)
- Native single-voice TTS — NPR anchor style; **Kokoro** as default engine (82M params, Apache licensed, no GPU required), **Orpheus TTS** as quality upgrade path (3B params, ElevenLabs-tier, requires 6-8GB VRAM)
- Additional voice styles beyond NPR (e.g. conversational, broadcast news) as options where TTS provider allows

## Vision

Briefing becomes the best open-source newsletter aggregator with audio delivery. In two to three years: users configure their label sources, define their topic taxonomy, and receive a daily briefing in the format that fits their morning — clean document, single-voice audio, or both. A hosted version eventually lowers the barrier for non-technical users, but the self-hosted open-source core stays the foundation.

The roadmap is honest: nail the aggregation and editorial synthesis first, add audio delivery second, and expand voice styles and sources from there.
