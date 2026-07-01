"""
GrantConnect API source.

API docs: https://www.grants.gov.au/api/documentation
Base URL: https://www.grants.gov.au/api/v1

Authentication: API key in X-Api-Key header.

Key endpoints:
  GET /GoSearch  — list grant opportunities
  GET /Go/{id}   — single grant detail

Rate limits: Not publicly documented. Implement exponential backoff.
Incremental fetches: use LastModifiedFrom query param.
"""

import logging
from datetime import datetime

import httpx

from app.config import settings
from app.services.grant_sources.registry import GrantSource, RawGrant

logger = logging.getLogger(__name__)

GRANTCONNECT_BASE = settings.grantconnect_base_url


class GrantConnectSource(GrantSource):
    source_key = "grantconnect"

    def __init__(self):
        self.headers = {
            "X-Api-Key": settings.grantconnect_api_key,
            "Accept": "application/json",
        }

    async def fetch_new_grants(self, since: datetime) -> list[RawGrant]:
        """Fetch all grants modified since the given datetime."""
        grants: list[RawGrant] = []
        page = 1
        page_size = 100

        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                try:
                    response = await client.get(
                        f"{GRANTCONNECT_BASE}/GoSearch",
                        headers=self.headers,
                        params={
                            "LastModifiedFrom": since.strftime("%Y-%m-%dT%H:%M:%S"),
                            "PageNumber": page,
                            "PageSize": page_size,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                except httpx.HTTPStatusError as e:
                    logger.error("GrantConnect API error: %s", e)
                    break

                items = data.get("GoList", [])
                if not items:
                    break

                for item in items:
                    grants.append(self._parse_item(item))

                # Check if there are more pages
                total = data.get("TotalRecords", 0)
                if page * page_size >= total:
                    break
                page += 1

        return grants

    async def fetch_grant_detail(self, external_id: str) -> RawGrant:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{GRANTCONNECT_BASE}/Go/{external_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return self._parse_item(response.json())

    def _parse_item(self, item: dict) -> RawGrant:
        """Map GrantConnect API response fields to RawGrant."""
        def parse_date(val: str | None):
            if not val:
                return None
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00")).date()
            except (ValueError, AttributeError):
                return None

        return RawGrant(
            external_id=str(item.get("GoId", "")),
            title=item.get("GoTitle", ""),
            funder_name=item.get("AgencyName"),
            description=item.get("GoDescription"),
            eligibility=item.get("EligibilityCriteria"),
            funding_min=item.get("FundingMinimum"),
            funding_max=item.get("FundingMaximum"),
            open_date=parse_date(item.get("OpeningDate")),
            close_date=parse_date(item.get("ClosingDate")),
            categories=item.get("Categories", []),
            state_territory=item.get("StateTerritories", []),
            raw_data=item,
        )
