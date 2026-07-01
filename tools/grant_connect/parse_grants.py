#!/usr/bin/env python3
"""
Parse GrantConnect API response items into the normalised RawGrant format.

Usage:
    python tools/grant_connect/fetch_grants.py | python tools/grant_connect/parse_grants.py

Reads JSON array of GrantConnect items from stdin.
Outputs normalised grant records as JSON to stdout.

Workflow: workflows/grant_discovery.md
"""

import json
import sys
from datetime import datetime


def parse_date(val: str | None) -> str | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00")).date().isoformat()
    except (ValueError, AttributeError):
        return None


def parse_amount(val) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def parse_item(item: dict) -> dict:
    """Map a raw GrantConnect API item to the normalised grant schema."""
    return {
        "source": "grantconnect",
        "external_id": str(item.get("GoId", "")),
        "title": item.get("GoTitle", "Untitled Grant"),
        "funder_name": item.get("AgencyName"),
        "description": item.get("GoDescription"),
        "eligibility": item.get("EligibilityCriteria"),
        "funding_min": parse_amount(item.get("FundingMinimum")),
        "funding_max": parse_amount(item.get("FundingMaximum")),
        "open_date": parse_date(item.get("OpeningDate")),
        "close_date": parse_date(item.get("ClosingDate")),
        "categories": item.get("Categories") or [],
        "state_territory": item.get("StateTerritories") or [],
        "raw_data": item,
    }


def main():
    raw = json.load(sys.stdin)
    if not isinstance(raw, list):
        raw = [raw]

    parsed = [parse_item(item) for item in raw]
    print(json.dumps(parsed, indent=2))


if __name__ == "__main__":
    main()
