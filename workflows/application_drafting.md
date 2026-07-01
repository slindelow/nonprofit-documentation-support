# Workflow: Application Draft Generation

## Objective
Generate a complete grant application draft using the org's knowledge base (RAG) and the grant's requirements. Produce a human-reviewable Tiptap JSON document.

## Trigger
- User clicks "Generate Draft" on an application record
- POST `/api/v1/applications/{id}/generate-draft`
- Enqueues `app.tasks.writing_tasks.generate_application_draft`

## Required Inputs
- `application_id` — must have a linked `grant_id`
- `org_id` — must have knowledge base documents processed (chunks with embeddings)
- Grant requirements — extracted from `grants.description`, `grants.eligibility`, and `grants.raw_data`
- Org profile — from `orgs` table: name, mission (from knowledge base), focus areas, tone of voice

## Pre-conditions
- At least 1 `knowledge_document` must exist for the org with `processed_at` not null
- `knowledge_chunks` must exist with non-null `embedding` values

## Steps

### Step 1: Load and parse grant requirements
```
Input: grant record from database
Output: list of sections with prompts
```
- Extract the grant's required sections from `raw_data` or description
- If sections are not machine-readable: use Claude to identify sections from free text
- Example sections: Organisation Overview, Project Description, Community Need, Budget Justification, Outcomes and Evaluation, Team Qualifications

### Step 2: RAG retrieval per section
```
Run: app/services/rag.py:retrieve_chunks()
Input: section prompt, org_id, top_k=5
Output: list of relevant knowledge chunks
```
- For each section, embed the section prompt
- Query `knowledge_chunks` using pgvector cosine similarity
- Boost `doc_type = 'past_application'` chunks (weight higher in ranking)
- Log similarity scores for debugging

### Step 3: Generate section content with Claude
```
For each section:
    System prompt: "You are a grant writer for {org_name}. Write in this style: {tone_of_voice}.
                    Use the organisation's own words and evidence where possible."
    User prompt: "Write the '{section_name}' section for the {grant_title} application.
                  Grant requirement: {section_requirement}
                  Relevant organisation context:
                  {chunk_1_text}
                  {chunk_2_text}
                  ...
                  Write 2-4 paragraphs. Be specific and evidence-based."
```
- Model: `claude-opus-4-6`
- Temperature: 0.3 (consistent, professional tone)
- Stream tokens back section by section via Redis pub/sub → SSE to frontend
- Log `prompt_tokens` and `completion_tokens` per section for usage tracking

### Step 4: Assemble Tiptap document
```
Input: list of (section_name, generated_text) pairs
Output: Tiptap JSON document
```
- Structure: heading for each section, paragraph nodes for content
- Include a "Budget" section placeholder (AI cannot generate exact budget figures)
- Add a draft watermark heading: "AI DRAFT — Requires review before submission"

### Step 5: Save draft and update application status
```
INSERT INTO application_drafts:
    version = max(existing versions) + 1
    content = Tiptap JSON
    content_text = plain text extract
    generated_by = 'ai'
    ai_model = 'claude-opus-4-6'
    prompt_tokens / completion_tokens = totals

UPDATE applications SET status = 'in_review'

Notify via Supabase Realtime: {event: 'draft_ready', application_id: ...}
```

## Expected Outputs
- One `application_drafts` row with `generated_by = 'ai'`
- Application status changed to `in_review`
- Real-time notification to the frontend
- SSE stream complete

## Human-in-the-Loop Gate
After this workflow completes, the application CANNOT be submitted until:
1. A human reviews and edits the draft in the Tiptap editor
2. An `application_approvals` record with `stage = 'draft_approved'` is created
3. (Optional) An exec sign-off approval: `stage = 'exec_sign_off'`
4. Final `stage = 'ready_to_submit'` approval unlocks the Submit button

## Error Handling
- Claude API error mid-generation: save partial draft with error marker, notify user
- Empty knowledge base: return error "Please upload at least one document to your knowledge base before generating a draft"
- RAG retrieval returns 0 chunks: proceed with org profile only (lower quality output), flag in draft with a warning banner
- Application already has a draft in `in_review`: ask user to confirm overwrite before generating a new version

## Quality Notes
- Draft quality is directly proportional to knowledge base quality
- Encourage orgs to upload past successful applications (doc_type = 'past_application') — these are the highest-signal documents
- The `tone_of_voice` field on the org profile significantly improves output consistency
- Budget sections should always be manually completed — never trust AI-generated budget figures

## Related Files
- `app/services/rag.py`
- `app/agents/writer.py`
- `app/tasks/writing_tasks.py`
- `skills/SKILL (6).md` — doc-coauthoring workflow (conceptual model for this workflow)
