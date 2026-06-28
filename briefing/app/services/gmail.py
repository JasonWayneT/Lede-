"""Gmail API wrapper."""

# Implements FR-001, FR-002, FR-003

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path
from typing import Any

from google.auth import exceptions as google_auth_exceptions
from google.auth.transport.requests import Request
from google.oauth2 import credentials as google_credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import credentials as credential_store
from app.core.config import AppConfig
from app.core.errors import AUTH_ERROR, StageError
from app.db.models import ProcessedEmail

GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"


@dataclass(frozen=True)
class GmailEmail:
    email_id: str
    subject: str
    sender_name: str
    sender_email: str
    date: datetime
    raw_html: str


OAUTH_CALLBACK_URI = "http://localhost:8001/oauth/callback"


def get_credentials_path(config: AppConfig) -> Path:
    _app_root = Path(__file__).parent.parent  # briefing/app/
    candidates = [
        config.data_dir / "credentials.json",
        _app_root.parent / "data" / "credentials.json",  # briefing/data/
        _app_root.parent / "credentials.json",             # briefing/
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "credentials.json not found. Place it in briefing/data/ or the briefing/ root."
    )


def build_auth_url(config: AppConfig) -> str:
    """Return the Google OAuth consent URL to redirect the user to."""
    path = get_credentials_path(config)
    flow = Flow.from_client_secrets_file(
        str(path),
        scopes=[GMAIL_READONLY_SCOPE],
        redirect_uri=OAUTH_CALLBACK_URI,
    )
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return auth_url


def exchange_code(code: str, config: AppConfig) -> None:
    """Exchange the OAuth callback code for a token and store it."""
    path = get_credentials_path(config)
    flow = Flow.from_client_secrets_file(
        str(path),
        scopes=[GMAIL_READONLY_SCOPE],
        redirect_uri=OAUTH_CALLBACK_URI,
    )
    flow.fetch_token(code=code)
    credential_store.set(credential_store.GMAIL_OAUTH_TOKEN, flow.credentials.to_json())


def get_service(*, stage_name: str) -> Any:
    token_json = credential_store.get(credential_store.GMAIL_OAUTH_TOKEN)
    if not token_json:
        raise StageError(
            stage_name,
            "Gmail not authorized. Re-authorize from Settings.",
            retryable=False,
            code=AUTH_ERROR,
        )

    try:
        token_info = json.loads(token_json)
        creds = google_credentials.Credentials.from_authorized_user_info(token_info)

        if getattr(creds, "expired", False) and getattr(creds, "refresh_token", None):
            creds.refresh(Request())

        return build("gmail", "v1", credentials=creds)
    except (google_auth_exceptions.TransportError, google_auth_exceptions.RefreshError) as e:
        raise StageError(
            stage_name,
            "Gmail token invalid or revoked. Re-authorize from Settings.",
            retryable=False,
            code=AUTH_ERROR,
        ) from e


async def fetch_unprocessed_emails(*, config: AppConfig, session: AsyncSession) -> list[GmailEmail]:
    """Fetch emails from a label and filter out already-processed message IDs."""
    service = get_service(stage_name="ingest")

    try:
        message_ids: list[str] = []
        page_token: str | None = None
        while True:
            req = service.users().messages().list(
                userId="me",
                labelIds=[config.gmail_label],
                pageToken=page_token,
            )
            resp = req.execute()
            message_ids.extend([m["id"] for m in resp.get("messages", []) if "id" in m])
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        processed_ids = await _dedup_processed_ids(session=session, message_ids=message_ids)

        emails: list[GmailEmail] = []
        for msg_id in message_ids:
            if msg_id in processed_ids:
                continue

            msg = (
                service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )
            emails.append(_parse_message(msg_id=msg_id, msg=msg))

        return emails
    except HttpError as e:
        raise StageError("ingest", f"Gmail API error: {e}", retryable=True) from e
    except OSError as e:
        raise StageError("ingest", f"Network error talking to Gmail: {e}", retryable=True) from e


async def _dedup_processed_ids(*, session: AsyncSession, message_ids: list[str]) -> set[str]:
    if not message_ids:
        return set()

    result = await session.execute(
        select(ProcessedEmail.email_id).where(ProcessedEmail.email_id.in_(message_ids))
    )
    return set(result.scalars().all())


def _parse_message(*, msg_id: str, msg: dict[str, Any]) -> GmailEmail:
    headers = {h["name"].lower(): h.get("value", "") for h in msg.get("payload", {}).get("headers", []) if "name" in h}
    subject = headers.get("subject", "")
    from_header = headers.get("from", "")
    date_header = headers.get("date", "")

    sender_name, sender_email = parseaddr(from_header)

    try:
        dt = parsedate_to_datetime(date_header)
    except Exception:
        dt = datetime.utcnow()

    raw_html = _extract_html_from_payload(msg.get("payload", {}))

    return GmailEmail(
        email_id=msg_id,
        subject=subject,
        sender_name=sender_name,
        sender_email=sender_email,
        date=dt,
        raw_html=raw_html,
    )


def _extract_html_from_payload(payload: dict[str, Any]) -> str:
    mime_type = payload.get("mimeType")
    if mime_type == "text/html":
        return _decode_body(payload.get("body", {}))

    for part in payload.get("parts", []) or []:
        html = _extract_html_from_payload(part)
        if html:
            return html

    if mime_type == "text/plain":
        # We intentionally prefer HTML when present; plain text is a fallback.
        return _decode_body(payload.get("body", {}))

    return ""


def _decode_body(body: dict[str, Any]) -> str:
    data = body.get("data")
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data + "===").decode("utf-8", errors="replace")
    except Exception:
        return ""

