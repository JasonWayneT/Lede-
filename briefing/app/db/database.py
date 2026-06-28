"""Async SQLAlchemy engine + session factory."""

# Implements ARCH-003

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.models import Base

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def build_sqlite_db_url(data_dir: Path) -> str:
    db_path = data_dir / "briefing.db"
    return f"sqlite+aiosqlite:///{db_path}"


def init_engine(db_url: str) -> None:
    global _engine, _sessionmaker

    _engine = create_async_engine(db_url, echo=False)
    _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine(db_url) first.")
    return _engine


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    if _sessionmaker is None:
        raise RuntimeError("Sessionmaker not initialized. Call init_engine(db_url) first.")

    async with _sessionmaker() as session:
        yield session


async def init_db() -> None:
    engine = get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

