---
stepsCompleted: [1, 2, 3, 4]
status: 'complete'
completedAt: '2026-06-26'
inputDocuments:
  - '_bmad-output/planning-artifacts/prds/prd-briefing-2026-06-26/prd.md'
  - '_bmad-output/planning-artifacts/architecture.md'
---

# Briefing - Epic Breakdown

## Overview

Complete epic and story breakdown for Briefing, decomposing requirements from the PRD and Architecture into implementable stories organized by user value.

---

## Requirements Inventory

### Functional Requirements

FR-1: User can authorize Gmail access via browser-based OAuth 2.0 during initial setup; token stored locally.
FR-2: System fetches emails from the user-configured Label that do not appear in the Processed Log on each Run.
FR-3: After a successful Run, system appends processed email IDs to the Processed Log; user can clear it from Settings.
FR-4: System extracts plain text, title, sender name, and date from each Newsletter's HTML body.
FR-5: System generates embeddings for extracted chunks and groups them into Clusters using similarity thresholds.
FR-6: Each Cluster is assigned to a user-configured Section; unmatched Clusters go to a catch-all "Other" Section.
FR-7: System assigns each Cluster a depth tier, lead angle, local stakes note, and guardrails before drafting.
FR-7a: System generates one Story per Cluster as natural editorial prose (broadcast-style) at the assigned depth tier.
FR-8: System assembles all Stories into a single dated Briefing document organized by Section with header metadata.
FR-9: System rewrites the assembled Briefing prose into a TTS-optimized narration script (spoken segues, pacing cues, pronunciation guide).
FR-10: System passes the TTS-optimized script to the TTS Engine and produces a dated Audio File alongside the markdown Briefing.
FR-11: User can select and configure the TTS Engine (Kokoro default, Orpheus if available) from Settings.
FR-12: After assembly and TTS preparation, system validates the Briefing package before marking the Run complete.
FR-13: When QA gate fails, pipeline attempts staged remediation (3 tiers) before escalating to Hold state.
FR-14: System uses a locally running Ollama instance as the default LLM Provider with a configurable model name.
FR-15: User can configure an API key for OpenAI, Anthropic, or Gemini as an alternative Provider.
FR-16: On first launch, app presents a step-by-step setup wizard (OAuth required; Kokoro download; optional BYOK/sections/schedule).
FR-17: User can return to any onboarding configuration from the Settings page at any time.
FR-18: User can trigger a Run manually by clicking a button in the UI.
FR-19: While a Run is active, UI displays a real-time log of pipeline stages and status messages.
FR-20: UI displays a list of all past Briefings with date, story count, section breakdown, and download links.
FR-21: User can configure the Gmail Label and re-authorize OAuth from Settings.
FR-22: User can add, remove, rename, and reorder Sections from Settings.
FR-23: User can select a default Briefing Depth (Brief, Standard, Deep) from Settings.
FR-24: User can select their LLM Provider, enter a model name or API key, and test the connection from Settings.
FR-25: User can configure a run cadence, preferred time, and optionally enable Daemon Mode.

### Non-Functional Requirements

NFR-1: Async-first -- the web server must never block on pipeline execution; pipeline runs as a background task.
NFR-2: Streaming -- live log requires SSE from worker to browser in real time.
NFR-3: Local-first security -- OAuth token and API keys encrypted at rest; never transmitted beyond the configured provider's API.
NFR-4: Partial rerun support -- handoff packet artifacts persisted to disk so failed stages can restart without replaying the full run.
NFR-5: Daemon mode -- scheduler must fire pipeline runs independently of the web server process.
NFR-6: Self-contained install -- dependencies (including Kokoro model weights) auto-downloaded during setup.
NFR-7: Setup time -- a new technical user completes setup and generates their first Briefing in under 15 minutes.
NFR-8: Entry point isolation -- pipeline/, services/, core/, db/ never import from main.py or mcp_server.py.

### Additional Requirements

- Architecture specifies project scaffolding as the first implementation story; the full directory tree must be created before any feature work begins.
- MCP Server (stdio) exposes 4 tools: trigger_briefing, get_run_status, list_briefings, get_briefing_content -- standalone entry point (mcp_server.py) with no FastAPI dependency.
- MCP Sampling is a 5th LLM provider option in llm.py; falls back to Ollama if no MCP host sampling context is available.
- SSE live log queue: dict[int, asyncio.Queue] module-level singleton in api/stream.py, keyed by run_id.
- HandoffPacket field definitions are populated in Story 4.1 via handoff-schema.yaml.
- Structured JSON logging: handlers registered in entry points only; logger = logging.getLogger(__name__) in all modules.
- pytest + httpx AsyncClient for API tests; mock HandoffPacket fixtures for pipeline unit tests.
- Missed run retry: on next app open, app detects missed scheduled runs and retries before showing the history list.

### UX Design Requirements

No UX design document provided. UI follows Pico.css classless defaults with dark mode (data-theme="dark") and HTMX for dynamic behavior as specified in Architecture.

---

### FR Coverage Map

FR-1: Epic 2 -- Gmail OAuth authorization
FR-2: Epic 2 -- Label-based email fetch service
FR-3: Epic 2 -- Processed Log management
FR-4: Epic 4 -- Extract stage (HTML-to-text)
FR-5: Epic 4 -- Embed + Cluster stages
FR-6: Epic 4 -- Select stage (section classification)
FR-7: Epic 5 -- Frame stage (depth tier assignment)
FR-7a: Epic 5 -- Draft stage (story synthesis)
FR-8: Epic 5 -- Assemble stage (briefing assembly)
FR-9: Epic 6 -- TTS Prep stage
FR-10: Epic 6 -- Kokoro synthesis + audio file output
FR-11: Epic 6 -- TTS Engine configuration in Settings
FR-12: Epic 7 -- QA Gate stage
FR-13: Epic 7 -- 3-tier retry + Hold state
FR-14: Epic 3 -- Ollama provider
FR-15: Epic 3 -- BYOK provider (OpenAI/Anthropic/Gemini)
FR-16: Epic 10 -- First-run onboarding wizard
FR-17: Epic 10 -- Onboarding revisit in Settings
FR-18: Epic 8 -- Run trigger button
FR-19: Epic 8 -- Live pipeline progress log (SSE)
FR-20: Epic 8 -- Briefing history list + downloads
FR-21: Epic 8 -- Settings: Gmail
FR-22: Epic 8 -- Settings: Topic Sections
FR-23: Epic 8 -- Settings: Briefing Depth
FR-24: Epic 8 -- Settings: LLM Provider
FR-25: Epic 8 + Epic 9 -- Schedule UI (Epic 8), schedule execution + daemon (Epic 9)
FR-26: Epic 13 -- YouTube transcript ingest service
FR-27: Epic 13 -- Article body extraction service (trafilatura + Jina Reader fallback)
FR-28: Epic 13 -- On-demand ingest UI and API endpoint

---

## Epic List

### Epic 1: Project Foundation -- App Skeleton and Core Infrastructure
Developers can run the app skeleton with database, configuration, credential storage, and error types in place -- everything needed to build features on top.
**FRs covered:** NFR-1, NFR-3, NFR-4, NFR-8 (foundational)

### Epic 2: Gmail Integration -- Connect and Ingest
Users can authorize Gmail and pull unread newsletter emails into the system ready for processing.
**FRs covered:** FR-1, FR-2, FR-3

### Epic 3: LLM Provider Layer -- Local and Cloud AI
The pipeline can make LLM calls through a single abstraction routing to Ollama, BYOK providers, or MCP sampling.
**FRs covered:** FR-14, FR-15, MCP sampling (architecture addition)

### Epic 4: Pipeline -- Content Processing
Raw emails flow through ingest, extract, embed, cluster, and select stages -- producing classified story candidates ready for synthesis.
**FRs covered:** FR-4, FR-5, FR-6

### Epic 5: Pipeline -- Editorial Synthesis
Story clusters are transformed into polished editorial prose and assembled into a complete dated briefing document.
**FRs covered:** FR-7, FR-7a, FR-8

### Epic 6: Audio Production -- Listen to Your Briefing
Users get a listenable audio narration of their briefing alongside the markdown file.
**FRs covered:** FR-9, FR-10, FR-11

### Epic 7: Pipeline Orchestration and QA
All pipeline stages run in sequence with live SSE progress, disk artifact persistence, automatic retry, and a Hold state for unrecoverable errors.
**FRs covered:** FR-12, FR-13, NFR-1, NFR-2, NFR-4

### Epic 8: Web UI -- Dashboard, History and Settings
Users can trigger runs, watch live progress, browse history, download briefings, and manage all settings through a browser UI.
**FRs covered:** FR-18, FR-19, FR-20, FR-21, FR-22, FR-23, FR-24, FR-25 (UI side)

### Epic 9: Scheduling and Daemon Mode
Users can set a schedule and have briefings generated automatically, even when the browser window is closed.
**FRs covered:** FR-25 (execution side), NFR-5

### Epic 10: First-Run Onboarding
A new user can go from clone to first briefing in under 15 minutes with a guided setup wizard.
**FRs covered:** FR-16, FR-17, NFR-6, NFR-7

### Epic 11: MCP Server -- Headless AI Integration
Claude Desktop and AI agents like Hermes can trigger and retrieve briefings as MCP tool calls without the web UI.
**FRs covered:** MCP architecture additions

### Epic 12: Testing and Documentation
The codebase has a complete test suite and a README enabling a new builder to set up in under 15 minutes.
**FRs covered:** SM-2, NFR-7

### Epic 13: On-Demand Ingest — YouTube and Article Modes
Users can paste YouTube URLs or article URLs and get a public radio-style audio briefing from that content, using the same pipeline and TTS delivery as the newsletter briefing.
**FRs covered:** FR-26, FR-27, FR-28

---

## Epic 1: Project Foundation -- App Skeleton and Core Infrastructure

After this epic, the app skeleton runs, the database initializes on startup, configuration loads from env, credentials are readable/writable via the OS keychain, and StageError is available to all modules. This is the foundation every other epic builds on.

### Story 1.1: Scaffold Project Structure and Initialize uv Project

As a developer,
I want the complete project directory structure scaffolded with all required files and uv dependencies installed,
So that I can begin implementing features immediately without spending time on project setup decisions.

**Acceptance Criteria:**

**Given** a machine with Python 3.11+ and uv installed
**When** I run the initialization command from the architecture doc
**Then** the briefing/ root directory exists with pyproject.toml, .env.example, .gitignore, setup.py, briefing.sh, briefing.bat

**Given** the scaffolded project
**When** I inspect the directory tree
**Then** all directories exist: app/core/, app/api/, app/pipeline/stages/, app/services/, app/db/, app/templates/, pipeline_prompts/stages/, data/briefings/, data/artifacts/, tests/api/, tests/pipeline/stages/, tests/services/, tests/mcp/

**Given** the scaffolded project
**When** I run `uv run python -c "import fastapi, sqlalchemy, mcp"`
**Then** all packages import without error

**Given** the .env.example file
**When** I read it
**Then** it contains template entries for BRIEFING_DATA_DIR and LOG_LEVEL with example values

**Given** the .gitignore file
**When** I read it
**Then** it excludes: data/, *.db, *.log, __pycache__/, .env, *.pyc, .venv/

**Given** the pipeline_prompts/ directory
**When** I inspect it
**Then** handoff-schema.yaml exists as an empty placeholder and stages/ contains select.md, frame.md, draft.md, tts_prep.md as empty placeholders

### Story 1.2: Core Configuration Module

As a developer,
I want AppConfig to load all application settings from environment variables and provide a validated llm_provider enum,
So that all modules can access typed configuration without reading env vars directly.

**Acceptance Criteria:**

**Given** a .env file with BRIEFING_DATA_DIR set
**When** AppConfig is instantiated
**Then** config.data_dir resolves to the configured path and defaults apply for all unset variables

**Given** AppConfig instantiated with defaults
**When** I read config.llm_provider
**Then** it defaults to "ollama" and accepts values: ollama, openai, anthropic, gemini, mcp_sampling

**Given** AppConfig with an invalid llm_provider value
**When** I instantiate AppConfig
**Then** a clear ValidationError is raised naming the invalid value and listing valid options

**Given** AppConfig
**When** I read config.log_level
**Then** it defaults to "INFO" and accepts DEBUG, INFO, WARNING, ERROR

**Given** AppConfig
**When** I read config.briefing_depth
**Then** it defaults to "standard" and accepts "brief", "standard", "deep"

**Given** a pipeline stage receiving config as a parameter
**When** I inspect the stage file
**Then** no direct os.environ or os.getenv calls appear -- all settings are read from config

### Story 1.3: Database Models and Async SQLite Initialization

As a developer,
I want SQLAlchemy async models for Run, BriefingOutput, and ProcessedEmail created and the database initialized on app startup,
So that all features that read or write persistent data have a ready-to-use schema.

**Acceptance Criteria:**

**Given** the app starting for the first time
**When** the FastAPI lifespan event fires
**Then** data/briefing.db is created and all three tables exist: runs, briefing_outputs, processed_emails

**Given** the runs table
**When** I inspect its schema
**Then** columns exist: id (int PK autoincrement), status (str, default "pending"), created_at (datetime), depth (str), section_config (JSON), error (str nullable)

**Given** the briefing_outputs table
**When** I inspect its schema
**Then** columns exist: id (int PK), run_id (int FK runs.id), markdown_path (str), audio_path (str nullable)

**Given** the processed_emails table
**When** I inspect its schema
**Then** columns exist: id (int PK), email_id (str unique), run_id (int FK runs.id), processed_at (datetime)

**Given** the database module
**When** I call get_session()
**Then** it returns an async SQLAlchemy session compatible with async with context management

**Given** the app restarting when briefing.db already exists
**When** the lifespan event fires
**Then** no error is raised and existing data is preserved (create_all is idempotent)

### Story 1.4: Credential Store -- Keyring Wrapper

As a developer,
I want a centralized credential module that reads and writes secrets to the OS keychain under the "briefing" service namespace,
So that no other module needs to know about keyring directly and credentials are never stored in plaintext.

**Acceptance Criteria:**

**Given** the credentials module
**When** I call credentials.set("gmail_oauth_token", token_json)
**Then** the token is stored in the OS keychain under service="briefing", username="gmail_oauth_token"

**Given** a stored credential
**When** I call credentials.get("gmail_oauth_token")
**Then** the stored value is returned as a string

**Given** a key that has not been set
**When** I call credentials.get("openai_key")
**Then** None is returned (not an exception)

**Given** the credentials module
**When** I call credentials.delete("anthropic_key")
**Then** the keychain entry is removed; subsequent get() returns None

**Given** all valid credential key names
**When** I inspect the module
**Then** constants gmail_oauth_token, openai_key, anthropic_key, gemini_key are defined at module level -- no other module hardcodes these strings

**Given** any credential operation
**When** it runs on Windows, macOS, or Linux
**Then** the native OS keychain is used (Windows Credential Manager / macOS Keychain / libsecret) without additional configuration

### Story 1.5: Error Types -- StageError and Error Code Constants

As a developer,
I want a StageError exception class and error code constants defined in app/core/errors.py,
So that all pipeline stages raise consistent structured errors that orchestrators and API handlers can interpret.

**Acceptance Criteria:**

**Given** a pipeline stage encountering a failure
**When** it raises StageError("embed", "FAISS index failed", retryable=True)
**Then** the exception carries stage_name="embed", message="FAISS index failed", retryable=True

**Given** a StageError instance
**When** I access its attributes
**Then** stage_name (str), message (str), and retryable (bool) are all accessible

**Given** app/core/errors.py
**When** I inspect it
**Then** error code constants are defined: STAGE_FAILED, AUTH_ERROR, PROVIDER_UNAVAILABLE, VALIDATION_ERROR, NOT_FOUND

**Given** a stage catching a raw exception
**When** it re-raises
**Then** it always wraps in StageError -- no raw Exception or RuntimeError propagates from stage code

**Given** the errors module
**When** imported by stages, orchestrator, and API handlers
**Then** no circular imports occur -- errors.py imports only from Python stdlib

---

## Epic 2: Gmail Integration -- Connect and Ingest

After this epic, users can authorize Gmail access, and the system can fetch unread newsletter emails from a configured label while tracking which emails have already been processed.

### Story 2.1: Gmail OAuth Authorization

As a user setting up Briefing for the first time,
I want to authorize Gmail access through a browser OAuth flow,
So that the app can read my newsletter emails without me managing credentials manually.

**Acceptance Criteria:**

**Given** a user running setup.py for the first time
**When** they reach the Gmail authorization step
**Then** their default browser opens to the Google OAuth consent screen with read-only Gmail scope

**Given** a successful OAuth authorization
**When** the browser redirects back to the local callback
**Then** the resulting token JSON is stored via credentials.set("gmail_oauth_token", ...) -- not on the filesystem in plaintext

**Given** a stored OAuth token
**When** the Gmail service makes an API call
**Then** google-auth automatically refreshes the token if expired, without prompting the user again

**Given** a revoked or invalid token
**When** the Gmail service attempts an API call
**Then** a StageError with code=AUTH_ERROR and retryable=False is raised with a clear message instructing the user to re-authorize from Settings

**Given** the OAuth scope requested
**When** I inspect the credentials.json and token
**Then** only the Gmail read-only scope is requested -- no write, send, or modify permissions

### Story 2.2: Label-Based Email Fetch Service

As a user triggering a Run,
I want the system to fetch only newsletter emails from my configured Gmail label that have not been processed before,
So that each Run only processes new content.

**Acceptance Criteria:**

**Given** a configured Gmail label (e.g. "Newsletters") and a valid OAuth token
**When** the ingest service runs
**Then** only emails under that exact label are fetched

**Given** a Processed Log containing previously processed email IDs
**When** the ingest service fetches emails
**Then** emails whose IDs appear in the Processed Log are excluded from the fetched results

**Given** zero unprocessed emails exist under the label
**When** the ingest service runs
**Then** it returns an empty list and signals the orchestrator to halt the Run early with a "No new newsletters" status

**Given** a successful fetch
**When** I inspect the returned email objects
**Then** each contains: email_id (str), subject (str), sender_name (str), sender_email (str), date (datetime), raw_html (str)

**Given** the Gmail API call
**When** it fails due to a network error or quota limit
**Then** a StageError with retryable=True is raised -- the Run does not crash silently

### Story 2.3: Processed Log Management

As a user,
I want the system to record which emails were processed after each successful Run and to be able to clear that log from Settings,
So that I am never shown the same newsletter content twice unless I choose to reprocess.

**Acceptance Criteria:**

**Given** a fully successful Run completing the QA gate
**When** the orchestrator finalizes the Run
**Then** all email IDs from that Run are written to the processed_emails table atomically in the same DB transaction as Run.status = "complete"

**Given** a Run that fails mid-pipeline
**When** I query the processed_emails table
**Then** no email IDs from the failed Run are present -- the table is unchanged

**Given** the processed_emails table
**When** the ingest service queries for unprocessed emails
**Then** it issues a single query comparing fetched email IDs against the table

**Given** a user clicking "Clear Processed Log" in Settings
**When** the action completes
**Then** all rows are deleted from the processed_emails table; the next Run fetches all emails under the label regardless of previous runs

**Given** the clear log action
**When** it executes
**Then** no changes are made to Gmail -- only the local processed_emails table is affected

---

## Epic 3: LLM Provider Layer -- Local and Cloud AI

After this epic, pipeline stages can make LLM calls through a single service abstraction that routes to Ollama, any BYOK provider, or the MCP host -- without the stage knowing which provider is active.

### Story 3.1: Ollama Provider Integration

As a developer building pipeline stages,
I want a llm.py service that routes LLM calls to a local Ollama instance by default,
So that the pipeline works out of the box without any API keys.

**Acceptance Criteria:**

**Given** Ollama running locally with a model loaded
**When** I call llm.complete(prompt, config) with config.llm_provider = "ollama"
**Then** the request is sent to the Ollama HTTP API and the response text is returned as a plain string

**Given** config.llm_provider = "ollama" and Ollama not reachable
**When** I call llm.complete(prompt, config)
**Then** a StageError with code=PROVIDER_UNAVAILABLE and retryable=True is raised

**Given** AppConfig.ollama_model_name
**When** the provider makes the API call
**Then** the configured model name is used in the request body -- not a hardcoded default

**Given** any LLM call in a pipeline stage
**When** I search the stage file
**Then** no direct import of ollama or httpx targeting Ollama appears -- all calls go through llm.complete()

### Story 3.2: BYOK Provider Integration -- OpenAI, Anthropic, Gemini

As a user who prefers cloud LLM quality,
I want to configure an API key for OpenAI, Anthropic, or Gemini and have all pipeline LLM calls use that provider,
So that I can get better synthesis quality by using a cloud model.

**Acceptance Criteria:**

**Given** config.llm_provider = "openai" and a valid openai_key in the credential store
**When** I call llm.complete(prompt, config)
**Then** the request is sent to the OpenAI Chat Completions API and the response text is returned

**Given** config.llm_provider = "anthropic" and a valid anthropic_key
**When** I call llm.complete(prompt, config)
**Then** the request uses the Anthropic Messages API via the anthropic SDK

**Given** config.llm_provider = "gemini" and a valid gemini_key
**When** I call llm.complete(prompt, config)
**Then** the request uses the Google Generative AI SDK

**Given** any BYOK provider call
**When** I inspect network traffic
**Then** the API key is sent only to the configured provider's domain -- it is never logged or stored in plaintext

**Given** a BYOK provider with an invalid or expired API key
**When** I call llm.complete(prompt, config)
**Then** a StageError with code=AUTH_ERROR and retryable=False is raised

**Given** switching config.llm_provider from "ollama" to "openai" at runtime
**When** the next pipeline Run starts
**Then** all LLM calls in that Run use the new provider -- no app restart required

### Story 3.3: MCP Sampling Provider and Fallback

As a user running Briefing via Claude Desktop or Hermes,
I want pipeline LLM calls to route through the host model's sampling capability,
So that I can use Claude quality without paying separate API token costs.

**Acceptance Criteria:**

**Given** config.llm_provider = "mcp_sampling" and an active MCP session with a host that supports sampling
**When** I call llm.complete(prompt, config)
**Then** the request is made via server.create_message() to the MCP host and the response text is returned

**Given** config.llm_provider = "mcp_sampling" but no active MCP sampling context is available
**When** I call llm.complete(prompt, config)
**Then** the call falls back to the Ollama provider and a WARNING log line is emitted noting the fallback

**Given** a pipeline stage making an LLM call
**When** config.llm_provider = "mcp_sampling"
**Then** the stage code is unchanged -- it still calls llm.complete(prompt, config) with no awareness of the provider

---

## Epic 4: Pipeline -- Content Processing

After this epic, raw emails flow through the ingest, extract, embed, cluster, and select stages -- producing classified story candidates ready for editorial synthesis.

### Story 4.1: HandoffPacket Schema and Disk I/O

As a developer building pipeline stages,
I want a HandoffPacket dataclass with typed fields and helpers to read/write packets to disk,
So that all stages share a consistent data contract and partial reruns are possible without replaying previous stages.

**Acceptance Criteria:**

**Given** a pipeline stage completing its work
**When** it returns a HandoffPacket
**Then** the packet can be serialized to JSON and written to data/artifacts/{run_id}/stage_{N:02d}_{stage_name}.json

**Given** a serialized packet on disk
**When** the orchestrator reads it for a partial rerun
**Then** a HandoffPacket with all original fields is reconstructed without data loss

**Given** the HandoffPacket class
**When** I inspect it
**Then** it contains fields for: run_id (int), emails (list), extracted_texts (list), embeddings (list), clusters (list), selected_clusters (list), framed_stories (list), drafted_stories (list), assembled_markdown (str), tts_script (str), pronunciation_guide (dict), qa_passed (bool), errors (list)

**Given** handoff-schema.yaml
**When** I read it
**Then** every HandoffPacket field is documented with its type, which stage populates it, and which stages consume it

**Given** a stage that only needs emails and extracted_texts
**When** it receives the HandoffPacket
**Then** it reads only those fields -- it does not inspect embeddings, clusters, or downstream fields

**Given** the handoff.py module
**When** imported by a stage
**Then** no imports from api/, main.py, or mcp_server.py appear

### Story 4.2: Ingest Stage -- Gmail Emails to HandoffPacket

As a developer running the pipeline,
I want the ingest stage to fetch unprocessed emails and place them in the HandoffPacket,
So that all subsequent stages have the raw email data they need.

**Acceptance Criteria:**

**Given** a valid Gmail OAuth token and a configured label with unprocessed emails
**When** the ingest stage runs
**Then** it returns a HandoffPacket with the emails field populated with all unprocessed emails from the label

**Given** zero unprocessed emails in the label
**When** the ingest stage runs
**Then** it returns a HandoffPacket with emails = [] and sets a flag that causes the orchestrator to halt the Run with status "no_new_emails"

**Given** a Gmail API failure during ingest
**When** the stage encounters the error
**Then** it raises StageError("ingest", message, retryable=True) -- the HandoffPacket is not written to disk for this stage

**Given** the ingest stage completing successfully
**When** the orchestrator processes the result
**Then** the HandoffPacket is written to data/artifacts/{run_id}/stage_01_ingest.json before the next stage begins

**Given** the ingest stage function signature
**When** I inspect it
**Then** it matches: async def run(packet: HandoffPacket, config: AppConfig) -> HandoffPacket

### Story 4.3: Extract Stage -- HTML to Text

As a developer,
I want the extract stage to convert raw newsletter HTML into clean structured text chunks with metadata,
So that downstream embedding and synthesis stages work with readable normalized content.

**Acceptance Criteria:**

**Given** a HandoffPacket with raw HTML emails
**When** the extract stage runs
**Then** it returns the packet with extracted_texts populated -- one entry per email

**Given** a newsletter email with HTML body
**When** extraction runs
**Then** the output contains clean readable text with no HTML tags, tracking pixels, navigation chrome, or footer unsubscribe blocks

**Given** each extracted text entry
**When** I inspect it
**Then** it contains: email_id (str), text (str), title (str), sender_name (str), date (datetime)

**Given** an email with a malformed or empty HTML body
**When** extraction runs on that email
**Then** the email is skipped with a WARNING log entry -- it does not cause a StageError for the whole stage

**Given** the extract stage
**When** I inspect it
**Then** it imports no LLM services -- extraction is pure Python text processing

**Given** the stage completing successfully
**When** the orchestrator processes the result
**Then** the HandoffPacket is written to data/artifacts/{run_id}/stage_02_extract.json

### Story 4.4: Embeddings Service -- sentence-transformers and FAISS

As a developer,
I want an embeddings service that generates vector embeddings for text chunks and supports FAISS similarity search,
So that the cluster stage can group newsletter excerpts about the same story without LLM calls.

**Acceptance Criteria:**

**Given** a list of text strings
**When** I call embeddings.encode(texts)
**Then** a list of float vectors is returned, one per input text, using the configured sentence-transformers model

**Given** the embedding service initializing for the first time
**When** the model is not cached locally
**Then** it downloads automatically and caches to the local HuggingFace cache directory

**Given** a list of vectors
**When** I call embeddings.build_index(vectors)
**Then** a FAISS flat index is created and returned

**Given** a FAISS index and a query vector
**When** I call embeddings.search(index, query_vector, k=5)
**Then** the k nearest neighbor indices and distances are returned

**Given** the embeddings service
**When** I inspect its imports
**Then** it imports sentence_transformers and faiss -- it does not call llm.complete() or any LLM provider

### Story 4.5: Embed and Cluster Stages

As a developer,
I want the embed stage to generate embeddings for extracted texts and the cluster stage to group similar excerpts into story clusters,
So that newsletters covering the same event are collapsed into a single story candidate.

**Acceptance Criteria:**

**Given** a HandoffPacket with extracted_texts
**When** the embed stage runs
**Then** it returns the packet with embeddings populated -- one vector per extracted text entry in the same order

**Given** a HandoffPacket with embeddings
**When** the cluster stage runs
**Then** it returns the packet with clusters populated -- each cluster is a list of extracted_text entries grouped by similarity

**Given** two extracted texts covering the same news event (high cosine similarity)
**When** the cluster stage runs
**Then** they appear in the same cluster regardless of which newsletter they came from

**Given** two extracted texts covering distinct events
**When** the cluster stage runs
**Then** they appear in different clusters

**Given** AppConfig
**When** I inspect it
**Then** a similarity_threshold setting exists (default 0.75) that controls cluster granularity

**Given** the embed and cluster stages each completing
**When** the orchestrator processes them
**Then** HandoffPackets are written to disk: stage_03_embed.json and stage_04_cluster.json

### Story 4.6: Select Stage -- Section Classification

As a developer,
I want the select stage to assign each cluster to a user-configured section using the LLM provider,
So that stories are organized by topic before synthesis.

**Acceptance Criteria:**

**Given** a HandoffPacket with clusters and config with sections = ["AI", "Technology", "Finance"]
**When** the select stage runs
**Then** it returns the packet with selected_clusters populated -- each cluster has an assigned section_name

**Given** a cluster that does not match any configured section
**When** the select stage classifies it
**Then** it is assigned to the "Other" catch-all section -- it is never dropped

**Given** each cluster
**When** classification runs
**Then** exactly one section is assigned -- no cluster receives multiple sections

**Given** the select stage
**When** it makes its classification decision
**Then** it calls llm.complete() with a prompt loaded from pipeline_prompts/stages/select.md -- the prompt is not hardcoded in the stage file

**Given** an LLM classification call that fails
**When** the stage encounters the error
**Then** it raises StageError("select", message, retryable=True)

**Given** the stage completing
**When** the orchestrator processes it
**Then** the HandoffPacket is written to data/artifacts/{run_id}/stage_05_select.json

---

## Epic 5: Pipeline -- Editorial Synthesis

After this epic, story clusters are transformed into framed, drafted stories and assembled into a complete dated briefing markdown document.

### Story 5.1: Frame Stage -- Depth Tier Assignment

As a developer,
I want the frame stage to assign each cluster a depth tier, lead angle, and guardrails before synthesis,
So that story drafts vary in length and focus based on the global depth setting and source strength.

**Acceptance Criteria:**

**Given** a HandoffPacket with selected_clusters and config.briefing_depth = "standard"
**When** the frame stage runs
**Then** each cluster in the result has: depth_tier (str: "brief"|"standard"|"deep"), lead_angle (str), local_stakes (str), guardrails (list[str])

**Given** config.briefing_depth = "brief"
**When** the frame stage runs
**Then** all clusters receive depth_tier = "brief" as the baseline; source-strength may upgrade clusters with many sources

**Given** a cluster with uncertain or unverified claims
**When** the frame stage analyzes it
**Then** the guardrails field contains explicit hedging instructions carried into the draft stage

**Given** the frame stage
**When** it makes its framing decisions
**Then** it calls llm.complete() with a prompt from pipeline_prompts/stages/frame.md

**Given** the stage completing
**When** the orchestrator processes it
**Then** the HandoffPacket is written to data/artifacts/{run_id}/stage_06_frame.json

### Story 5.2: Draft Stage -- Story Synthesis

As a developer,
I want the draft stage to generate one editorial story per cluster as broadcast-style prose at the assigned depth tier,
So that the briefing reads as if written by a single editor who synthesized multiple sources.

**Acceptance Criteria:**

**Given** a cluster with depth_tier = "brief"
**When** the draft stage synthesizes it
**Then** the resulting story is 2-3 sentences: headline plus essential context

**Given** a cluster with depth_tier = "standard"
**When** the draft stage synthesizes it
**Then** the resulting story is a short narrative paragraph covering what happened, why it matters, and local stakes

**Given** a cluster with depth_tier = "deep"
**When** the draft stage synthesizes it
**Then** the resulting story is a full mini-segment with nuance, conflicting angles if present, and background context

**Given** any drafted story
**When** I read it
**Then** it reads as natural spoken prose -- no bullet points, no markdown headers within the story, no raw URLs

**Given** any drafted story
**When** I inspect it
**Then** source attribution is present -- the names of newsletters that contributed are listed

**Given** any drafted story with guardrails from the frame stage
**When** I read it
**Then** hedging language is present for uncertain claims -- no guardrail is silently dropped

**Given** the draft stage
**When** it synthesizes each story
**Then** it calls llm.complete() with a prompt from pipeline_prompts/stages/draft.md, passing only the cluster's framing fields -- not the full pipeline history

**Given** the stage completing
**When** the orchestrator processes it
**Then** the HandoffPacket is written to data/artifacts/{run_id}/stage_07_draft.json

### Story 5.3: Assemble Stage -- Briefing Document Assembly

As a developer,
I want the assemble stage to organize all drafted stories into a single dated markdown briefing file grouped by section,
So that the output is a readable document the user can download and review.

**Acceptance Criteria:**

**Given** a HandoffPacket with drafted_stories and a section order from config
**When** the assemble stage runs
**Then** stories are organized into sections in the user-configured section order

**Given** stories within a section
**When** assembly orders them
**Then** stories are sorted by source count (most newsletters covering the story appears first)

**Given** the assembled briefing
**When** I read the markdown file
**Then** it contains a header with: date, run ID, total story count, and section breakdown (e.g. "AI: 3 stories, Technology: 2 stories")

**Given** the assembled markdown
**When** I inspect the file path
**Then** it is saved to data/briefings/{run_id}/briefing.md

**Given** the assemble stage
**When** it completes
**Then** packet.assembled_markdown contains the full markdown string and the BriefingOutput DB record is updated with markdown_path

**Given** the stage completing
**When** the orchestrator processes it
**Then** the HandoffPacket is written to data/artifacts/{run_id}/stage_08_assemble.json

---

## Epic 6: Audio Production -- Listen to Your Briefing

After this epic, each briefing run produces an mp3 audio file alongside the markdown, optimized for spoken delivery via Kokoro TTS. Audio failure degrades gracefully -- the markdown briefing is always delivered.

### Story 6.1: TTS Prep Stage -- Spoken-Form Optimization

As a developer,
I want the TTS prep stage to rewrite the assembled briefing prose into a narration-optimized script,
So that the audio output sounds like a real broadcast rather than a text document read aloud.

**Acceptance Criteria:**

**Given** a HandoffPacket with assembled_markdown
**When** the TTS prep stage runs
**Then** packet.tts_script is populated with a spoken-form version of the briefing

**Given** the TTS script
**When** I read it
**Then** it contains no markdown syntax (no #, **, _, [], etc.), no raw URLs, and no attribution brackets

**Given** section transitions in the briefing
**When** they appear in the TTS script
**Then** they are natural spoken segues (e.g. "Turning now to technology..." not "## Technology")

**Given** proper nouns and acronyms in the briefing
**When** the TTS script is generated
**Then** a pronunciation guide is produced as packet.pronunciation_guide (dict mapping term to pronunciation)

**Given** the TTS prep stage
**When** it generates the script
**Then** it calls llm.complete() with a prompt from pipeline_prompts/stages/tts_prep.md

**Given** the stage completing
**When** the orchestrator processes it
**Then** the HandoffPacket is written to data/artifacts/{run_id}/stage_09_tts_prep.json

### Story 6.2: Kokoro TTS Service and Audio Synthesis

As a developer,
I want a TTS service wrapper around Kokoro that synthesizes the narration script into an mp3 file,
So that users get a listenable audio briefing without needing GPU hardware.

**Acceptance Criteria:**

**Given** a TTS script string
**When** I call tts.synthesize(script, output_path)
**Then** an mp3 file is written to the specified path

**Given** Kokoro model weights not present in the local cache
**When** tts.synthesize() is called for the first time
**Then** the weights are downloaded automatically from HuggingFace before synthesis begins

**Given** the synthesized audio file
**When** I inspect the output path
**Then** it is saved to data/briefings/{run_id}/briefing.mp3

**Given** the TTS service
**When** synthesis fails (model unavailable, OOM, etc.)
**Then** a StageError with retryable=False is raised -- the orchestrator catches it, logs it, and continues the Run without audio (not a fatal Run failure)

**Given** a successful synthesis
**When** the orchestrator handles the result
**Then** the BriefingOutput DB record is updated with audio_path -- markdown_path is always set regardless of audio success/failure

### Story 6.3: TTS Engine Configuration in Settings

As a user,
I want to select and test my TTS engine from the Settings page,
So that I can verify audio output quality before running a full briefing.

**Acceptance Criteria:**

**Given** the Settings -- Audio section
**When** I view it
**Then** the current TTS engine is shown (Kokoro as default)

**Given** I click "Test Voice"
**When** the action completes
**Then** a short sample sentence is synthesized and plays in the browser

**Given** I select Orpheus TTS when my machine has no GPU
**When** I attempt to save
**Then** a hardware requirement warning is shown: "Orpheus requires a CUDA-compatible GPU"

**Given** the TTS engine setting changed and saved
**When** the next Run starts
**Then** the newly configured engine is used

---

## Epic 7: Pipeline Orchestration and QA

After this epic, all pipeline stages run in sequence under the orchestrator's control, with live SSE progress streaming, disk artifact persistence after each stage, automatic 3-tier retry on failure, and a Hold state for unrecoverable errors.

### Story 7.1: Pipeline Orchestrator -- Stage Sequencing and DB Writes

As a developer,
I want the pipeline orchestrator to execute all 9 stages in sequence, write HandoffPacket artifacts to disk after each stage, and write Run state to the database,
So that the pipeline is observable, recoverable, and produces durable artifacts.

**Acceptance Criteria:**

**Given** a Run is triggered
**When** the orchestrator starts
**Then** a Run record is created in the DB with status="running" before any stage executes

**Given** each stage completing successfully
**When** the orchestrator processes the result
**Then** the HandoffPacket is written to data/artifacts/{run_id}/stage_{N:02d}_{name}.json before the next stage starts

**Given** all stages completing successfully
**When** the orchestrator finalizes
**Then** Run.status is set to "complete" and BriefingOutput is written in the same DB transaction as ProcessedEmail records

**Given** a stage raising StageError
**When** the orchestrator catches it
**Then** it initiates the retry sequence from Story 7.4 before marking the Run failed or held

**Given** the orchestrator
**When** I inspect its imports
**Then** it imports from pipeline/stages/*, pipeline/handoff.py, db/, core/errors.py, and api/stream.py -- it does not import from main.py or mcp_server.py

**Given** the orchestrator running as a FastAPI BackgroundTask
**When** the web server receives a new HTTP request during pipeline execution
**Then** the server remains responsive -- the pipeline does not block the event loop

### Story 7.2: SSE Live Log Queue Integration

As a developer,
I want a shared async queue that the orchestrator writes log events to and the SSE endpoint reads from,
So that the browser receives real-time pipeline progress without polling.

**Acceptance Criteria:**

**Given** a Run starting
**When** the orchestrator begins
**Then** a new asyncio.Queue is created in the SSE queue registry keyed by run_id (dict[int, asyncio.Queue] singleton in api/stream.py)

**Given** each pipeline stage starting or completing
**When** the orchestrator emits a log event
**Then** a JSON object is placed on the queue: {"event": "log", "data": {"level": "info", "stage": "embed", "message": "...", "ts": "ISO8601"}}

**Given** a Run completing
**When** the orchestrator emits the final event
**Then** {"event": "complete", "data": {"run_id": N, "audio_path": "...", "markdown_path": "..."}} is placed on the queue

**Given** a Run entering Hold state
**When** the orchestrator emits the error event
**Then** {"event": "error", "data": {"code": "STAGE_FAILED", "stage": "...", "message": "...", "retryable": false}} is placed on the queue

**Given** the SSE endpoint at /api/stream/{run_id}
**When** a browser connects
**Then** it reads from the queue for that run_id and streams events as text/event-stream until the queue signals completion

**Given** the SSE client disconnecting
**When** the connection closes
**Then** the queue entry for that run_id is cleaned up -- no memory leak

### Story 7.3: QA Gate Stage -- Pre-Delivery Validation

As a developer,
I want the QA gate stage to validate the assembled briefing before it is marked complete,
So that users never receive a silently broken or incomplete briefing.

**Acceptance Criteria:**

**Given** an assembled briefing
**When** the QA gate runs
**Then** it checks: every configured section has at least one story; every story has source attribution; the TTS script contains no unresolved markdown or raw URLs; estimated audio runtime is within a reasonable range (30 seconds to 90 minutes)

**Given** all QA checks passing
**When** the gate completes
**Then** packet.qa_passed = True and the orchestrator proceeds to finalize the Run

**Given** any QA check failing
**When** the gate completes
**Then** packet.qa_passed = False and a StageError("qa_gate", description_of_failure, retryable=True) is raised

**Given** the QA gate
**When** it runs
**Then** it makes no LLM calls -- all checks are deterministic rule-based validations

### Story 7.4: Three-Tier Retry and Hold State

As a user,
I want the pipeline to automatically attempt recovery when a stage fails, and surface a clear Needs Review state when it cannot recover automatically,
So that I am never left with a silent failure and always have a manual option.

**Acceptance Criteria:**

**Given** a stage raising StageError with retryable=True
**When** the orchestrator catches it
**Then** Tier 1: the failing stage is retried once with a concise error message injected into the stage's context prompt

**Given** Tier 1 retry also failing
**When** the orchestrator handles the second failure
**Then** Tier 2: the stage is retried once more with expanded context and explicit correction guidance in the prompt

**Given** Tier 2 retry also failing
**When** the orchestrator handles the third failure
**Then** Run.status is set to "hold", the briefing appears in history marked "Needs Review", and the error description is stored in Run.error

**Given** a Run in Hold state
**When** the user views it in history
**Then** they see: the stage that failed, a plain-English description of the issue, and a "Retry" button

**Given** the user clicking "Retry" on a held Run
**When** the retry is triggered
**Then** the pipeline resumes from the failed stage using the persisted HandoffPacket artifacts -- it does not restart from ingest

**Given** a StageError with retryable=False
**When** the orchestrator catches it
**Then** it skips the retry tiers and immediately enters Hold state

**Given** any failure
**When** the orchestrator handles it
**Then** an error event is emitted to the SSE queue -- the failure is always visible in the live log

---

## Epic 8: Web UI -- Dashboard, History and Settings

After this epic, users can use a browser-based interface to trigger runs, watch live progress, browse and download past briefings, and manage all application settings.

### Story 8.1: FastAPI App Setup and Base Templates

As a developer,
I want the FastAPI app initialized with all routers registered and Jinja2 base templates rendering with Pico.css,
So that all UI stories have a working app shell to build on.

**Acceptance Criteria:**

**Given** running `uvicorn app.main:app --host 127.0.0.1 --port 8000`
**When** I open http://localhost:8000
**Then** the dashboard page renders with no 500 errors

**Given** the base.html template
**When** rendered
**Then** it includes Pico.css from CDN, dark mode (data-theme="dark"), and HTMX from CDN

**Given** all router modules (briefings, downloads, settings, stream)
**When** the app starts
**Then** they are registered and their routes appear in FastAPI auto-docs at /docs

**Given** the FastAPI lifespan event
**When** the app starts
**Then** the database is initialized before any request is served

**Given** any unhandled StageError reaching the app level
**When** the exception handler fires
**Then** a JSON error response is returned: {"error": "...", "code": "...", "retryable": bool}

### Story 8.2: Dashboard -- Run Trigger and Live Pipeline Log

As a user,
I want to click a button to start a briefing run and watch real-time progress in my browser,
So that I know exactly what the pipeline is doing and can spot any issues immediately.

**Acceptance Criteria:**

**Given** the dashboard page loaded
**When** I view it
**Then** a "Run Briefing" button is visible and enabled

**Given** I click "Run Briefing"
**When** the button is clicked
**Then** a POST /api/briefings request is sent, a run_id is returned, the button becomes disabled, and the live log panel appears

**Given** the live log panel active
**When** the pipeline progresses
**Then** each stage (ingest, extract, embed, cluster, select, frame, draft, tts_prep, assemble, qa_gate) appears in the log as it starts and completes via SSE

**Given** any stage error occurring
**When** the error event arrives
**Then** the error appears inline in the log with a plain-English description -- the user does not need to check a terminal

**Given** the Run completing
**When** the complete event arrives
**Then** the new briefing entry appears in the history list without a page refresh and the "Run Briefing" button re-enables

**Given** a Run already in progress
**When** I view the dashboard
**Then** the "Run Briefing" button is disabled and the live log shows current progress

### Story 8.3: Briefing History List and Download Endpoints

As a user,
I want to see a list of all my past briefings with download options,
So that I can access any previous briefing whenever I want.

**Acceptance Criteria:**

**Given** past completed Runs in the database
**When** I view the history page
**Then** each entry shows: date, story count, section breakdown, and status

**Given** a history entry
**When** I view it
**Then** it has separate download buttons for the markdown file and audio file

**Given** I click the markdown download button
**When** the request completes
**Then** the briefing.md file downloads with a filename matching the briefing date

**Given** a Run where audio generation failed
**When** I view its history entry
**Then** the audio download button is absent or disabled with a tooltip "Audio not available for this run"

**Given** the history list
**When** rendered
**Then** entries are sorted newest-first

**Given** a Run in Hold state
**When** it appears in history
**Then** it shows a distinct "Needs Review" indicator and a "Retry" button

### Story 8.4: Settings -- Gmail Configuration

As a user,
I want to change my Gmail label and re-authorize OAuth from Settings,
So that I can reconfigure my Gmail source at any time without re-running the full onboarding wizard.

**Acceptance Criteria:**

**Given** the Settings -- Gmail section
**When** I view it
**Then** the current configured label is shown in an editable text field

**Given** I change the label and click Save
**When** the save completes
**Then** the new label is stored in config and takes effect on the next Run

**Given** I click "Re-authorize Gmail"
**When** the button is clicked
**Then** the Google OAuth browser flow opens; on completion the new token replaces the old one in the credential store

**Given** the current OAuth token status
**When** shown in Settings
**Then** it displays "Authorized" or "Not authorized" with the authorized email address if known

### Story 8.5: Settings -- Topic Sections Management

As a user,
I want to add, rename, remove, and reorder my topic sections from Settings,
So that my briefing is organized around the topics I actually care about.

**Acceptance Criteria:**

**Given** the Settings -- Sections page
**When** I view it
**Then** all currently configured sections are listed with their names and order

**Given** I click "Add Section" and type a name then save
**When** I save
**Then** the new section appears in the list and is used on the next Run

**Given** I try to delete the last remaining section
**When** I click delete
**Then** the UI prevents deletion with the message: "At least one section is required"

**Given** the "Other" catch-all section
**When** I view the section list
**Then** it appears in the list but cannot be renamed or deleted

**Given** I reorder sections and save
**When** the save completes
**Then** the new order is persisted and applied to the next Run

### Story 8.6: Settings -- Briefing Depth and LLM Provider

As a user,
I want to select my preferred briefing depth and LLM provider -- and test the connection -- from Settings,
So that I can tune quality and cost without editing config files.

**Acceptance Criteria:**

**Given** the Settings -- Briefing Depth section
**When** I view it
**Then** Brief, Standard, and Deep options are shown with a description of each; Standard is highlighted as default

**Given** I select a depth and save
**When** the next Run starts
**Then** the pipeline uses the selected depth for all story framing

**Given** the Settings -- LLM Provider section
**When** I view it
**Then** the five provider options are listed: Ollama, OpenAI, Anthropic, Gemini, MCP Sampling

**Given** I select Ollama and click "Test Connection"
**When** Ollama is reachable
**Then** a green "Connected" indicator appears showing the configured model name

**Given** I select OpenAI and enter an API key then click "Test Connection"
**When** the key is valid
**Then** "Connected" indicator appears; when invalid, a clear error message appears

**Given** I save a BYOK API key
**When** I view Settings again
**Then** the key is masked (e.g. "sk-...abc") -- the full key is never displayed after entry

### Story 8.7: Settings -- Schedule and Daemon Mode Display

As a user,
I want to configure my briefing schedule and toggle daemon mode from Settings,
So that I can control when my briefings run and whether they run even when the browser is closed.

**Acceptance Criteria:**

**Given** the Settings -- Schedule section
**When** I view it
**Then** cadence options are shown: Off, Daily, Every Other Day, Weekly; plus a time picker

**Given** I set cadence to Daily at 7:00 AM and save
**When** I view Settings later
**Then** it shows "Next scheduled run: tomorrow at 7:00 AM"

**Given** the Daemon Mode toggle
**When** I view it
**Then** it shows current status (On/Off) and a description of what it does

**Given** a missed scheduled run
**When** I open the app after the missed time
**Then** a banner shows: "Missed run at [time] -- retrying now" and a retry Run appears in the live log

---

## Epic 9: Scheduling and Daemon Mode

After this epic, the app runs scheduled briefings automatically. With Daemon Mode enabled, runs fire even when the browser is closed. Missed runs are detected and retried on next app open.

### Story 9.1: APScheduler Integration and Run Scheduling

As a user who configured a daily schedule,
I want the app to automatically trigger a briefing run at my configured time when the app is open,
So that a fresh briefing is ready for me without manual action.

**Acceptance Criteria:**

**Given** a schedule configured to run daily at 7:00 AM and the app is open at 7:00 AM
**When** the scheduled time arrives
**Then** APScheduler fires and the orchestrator starts a Run exactly as if the user had clicked "Run Briefing"

**Given** a Run triggered by the scheduler
**When** it completes
**Then** it appears in the history list exactly like a manually triggered Run

**Given** the scheduler configuration changing in Settings
**When** the user saves a new cadence or time
**Then** APScheduler's job is updated in memory immediately -- no restart required

**Given** cadence set to "Off"
**When** the scheduler evaluates
**Then** no automatic Runs fire

**Given** a Run already in progress
**When** the scheduler fires for a new run
**Then** the new Run is queued and not started until the current Run completes

### Story 9.2: Daemon Mode -- Background Process

As a user who wants briefings even when the browser is closed,
I want to enable Daemon Mode so the scheduler runs as a background service,
So that my morning briefing is ready even if I have not opened the app.

**Acceptance Criteria:**

**Given** I enable Daemon Mode in Settings and save
**When** the setting is saved
**Then** a detached background subprocess is spawned and a PID file is written to data/briefing.pid

**Given** the daemon process running and the app's browser UI is closed
**When** the scheduled time arrives
**Then** the daemon fires the Run and completes it

**Given** the daemon process running
**When** I open the app's browser UI
**Then** the UI reads the PID file, confirms the daemon is alive, and shows "Daemon Mode: Running"

**Given** I disable Daemon Mode and save
**When** the save completes
**Then** the daemon process is terminated, the PID file is deleted, and Settings shows "Daemon Mode: Off"

**Given** the PID file existing but the process no longer running
**When** the app starts
**Then** it detects the stale PID, removes the file, and shows "Daemon Mode: Off (process not found)"

### Story 9.3: Missed Run Detection and Auto-Retry

As a user who does not use Daemon Mode,
I want the app to detect and retry any missed scheduled runs when I open it,
So that I still get my briefing even if the app was not running at the scheduled time.

**Acceptance Criteria:**

**Given** a scheduled run that fired at 7:00 AM while the app was closed
**When** I open the app at 9:00 AM
**Then** the app detects the missed run and displays: "Missed run at 7:00 AM -- retrying now"

**Given** the missed run detection firing
**When** the app initializes
**Then** a new Run starts automatically before the history list renders

**Given** multiple missed runs (app closed for 3 days with daily schedule)
**When** the app opens
**Then** only one retry Run fires (the most recent missed run) -- not multiple simultaneous runs

---

## Epic 10: First-Run Onboarding

After this epic, a new user is guided through setup with a step-by-step wizard. Gmail OAuth is the only required step. Everything else can be skipped and configured later in Settings.

### Story 10.1: First-Run Onboarding Wizard

As a new user setting up Briefing for the first time,
I want a guided setup wizard that walks me through authorization and configuration,
So that I can go from clone to first briefing in under 15 minutes.

**Acceptance Criteria:**

**Given** launching the app for the first time (no existing config or token)
**When** I open http://localhost:8000
**Then** I am redirected to the onboarding wizard, not the dashboard

**Given** the wizard's first step
**When** I view it
**Then** it prompts me to authorize Gmail and explains the read-only access scope

**Given** completing OAuth authorization
**When** the token is stored
**Then** the wizard advances to the next step automatically

**Given** any step after OAuth
**When** I view it
**Then** a "Skip for now" button is visible and functional

**Given** the Kokoro model download step
**When** I reach it
**Then** the download starts automatically with a progress bar -- no manual command needed

**Given** completing or skipping the wizard
**When** it closes
**Then** I land on the dashboard ready to click "Run Briefing"

**Given** reopening the app after completing onboarding
**When** the app initializes
**Then** the wizard does not appear -- I go directly to the dashboard

**Given** the wizard completing with some steps skipped
**When** I view Settings
**Then** skipped items are shown as "Incomplete" with a prompt to configure them

### Story 10.2: Onboarding Status and Revisit in Settings

As a returning user who skipped steps during onboarding,
I want to complete or reconfigure any setup item from the Settings page,
So that I can set things up at my own pace without going through the full wizard again.

**Acceptance Criteria:**

**Given** the Settings page
**When** I view the Setup Status section
**Then** each item shows its status: Gmail (Authorized / Not authorized), Kokoro (Downloaded / Not downloaded), Sections (N configured), LLM Provider (configured provider), Schedule (cadence and time or Off)

**Given** a status item showing "Not configured"
**When** I click it
**Then** I am taken directly to the relevant Settings section for that item

**Given** I complete a previously skipped item from Settings
**When** I save
**Then** its status in the Setup Status section updates to the configured state

---

## Epic 11: MCP Server -- Headless AI Integration

After this epic, Claude Desktop and AI agents like Hermes can trigger and retrieve briefings as MCP tool calls over stdio. Pipeline stages also support routing LLM calls through the host model via MCP sampling.

### Story 11.1: MCP Server Entry Point and Tool Definitions

As a developer or AI agent user,
I want a standalone MCP server exposing the four core briefing tools over stdio,
So that Claude Desktop or Hermes can control Briefing without launching the web UI.

**Acceptance Criteria:**

**Given** running `uv run python -m app.mcp_server`
**When** the process starts
**Then** it initializes the MCP server over stdio without starting FastAPI or a web server

**Given** the MCP server running
**When** a client calls `trigger_briefing` with optional depth argument
**Then** a Run is started via the pipeline orchestrator and the run_id is returned as a text response

**Given** the MCP server running
**When** a client calls `get_run_status` with a run_id
**Then** the current Run status (pending, running, complete, failed, hold) is returned

**Given** the MCP server running
**When** a client calls `list_briefings`
**Then** a list of past completed Runs is returned with date, story count, and section breakdown

**Given** the MCP server running
**When** a client calls `get_briefing_content` with a run_id and content_type ("markdown" or "script")
**Then** the requested file content is returned as text

**Given** mcp_server.py
**When** I inspect its imports
**Then** it imports from pipeline/, core/, db/ only -- no import of api/, main.py, or FastAPI

**Given** the Claude Desktop config from the architecture doc added to claude_desktop_config.json
**When** Claude Desktop loads
**Then** it can discover and call all four tools

### Story 11.2: MCP Sampling Integration in llm.py

As a user running Briefing via Claude Desktop with Sonnet,
I want pipeline LLM calls to use the host Claude model when MCP sampling is available,
So that I get Claude quality for synthesis without paying separate API token costs.

**Acceptance Criteria:**

**Given** the MCP server running inside a Claude Desktop session
**When** config.llm_provider = "mcp_sampling" and a stage calls llm.complete(prompt, config)
**Then** the call uses server.create_message() to route the prompt to the Claude host model

**Given** config.llm_provider = "mcp_sampling" but the server is running without a sampling-capable host
**When** llm.complete() is called
**Then** the call falls back silently to Ollama and logs a WARNING: "MCP sampling not available, falling back to Ollama"

**Given** switching the MCP host from Claude to a smaller model in Hermes
**When** the Hermes session uses a different model
**Then** pipeline calls automatically use the Hermes-configured model -- no config change needed in Briefing

---

## Epic 12: Testing and Documentation

After this epic, the codebase has a complete test suite covering all API routes, pipeline stages, services, and MCP tools -- and a README enabling a new builder to set up Briefing in under 15 minutes.

### Story 12.1: Test Infrastructure -- Conftest, Fixtures, and Test Database

As a developer,
I want a test infrastructure with shared fixtures, a test database, and mock HandoffPacket builders,
So that writing new tests requires minimal boilerplate and no side effects on real data.

**Acceptance Criteria:**

**Given** running `uv run pytest`
**When** the test suite starts
**Then** a fresh in-memory SQLite database is created for the test session and torn down after

**Given** any test needing an AppConfig
**When** it uses the config fixture
**Then** it receives a test-mode config pointing at the test database and a temp data directory -- no real data files are touched

**Given** any test needing a HandoffPacket
**When** it uses the mock_packet fixture
**Then** it receives a HandoffPacket pre-populated with realistic test data for all fields

**Given** any test needing an HTTP client
**When** it uses the async_client fixture
**Then** it receives an httpx AsyncClient configured against the test FastAPI app

**Given** the test suite running
**When** all tests complete
**Then** no real keyring entries, Gmail API calls, or LLM calls are made -- all external services are mocked

### Story 12.2: API Route Tests

As a developer,
I want tests for all FastAPI routes covering happy path and error cases,
So that any regression in the API layer is caught before it reaches users.

**Acceptance Criteria:**

**Given** POST /api/briefings called with a valid request
**When** the test runs
**Then** a 200 response is returned with {"run_id": N, "status": "pending"}

**Given** GET /api/briefings with completed Runs in the test DB
**When** the test runs
**Then** a 200 response is returned with a list of briefing entries sorted newest-first

**Given** GET /api/briefings/{id}/download/markdown for a completed Run
**When** the test runs
**Then** the markdown file is returned with Content-Type: text/markdown

**Given** GET /api/briefings/{id}/download/markdown for a non-existent Run
**When** the test runs
**Then** a 404 response is returned with the defined error envelope

**Given** PUT /api/settings/{section} with valid data
**When** the test runs
**Then** a 200 response confirms the settings are saved

### Story 12.3: Pipeline Stage Tests

As a developer,
I want unit tests for each of the 9 pipeline stages using mock HandoffPackets and mocked external services,
So that stage logic is verified independently of Gmail, LLM providers, and TTS.

**Acceptance Criteria:**

**Given** the extract stage with a HandoffPacket containing raw HTML emails
**When** the test runs
**Then** extracted_texts is populated with clean text, title, sender, and date for each email

**Given** the cluster stage with pre-computed mock embeddings
**When** the test runs
**Then** texts with high cosine similarity are grouped into the same cluster

**Given** the select stage with a mock LLM returning section names
**When** the test runs
**Then** each cluster receives a section assignment; unmatched clusters go to "Other"

**Given** the draft stage with mock LLM responses for each depth tier
**When** the test runs
**Then** brief stories are 2-3 sentences, standard stories are paragraphs, deep stories are mini-segments

**Given** the qa_gate stage with a valid briefing package
**When** the test runs
**Then** qa_passed = True is set

**Given** the qa_gate stage with a briefing missing source attribution on a story
**When** the test runs
**Then** a StageError is raised with a message identifying the validation failure

**Given** every stage test
**When** it runs
**Then** no real LLM calls, Gmail calls, or TTS synthesis occur -- all mocked via pytest fixtures

### Story 12.4: Service and MCP Tests

As a developer,
I want tests for the LLM provider router, Gmail service, TTS service, and MCP tools,
So that service integrations and tool contracts are verified.

**Acceptance Criteria:**

**Given** llm.complete() with provider = "ollama" and a mocked Ollama HTTP response
**When** the test runs
**Then** the mocked response text is returned

**Given** llm.complete() with provider = "mcp_sampling" and no active MCP context
**When** the test runs
**Then** the call falls back to Ollama (mocked) and a WARNING is logged

**Given** the Gmail service with a mocked Gmail API client
**When** fetching emails
**Then** only emails not in the Processed Log are returned

**Given** the MCP trigger_briefing tool called with a mock orchestrator
**When** the test runs
**Then** the mock orchestrator's start_run() is called and the run_id is returned in the response

**Given** the MCP list_briefings tool with test DB entries
**When** the test runs
**Then** the correct list of briefings is returned

### Story 12.5: README and Google OAuth Setup Guide

As a new technical user,
I want a README that guides me from clone to first briefing in under 15 minutes,
So that I can get value from Briefing without needing to read source code.

**Acceptance Criteria:**

**Given** the README
**When** I read it
**Then** it contains in order: what Briefing does (1 paragraph), prerequisites (Python, uv, Ollama, Google Cloud project), installation steps, Google OAuth setup guide, first run instructions, and a settings overview

**Given** the Google OAuth setup guide section
**When** I follow it
**Then** I can create a Google Cloud project, enable the Gmail API, download credentials.json, and complete OAuth authorization without external documentation

**Given** the README installation steps followed on a fresh machine
**When** I run `uv run python setup.py`
**Then** onboarding completes without errors

**Given** the README
**When** I read it
**Then** it includes a troubleshooting section covering: Ollama not running, OAuth token expired, Kokoro download failing, and first run producing no stories

**Given** the README followed by a new technical user meeting the prerequisites
**When** they time a full setup from clone to first briefing
**Then** it takes under 15 minutes (SM-2)

---

## Epic 13: On-Demand Ingest — YouTube and Article Modes

After this epic, users can paste YouTube URLs or article URLs into the dashboard and receive a public radio-style briefing and audio file from that content. The same pipeline, TTS engine, and history list are used — only the ingest source changes.

### Story 13.1: YouTube Transcript Ingest Service

As a user,
I want to paste a YouTube URL and have the system extract the transcript,
So that I can get a briefing from a video without watching it.

**Acceptance Criteria:**

**Given** a valid YouTube URL with an available transcript
**When** the YouTube ingest service runs
**Then** the full transcript text is returned as a single string with speaker labels and timestamps stripped

**Given** a YouTube URL where no transcript is available (disabled captions)
**When** the ingest service runs
**Then** the URL is skipped with a WARNING log and a user-visible message: "No transcript available for [URL]"

**Given** multiple YouTube URLs submitted together
**When** the ingest service runs
**Then** each transcript is extracted independently and returned as a separate content item keyed by URL

**Given** the YouTube ingest service
**When** I inspect its dependencies
**Then** it uses `youtube-transcript-api` — no browser automation, no scraping, no Selenium

**Given** a private or age-restricted YouTube video
**When** the ingest service attempts extraction
**Then** it returns a clear error message and skips that URL — it does not crash the run

### Story 13.2: Article Body Extraction Service

As a user,
I want to paste an article URL and have the system extract just the article body,
So that I can get a briefing from a web article without ads, navigation, or paywalls cluttering the content.

**Acceptance Criteria:**

**Given** a public article URL
**When** the article extraction service runs
**Then** `trafilatura` is used as the primary extractor and returns the article body as clean plain text

**Given** a URL where `trafilatura` returns fewer than 200 words
**When** the extraction service evaluates the result
**Then** it falls back to Jina Reader (`r.jina.ai/{url}`) and uses that response as the article body

**Given** both `trafilatura` and Jina Reader returning insufficient content (< 200 words)
**When** the extraction service finishes
**Then** the URL is skipped with a WARNING: "Could not extract sufficient content from [URL]"

**Given** a JavaScript-rendered page that trafilatura cannot parse
**When** trafilatura returns sparse or empty content
**Then** the Jina Reader fallback handles it and returns clean markdown body text

**Given** the article extraction service
**When** I inspect its dependencies
**Then** `trafilatura` is in pyproject.toml and Jina Reader is called via HTTP — no headless browser required

### Story 13.3: On-Demand Pipeline Run — Bypass Gmail Ingest

As a developer,
I want on-demand content (YouTube transcripts or article bodies) to enter the pipeline at the embed stage, bypassing Gmail ingest,
So that all downstream stages work identically to a newsletter run without code duplication.

**Acceptance Criteria:**

**Given** a set of extracted content items from YouTube or article sources
**When** the on-demand run starts
**Then** the HandoffPacket is populated with `extracted_texts` directly — the ingest stage is skipped entirely

**Given** the HandoffPacket populated by on-demand ingest
**When** the embed stage runs
**Then** it processes the content identically to newsletter-sourced extracted_texts — no stage-level awareness of the source type

**Given** an on-demand run completing
**When** it appears in the Run DB record
**Then** `section_config` includes a `source_type` field set to "youtube" or "article" (or "mixed" if both)

**Given** an on-demand run that produces no usable content (all URLs skipped)
**When** the pipeline evaluates after ingest
**Then** it halts early with status "no_content" and a user-visible message identifying which URLs failed

**Given** the on-demand pipeline path
**When** I inspect the orchestrator
**Then** it reuses the same STAGES list from Story 7.1, starting at embed — no parallel code path exists

### Story 13.4: On-Demand Ingest API and Dashboard UI

As a user,
I want a URL input area on the dashboard where I can paste links and trigger an on-demand briefing,
So that getting a briefing from a video or article is as simple as pasting a link.

**Acceptance Criteria:**

**Given** the dashboard
**When** I view it
**Then** a "From URLs" input section is visible below the "Run Briefing" button, with a multi-line text area and a "Run from URLs" submit button

**Given** I paste one or more URLs (YouTube, article, or mixed) into the text area and click submit
**When** the request is processed
**Then** `POST /api/briefings/on-demand` is called with `{"urls": [...]}`, a run_id is returned, and the live SSE log activates

**Given** a submitted URL list containing YouTube URLs
**When** the system processes them
**Then** YouTube URLs (matching `youtube.com` or `youtu.be`) are auto-detected and routed to the YouTube ingest service — the user does not need to specify the type

**Given** the on-demand run completing
**When** the result appears in history
**Then** the history entry shows a "YouTube" or "Article" or "Mixed" badge alongside the date and story count

**Given** a concurrent newsletter run already in progress
**When** I submit an on-demand request
**Then** a 409 response is returned: "A run is already in progress" — same behavior as duplicate newsletter runs

**Given** `POST /api/briefings/on-demand` receiving an empty URL list
**When** the endpoint validates the request
**Then** a 400 response is returned: "At least one URL is required"

### Story 13.5: Tests for On-Demand Ingest

As a developer,
I want tests for the YouTube service, article extraction service, on-demand API endpoint, and pipeline bypass logic,
So that the on-demand path has the same test coverage as the newsletter path.

**Acceptance Criteria:**

**Given** the YouTube ingest service with a mocked `youtube-transcript-api` response
**When** the test runs
**Then** the returned transcript matches the mocked content with timestamps and speaker labels stripped

**Given** a URL where the mocked transcript API raises `TranscriptsDisabled`
**When** the test runs
**Then** the service returns an empty result and logs a warning — no exception propagates

**Given** the article extraction service with a mocked `trafilatura.extract()` returning fewer than 200 words
**When** the test runs
**Then** the service falls back to Jina Reader (mocked HTTP response) and returns that content

**Given** `POST /api/briefings/on-demand` with a valid URL list and mocked pipeline
**When** the test runs
**Then** a 200 response is returned with a run_id

**Given** `POST /api/briefings/on-demand` with an empty URL list
**When** the test runs
**Then** a 400 response is returned

**Given** the on-demand orchestrator path with mocked extracted content
**When** the test runs
**Then** the embed stage receives the content directly and the ingest stage is not called
