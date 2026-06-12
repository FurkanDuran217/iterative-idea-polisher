from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tracking_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    current_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    versions: Mapped[list[TextVersion]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="TextVersion.version_number",
    )
    audits: Mapped[list[Audit]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="Audit.created_at",
    )
    llm_calls: Mapped[list[LLMCall]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="LLMCall.created_at",
    )


class TextVersion(Base):
    __tablename__ = "text_versions"
    __table_args__ = (UniqueConstraint("run_id", "version_number"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("pipeline_runs.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_step: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    run: Mapped[PipelineRun] = relationship(back_populates="versions")


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("pipeline_runs.id"), index=True)
    iteration: Mapped[int] = mapped_column(Integer, nullable=False)
    suggestions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    needs_polish: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    run: Mapped[PipelineRun] = relationship(back_populates="audits")


class LLMCall(Base):
    __tablename__ = "llm_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("pipeline_runs.id"), index=True)
    input_text_version_id: Mapped[int | None] = mapped_column(ForeignKey("text_versions.id"))
    output_text_version_id: Mapped[int | None] = mapped_column(ForeignKey("text_versions.id"))
    iteration: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(128))
    prompt_type: Mapped[str] = mapped_column(String(32), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(32), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    request_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    provider_params: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    raw_output: Mapped[str | None] = mapped_column(Text)
    parsed_output: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(JSON)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    run: Mapped[PipelineRun] = relationship(back_populates="llm_calls")
