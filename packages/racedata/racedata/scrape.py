"""Future bronze producer.

A scraper is just another producer: it fetches raw results and calls
``store.put(ref, data, source_url=...)``. Every consuming agent is unchanged
whether bronze came from a manual download or this scraper. Not implemented yet.
"""
from __future__ import annotations

from .store import RaceRef, get_bronze_store  # noqa: F401


def scrape_race(ref: RaceRef) -> None:
    raise NotImplementedError(
        "Web scraping lands in Phase 5. See docs/four-agent-monorepo-plan.md."
    )
