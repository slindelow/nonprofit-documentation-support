# Workflow: Grant Portal Auto-Fill (Playwright)

## Objective
Pre-fill a grant application portal with the approved application draft using Playwright browser automation. The user watches a live preview and clicks the final Submit button themselves.

## Trigger
- User clicks "Submit to portal" on an application with `stage = 'ready_to_submit'`
- POST `/api/v1/applications/{id}/submit`
- Starts a Playwright session on the Railway worker container

## Pre-conditions
- `application_approvals` must have a row with `stage = 'ready_to_submit'`
- `applications.portal_url` must be set
- `applications.portal_type` must be set (to select the right portal filler)

## Supported Portals
| portal_type | Class | Status |
|---|---|---|
| grantconnect | GrantConnectPortalFiller | Phase 3 |
| smartygrants | SmartyGrantsFiller | Phase 3 |
| generic | GenericFormFiller | Phase 3 (fallback) |

## Steps

### Step 1: Launch Playwright session
```
Run: tools/playwright_autofill/session_manager.py
Input: session_id (UUID), portal_url, application_id, org_id
Output: session handle, WebSocket URL for live preview
```
- Launch Chromium in non-headless mode on the worker container
- Stream screenshots to frontend via WebSocket at 2 fps (configurable)
- Store session metadata in Redis: `playwright:session:{session_id}` with TTL 30 minutes
- Navigate to portal_url

### Step 2: Handle portal login
```
The user must log in to the portal themselves.
Show prompt: "Please log in to {portal_name} in the browser window, then click Continue."
Wait for user confirmation before proceeding.
```
- Do not store portal credentials — always require user authentication
- Detect successful login by checking for authenticated page elements (portal-specific selectors in config)

### Step 3: Identify form fields (portal-specific or generic)
```
If portal_type in PORTAL_REGISTRY and portal has specific selectors:
    Use pre-configured selector map from config
Else (generic fallback):
    Use GenericFormFiller:
        1. Take a screenshot
        2. Call Claude Vision: "Identify all form fields in this screenshot.
           Return JSON: [{field_label: str, css_selector: str, field_type: input|textarea|select}]"
        3. Map field labels to application draft sections
```
- Config files: `tools/playwright_autofill/portals/{portal_type}.json`
- Update config file (not code) when a portal changes its UI

### Step 4: Fill form fields
```
Run: tools/playwright_autofill/fill_grant_portal.py
Input: field map, application draft content
For each field:
    1. Locate element via selector
    2. Clear existing content
    3. Type draft content for matching section
    4. Validate field filled (check element value)
```
- Match draft sections to form fields by label similarity (fuzzy match)
- Skip fields not present in draft (budget fields, signature fields)
- Pause between field fills for 200ms to avoid triggering bot detection
- Stream screenshot updates after each field fill

### Step 5: Human review and final submit
```
Show prompt: "Auto-fill complete. Please review all fields in the browser window.
             Make any corrections directly in the portal.
             When you are ready, click Submit in the portal."
```
- Wait for user to manually submit in the portal
- Detect submission by monitoring URL change or success page text
- Update `applications.status = 'submitted'`, set `applications.submitted_at`
- Create audit event

### Step 6: Session cleanup
```
Close Playwright browser
Delete Redis session key
Log session summary (fields filled, time taken, any errors)
```

## Error Handling
- Portal UI has changed (selector not found): show error "Portal layout may have changed. Please fill this section manually." and highlight the affected field
- "Report broken portal" button: sends Slack webhook to notify developer with session log
- Session timeout (30 min idle): notify user, close session, preserve application draft
- GenericFormFiller fails: fall back to manual fill instructions with draft content pre-loaded in a side panel

## Security Notes
- Never store portal credentials
- Playwright sessions run in isolated containers — one per session, destroyed after completion
- All session activity is logged in audit_events
- Final submit is always a deliberate human action

## Related Files
- `tools/playwright_autofill/session_manager.py`
- `tools/playwright_autofill/fill_grant_portal.py`
- `tools/playwright_autofill/portals/` — per-portal selector configs (JSON)
- `app/services/playwright_session.py`
- `skills/forms.md` — coordinate/field extraction conceptual foundation
