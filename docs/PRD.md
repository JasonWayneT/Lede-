---
title: "PRD: Briefing"
status: final
created: 2026-06-26
updated: 2026-06-26
revised: 2026-06-26
---

# PRD: Briefing

## 0. Document Purpose

This PRD is written for the builder implementing Briefing and for downstream architecture and epic planning. It defines what the system does and what success looks like — not how it is implemented. Technical mechanism decisions (embedding model choice, LLM routing logic, packaging approach) live in the addendum. Vocabulary is anchored in §3 Glossary; all FRs use those terms exactly.

---

## 1. Vision

Briefing is an open-source, self-hostable newsletter aggregator that converts a cluttered inbox into a single structured editorial briefing — readable or listenable. It connects to Gmail via OAuth, pulls everything under a configured label, and synthesizes stories across sources into topic sections. The unit of value is the **Story**, not the email: if five newsletters covered the same event, Briefing collapses them into one entry with attribution.

The user experience is modeled after NotebookLM — a dated text file and audio file waiting for them when they want it, triggered either on a schedule or manually. The output reads as if written by a single editor who read everything so the user didn't have to.

Built for builders and PMs, Briefing runs locally, defaults to a local LLM via Ollama, and supports BYOK for cloud providers. It is designed to be cloned, configured, and run by anyone technical enough to set it up.

---

## 2. Target User

### 2.1 Jobs To Be Done

- Read across many newsletters without reading any of them individually
- Stay informed on a few specific topics (AI, tech, finance, politics) without inbox-scanning
- Have a briefing ready to listen to during a commute or walk — without manually assembling it
- Self-host a tool that handles their information diet without giving their data to a third party
- Show or share a well-built open-source project with other builders

### 2.2 Non-Users (V1)

- Non-technical users who cannot run a local server or configure OAuth
- Teams wanting a shared briefing (multi-user is out of scope)
- Users on email providers other than Gmail

### 2.3 Key User Journeys

- **UJ-1. Jason runs his first briefing.**
  - **Persona + context:** Jason, a PM, has cloned the repo, completed setup, and has 30+ unread newsletters in his Gmail "Newsletters" label.
  - **Entry state:** Browser open to `localhost:3000`. Gmail OAuth already authorized during setup. Ollama running locally.
  - **Path:** He clicks **Run Briefing**. The UI shows a progress indicator. The pipeline runs: emails pulled, stories clustered, briefing synthesized. A new dated entry appears in the Briefing History list showing today's date, story count, and section breakdown.
  - **Climax:** He clicks the entry, reads the briefing in the browser, and downloads both the markdown and audio files.
  - **Resolution:** Processed email IDs are logged locally. They will not appear in future runs.
  - **Edge case:** If no new emails exist under the label since the last run, the UI shows "No new newsletters since your last briefing" and does not create a new entry.

- **UJ-2. Jason sets a daily schedule.**
  - **Persona + context:** After using Briefing manually for a week, Jason wants a briefing ready every morning without thinking about it.
  - **Entry state:** Settings page open.
  - **Path:** He sets cadence to "Daily" and picks a time (7:00 AM). He saves. The app confirms the schedule is active.
  - **Climax:** The next morning, a new briefing entry is in the history list when he opens the app — without him triggering it.
  - **Resolution:** He downloads the audio file and listens on his commute.
  - **Edge case:** If the app is not running at the scheduled time and daemon mode is off, the run is missed. On next app open, the app detects the missed run and retries it automatically before showing the history list.

- **UJ-3. A builder clones and configures Briefing for the first time.**
  - **Persona + context:** A PM who saw the repo on GitHub wants to set it up for their own newsletters.
  - **Entry state:** Fresh clone, README open.
  - **Path:** Runs setup script. Authorizes Gmail OAuth via browser redirect. Opens Settings, configures their Gmail label, selects topic sections, enters their Ollama model name (or BYOK API key). Saves.
  - **Climax:** Runs their first briefing. A briefing appears that reflects their actual newsletter diet.
  - **Resolution:** Under 15 minutes from clone to first briefing.

---

## 3. Glossary

- **Briefing** — The final output document produced by one pipeline run. Contains topic sections, each with one or more Story entries. Identified by date and run ID.
- **Run** — One execution of the full pipeline: ingest → extract → embed → cluster → classify → synthesize → assemble. Triggered manually or on schedule.
- **Newsletter** — A single email pulled from the configured Gmail label.
- **Story** — The atomic unit of content in a Briefing. Represents one topic or event, potentially synthesized from multiple Newsletters that covered the same subject. Contains a summary, "why it matters" note, and source attribution.
- **Section** — A user-configured topic grouping within a Briefing (e.g. AI, Technology, Finance, Politics). Each Section contains one or more Stories.
- **Label** — A Gmail label the user configures as the source for ingest (e.g. "Newsletters").
- **Cluster** — A group of Newsletter excerpts determined by the pipeline to be covering the same Story, identified via embedding similarity before LLM synthesis.
- **BYOK** — Bring Your Own Key. User-supplied API key for a cloud LLM provider (OpenAI, Anthropic, Gemini) used instead of the local Ollama default.
- **Provider** — The LLM backend used for synthesis: Ollama (local default) or a BYOK cloud provider.
- **Briefing History** — The list of past Briefings shown in the UI, each with download links.
- **Processed Log** — A lightweight local file (maintained by the app) recording the email IDs that have already been included in a Run. Used to skip previously processed emails on future Runs. Can be cleared by the user to reprocess emails.
- **Audio File** — A generated audio narration of a Briefing, produced by the TTS engine. Delivered as an `.mp3` or `.wav` file alongside the markdown file.
- **TTS Engine** — The local text-to-speech model used to generate Audio Files. Default: Kokoro (82M params, Apache 2.0). Upgrade path: Orpheus TTS (3B params, requires GPU).
- **Daemon Mode** — An optional background service that keeps the scheduler running even when the browser UI is closed, so scheduled Runs fire at their configured time without the user having the app open.

---

## 4. Features

### 4.1 Gmail Ingest

**Description:** The system connects to Gmail via OAuth 2.0 (read-only scope) and pulls emails from the configured Label that have not been previously processed. Already-processed emails are identified via the local Processed Log — Gmail is never modified. Realizes UJ-1, UJ-2, UJ-3.

**Functional Requirements:**

#### FR-1: Gmail OAuth Authorization
User can authorize Gmail access via a browser-based OAuth 2.0 flow during initial setup. The system stores the resulting token locally.

**Consequences (testable):**
- After authorization, the app can read emails from the user's Gmail account without re-prompting
- Token is stored on the local filesystem, not transmitted to any remote service
- Re-authorization is triggered if the token expires or is revoked

#### FR-2: Label-Based Email Fetch
The system fetches emails from the user-configured Label that do not appear in the Processed Log on each Run.

**Consequences (testable):**
- Only emails under the configured Label are fetched
- Emails whose IDs are in the Processed Log are skipped
- If zero unprocessed emails exist, the Run halts early and the UI reports "No new newsletters since your last briefing"

#### FR-3: Processed Log Management
After a successful Run, the system appends the processed email IDs and timestamps to the local Processed Log. The user can clear the log from Settings to reprocess all emails.

**Consequences (testable):**
- Processed email IDs are written to the log only after a fully successful Run
- If the Run fails mid-pipeline, no IDs are written — all emails will be retried on the next Run
- Clearing the log does not modify anything in Gmail
- Gmail OAuth scope remains read-only at all times

---

### 4.2 Pipeline — Modular Production Architecture

**Description:** The core intelligence of Briefing is implemented as a series of bounded pipeline modules, each with a single responsibility and a structured handoff packet output. No module receives full pipeline history — only the minimum context required for its job. This discipline enables reliable operation on local LLMs with limited context windows, supports partial reruns when a stage fails, and makes each stage independently testable. The pipeline follows: Extract → Embed → Cluster → Editorial Selection → Story Framing → Script Drafting → TTS Preparation → Assembly → QA Gate. Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-4: HTML-to-Text Extraction
The system extracts plain text, title, sender name, and date from each Newsletter's HTML body.

**Consequences (testable):**
- Output is clean readable text with no HTML tags, tracking pixels, or navigation chrome
- Title, sender, and date are preserved as metadata on each extracted chunk

#### FR-5: Embedding-Based Story Clustering
The system generates embeddings for extracted Newsletter chunks and groups them into Clusters using similarity thresholds.

**Consequences (testable):**
- Chunks covering the same event (e.g. a Fed rate decision) are grouped into a single Cluster regardless of which Newsletter they came from
- Chunks covering distinct events are not merged
- Clustering runs without LLM calls [ASSUMPTION: local embedding model via Ollama or a lightweight library; to be decided in architecture]

#### FR-6: Section Classification
Each Cluster is assigned to a user-configured Section (e.g. AI, Technology, Finance, Politics).

**Consequences (testable):**
- Every Cluster is assigned to exactly one Section
- Clusters that do not fit any configured Section are placed in a catch-all "Other" Section
- Classification uses the configured LLM Provider

#### FR-7: Story Framing
Before drafting, the system assigns each Cluster a depth tier, lead angle, local stakes note, and guardrails based on the user's Briefing Depth setting and the story's source strength.

**Consequences (testable):**
- Every Cluster receives a depth tier: Brief (bulletin), Standard (secondary item), or Deep (mini-segment)
- Depth tier determines synthesis prompt behavior in FR-7a
- Stories with uncertain claims receive explicit guardrail notes carried into drafting

#### FR-7a: Story Synthesis (Script Drafting)
The system generates one Story per Cluster as natural editorial prose — a broadcast-style narrative with a clear lead, "why it matters" note, and source attribution. Synthesis depth follows the assigned tier from FR-7.

**Consequences (testable):**
- Brief tier: 2–3 sentences, headline plus essential context
- Standard tier: short narrative paragraph with what happened, why it matters, and local stakes
- Deep tier: full mini-segment with nuance, conflicting angles if present, and background context
- Each Story reads as spoken prose, not bullet points
- Source attribution names each Newsletter that contributed
- Synthesis uses the configured LLM Provider

#### FR-8: Briefing Assembly
The system assembles all Stories into a single Briefing document, organized by Section, with a header showing the date, total story count, and section breakdown.

**Consequences (testable):**
- Sections appear in the order configured by the user
- Each Section contains its Stories sorted by relevance [ASSUMPTION: relevance = number of sources that covered the story; most-covered first]
- The assembled Briefing is saved as a dated markdown file

---

### 4.3 Audio Generation (TTS)

**Description:** Audio generation is a two-stage process. First, the assembled Briefing prose is rewritten specifically for spoken delivery (TTS Preparation). Second, the optimized script is passed to the TTS Engine to produce an Audio File. Separating these stages ensures the spoken output sounds like a real broadcast rather than a text document read aloud. The default TTS Engine is Kokoro (no GPU required). Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-9: TTS Script Preparation
The system rewrites the assembled Briefing prose into a TTS-optimized narration script: shorter sentences, punctuation as pacing cues, spoken segues between sections, and a pronunciation guide for names and acronyms.

**Consequences (testable):**
- Output contains no markdown syntax, raw URLs, or attribution brackets
- Section transitions are natural spoken segues ("Turning to technology…")
- Sentences are short enough for natural spoken delivery — no print-style density
- A pronunciation guide for proper nouns and acronyms is produced alongside the script

#### FR-10: Audio File Generation
The system passes the TTS-optimized script to the TTS Engine and produces a dated Audio File saved alongside the markdown Briefing.

**Consequences (testable):**
- Audio file is saved in the same output location as the markdown file
- File is named consistently with the Briefing date and run ID
- If TTS Engine is unavailable or fails, the Run completes with the markdown file only and surfaces a clear warning in the pipeline log — audio failure does not fail the whole Run

#### FR-11: TTS Engine Configuration
User can select and configure the TTS Engine from the Settings page (Kokoro default, Orpheus if available).

**Consequences (testable):**
- Default engine (Kokoro) works on CPU with no GPU required
- Switching to Orpheus surfaces a hardware requirement warning if no GPU is detected
- A "Test Voice" action plays a sample sentence so the user can verify output quality before running

---

### 4.4 QA Gate and Error Recovery

**Description:** Before a Briefing is delivered to the history list, it passes through a lightweight QA gate that validates completeness, source attribution, and runtime budget. If the gate catches an issue, the pipeline attempts automatic remediation via a structured retry policy before surfacing a recoverable hold state to the user — not a silent failure or a crash. Realizes UJ-1, UJ-2.

**Functional Requirements:**

#### FR-12: Pre-Delivery QA Validation
After assembly and TTS preparation, the system validates the Briefing package before marking the Run complete.

**Consequences (testable):**
- Validation checks: all configured Sections have at least one Story, all Stories have source attribution, TTS script contains no unresolved markdown or URL strings, estimated audio runtime is within a reasonable range of content volume
- A passing QA gate marks the Run complete and delivers the Briefing to history
- A failing gate triggers FR-13 retry logic before surfacing the error to the user

#### FR-13: Structured Retry and Remediation
When the QA gate catches an issue, the pipeline attempts staged remediation before escalating to the user.

**Consequences (testable):**
- First failure: the failing pipeline stage retries with concise error feedback injected into its context
- Second failure: the stage retries with expanded context and explicit correction guidance
- Third failure: the Run enters a **Hold** state — the Briefing appears in history marked "Needs Review" with a plain-English description of the issue and a manual retry option
- The user can trigger a manual retry from the Hold state or dismiss it
- No Run silently fails — every failure surfaces in the pipeline log with a specific error description

---

### 4.5 LLM Provider Configuration

**Description:** Briefing defaults to a local Ollama instance for all LLM calls. Users can override this with a BYOK API key for OpenAI, Anthropic, or Gemini. Provider selection and model name are configured in Settings. Realizes UJ-3.

**Functional Requirements:**

#### FR-14: Ollama Local Default
The system uses a locally running Ollama instance as the default LLM Provider, with a configurable model name.

**Consequences (testable):**
- If Ollama is running and the configured model is available, the pipeline runs without any internet connection or API key
- If Ollama is not reachable, the system surfaces a clear error before the pipeline starts

#### FR-15: BYOK Cloud Provider Support
User can configure an API key for OpenAI, Anthropic, or Gemini as an alternative Provider.

**Consequences (testable):**
- API key is stored in an encrypted local store and never transmitted beyond the selected provider's API
- Switching providers takes effect on the next Run without restarting the app

---

### 4.6 First-Run Onboarding

**Description:** On first launch, the app presents a guided onboarding wizard that collects the minimum required configuration to run a briefing. OAuth is required and cannot be skipped. Everything else (API keys, topic sections, schedule) is optional and skippable — the user can configure those later in Settings. The wizard is not shown again after completion unless the user resets onboarding from Settings. Realizes UJ-3.

**Functional Requirements:**

#### FR-16: First-Run Onboarding Wizard
On first launch, the app presents a step-by-step setup flow covering: Google OAuth authorization, Kokoro model download, optional BYOK API key entry, and optional topic section configuration.

**Consequences (testable):**
- Wizard is shown only on first launch or after a settings reset
- OAuth step is required — the wizard cannot proceed past it without a valid token
- Kokoro download runs automatically with a progress indicator; user does not need to take manual action
- All steps after OAuth display a "Skip for now" option
- Skipped steps are surfaced as incomplete in Settings with a prompt to complete them
- On completion, the user lands on the main dashboard ready to run their first briefing

#### FR-17: Onboarding Revisit in Settings
User can return to any onboarding configuration (OAuth, API keys, topic sections, schedule) from the Settings page at any time.

**Consequences (testable):**
- Settings surface a clear status for each onboarding item (configured / incomplete)
- Incomplete items are callable from Settings without going through the full wizard again

---

### 4.7 Local Web UI

**Description:** A lightweight web interface served at `localhost` that gives the user a trigger button, a live pipeline log, a Briefing History list, and a Settings page. The app runs as a local server; the user interacts via their browser. Realizes UJ-1, UJ-2, UJ-3.

**Functional Requirements:**

#### FR-18: Run Briefing Trigger
User can trigger a Run manually by clicking a button in the UI.

**Consequences (testable):**
- The trigger button is disabled while a Run is in progress
- On completion, the new Briefing appears in Briefing History without a page refresh

#### FR-19: Live Pipeline Progress Log
While a Run is active, the UI displays a real-time log of pipeline stages and status messages.

**Consequences (testable):**
- Each pipeline stage (ingest, extract, cluster, classify, synthesize, assemble, audio) appears as it begins and completes
- Errors surface inline in the log with a clear message — the user does not need to check a terminal
- Log persists after Run completion so the user can review what happened

#### FR-20: Briefing History List
The UI displays a list of all past Briefings, each showing date, story count, and section breakdown.

**Consequences (testable):**
- Each entry links to a readable view of the Briefing in the browser
- Each entry has separate download buttons for the markdown file and Audio File
- Entries are sorted newest-first

#### FR-21: Settings — Gmail
User can configure the Gmail Label used for ingest and re-authorize OAuth from the Settings page.

**Consequences (testable):**
- Label change takes effect on the next Run
- Re-authorization opens the Google OAuth flow in the browser

#### FR-22: Settings — Topic Sections
User can add, remove, rename, and reorder their Sections from the Settings page.

**Consequences (testable):**
- Section changes take effect on the next Run
- At least one Section must be configured; the UI prevents removing the last one
- An "Other" catch-all Section always exists and cannot be removed

#### FR-23: Settings — Briefing Depth
User can select a default Briefing Depth (Brief, Standard, Deep) from the Settings page.

**Consequences (testable):**
- Brief: each Story is 2–3 sentences — headline plus essential context
- Standard: each Story is a short narrative paragraph — what happened, why it matters, local stakes
- Deep: each Story is a full mini-segment — nuance, conflicting angles if present, background context
- Depth setting applies to all Stories in a Run; individual story depth may vary based on source strength [ASSUMPTION: depth is a global setting, not per-story, in V1]
- Default is Standard

#### FR-24: Settings — LLM Provider
User can select their Provider (Ollama or a BYOK cloud provider), enter a model name or API key, and test the connection from the Settings page.

**Consequences (testable):**
- A "Test Connection" action confirms the Provider is reachable before saving
- API keys are masked in the UI after entry and stored in an encrypted local store

#### FR-25: Settings — Schedule and Daemon
User can configure a run cadence (daily, every other day, weekly, or off), a preferred time, and optionally enable Daemon Mode from the Settings page.

**Consequences (testable):**
- Without Daemon Mode: Runs trigger at the configured time only if the app is open; any missed Runs are retried automatically on next app open
- With Daemon Mode enabled: the background service runs the schedule regardless of whether the browser UI is open
- The UI clearly indicates whether Daemon Mode is on, when the next scheduled Run will occur, and whether any missed Runs are pending retry
- Daemon Mode can be toggled independently of cadence and time settings

---

---

### 4.8 On-Demand Ingest — YouTube and Article Modes

**Description:** In addition to the scheduled Gmail ingest, users can feed individual pieces of content into the pipeline on demand. Two modes are supported: YouTube videos (transcript extraction) and web articles (body extraction). Both modes skip the Gmail ingest stage entirely and inject content directly into the extract stage, producing a briefing from whatever the user provides. The same public radio narrative style and TTS delivery apply as in the newsletter briefing. Realizes a new user journey: *UJ-4. Jason drops a YouTube link and gets a listenble NPR-style segment about it.*

**Functional Requirements:**

#### FR-26: YouTube Transcript Ingest
User can paste one or more YouTube URLs into the app and trigger a pipeline run using the video transcript(s) as source material.

**Consequences (testable):**
- The system extracts the transcript from each YouTube URL using the YouTube transcript API (no browser or scraping required)
- If a video has no available transcript (auto-generated or manual), the URL is skipped with a warning and processing continues with remaining URLs
- Transcripts are treated as extracted text and injected at the embed stage, bypassing Gmail ingest and HTML extraction
- All downstream stages (cluster, select, frame, draft, tts_prep, assemble, qa_gate) run identically to a newsletter run
- A YouTube run is recorded in history alongside newsletter runs with a distinct "YouTube" source label

#### FR-27: Article URL Ingest
User can paste one or more article URLs and trigger a pipeline run using the article body text as source material.

**Consequences (testable):**
- The system extracts the article body using `trafilatura` as the primary extractor
- If `trafilatura` returns fewer than 200 words, the system falls back to Jinja Reader (`r.jina.ai/{url}`) as a secondary extractor
- If both extractors fail or return insufficient content, the URL is skipped with a warning
- Extracted article text is injected at the embed stage, bypassing Gmail ingest and HTML extraction
- An article run is recorded in history with a distinct "Article" source label

#### FR-28: On-Demand Ingest UI
The dashboard includes a secondary input area for on-demand ingest alongside the newsletter "Run Briefing" button.

**Consequences (testable):**
- User can paste one or more URLs (YouTube or article, mixed is supported) into a text area
- Selecting the ingest mode (YouTube / Article / Auto-detect) is optional — the system auto-detects YouTube URLs by domain
- Submitting triggers a run via `POST /api/briefings/on-demand` with the provided URLs and detected mode
- The same live SSE pipeline log displays progress for on-demand runs
- On-demand runs appear in history identically to newsletter runs with source label indicating type

---

## 5. Non-Goals (Explicit)

- **No multi-user support** — one Gmail account, one local instance
- **No hosted / cloud version** — self-hosted only in V1
- **No non-Gmail sources** — RSS, Substack API, other inboxes are out of scope for V1 *[NOTE: YouTube and article on-demand modes added in V1.1 as FR-26/27/28]*
- **No email delivery of the Briefing** — output is local files only
- **No mobile app** — browser UI on desktop only

---

## 6. MVP Scope

### 6.1 In Scope

- Gmail OAuth (read-only), label-based ingest, local Processed Log (no Gmail mutations)
- Modular pipeline: extract → embed → cluster → editorial selection → story framing → script drafting → TTS preparation → assembly → QA gate
- Embedding-based clustering (no LLM for clustering stage)
- Briefing Depth setting: Brief / Standard / Deep (global per run, default Standard)
- Local TTS audio generation via Kokoro (auto-downloaded during onboarding, single voice, NPR style)
- Ollama local default + BYOK for OpenAI, Anthropic, Gemini
- Encrypted local storage for API keys
- QA gate with structured 3-tier retry and Hold state with manual remediation
- First-run onboarding wizard (OAuth required, all else skippable; revisitable in Settings)
- Local web UI: trigger button, live pipeline log, briefing history, download (markdown + audio), settings
- User-configurable topic Sections
- Schedule configuration (daily / every other day / weekly / off) with optional Daemon Mode
- Missed run retry on next app open
- Clean README with Google Cloud OAuth setup guide, example config

### 6.2 Out of Scope for MVP

- Orpheus TTS (GPU upgrade path) — deferred to V2
- Additional voice styles beyond NPR default — deferred to V2
- Web UI beyond localhost (auth, HTTPS, multi-user) — deferred to V3+
- Non-Gmail sources (RSS, Substack) — deferred to V2+
- Python packaging / installer to hide terminal setup — deferred to V2+ `[NOTE FOR PM: real friction point for broader distribution]`

### 6.3 V1.1 Additions (On-Demand Ingest)

- **FR-26:** YouTube transcript ingest — paste YouTube URLs, get a briefing from the transcript
- **FR-27:** Article URL ingest — paste article URLs, body extracted via trafilatura + Jinja Reader fallback
- **FR-28:** On-demand ingest UI — URL text area on dashboard, auto-detects YouTube vs. article, runs same pipeline

---

## 7. Success Metrics

**Primary**
- **SM-1:** Author uses Briefing as primary newsletter consumption method within 2 weeks of first run. Validates FR-14, FR-16, FR-8.
- **SM-2:** A new technical user completes setup and generates their first Briefing in under 15 minutes. Validates FR-1, FR-12, UJ-3.

**Secondary**
- **SM-3:** GitHub stars / forks within 60 days of public release — proxy for builder adoption.
- **SM-4:** Stories from the same event are collapsed to a single entry (no duplicate Stories for the same news event in the same Briefing). Validates FR-5, FR-7.
- **SM-5:** Audio file is listenable during a commute without needing to re-listen for context. Validates FR-10.

**Counter-metrics (do not optimize)**
- **SM-C1:** Briefing length — do not optimize for longer Briefings. A 5-story briefing that's accurate is better than a 20-story briefing with noise. Counterbalances SM-4.
- **SM-C2:** Setup complexity — do not add features that extend setup time past 15 minutes. Counterbalances SM-3.

---

## 8. Open Questions

1. What embedding model runs locally for clustering? Needs validation against quality and speed on average hardware. (Architecture decision.)
2. Default Ollama model for synthesis — llama3, mistral, or other? Depends on synthesis quality testing.
3. What encryption library/approach for local API key storage? (Architecture decision — keyring, Fernet, etc.)
4. Should Briefing Depth be overridable per-run at trigger time (e.g. a dropdown on the Run button), or only changeable in Settings? V1 assumption is Settings-only.

---

## 9. Assumptions Index

- **§4.2 FR-5** — Clustering uses a local embedding model (not the synthesis LLM Provider); specific model decided in architecture.
- **§4.2 FR-8** — Story relevance ordering = number of source Newsletters that covered it (most-covered first).
- **§4.6 FR-16** — OAuth is the only required onboarding step; all others are skippable and revisitable in Settings.
- **§4.7 FR-23** — Briefing Depth is a global run setting in V1; per-story depth override is deferred to V2.
- **§4.7 FR-25** — Without Daemon Mode, missed scheduled Runs are retried on next app open, picking up all unprocessed emails since the last successful Run.
- **Modular pipeline research doc** (`modular-news-production-report.md`) — adopted as the production pipeline foundation; handoff packet schema and module boundaries to be defined in architecture.
