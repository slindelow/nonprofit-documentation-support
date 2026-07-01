import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from app.models.user import User


class Org(Base, TimestampMixin):
    __tablename__ = "orgs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    abn: Mapped[str | None] = mapped_column(String(11))
    acnc_number: Mapped[str | None] = mapped_column(String(20))
    subscription_tier: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255))
    data_region: Mapped[str] = mapped_column(String(20), default="ap-southeast-2", nullable=False)

    # Settings stored as JSONB
    focus_areas: Mapped[list | None] = mapped_column(default=None)
    state_territory: Mapped[str | None] = mapped_column(String(10))
    org_type: Mapped[str | None] = mapped_column(String(50))  # association | company | indigenous | trust
    revenue_range: Mapped[str | None] = mapped_column(String(50))
    tone_of_voice: Mapped[str | None] = mapped_column(Text)  # Used in AI system prompts

    users: Mapped[list["User"]] = relationship("User", back_populates="org")
