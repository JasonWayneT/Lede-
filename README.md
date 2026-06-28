# Lede

> Your reads, one briefing.

---

## What This Is

Lede pulls the newsletters you subscribe to from Gmail, synthesizes cross-source stories, and delivers a dated editorial briefing as markdown and NPR-style audio. Built for builders and PMs who want to stay informed without the inbox pile-up.

**What this is not:**
- A per-email summarizer — Lede synthesizes across sources, not within them
- A cloud service — runs locally, your data stays local
- An RSS reader — works entirely through Gmail labels

---

## Status

| Field | Value |
|---|---|
| **Phase** | Beta — core pipeline working end-to-end |
| **Stability** | Functional; setup wizard required on first run |
| **Last updated** | June 2026 |

---

## How It Works

**Core workflow:**
1. Authenticate with Gmail and select a label containing your newsletters
2. Lede ingests emails, extracts content, embeds and clusters by topic
3. An LLM frames, drafts, and assembles a sectioned editorial briefing
4. Kokoro TTS renders the briefing as an audio file
5. View, download, or listen from the web UI — or trigger via MCP from Claude Desktop or Hermes

---

## Installation

### Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- A Gmail account with OAuth credentials (see setup wizard)
- Optional: Ollama for local LLM, or an API key for OpenAI / Anthropic / Gemini

### Gmail OAuth setup (required)

Before running Lede you need a Google Cloud OAuth credential. This takes about 10 minutes.

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a project named **Lede**
2. Search **Gmail API** → Enable it
3. Left menu → **APIs & Services → OAuth consent screen**
   - User type: **External**
   - Fill in app name, your email for support and developer contact
4. Left menu → **Data Access** → add scope `https://www.googleapis.com/auth/gmail.readonly`
5. Left menu → **Audience** → add your Gmail address as a test user
6. Left menu → **Clients** → Create OAuth client → **Desktop app** → Create → Download JSON
7. Rename the downloaded file to `credentials.json` and place it in `briefing/data/`

> The `data/` folder is gitignored — your credentials will never be committed.

### Setup

```bash
git clone https://github.com/JasonWayneT/Lede-.git
cd Lede/briefing
uv sync
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### First run

Open `http://localhost:8001` in your browser. The setup wizard will walk you through:

1. **Authorize Gmail** — click the button, sign in with Google, approve `gmail.readonly`. If you see an "unverified app" warning, click **Advanced → Go to Lede (unsafe)** — this is expected for personal OAuth apps in testing mode.
2. **Text-to-speech** — Kokoro (~300 MB) downloads automatically on first briefing run. Skip if you want text-only.
3. **Inbox label** — set the Gmail label Lede should pull from (e.g. `Newsletters`)
4. **Schedule** — choose daily, every other day, weekly, or manual-only

---

## Usage

### Web UI

```bash
uv run python -m app.main
```

Opens the dashboard at `http://localhost:8000`. Run a briefing, view history, download audio.

### MCP Server (Claude Desktop / Hermes)

```bash
uv run python -m app.mcp_server
```

Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "lede": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp_server"],
      "cwd": "/path/to/Lede"
    }
  }
}
```

Available tools: `trigger_briefing`, `get_run_status`, `list_briefings`, `get_briefing_content`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI |
| Frontend | HTMX, Jinja2, custom design system (Material Design 3 + 8pt grid) |
| Database | SQLite, SQLAlchemy async |
| Pipeline | sentence-transformers, FAISS, Kokoro TTS |
| Scheduling | APScheduler + daemon subprocess |
| LLM providers | Ollama, OpenAI, Anthropic, Gemini, MCP Sampling |
| Credentials | keyring (OS-native store) |
| MCP | mcp (Anthropic Python SDK), stdio transport |
| Package manager | uv |

---

## Project Structure

```
Lede/
├── app/                   # Application source
│   ├── main.py            # FastAPI entry point
│   ├── mcp_server.py      # Standalone MCP entry point
│   ├── api/               # Route handlers and SSE
│   ├── pipeline/          # 9-stage processing pipeline
│   ├── services/          # LLM, TTS, Gmail services
│   ├── core/              # Config, errors, scheduling
│   └── db/                # Models, migrations, session
├── docs/                  # Planning artifacts (BMAD outputs)
│   ├── product-brief.md   # Product brief
│   ├── PRD.md             # Product requirements
│   ├── ARCHITECTURE.md    # Architecture decisions
│   ├── epics-stories.md   # Epics and stories
│   └── spec/              # Implementation specs (Stage 3)
├── tests/                 # Test suite
├── data/                  # Runtime data (gitignored)
├── AGENTS.md              # Agent operating rules
├── CHANGELOG.md           # Release history
└── README.md              # This file
```

---

## Documentation

| Document | Purpose |
|---|---|
| [AGENTS.md](./AGENTS.md) | Agent operating rules — methodology, coding standards, CHANGELOG format |
| [docs/product-brief.md](./docs/product-brief.md) | Product brief from BMAD |
| [docs/PRD.md](./docs/PRD.md) | Full product requirements |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Architecture decisions |
| [docs/epics-stories.md](./docs/epics-stories.md) | 12 epics, 44 stories |
| [docs/spec/00-project-constitution.md](./docs/spec/00-project-constitution.md) | Project scope, operating mode, constraints |
| [docs/spec/02-requirements-registry.md](./docs/spec/02-requirements-registry.md) | Canonical requirement IDs — source of truth |

---

## How This Was Built

Lede went through the full PM-led methodology before a line of code was written: idea validation, a complete PRD, architecture decisions across 8 steps, and 44 implementation-ready stories across 12 epics. Everything in `docs/` is the output of that process. The spec layer in `docs/spec/` bridges those artifacts to the implementation.

---

## License

MIT
