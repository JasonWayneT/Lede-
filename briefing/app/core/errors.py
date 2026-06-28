"""Error types and error codes."""

# Implements ARCH-005

from __future__ import annotations

STAGE_FAILED = "STAGE_FAILED"
AUTH_ERROR = "AUTH_ERROR"
PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
VALIDATION_ERROR = "VALIDATION_ERROR"
NOT_FOUND = "NOT_FOUND"


class StageError(Exception):
    def __init__(
        self,
        stage_name: str,
        message: str,
        retryable: bool = True,
        code: str = STAGE_FAILED,
    ) -> None:
        super().__init__(message)
        self.stage_name = stage_name
        self.message = message
        self.retryable = retryable
        self.code = code

    def __str__(self) -> str:  # pragma: no cover
        return f"[{self.stage_name}] {self.message}"

