# Workflow: Grant Discovery

## Objective
Fetch new grant opportunities from all registered sources, upsert them into the database, and score each grant's relevance for every active organisation.

## Trigger
- **Scheduled**: Celery beat, every 6 hours (`app.tasks.discovery_tasks.fetch_and_score_grants`)
- **On-demand**: After a new org completes onboarding (`score_grants_for_org` task)

## Required Inputs
- Registered grant sources (`app.services.grant_sources.registry.GRANT_SOURCE_REGISTRY`)
- Last-run timestamp (stored in Redis key `grantconnect:last_fetched`)
- Org profiles (from `orgs` table — must have `focus_areas`, `state_territory`, `org_type` set)

## Steps

### Step 1: Fetch from each registered source
```
For each source in GRANT_SOURCE_REGISTRY:
    Run: tools/grant_connect/fetch_grants.py (or equivalent for source)
    Input: since = last_fetched timestamp
    Output: list of RawGrant objects
```
- Use incremental fetch (`since` param) — do not re-fetch all grants on every run
- Implement exponential backoff with jitter for rate limit / 429 errors
- If a source fails, log the error and continue with remaining sources (partial failure is acceptable)
- Update `grantconnect:last_fetched` Redis key after a successful run

### Step 2: Upsert into `grants` table
```
Run: tools/grant_connect/parse_grants.py
Input: list of RawGrant objects
Output: list of (grant_id, is_new)
```
- Upsert on `(source, external_id)` unique constraint
- Only update `last_fetched_at` and `raw_data` for existing grants (do not overwrite scored data)
- New grants: insert all fields

### Step 3: Score relevance for each org (Phase 2 — AI scoring)
```
For each org with status = 'active' and onboarding complete:
    Run: tools/grant_connect/match_grants.py
    Input: org profile, list of new grant_ids
    Output: list of (grant_id, relevance_score, reasoning)
```
- Build org context: mission statement, focus areas, state, org type, tone of voice
- For each new grant: call Claude with org context + grant description
- Prompt: "Score 0.0–1.0 how relevant this grant is for this organisation. Return JSON: {score: float, reasoning: string (max 2 sentences)}"
- Write results to `org_grants` table
- **Phase 1**: Skip scoring. Insert `org_grants` rows with `relevance_score = null`, `status = 'discovered'`

### Step 4: Notify on high-score matches
```
Threshold: relevance_score >= 0.7
For matching org_grants:
    - Create in-app notification record
    - If org has email notifications enabled: send via Resend
```

## Expected Outputs
- New rows in `grants` table
- Rows in `org_grants` per org per new grant
- Notifications for high-relevance matches

## Error Handling
- GrantConnect API down: log error, retry task in 30 minutes, fall back to cached grant list in UI
- Rate limit (429): exponential backoff — wait 2^n seconds, max 5 retries
- Claude API error during scoring: skip scoring for that batch, retry at next scheduled run
- Database write failure: rollback transaction, log, alert via Sentry

## Known Constraints (update as discovered)
- GrantConnect `LastModifiedFrom` param format: `YYYY-MM-DDTHH:MM:SS` (no timezone suffix)
- GrantConnect returns max 100 records per page — always paginate
- GrantConnect field names: `GoId`, `GoTitle`, `AgencyName`, `ClosingDate`, `OpeningDate`, `FundingMinimum`, `FundingMaximum`

## Related Files
- `tools/grant_connect/fetch_grants.py`
- `tools/grant_connect/parse_grants.py`
- `tools/grant_connect/match_grants.py`
- `app/services/grant_sources/grantconnect.py`
- `app/services/grant_sources/registry.py`
- `app/tasks/discovery_tasks.py`
