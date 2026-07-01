import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, new_uuid


class Grant(Base, TimestampMixin):
    """Shared grant record fetched from discovery sources. Not org-specific."""

    __tablename__ = "grants"
    __table_args__ = (UniqueConstraint("source", "external_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # grantconnect | ...
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    funder_name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    eligibility: Mapped[str | None] = mapped_column(Text)
    funding_min: Mapped[float | None] = mapped_column(Numeric(12, 2))
    funding_max: Mapped[float | None] = mapped_column(Numeric(12, 2))
    open_date: Mapped[date | None] = mapped_column(Date)
    close_date: Mapped[date | None] = mapped_column(Date)
    categories: Mapped[list | None] = mapped_column(ARRAY(String))
    state_territory: Mapped[list | None] = mapped_column(ARRAY(String))
    raw_data: Mapped[dict | None] = mapped_column(JSONB)
    last_fetched_at: Mapped[str | None] = mapped_column()


class OrgGrant(Base, TimestampMixin):
    """Per-org relevance scoring and pipeline status for a grant."""

    __tablename__ = "org_grants"
    __table_args__ = (UniqueConstraint("org_id", "grant_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orgs.id"), nullable=False)
    grant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("grants.id"), nullable=False)
    relevance_score: Mapped[float | None] = mapped_column()
    relevance_reasoning: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30),
        default="discovered",
        nullable=False,
    )
    # Status values: discovered | saved | applying | submitted | awarded | declined | not_relevant
    pinned: Mapped[bool] = mapped_column(default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
