# Privacy Policy — Briefing

Briefing is a personal, local-first application. It is not a hosted service —
it runs on your own machine, for your own use.

## What it accesses

- **Gmail (read-only):** Briefing requests the
  `https://www.googleapis.com/auth/gmail.readonly` scope to fetch newsletter
  emails matching a label you configure. It never sends, modifies, or
  deletes email, and requests no broader Gmail permission.
- **LLM providers (optional, user-configured):** if you enable a
  non-local provider (OpenAI, Anthropic, Gemini) for summarization, the
  content of fetched emails is sent to that provider under your own API key
  (BYOK). By default, Briefing uses a local Ollama model and sends no data
  anywhere.

## Where data is stored

- The Gmail OAuth token and any LLM API keys are stored encrypted in your
  operating system's credential store (Windows Credential Manager / macOS
  Keychain / libsecret via Python's `keyring` library) — never in plaintext
  on disk.
- Fetched email content, generated briefings, and pipeline run history are
  stored locally in a SQLite database on your machine.

## What is not done

- No data is transmitted to the developer of Briefing.
- No analytics, telemetry, or tracking is included.
- No data is shared with any third party other than the LLM provider you
  explicitly configure, and only for the purpose of generating your
  briefing.

## Revoking access

You can revoke Gmail access at any time via
[Google Account → Security → Third-party access](https://myaccount.google.com/permissions).
This immediately invalidates Briefing's stored token.

## Contact

Questions about this policy: jason.wayne.t@gmail.com
