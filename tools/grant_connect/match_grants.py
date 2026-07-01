#!/usr/bin/env python3
"""
Score grant relevance for an organisation using Claude.

Usage:
    python tools/grant_connect/match_grants.py \
        --org-id <uuid> \
        --grant-ids <uuid1> <uuid2> ...

Reads org profile and grant records from the database.
Calls Claude to score relevance for each grant.
Updates org_grants table with scores.

Phase 2 feature — requires Claude API key and database connection.
Workflow: workflows/grant_discovery.md
"""

import argparse
import json
import logging
import os
from uuid import UUID

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SCORING_PROMPT = """You are evaluating whether a grant is relevant to an Australian nonprofit organisation.

Organisation profile:
Name: {org_name}
Focus areas: {focus_areas}
State/Territory: {state_territory}
Organisation type: {org_type}
Mission (from knowledge base): {mission_summary}

Grant:
Title: {grant_title}
Funder: {funder_name}
Description: {description}
Eligibility: {eligibility}
Categories: {categories}
States: {state_territory_grant}
Funding: ${funding_min} - ${funding_max}
Close date: {close_date}

Score how relevant this grant is for this organisation on a scale of 0.0 to 1.0.

Return JSON only, no explanation outside JSON:
{{
  "score": <float between 0.0 and 1.0>,
  "reasoning": "<2 sentence explanation of why this grant does or does not fit>"
}}

Scoring guide:
- 0.9–1.0: Near-perfect fit. Organisation is clearly eligible, grant aligns directly with mission.
- 0.7–0.9: Strong fit. Minor eligibility questions but high mission alignment.
- 0.5–0.7: Moderate fit. Some alignment but significant gaps or uncertainties.
- 0.3–0.5: Weak fit. Little alignment, would require significant stretch.
- 0.0–0.3: Not relevant. Organisation is ineligible or mission mismatch.
"""


def score_grant(org_profile: dict, grant: dict, anthropic_client) -> dict:
    """Score a single grant for an org. Returns {score, reasoning}."""
    prompt = SCORING_PROMPT.format(
        org_name=org_profile.get("name", ""),
        focus_areas=", ".join(org_profile.get("focus_areas") or []),
        state_territory=org_profile.get("state_territory", ""),
        org_type=org_profile.get("org_type", ""),
        mission_summary=org_profile.get("mission_summary", ""),
        grant_title=grant.get("title", ""),
        funder_name=grant.get("funder_name", ""),
        description=(grant.get("description") or "")[:1000],
        eligibility=(grant.get("eligibility") or "")[:500],
        categories=", ".join(grant.get("categories") or []),
        state_territory_grant=", ".join(grant.get("state_territory") or ["National"]),
        funding_min=grant.get("funding_min") or "Not specified",
        funding_max=grant.get("funding_max") or "Not specified",
        close_date=grant.get("close_date") or "Not specified",
    )

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=256,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    try:
        result = json.loads(text)
        score = max(0.0, min(1.0, float(result["score"])))
        reasoning = str(result.get("reasoning", ""))
        return {"score": score, "reasoning": reasoning}
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        log.error("Failed to parse scoring response: %s — %s", text, e)
        return {"score": 0.0, "reasoning": "Scoring failed — manual review required."}


def main():
    parser = argparse.ArgumentParser(description="Score grant relevance for an org")
    parser.add_argument("--org-id", required=True, help="Organisation UUID")
    parser.add_argument("--grant-ids", nargs="+", required=True, help="Grant UUIDs to score")
    parser.add_argument("--dry-run", action="store_true", help="Print scores without writing to DB")
    args = parser.parse_args()

    # Import here so script is importable without all deps present
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    log.info("Scoring %d grants for org %s", len(args.grant_ids), args.org_id)
    log.info("Phase 2 — database integration not yet implemented in this script")
    log.info("See app/tasks/discovery_tasks.py:score_grants_for_org for the full implementation")


if __name__ == "__main__":
    main()
