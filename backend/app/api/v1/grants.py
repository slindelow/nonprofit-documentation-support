from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user_id

router = APIRouter()


@router.get("", summary="Discovery feed — list grants with relevance scores")
async def list_grants(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    status: str | None = Query(None),
    min_score: float | None = Query(None, ge=0, le=1),
    category: str | None = Query(None),
    state: str | None = Query(None),
    close_after: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Returns grants scored for the current org, ordered by relevance."""
    return {"status": "not_implemented"}


@router.get("/{grant_id}", summary="Get a single grant detail")
async def get_grant(
    grant_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}


@router.post("/{grant_id}/save", summary="Save a grant to the pipeline")
async def save_grant(
    grant_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}


@router.delete("/{grant_id}/save", summary="Remove a grant from saved")
async def unsave_grant(
    grant_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}
