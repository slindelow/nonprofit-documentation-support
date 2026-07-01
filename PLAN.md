# GrantFlow AI — Product Strategy & Build Plan

## What this is

A multi-tenant SaaS platform for nonprofits to discover grant opportunities, generate AI-assisted application drafts, and manage post-award compliance reporting. Built on the WAT framework (Workflows, Agents, Tools).

---

## Current state

The scaffolding is solid. What exists:

- All data models defined (grants, applications, compliance, knowledge, users, orgs)
- All API routes declared — none implemented (all return `not_implemented`)
- All Celery tasks declared — none implemented (all `pass`)
- All frontend pages exist — all static shells with empty states
- 5 detailed workflows written
- `fetch_grants.py` and `grantconnect.py` service fully implemented
- `rag.py` (`embed_text` + `retrieve_chunks`) implemented
- Tool stubs for parse, match, extract, chunk, embed — partially written headers
- **Zero Alembic migrations exist** — the database schema has never been created

---

## Strategic considerations (challenge these before building)

### The codebase is already generic

The architecture is already multi-tenant — `org_id` on every table, `TenantContextMiddleware`, `UserRole`, org-scoped billing. The question isn't "how do we make it generic" — it already is. The real question is about product strategy and data.

### "Any nonprofit" is not a market

"Any nonprofit" has no TAM you can act on. You can't find, message, or sell to "any nonprofit." A beachhead is required: Australian nonprofits? Small community foundations? A specific sector (arts, housing, environmental)? The grant landscape is jurisdiction-specific regardless — GrantConnect only covers Australian federal grants.

### Grant discovery may not be the best entry point

Many nonprofits already know which funders they're targeting through board connections, sector networks, and prior relationships. Automated discovery may not be the actual bottleneck. The real pain is the writing and reporting — that's where development staff lose the most hours.

**Compliance as a better wedge:**
- Reporting, acquittal writing, milestone tracking — concrete, measurable time drain
- Clearer ROI: "avoid losing your funding due to a missed reporting deadline"
- Less competitive than discovery
- Doesn't depend on the data sourcing problem

### The data sourcing problem is the highest-risk assumption

You have one source: GrantConnect (~200–500 active federal grants at a time). "Any nonprofit" implies state/territory grants (no API, require scraping), private foundations (PDF on a website), corporate philanthropy (opaque, relationship-driven), and potentially international sources. The discovery feed is only as good as the data behind it. This is the biggest unresolved risk in the plan.

### The cold start problem is underestimated

A new org with zero knowledge base documents gets nothing useful from the AI. The entire draft quality depends on what they upload. What's the minimum viable knowledge base? Can you produce a useful draft from just an org profile and public information? The current design has no answer.

### Missing: eligibility pre-screening

Before spending 40+ hours writing an application, an org needs to know if they're actually eligible. The current flow generates a full draft with no eligibility check. A lightweight pre-screen ("here are 3 potential disqualifiers based on your profile") prevents wasted effort and would be a differentiator.

### Missing: funder relationship tracking

Grant success is heavily relationship-dependent. Which funders have you applied to before? What was the outcome? Who's your contact? There is no CRM layer for funder relationships, which is where experienced grant writers spend significant time.

### Missing: grant outcome feedback loop

Did this application get funded? For how much? Over time, this teaches the system which grants the org is likely to win — more useful than pure profile-match scoring.

### Playwright auto-fill is high-risk

A submission failure at the final step due to CAPTCHA, UI changes, session timeout, or bot detection is catastrophic. A simpler alternative: format the approved draft as a clean per-field copy-paste document with a submission checklist. Less impressive, much more reliable.

### Pricing model deserves scrutiny

$99–249/month is a significant ask for organizations with no recurring software budget. Grant writers at small nonprofits rarely have $3k/year procurement authority. Success-fee pricing (% of funded grants) aligns better with delivered value and removes upfront commitment — but creates a 3–6 month receivables lag. Decide before building billing.

### Data rights and privacy

Nonprofits upload financial statements, client impact data, board information. A data processing agreement, data residency decisions, and eventually SOC 2 are not optional for anything beyond very small orgs.

---

## Build plan

### Phase 1 — Foundation (nothing works without this)

**Database**
- Generate Alembic initial migration from existing models
- Enable pgvector extension in Postgres before migration runs

**Auth & Onboarding**
- `POST /auth/setup-org` — create Org + User in DB after Supabase signup
- `POST /auth/invite` + `POST /auth/accept-invite/{token}` — team member invitations via Resend
- Frontend login/signup pages (Supabase JS client)
- Onboarding page: org profile form (name, mission, focus areas, state, org type, tone of voice)

**Grant Discovery (Phase 1 — no AI)**
- Complete `parse_grants.py` — normalize RawGrant → DB row format
- Implement `fetch_and_score_grants` task — wire GrantConnectSource → parse → upsert + Redis `last_fetched` key
- Implement `GET /grants` — query `org_grants` joined to `grants` with filters + pagination
- Implement `POST /grants/{id}/save` and `DELETE /grants/{id}/save`

**Knowledge Base pipeline**
- Implement `extract_text.py` — pdfplumber + OCR fallback + DOCX support
- Implement `chunk_documents.py` — 512-token chunks with 64-token overlap
- Implement `embed_chunks.py` — OpenAI `text-embedding-3-small` → store in `knowledge_chunks`
- Implement `upload_document` API — Supabase Storage upload → DB record → enqueue Celery task
- Implement `process_knowledge_document` task — chains the three tools above

**Frontend wiring (Phase 1 pages)**
- Discover page: real grant feed, save/unsave actions, relevance score display
- Knowledge page: file upload (drag-and-drop), per-doc processing status indicator
- Applications page: Kanban connected to real data
- Dashboard: live stats from API

---

### Phase 2 — AI Features

**Grant scoring**
- Implement `match_grants.py` — Claude relevance scoring → write to `org_grants`
- Implement `score_grants_for_org` Celery task (triggered after onboarding)
- Wire into discovery pipeline

**Application drafting**
- Create `app/agents/writer.py` — ApplicationWriterAgent
- Implement `generate_application_draft` task — RAG retrieval per section → Claude → Tiptap JSON → save draft → Supabase Realtime notify
- SSE streaming endpoint for live draft progress (`/applications/{id}/draft-stream`)
- Frontend: Tiptap editor for reviewing/editing AI draft
- Frontend: draft version history, approval workflow UI
- Implement `approve_draft` endpoint

**Compliance**
- Create `app/agents/compliance.py` — ComplianceAgent
- Implement `parse_grant_agreement` task — pdfplumber → Claude → milestone rows → notify
- Implement `parse-agreement` API endpoint (PDF upload → Supabase Storage → enqueue task)
- Implement `generate_report_draft` task
- Compliance page: milestone timeline, status badges, PDF upload trigger

**Deadline monitoring**
- Create `app/agents/deadline.py` — DeadlineAgent
- Implement `check_deadlines` and `send_weekly_digest` Celery tasks
- In-app notifications: model + API endpoint + frontend bell/panel
- Email notifications via Resend (deadline alerts, weekly digest, invite emails)

**Billing**
- Stripe SDK: `create_checkout`, `billing_portal`, `stripe_webhook` endpoints
- Subscription enforcement middleware (check plan limits per org)

---

### Phase 3 — Portal Submission

Reconsider before building. The Playwright approach is technically ambitious but a submission failure at the final step is catastrophic. Evaluate: structured copy-paste export vs. full automation.

If proceeding with automation:
- `tools/playwright_autofill/` directory — `session_manager.py`, `fill_grant_portal.py`, portal JSON selector configs
- `app/services/playwright_session.py`
- WebSocket screenshot streaming to frontend
- `submit_application` endpoint wired to Playwright session
- Frontend: live browser preview panel during submission

---

### Phase 4 — Data & Intelligence (post-PMF)

These are high-value but should not be built before validating the core:

- Additional grant sources: state/territory portals, foundation web scraping, manual source entry
- Grant source plugin architecture (pluggable auth, rate limits, field mapping)
- Eligibility pre-screening before draft generation
- Funder CRM: relationship history, contact tracking, outcome logging
- Grant outcome feedback loop → improves relevance scoring over time
- Sector-specific prompt tuning (arts, social services, housing, environment, health)
- Org type–aware writing style adaptation
- Data processing agreements + privacy controls for enterprise orgs

---

## Files to create

| File | Purpose |
|---|---|
| `backend/alembic/versions/0001_initial.py` | Creates all tables |
| `app/agents/writer.py` | ApplicationWriterAgent |
| `app/agents/compliance.py` | ComplianceAgent |
| `app/agents/deadline.py` | DeadlineAgent |
| `frontend/app/login/page.tsx` | Auth page |
| `frontend/app/signup/page.tsx` | Auth page |
| `frontend/app/onboarding/page.tsx` | Org profile setup |
| `frontend/app/(app)/applications/[id]/page.tsx` | Draft editor |
| `tools/playwright_autofill/` | Phase 3 (entire directory) |

---

## Critical path to a working Phase 1 demo

1. Alembic migration → database exists
2. Auth + org setup → can create an account
3. Onboarding flow → org profile populated
4. Knowledge upload pipeline → knowledge base populated
5. Grant fetch task → grants in DB
6. Grant list API + frontend → discovery feed visible
7. Applications Kanban → pipeline usable

Phase 2 depends entirely on Phase 1 being solid. RAG quality is the ceiling on draft quality — and RAG quality depends on the knowledge base pipeline.
