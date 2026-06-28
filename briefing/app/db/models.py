"""SQLAlchemy ORM models."""

# Implements ARCH-003

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    depth: Mapped[str] = mapped_column(String)
    section_config: Mapped[dict] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(String, nullable=True)


class BriefingOutput(Base):
    __tablename__ = "briefing_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("runs.id"))
    markdown_path: Mapped[str] = mapped_column(String)
    audio_path: Mapped[str | None] = mapped_column(String, nullable=True)


class ProcessedEmail(Base):
    __tablename__ = "processed_emails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_id: Mapped[str] = mapped_column(String, unique=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("runs.id"))
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

