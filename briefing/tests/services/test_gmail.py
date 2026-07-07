from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest


def test_build_auth_url_returns_consent_url():
    from app.core.config import AppConfig

    fake_flow = Mock()
    fake_flow.authorization_url.return_value = ("https://accounts.google.com/o/oauth2/auth?...", "state-123")

    with (
        patch("app.services.gmail.get_credentials_path", return_value=Path("/fake/credentials.json")),
        patch("app.services.gmail.Flow") as flow_cls,
    ):
        flow_cls.from_client_secrets_file.return_value = fake_flow

        from app.services import gmail

        auth_url = gmail.build_auth_url(AppConfig())

        flow_cls.from_client_secrets_file.assert_called_once()
        assert auth_url == "https://accounts.google.com/o/oauth2/auth?..."


def test_exchange_code_stores_token_via_credentials_set():
    from app.core import credentials as credential_store
    from app.core.config import AppConfig

    fake_creds = Mock()
    fake_creds.to_json.return_value = '{"access_token":"x"}'

    fake_flow = Mock()
    fake_flow.credentials = fake_creds

    with (
        patch("app.services.gmail.get_credentials_path", return_value=Path("/fake/credentials.json")),
        patch("app.services.gmail.Flow") as flow_cls,
        patch("app.services.gmail.credential_store.set") as set_cred,
    ):
        flow_cls.from_client_secrets_file.return_value = fake_flow

        from app.services import gmail

        gmail.exchange_code("auth-code", "state-123", AppConfig())

        flow_cls.from_client_secrets_file.assert_called_once()
        fake_flow.fetch_token.assert_called_once_with(code="auth-code")
        set_cred.assert_called_once_with(credential_store.GMAIL_OAUTH_TOKEN, fake_creds.to_json())


def test_get_service_raises_stageerror_on_refresh_error():
    from app.core.errors import AUTH_ERROR, StageError

    token_json = json.dumps(
        {
            "access_token": "x",
            "refresh_token": "r",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "cid",
            "client_secret": "cs",
            "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
        }
    )

    fake_creds = Mock()
    fake_creds.expired = True
    fake_creds.refresh_token = "r"

    class FakeRefreshError(Exception):
        pass

    fake_creds.refresh.side_effect = FakeRefreshError()

    with (
        patch("app.services.gmail.credential_store.get", return_value=token_json),
        patch("app.services.gmail.google_credentials.Credentials.from_authorized_user_info", return_value=fake_creds),
        patch("app.services.gmail.google_auth_exceptions.RefreshError", FakeRefreshError),
    ):
        from app.services import gmail

        with pytest.raises(StageError) as excinfo:
            gmail.get_service(stage_name="ingest")

        exc = excinfo.value
        assert exc.code == AUTH_ERROR
        assert exc.retryable is False
        assert "Re-authorize from Settings" in exc.message


@pytest.mark.asyncio
async def test_fetch_unprocessed_emails_filters_processed_ids_and_extracts_fields():
    # Fake Gmail API response with 2 message IDs; one already processed.
    list_response = {"messages": [{"id": "m1"}, {"id": "m2"}]}

    def _message(subject: str, from_header: str, date_header: str, html: str):
        import base64

        encoded_html = base64.urlsafe_b64encode(html.encode("utf-8")).decode("ascii")
        return {
            "id": subject,
            "payload": {
                "headers": [
                    {"name": "Subject", "value": subject},
                    {"name": "From", "value": from_header},
                    {"name": "Date", "value": date_header},
                ],
                "mimeType": "multipart/alternative",
                "parts": [
                    {
                        "mimeType": "text/html",
                        "body": {"data": encoded_html},
                    }
                ],
            },
        }

    msg1 = _message(
        subject="Hello",
        from_header="Sender One <one@example.com>",
        date_header="Mon, 01 Jan 2024 12:00:00 +0000",
        html="<p>hi</p>",
    )
    msg2 = _message(
        subject="World",
        from_header="Sender Two <two@example.com>",
        date_header="Tue, 02 Jan 2024 12:00:00 +0000",
        html="<p>yo</p>",
    )

    # Fake service call chain.
    service = Mock()
    users = service.users.return_value
    messages = users.messages.return_value

    messages.list.return_value.execute.return_value = list_response
    def _get(*, userId: str, id: str, format: str):
        if id == "m1":
            return Mock(execute=Mock(return_value=msg1))
        if id == "m2":
            return Mock(execute=Mock(return_value=msg2))
        raise AssertionError(f"unexpected message id: {id}")

    messages.get.side_effect = _get

    session = AsyncMock()
    session.execute.return_value.scalars.return_value.all.return_value = ["m1"]

    with (
        patch("app.services.gmail.get_service", return_value=service),
        patch("app.services.gmail._dedup_processed_ids", return_value={"m1"}),
    ):
        from app.core.config import AppConfig
        from app.services import gmail

        config = AppConfig()
        emails = await gmail.fetch_unprocessed_emails(config=config, session=session)

    assert len(emails) == 1
    e = emails[0]
    assert e.email_id == "m2"
    assert e.subject == "World"
    assert e.sender_name == "Sender Two"
    assert e.sender_email == "two@example.com"
    assert isinstance(e.date, datetime)
    assert e.raw_html == "<p>yo</p>"


@pytest.mark.asyncio
async def test_fetch_unprocessed_emails_returns_empty_list_when_none_remaining():
    service = Mock()
    users = service.users.return_value
    messages = users.messages.return_value
    messages.list.return_value.execute.return_value = {"messages": [{"id": "m1"}]}
    messages.get.return_value.execute.return_value = {
        "id": "m1",
        "payload": {"headers": [], "mimeType": "text/html", "body": {"data": ""}},
    }

    session = AsyncMock()

    with (
        patch("app.services.gmail.get_service", return_value=service),
        patch("app.services.gmail._dedup_processed_ids", return_value={"m1"}),
    ):
        from app.core.config import AppConfig
        from app.services import gmail

        emails = await gmail.fetch_unprocessed_emails(config=AppConfig(), session=session)

    assert emails == []

# placeholder

