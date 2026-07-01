"""
Application draft generation tasks.

Workflow: workflows/application_drafting.md
"""

from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def generate_application_draft(self, application_id: str, org_id: str, user_id: str):
    """
    Runs ApplicationWriterAgent to produce a draft.

    Steps:
    1. Load application + grant requirements
    2. RAG: retrieve top-k chunks from knowledge_chunks for each section
    3. Call Claude API section by section
    4. Save ApplicationDraft version N with generated_by='ai'
    5. Update application status to 'in_review'
    6. Notify assigned user via Supabase Realtime

    Streams SSE progress updates via Redis pub/sub channel.
    """
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task
def process_knowledge_document(document_id: str, org_id: str):
    """
    Processes an uploaded document:
    1. Extract text (PDF via pdfplumber, DOCX via python-docx)
    2. Chunk into 512-token segments with 64-token overlap
    3. Embed each chunk via OpenAI text-embedding-3-small
    4. Store in knowledge_chunks with embedding

    Uses tools/knowledge_base/ scripts.
    """
    pass
