"""
Compliance parsing and report generation tasks.

Workflow: workflows/compliance_check.md
"""

from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=2)
def parse_grant_agreement(self, application_id: str, org_id: str, storage_path: str):
    """
    Runs ComplianceAgent on an uploaded grant agreement PDF.

    Steps:
    1. Extract text via tools/knowledge_base/extract_text.py (reuses skills/SKILL (5).md)
    2. Call Claude to extract: reporting dates, milestones, acquittal requirements
    3. Create compliance_milestones rows
    4. Notify org admin
    """
    try:
        pass
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task
def generate_report_draft(milestone_id: str, org_id: str):
    """
    Generates a progress or acquittal report draft using ReportWriterAgent.
    Reuses RAG against knowledge_chunks + milestone context.
    """
    pass
