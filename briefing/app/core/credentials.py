"""Credential storage wrapper."""

# Implements ARCH-004

from __future__ import annotations

import keyring

SERVICE_NAME = "briefing"

GMAIL_OAUTH_TOKEN = "gmail_oauth_token"
OPENAI_KEY = "openai_key"
ANTHROPIC_KEY = "anthropic_key"
GEMINI_KEY = "gemini_key"


def set(key: str, value: str) -> None:
    keyring.set_password(SERVICE_NAME, key, value)


def get(key: str) -> str | None:
    return keyring.get_password(SERVICE_NAME, key)


def delete(key: str) -> None:
    try:
        keyring.delete_password(SERVICE_NAME, key)
    except keyring.errors.PasswordDeleteError:
        return

