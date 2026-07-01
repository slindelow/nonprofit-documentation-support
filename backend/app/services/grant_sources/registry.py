"""
Pluggable grant source registry.

To add a new source:
1. Create a new class in this package implementing GrantSource
2. Add it to GRANT_SOURCE_REGISTRY below
3. No changes needed to the discovery agent or tasks

Each source must implement:
- fetch_new_grants(since: datetime) -> list[RawGrant]
- fetch_grant_detail(external_id: str) -> RawGrant
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass
class RawGrant:
    external_id: str
    title: str
    funder_name: str | None
    description: str | None
    eligibility: str | None
    funding_min: float | None
    funding_max: float | None
    open_date: date | None
    close_date: date | None
    categories: list[str]
    state_territory: list[str]
    raw_data: dict[str, Any]


class GrantSource(ABC):
    source_key: str  # Must match the key in GRANT_SOURCE_REGISTRY

    @abstractmethod
    async def fetch_new_grants(self, since: datetime) -> list[RawGrant]:
        """Fetch grants updated or published since the given datetime."""
        ...

    @abstractmethod
    async def fetch_grant_detail(self, external_id: str) -> RawGrant:
        """Fetch full detail for a single grant."""
        ...


# Registry — add new sources here
GRANT_SOURCE_REGISTRY: dict[str, type[GrantSource]] = {}

# Import and register sources
try:
    from app.services.grant_sources.grantconnect import GrantConnectSource
    GRANT_SOURCE_REGISTRY["grantconnect"] = GrantConnectSource
except ImportError:
    pass
