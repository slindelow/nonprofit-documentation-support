"""
Deadline monitoring and notification tasks.

Workflow: workflows/deadline_monitoring.md
"""

from app.tasks.celery_app import celery_app


@celery_app.task
def check_deadlines():
    """
    Runs daily at 8am AEST. Checks all upcoming deadlines across:
    - grants.close_date (for unsaved/discovered grants)
    - applications.due_date
    - compliance_milestones.due_date

    Lead times: 30, 14, 7, 3, 1 days before deadline.
    Sends email via Resend + in-app notification.

    Nudge: if a grant closes in 7 days with no application started,
    sends a "Start this application?" prompt.
    """
    pass


@celery_app.task
def send_weekly_digest():
    """
    Runs every Monday at 8am AEST.
    Sends a digest email to each org admin with:
    - Grants closing this week
    - Upcoming compliance milestones
    - Applications in review
    """
    pass
