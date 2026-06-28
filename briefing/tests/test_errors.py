import pytest


def test_error_code_constants_have_expected_values():
    from app.core.errors import (
        AUTH_ERROR,
        NOT_FOUND,
        PROVIDER_UNAVAILABLE,
        STAGE_FAILED,
        VALIDATION_ERROR,
    )

    assert STAGE_FAILED == "STAGE_FAILED"
    assert AUTH_ERROR == "AUTH_ERROR"
    assert PROVIDER_UNAVAILABLE == "PROVIDER_UNAVAILABLE"
    assert VALIDATION_ERROR == "VALIDATION_ERROR"
    assert NOT_FOUND == "NOT_FOUND"


def test_stage_error_attributes_and_str():
    from app.core.errors import StageError, STAGE_FAILED

    exc = StageError("embed", "FAISS index failed", retryable=True, code=STAGE_FAILED)
    assert exc.stage_name == "embed"
    assert exc.message == "FAISS index failed"
    assert exc.retryable is True
    assert exc.code == "STAGE_FAILED"
    assert str(exc) == "[embed] FAISS index failed"


def test_stage_error_defaults():
    from app.core.errors import StageError, STAGE_FAILED

    exc = StageError("x", "y")
    assert exc.retryable is True
    assert exc.code == STAGE_FAILED


@pytest.mark.asyncio
async def test_stage_error_exception_handler_returns_envelope():
    from app.core.errors import StageError
    from app.main import app

    @app.get("/_test_stage_error")
    async def _raise():
        raise StageError("select", "boom", retryable=False)

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/_test_stage_error")

    assert resp.status_code == 500
    body = resp.json()
    assert body["code"]
    assert body["stage"] == "select"
    assert body["retryable"] is False
    assert "boom" in body["error"]

