#!/usr/bin/env python3
"""
Fetch new grants from the GrantConnect API.

Usage:
    python tools/grant_connect/fetch_grants.py [--since YYYY-MM-DDTHH:MM:SS]

If --since is not provided, fetches grants from the last 7 days.
Outputs the grants as JSON to stdout (for piping to parse_grants.py).

Workflow: workflows/grant_discovery.md
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timedelta, timezone

import httpx

# Load environment
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

GRANTCONNECT_BASE = os.getenv("GRANTCONNECT_BASE_URL", "https://www.grants.gov.au/api/v1")
GRANTCONNECT_API_KEY = os.getenv("GRANTCONNECT_API_KEY", "")
PAGE_SIZE = 100
MAX_RETRIES = 5


def fetch_with_backoff(client: httpx.Client, url: str, params: dict, headers: dict) -> dict:
    """GET with exponential backoff. Raises after MAX_RETRIES."""
    delay = 1
    for attempt in range(MAX_RETRIES):
        try:
            response = client.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 429:
                wait = delay * (2 ** attempt)
                log.warning("Rate limited. Waiting %ds before retry %d/%d", wait, attempt + 1, MAX_RETRIES)
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            log.error("HTTP error %s on attempt %d: %s", e.response.status_code, attempt + 1, e)
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(delay * (2 ** attempt))
    raise RuntimeError(f"Failed after {MAX_RETRIES} attempts")


def fetch_grants(since: datetime) -> list[dict]:
    headers = {
        "X-Api-Key": GRANTCONNECT_API_KEY,
        "Accept": "application/json",
    }
    since_str = since.strftime("%Y-%m-%dT%H:%M:%S")
    log.info("Fetching grants modified since %s", since_str)

    all_grants = []
    page = 1

    with httpx.Client() as client:
        while True:
            data = fetch_with_backoff(
                client,
                f"{GRANTCONNECT_BASE}/GoSearch",
                params={
                    "LastModifiedFrom": since_str,
                    "PageNumber": page,
                    "PageSize": PAGE_SIZE,
                },
                headers=headers,
            )

            items = data.get("GoList", [])
            total = data.get("TotalRecords", 0)
            log.info("Page %d: got %d items (total: %d)", page, len(items), total)

            all_grants.extend(items)

            if not items or page * PAGE_SIZE >= total:
                break
            page += 1

    log.info("Fetched %d grants total", len(all_grants))
    return all_grants


def main():
    parser = argparse.ArgumentParser(description="Fetch grants from GrantConnect API")
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="ISO datetime string (YYYY-MM-DDTHH:MM:SS). Defaults to 7 days ago.",
    )
    args = parser.parse_args()

    if args.since:
        since = datetime.fromisoformat(args.since)
    else:
        since = datetime.now(timezone.utc) - timedelta(days=7)

    grants = fetch_grants(since)
    print(json.dumps(grants, default=str, indent=2))


if __name__ == "__main__":
    main()
