from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.security import get_current_user_id

router = APIRouter()


@router.get("", summary="Compliance dashboard — all milestones across all applications")
async def compliance_dashboard(user_id: Annotated[UUID, Depends(get_current_user_id)]):
    return {"status": "not_implemented"}


@router.get("/{application_id}/milestones", summary="List milestones for an application")
async def list_milestones(
    application_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    return {"status": "not_implemented"}


@router.post("/{application_id}/parse-agreement", summary="Upload grant agreement PDF and extract milestones")
async def parse_agreement(
    application_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    file: UploadFile = File(...),
):
    """
    Extracts text from the grant agreement PDF using skills/SKILL (5).md approach,
    then runs ComplianceAgent to extract milestones and reporting obligations.
    """
    return {"status": "not_implemented"}


@router.get("/milestones/{milestone_id}/generate-report", summary="Generate a report draft for a milestone")
async def generate_report(
    milestone_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """Enqueues ReportWriterAgent task."""
    return {"status": "not_implemented"}
