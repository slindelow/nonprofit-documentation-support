import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class ComplianceMilestone(Base, TimestampMixin):
    __tablename__ = "compliance_milestones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False
    )
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=False)
    milestone_type: Mapped[str | None] = mapped_column(String(50))
    # Types: progress_report | acquittal | financial_statement | audit | invoice
    title: Mapped[str | None] = mapped_column(String(255))
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    completed_at: Mapped[str | None] = mapped_column()
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    # Status: pending | in_progress | submitted | overdue


class Report(Base, TimestampMixin):
    """Progress or acquittal report drafts."""

    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    milestone_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("compliance_milestones.id")
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False
    )
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=False)
    report_type: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[dict | None] = mapped_column(JSONB)  # Tiptap JSON
    content_text: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    submitted_at: Mapped[str | None] = mapped_column()
