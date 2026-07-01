from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "grantflow",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.discovery_tasks",
        "app.tasks.writing_tasks",
        "app.tasks.compliance_tasks",
        "app.tasks.deadline_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Australia/Sydney",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Scheduled tasks (Celery beat)
celery_app.conf.beat_schedule = {
    # Fetch new grants from all sources every 6 hours
    "fetch-grants-every-6h": {
        "task": "app.tasks.discovery_tasks.fetch_and_score_grants",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    # Check deadlines and send reminders daily at 8am AEST
    "deadline-check-daily": {
        "task": "app.tasks.deadline_tasks.check_deadlines",
        "schedule": crontab(minute=0, hour=8),
    },
    # Weekly digest every Monday at 8am AEST
    "weekly-digest-monday": {
        "task": "app.tasks.deadline_tasks.send_weekly_digest",
        "schedule": crontab(minute=0, hour=8, day_of_week=1),
    },
}
