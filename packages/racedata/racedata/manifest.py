"""meta.yaml provenance for the bronze layer.

Records where each raw file came from and a checksum, so provenance survives the
move from manual downloads to live scraping.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .store import RaceRef


def write_meta(
    dir_path: str | Path,
    ref: RaceRef,
    *,
    content_type: str,
    source_url: str | None,
    data: bytes,
) -> Path:
    meta_path = Path(dir_path) / "meta.yaml"
    meta = {}
    if meta_path.exists():
        meta = yaml.safe_load(meta_path.read_text()) or {}
    meta.setdefault("race", ref.race)
    meta.setdefault("year", ref.year)
    files = meta.setdefault("files", {})
    files[ref.distance] = {
        "filename": f"results_{ref.distance}.pdf",
        "content_type": content_type,
        "source_url": source_url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False))
    return meta_path
