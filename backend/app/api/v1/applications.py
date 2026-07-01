from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.security import get_current_user_id

router = APIRouter()


class ApplicationCreateRequest(BaseModel):
    grant_id: UUID
    title: str | None = None
    requested_amount: float | None = None
    portal_url: str | None = None
    portal_type: str | None = None
    due_date: str | None = None


class ApplicationUpdateRequest(BaseModel):
    title: str | None = None
    status: str | None = None
    assigned_to: UUID | None = None
    requested_amount: float | None = None
    portal_url: str | None = None
    portal_type: str | None = None
    due_date: str | None = None


@router.get("", summary="List applications (Kanban pipeline)")
async def list_applications(user_id: Annotated[UUID, Depends(get_current_user_id)]):
    return {"status": "not_implemented"}


@router.post("", summary="Create a new application")
async def create_application(
    body: ApplicationCreateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}


@router.get("/{application_id}", summary="Get application detail")
async def get_application(
    application_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}


@router.patch("/{application_id}", summary="Update application")
async def update_application(
    application_id: UUID,
    body: ApplicationUpdateRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}


@router.post("/{application_id}/generate-draft", summary="Enqueue AI draft generation")
async def generate_draft(
    application_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """
    Enqueues a Celery task that runs the ApplicationWriterAgent.
    Returns a task_id for polling status.
    Draft generation streams progress via SSE — see GET .../draft-stream.
    """
    return {"status": "not_implemented", "task_id": None}


@router.get("/{application_id}/drafts", summary="List all draft versions")
async def list_drafts(
    application_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}


@router.post("/{application_id}/drafts/{version}/approve", summary="Approve a draft version")
async def approve_draft(
    application_id: UUID,
    version: int,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """Creates an application_approvals record with stage='draft_approved'."""
    return {"status": "not_implemented"}


@router.post("/{application_id}/submit", summary="Enqueue Playwright portal submission")
async def submit_application(
    application_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """
    Only available when application_approvals has stage='ready_to_submit'.
    Starts a Playwright session and returns a session_id for the live preview.
    """
    return {"status": "not_implemented", "session_id": None}
