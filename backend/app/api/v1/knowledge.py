from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.security import get_current_user_id

router = APIRouter()


@router.get("", summary="List knowledge base documents")
async def list_documents(user_id: Annotated[UUID, Depends(get_current_user_id)]):
    return {"status": "not_implemented"}


@router.post("/upload", summary="Upload a document to the knowledge base")
async def upload_document(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    file: UploadFile = File(...),
    doc_type: str = Form(...),
):
    """
    Accepts PDF, DOCX, or TXT.
    1. Saves to Supabase Storage under /{org_id}/documents/
    2. Enqueues a Celery task for text extraction + chunking + embedding
    3. Returns document_id immediately; processing is async
    """
    return {"status": "not_implemented", "document_id": None}


@router.delete("/{document_id}", summary="Delete a knowledge base document")
async def delete_document(
    document_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """Deletes the document record, all its chunks, and the storage file."""
    return {"status": "not_implemented"}
