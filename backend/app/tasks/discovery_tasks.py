"""
Grant discovery background tasks.

Workflow: workflows/grant_discovery.md
"""

from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_and_score_grants(self):
    """
    Fetches new grants from all registered sources and scores them
    for each org that has completed onboarding.

    Steps:
    1. Iterate GRANT_SOURCE_REGISTRY
    2. For each source, call fetch_new_grants(since=last_run)
    3. Upsert into grants table
    4. For each org, run DiscoveryAgent relevance scoring
    5. Notify orgs of high-scoring new grants (score > 0.7)
    """
    try:
        # TODO: implement in Phase 2 (AI scoring)
        # Phase 1: implement steps 1-3 (fetch + upsert only)
        pass
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task
def score_grants_for_org(org_id: str):
    """
    Scores all unscored grants for a specific org.
    Called after onboarding completes to populate the discovery feed immediately.
    """
    pass
