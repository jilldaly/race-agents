"""Bronze-layer access: the ONLY thing the four agents share.

Bronze is the immutable raw race-results layer. It is append-only: producers
(manual downloads today, the web scraper later) call ``put()``; every agent only
ever reads via ``list_races()`` / ``open()``. No agent knows or cares whether
bronze lives on local disk or in object storage -- that is decided by the
BRONZE_BACKEND env var, not by agent code.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import BinaryIO, Protocol, runtime_checkable

DISTANCES = ("full", "half", "10k")


@dataclass(frozen=True)
class RaceRef:
    """Identifies one raw results file: a race, a year, a distance."""

    race: str
    year: int
    distance: str  # one of DISTANCES

    @property
    def slug(self) -> str:
        return f"{self.race}_{self.year}_{self.distance}"


@runtime_checkable
class BronzeStore(Protocol):
    def list_races(self) -> list[RaceRef]: ...
    def exists(self, ref: RaceRef) -> bool: ...
    def open(self, ref: RaceRef) -> BinaryIO: ...
    def put(
        self,
        ref: RaceRef,
        data: bytes,
        *,
        content_type: str = "application/pdf",
        source_url: str | None = None,
    ) -> None: ...


def get_bronze_store() -> BronzeStore:
    """Factory. BRONZE_BACKEND=local (default) | s3 | gcs."""
    backend = os.environ.get("BRONZE_BACKEND", "local").lower()
    if backend == "local":
        from .local_store import LocalStore

        return LocalStore()
    if backend in {"s3", "gcs", "object"}:
        from .object_store import ObjectStore

        return ObjectStore()
    raise ValueError(
        f"Unknown BRONZE_BACKEND={backend!r} (expected 'local' or 's3'/'gcs')"
    )
