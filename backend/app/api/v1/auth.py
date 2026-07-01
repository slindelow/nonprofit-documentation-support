"""Auth routes — thin wrapper around Supabase Auth.

Sign-up and login are handled client-side via the Supabase JS SDK.
These endpoints handle server-side concerns: org creation on first sign-up,
invitation acceptance, and session validation.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.models.user import Invitation, User, UserRole

router = APIRouter()


class OrgCreateRequest(BaseModel):
    org_name: str
    full_name: str | None = None


class InviteRequest(BaseModel):
    email: EmailStr
    role: UserRole


class AcceptInviteRequest(BaseModel):
    token: str
    full_name: str | None = None


@router.post("/setup-org", summary="Create org for a newly signed-up user")
async def setup_org(
    body: OrgCreateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """
    Called immediately after a user signs up via Supabase Auth.
    Creates the Org record and assigns the user as owner.
    """
    # Implementation: create Org, create User with role=owner, set org context
    return {"status": "not_implemented"}


@router.post("/invite", summary="Invite a team member by email")
async def invite_member(
    body: InviteRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """Creates an Invitation record and sends an email via Resend."""
    return {"status": "not_implemented"}


@router.post("/accept-invite/{token}", summary="Accept a team invitation")
async def accept_invite(token: str, body: AcceptInviteRequest):
    """Validates the token, creates the User record, marks invitation accepted."""
    return {"status": "not_implemented"}
