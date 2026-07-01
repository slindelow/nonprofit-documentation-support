# Workflow: Deadline Monitoring and Notification

## Objective
Proactively alert organisations about upcoming grant close dates, application deadlines, and compliance reporting obligations. Prevent missed deadlines.

## Triggers
- **Scheduled daily**: Celery beat, 8am AEST (`deadline_tasks.check_deadlines`)
- **Scheduled weekly**: Every Monday 8am AEST (`deadline_tasks.send_weekly_digest`)

## Deadline Sources (3 types)
1. `grants.close_date` — Grant application close dates (for saved/applying org_grants)
2. `applications.due_date` — Application submission deadlines set manually
3. `compliance_milestones.due_date` — Reporting/acquittal obligations

## Lead Time Schedule
Alert at these intervals before each deadline:
- 30 days — first heads-up
- 14 days — planning reminder
- 7 days — urgent action required
- 3 days — critical
- 1 day — final warning

Track which reminders have been sent per milestone to avoid duplicates (use `reminder_sent_at` JSONB array or a separate reminder_log table in future).

## Daily Check Steps

### Step 1: Query all upcoming deadlines
```sql
-- Grant close dates (org_grants where status IN ('saved', 'applying'))
SELECT og.org_id, g.id as grant_id, g.title, g.close_date as deadline,
       'grant_close' as deadline_type
FROM org_grants og
JOIN grants g ON g.id = og.grant_id
WHERE og.status IN ('saved', 'applying')
  AND g.close_date BETWEEN NOW() AND NOW() + INTERVAL '30 days'

UNION ALL

-- Application due dates
SELECT a.org_id, a.id, a.title, a.due_date as deadline, 'application_due'
FROM applications a
WHERE a.status NOT IN ('submitted', 'closed', 'awarded')
  AND a.due_date BETWEEN NOW() AND NOW() + INTERVAL '30 days'

UNION ALL

-- Compliance milestones
SELECT cm.org_id, cm.id, cm.title, cm.due_date as deadline, 'milestone_due'
FROM compliance_milestones cm
WHERE cm.status NOT IN ('submitted')
  AND cm.due_date BETWEEN NOW() AND NOW() + INTERVAL '30 days'
```

### Step 2: Filter to lead times that haven't been notified yet
For each deadline, check `days_until_deadline` against lead time schedule.
Only send notifications for lead times not yet recorded.

### Step 3: Send notifications
```
For each deadline requiring notification:
    - Create in-app notification record
    - If org email notifications enabled:
        Send email via Resend template
```

Email template variables: `{org_name}`, `{deadline_type}`, `{title}`, `{days_until}`, `{due_date}`, `{action_url}`

### Step 4: Nudge for unopened grants
```
SELECT g.*, og.*
FROM org_grants og
JOIN grants g ON g.id = og.grant_id
WHERE og.status = 'saved'
  AND g.close_date BETWEEN NOW() AND NOW() + INTERVAL '7 days'
  AND NOT EXISTS (
    SELECT 1 FROM applications a
    WHERE a.grant_id = g.id AND a.org_id = og.org_id
  )
```
Send nudge notification: "The {grant_title} closes in {N} days and you haven't started an application yet."

### Step 5: Mark milestones as overdue
```
UPDATE compliance_milestones
SET status = 'overdue'
WHERE due_date < NOW()::DATE
  AND status = 'pending'
```
Send escalation email to org admin for each newly overdue milestone.

## Weekly Digest Steps
Every Monday, send one email per org admin with:
- Grants closing this week (next 7 days)
- Compliance milestones due this month
- Applications currently in review awaiting approval
- Stats: applications submitted this month, funds applied for

## Expected Outputs
- In-app notification records
- Emails via Resend
- Overdue milestones status updated
- No duplicate notifications for same deadline + lead time combination

## Error Handling
- Resend API error: log failure, retry once, continue to next org (don't let one email failure block others)
- No contact email for org: log warning, skip email, create in-app notification only
- Task crashes mid-run: the next daily run will catch any missed notifications (idempotent checks)

## Related Files
- `app/tasks/deadline_tasks.py`
- `app/agents/deadline.py`
