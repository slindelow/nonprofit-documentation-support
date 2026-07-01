from contextvars import ContextVar
from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Per-request tenant context — set by auth dependency, read by services
current_org_id: ContextVar[UUID | None] = ContextVar("current_org_id", default=None)


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Clears the tenant context var at the start of each request.

    The actual org_id is set later by the get_current_user dependency
    once the JWT is validated and the user record is fetched.
    """

    async def dispatch(self, request: Request, call_next):
        token = current_org_id.set(None)
        try:
            response = await call_next(request)
        finally:
            current_org_id.reset(token)
        return response


def set_org_context(org_id: UUID) -> None:
    current_org_id.set(org_id)


def get_org_context() -> UUID:
    org_id = current_org_id.get()
    if org_id is None:
        raise RuntimeError("Org context not set — called outside of authenticated request")
    return org_id
