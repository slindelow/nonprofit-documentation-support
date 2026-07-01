# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

## File Structure

**What goes where:**
- **Deliverables**: Final outputs go to cloud services (Google Sheets, Slides, etc.) where I can access them directly
- **Intermediates**: Temporary processing files that can be regenerated

**Directory layout:**
```
.tmp/           # Temporary files (scraped data, intermediate exports). Regenerated as needed.
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
skills/         # Reusable skill definitions (markdown) that agents can invoke during task execution
.env            # API keys and environment variables (NEVER store secrets anywhere else)
credentials.json, token.json  # Google OAuth (gitignored)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Skills Reference

Skills are reusable capability definitions stored in `skills/`. **Always consult the relevant skill before starting any documentation, form, or document-creation task.** Skills take precedence over improvised approaches.

### Available Skills

| Skill file | Name | When to use |
|---|---|---|
| `skills/SKILL (5).md` | **pdf** | Any PDF task: reading, extracting text/tables, merging, splitting, rotating, creating, watermarking, OCR on scanned PDFs, encrypting |
| `skills/forms.md` | **forms** | Filling PDF forms — always read this before filling any form. Covers both fillable-field PDFs and non-fillable/scanned PDFs (annotation approach) |
| `skills/reference (1).md` | **pdf-reference** | Advanced PDF techniques (pypdfium2, pdf-lib JS, complex qpdf operations) — supplement to the pdf skill |
| `skills/SKILL (4).md` | **docx** | Any Word document task: creating, editing, reading .docx files, tracked changes, comments, tables, TOC, headers/footers |
| `skills/SKILL (6).md` | **doc-coauthoring** | Collaboratively drafting documents — proposals, specs, decision docs, reports. Provides a structured 3-stage workflow: context gathering → section-by-section drafting → reader testing |

### Mandatory Rules for Documentation Tasks

1. **PDF forms**: Always run `skills/forms.md` first. Check for fillable fields, follow the correct approach (fillable vs. non-fillable), validate bounding boxes before filling, and verify output.
2. **Word documents**: Always follow `skills/SKILL (4).md`. Never use `\n` in docx-js, never use unicode bullets, always set explicit page size (US Letter unless told otherwise), always use `WidthType.DXA` for tables.
3. **Creating any structured document** (report, proposal, memo, spec, letter): Offer the doc-coauthoring workflow from `skills/SKILL (6).md` unless the user explicitly wants to work freeform.
4. **Any PDF operation**: Check `skills/SKILL (5).md` for the right library/tool before writing code. Use pdfplumber for tables, pypdf for merging/splitting, reportlab for creating, pytesseract for OCR.
5. **Never improvise** a document or form-filling approach when a skill covers the task. Read the skill, follow its steps in order, and use its scripts.

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
