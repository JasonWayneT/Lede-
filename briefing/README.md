# Lede

Lede is a self-hostable newsletter intelligence briefing. It reads your Gmail newsletters, synthesizes them with a local LLM, and delivers a structured briefing as both a readable document and an MP3 audio file — ready every morning before you open your laptop.

**Pipeline:** Gmail ingest → text extraction → embedding → clustering → LLM selection → framing → drafting → TTS synthesis → QA gate

**Status:** Working end-to-end. Runs locally with no cloud dependencies beyond Gmail OAuth.

---

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — fast Python package manager
- [Ollama](https://ollama.ai/) running locally (or a BYOK API key for OpenAI / Anthropic / Gemini)
- A Google Cloud project with the Gmail API enabled (see setup below)

Recommended Ollama model: `qwen2.5:7b-instruct-q4_K_M` (good instruction-following, runs on 8GB RAM). Pull it with:

```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
```

---

## Installation

```bash
git clone https://github.com/JasonWayneT/Lede-.git
cd Lede-/briefing
uv sync
```

---

## Google OAuth Setup

Lede uses Google's read-only Gmail API. You need a credentials file from Google Cloud.

**1. Create a Google Cloud project**

Go to [console.cloud.google.com](https://console.cloud.google.com) → **Select a project → New Project** → name it "Lede" → Create.

**2. Enable the Gmail API**

**APIs & Services → Library** → search "Gmail API" → Enable.

**3. Create an OAuth 2.0 Client ID**

**APIs & Services → Credentials → Create credentials → OAuth client ID**
- Application type: **Web application**
- Name: "Lede"
- Authorized redirect URIs: `http://localhost:8001/oauth/callback`
- Click **Create** then **Download JSON**

**4. Place the credentials file**

Save the downloaded file as `credentials.json` in `briefing/data/`. This file is gitignored.

**5. Add yourself as a test user**

**APIs & Services → OAuth consent screen → Audience → Add users** → add your Gmail address.

---

## First Run

```bash
cd briefing
uv run uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Open [http://localhost:8001](http://localhost:8001). The onboarding wizard walks you through:

1. Gmail authorization (click Authorize Gmail → approve in browser)
2. Topic sections and Gmail label configuration
3. Schedule configuration

Once setup is complete, click **Run now** on the dashboard.

> **Unverified app screen:** Google will show a warning since the app isn't published. Click **Advanced → Go to Lede (unsafe)** to proceed. This is expected for a personal local app.

---

## Settings Overview

| Section | Description |
|---|---|
| Gmail | Change the Gmail label; set lookback window (default 7 days); re-authorize |
| Briefing Depth | Brief / Standard / Deep — controls story length |
| LLM Provider | Ollama (local), OpenAI, Anthropic, Gemini, or MCP Sampling |
| TTS Engine | Kokoro (local neural TTS) or disabled |
| Schedule | Daily / Every other day / Weekly at a configured time |

---

## Claude Desktop / MCP

Lede exposes an MCP server for use with Claude Desktop:

```json
{
  "mcpServers": {
    "lede": {
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

**"Invalid label" error on first run**  
The Gmail label must exist in your account. Go to Settings → Gmail and confirm the label name matches exactly.

**OAuth token expired**  
Go to **Settings → Gmail → Re-authorize Gmail**.

**Kokoro download failing**  
Kokoro downloads from HuggingFace (`hexgrad/Kokoro-82M`) on first run. The briefing still completes without audio if TTS fails — check the archive for the markdown file.

**No new emails found**  
The default lookback window is 7 days. Adjust it in Settings → Gmail → Lookback window if you need to pull older emails.

---

## Development

```bash
cd briefing
uv run pytest          # run all tests
uv run pytest -q -x   # stop on first failure
```

Tests use an in-memory SQLite database and mock all external services.
