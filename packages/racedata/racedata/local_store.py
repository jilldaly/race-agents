"""Filesystem bronze store.

Layout: ``<root>/<race>/<year>/results_<distance>.pdf`` plus a ``meta.yaml`` per
year capturing provenance. This is the canonical store for local development;
swap to ObjectStore for hosted deployments without touching any agent.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO

from .manifest import write_meta
from .store import DISTANCES, RaceRef


class LocalStore:
    def __init__(self, root: str | os.PathLike | None = None) -> None:
        self.root = Path(root or os.environ.get("BRONZE_ROOT", "data/bronze")).resolve()

    def _path(self, ref: RaceRef) -> Path:
        return self.root / ref.race / str(ref.year) / f"results_{ref.distance}.pdf"

    def list_races(self) -> list[RaceRef]:
        out: list[RaceRef] = []
        if not self.root.exists():
            return out
        for race_dir in sorted(p for p in self.root.iterdir() if p.is_dir()):
            for year_dir in sorted(p for p in race_dir.iterdir() if p.is_dir()):
                if not year_dir.name.isdigit():
                    continue
                for dist in DISTANCES:
                    if (year_dir / f"results_{dist}.pdf").exists():
                        out.append(RaceRef(race_dir.name, int(year_dir.name), dist))
        return out

    def exists(self, ref: RaceRef) -> bool:
        return self._path(ref).exists()

    def open(self, ref: RaceRef) -> BinaryIO:
        p = self._path(ref)
        if not p.exists():
            raise FileNotFoundError(f"No bronze file for {ref.slug} at {p}")
        return p.open("rb")

    def put(
        self,
        ref: RaceRef,
        data: bytes,
        *,
        content_type: str = "application/pdf",
        source_url: str | None = None,
    ) -> None:
        p = self._path(ref)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        write_meta(
            p.parent, ref, content_type=content_type, source_url=source_url, data=data
        )
