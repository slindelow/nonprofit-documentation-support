# Workflow: Compliance Parsing and Milestone Tracking

## Objective
Parse an awarded grant's agreement document to extract all reporting obligations, create compliance milestones, and monitor them for approaching deadlines.

## Trigger
- User uploads a grant agreement PDF via POST `/api/v1/compliance/{application_id}/parse-agreement`
- Enqueues `app.tasks.compliance_tasks.parse_grant_agreement`

## Required Inputs
- Uploaded grant agreement PDF (stored in Supabase Storage)
- `application_id` — must have `status = 'awarded'`
- `org_id`

## Steps

### Step 1: Extract text from grant agreement PDF
```
Run: tools/knowledge_base/extract_text.py
Input: storage_path of grant agreement PDF
Output: full text string
```
- Use `pdfplumber` for text extraction (handles columns and tables better than pypdf)
- See `skills/SKILL (5).md` for the correct extraction approach
- If text extraction returns empty (scanned PDF): run OCR via `pytesseract`
- Clean extracted text: remove headers/footers, page numbers, excessive whitespace

### Step 2: Extract milestones with Claude
```
System prompt: "You are extracting grant compliance obligations from a grant agreement.
               Return a JSON array of milestones."

User prompt: "Extract all reporting obligations, milestones, and acquittal requirements
             from this grant agreement. For each obligation, return:
             {
               milestone_type: 'progress_report' | 'acquittal' | 'financial_statement' | 'audit' | 'invoice' | 'other',
               title: string,
               due_date: 'YYYY-MM-DD' or 'relative: X months after grant end',
               description: string
             }

             Grant agreement text:
             {extracted_text}"
```
- Parse the returned JSON array
- For relative dates (e.g. "within 30 days of project completion"): store as a note in `title` field and set `due_date` manually flagged for human review
- Flag any ambiguous dates for manual review

### Step 3: Create compliance_milestones rows
```
For each extracted milestone:
    INSERT INTO compliance_milestones:
        application_id, org_id
        milestone_type
        title
        due_date
        status = 'pending'
```
- If the same milestone was already created (reprocessing): upsert on (application_id, milestone_type, due_date)

### Step 4: Notify org admin
```
Create in-app notification: "Grant agreement parsed. {N} milestones created."
Email summary to org admin via Resend
```

## Ongoing Monitoring (DeadlineAgent)
After milestones are created, the DeadlineAgent (`deadline_tasks.check_deadlines`) handles ongoing monitoring:
- Lead time alerts: 30, 14, 7, 3, 1 days before each milestone due date
- Mark milestones `overdue` if `due_date < today` and `status != 'submitted'`
- Escalate overdue milestones via email to org admin

## Report Generation (Sub-workflow)
When a milestone is due, the user can trigger report generation:
- POST `/api/v1/compliance/milestones/{id}/generate-report`
- Runs `compliance_tasks.generate_report_draft`
- Uses RAG + milestone context to draft a progress or acquittal report
- Follows the same human-in-the-loop review process as application drafts

## Expected Outputs
- `compliance_milestones` rows for each obligation
- In-app notification
- Email summary

## Error Handling
- PDF cannot be parsed (corrupted file): return error to user, ask to re-upload
- Claude returns invalid JSON: retry once with stricter prompt, fall back to empty milestones list with manual entry prompt
- Ambiguous dates: insert milestone with `due_date = null` and `status = 'pending'`, flag for manual entry in UI

## Related Files
- `tools/knowledge_base/extract_text.py`
- `app/agents/compliance.py`
- `app/tasks/compliance_tasks.py`
- `skills/SKILL (5).md` — PDF extraction reference
