from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import get_current_user_id

router = APIRouter()


class OrgUpdateRequest(BaseModel):
    name: str | None = None
    abn: str | None = None
    acnc_number: str | None = None
    focus_areas: list[str] | None = None
    state_territory: str | None = None
    org_type: str | None = None
    revenue_range: str | None = None
    tone_of_voice: str | None = None


@router.get("/me", summary="Get current org profile")
async def get_org(user_id: Annotated[UUID, Depends(get_current_user_id)]):
    return {"status": "not_implemented"}


@router.patch("/me", summary="Update org profile")
async def update_org(
    body: OrgUpdateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}


@router.get("/members", summary="List org team members")
async def list_members(user_id: Annotated[UUID, Depends(get_current_user_id)]):
    return {"status": "not_implemented"}


@router.delete("/members/{member_id}", summary="Remove a team member")
async def remove_member(
    member_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}
