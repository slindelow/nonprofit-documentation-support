from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditEvent


async def log_event(
    db: AsyncSession,
    org_id: UUID,
    entity_type: str,
    entity_id: UUID,
    action: str,
    user_id: UUID | None = None,
    diff: dict[str, Any] | None = None,
) -> None:
    """Append an immutable audit record. Never update or delete these rows."""
    event = AuditEvent(
        org_id=org_id,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        diff=diff,
    )
    db.add(event)
    # Caller is responsible for commit
