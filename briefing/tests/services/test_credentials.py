from unittest.mock import patch

import pytest


def test_constants_defined_with_exact_values():
    from app.core import credentials

    assert credentials.SERVICE_NAME == "briefing"
    assert credentials.GMAIL_OAUTH_TOKEN == "gmail_oauth_token"
    assert credentials.OPENAI_KEY == "openai_key"
    assert credentials.ANTHROPIC_KEY == "anthropic_key"
    assert credentials.GEMINI_KEY == "gemini_key"


def test_set_stores_value_in_keyring():
    from app.core import credentials

    with patch("app.core.credentials.keyring.set_password") as set_password:
        credentials.set(credentials.GMAIL_OAUTH_TOKEN, "token-json")
        set_password.assert_called_once_with("briefing", "gmail_oauth_token", "token-json")


def test_get_returns_value_when_present():
    from app.core import credentials

    with patch("app.core.credentials.keyring.get_password", return_value="secret") as get_password:
        assert credentials.get(credentials.OPENAI_KEY) == "secret"
        get_password.assert_called_once_with("briefing", "openai_key")


def test_get_returns_none_when_missing():
    from app.core import credentials

    with patch("app.core.credentials.keyring.get_password", return_value=None):
        assert credentials.get(credentials.OPENAI_KEY) is None


def test_delete_does_not_raise_when_missing():
    from app.core import credentials

    class FakeDeleteError(Exception):
        pass

    with (
        patch("app.core.credentials.keyring.delete_password", side_effect=FakeDeleteError),
        patch("app.core.credentials.keyring.errors.PasswordDeleteError", FakeDeleteError),
    ):
        credentials.delete(credentials.ANTHROPIC_KEY)

