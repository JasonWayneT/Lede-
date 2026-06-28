# Briefing

Briefing is a self-hostable newsletter aggregator that reads your Gmail newsletters, synthesizes them with an LLM, and delivers a structured briefing as both a markdown document and an audio file — ready every morning before you open your laptop.

---

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — fast Python package manager
- [Ollama](https://ollama.ai/) running locally (or a BYOK API key for OpenAI / Anthropic / Gemini)
- A Google Cloud project with the Gmail API enabled (see setup guide below)

---

## Installation

```bash
git clone https://github.com/your-org/briefing.git
cd briefing
uv sync
cp .env.example .env
```

Edit `.env` to set your preferred LLM provider and Gmail label.

---

## Google OAuth Setup Guide

Briefing uses Google's read-only Gmail API to fetch newsletters. Follow these steps to create credentials:

**1. Create a Google Cloud project**

Go to [console.cloud.google.com](https://console.cloud.google.com), click **Select a project → New Project**, name it "Briefing", and click **Create**.

**2. Enable the Gmail API**

In your project, go to **APIs & Services → Library**. Search for "Gmail API" and click **Enable**.

**3. Create an OAuth 2.0 Client ID**

Go to **APIs & Services → Credentials → Create credentials → OAuth client ID**.
- Application type: **Desktop app**
- Name: "Briefing"
- Click **Create** then **Download JSON**

**4. Place the credentials file**

Save the downloaded file as `credentials.json` in the project root. This file is gitignored — never commit it.

**5. Complete authorization**

Run the setup wizard (next section) and click "Authorize Gmail" when prompted. A browser window opens for the Google OAuth consent screen.

---

## First Run

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open [http://localhost:8000](http://localhost:8000). The onboarding wizard will guide you through:

1. Gmail authorization
2. (Optional) Kokoro TTS model download
3. (Optional) Topic sections and schedule configuration

Once setup is complete, click **Run Briefing** on the dashboard.

---

## Settings Overview

| Section | Description |
|---|---|
| Gmail | Change the Gmail label Briefing reads from; re-authorize OAuth |
| Topic Sections | Add, remove, or reorder topic categories |
| Briefing Depth | Brief / Standard / Deep — controls story length and source count |
| LLM Provider | Ollama (local), OpenAI, Anthropic, Gemini, or MCP Sampling |
| Schedule | Daily / Every other day / Weekly at a configured time |
| Daemon Mode | Run scheduled briefings even when the browser is closed |

---

## Claude Desktop / MCP

Briefing exposes an MCP server for use with Claude Desktop or Hermes:

```json
{
  "mcpServers": {
    "briefing": {
      "command": "uv",
      "args": ["run", "python", "-m", "app.mcp_server"],
      "cwd": "/path/to/briefing"
    }
  }
}
```

Available tools: `trigger_briefing`, `get_run_status`, `list_briefings`, `get_briefing_content`.

Set `LLM_PROVIDER=mcp_sampling` in `.env` to route pipeline LLM calls through Claude Desktop.

---

## Troubleshooting

**Ollama not running**
Run `ollama serve` in a separate terminal. Confirm with `ollama list`.

**OAuth token expired**
Go to **Settings → Gmail → Re-authorize Gmail**. The browser OAuth flow will refresh the token.

**Kokoro download failing**
Kokoro downloads from HuggingFace (`hexgrad/Kokoro-82M`). Check your internet connectivity or set `HF_ENDPOINT` to a mirror. Text-only briefings work without Kokoro.

**First run produces no stories**
Verify your Gmail label matches exactly (case-sensitive) what you configured in Settings. The label must exist in Gmail and have unread emails. Check **Settings → Gmail** and confirm the label name.

---

## Development

```bash
uv run pytest          # run all tests
uv run pytest -q -x   # stop on first failure
```

Tests use an in-memory SQLite database and mock all external services (keyring, Gmail API, LLM providers). No real API calls are made during `pytest`.
