"""S3 / GCS / R2 bronze store -- Phase 5 (hosting) placeholder.

Implement against boto3 (S3/R2) or google-cloud-storage (GCS) when you move off
local disk. The interface is identical to LocalStore, so agents need no changes
-- only BRONZE_BACKEND flips from 'local' to 's3'/'gcs'.
"""
from __future__ import annotations

from typing import BinaryIO

from .store import RaceRef


class ObjectStore:
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError(
            "ObjectStore is a Phase 5 hosting stub. Use BRONZE_BACKEND=local for now."
        )

    def list_races(self) -> list[RaceRef]:  # pragma: no cover
        ...

    def exists(self, ref: RaceRef) -> bool:  # pragma: no cover
        ...

    def open(self, ref: RaceRef) -> BinaryIO:  # pragma: no cover
        ...

    def put(self, ref: RaceRef, data: bytes, **kw) -> None:  # pragma: no cover
        ...
