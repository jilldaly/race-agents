"""The data plane: deterministic tools the LLM may call (ADR 0003 function-calling).

Tools read through the silver repository and compute statistics in Python
("numbers from code"). They never expose PII (name, bib). Bad arguments return
an ``{"error": ...}`` dict rather than raising, so the model can recover. Times
are reported as H:MM:SS (medians floored to whole seconds, matching the report).
"""
from __future__ import annotations

import statistics

from backend import silver

_METRICS = {"count", "median", "mean", "fastest", "slowest"}


def _fmt(sec: int) -> str:
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"


def compute_stat(
    race: str,
    year: int,
    metric: str,
    sex: str | None = None,
    age_group: str | None = None,
    club: str | None = None,
) -> dict:
    """One statistic over a filtered slice of finishers."""
    meta = silver.query_meta()
    if race not in meta["races"]:
        return {"error": f"unknown race {race!r}; valid: {meta['races']}"}
    if year not in meta["years"]:
        return {"error": f"unknown year {year!r}; valid: {meta['years']}"}
    if metric not in _METRICS:
        return {"error": f"unknown metric {metric!r}; valid: {sorted(_METRICS)}"}
    if sex is not None and sex not in ("M", "F"):
        return {"error": f"sex must be 'M' or 'F', got {sex!r}"}
    if age_group is not None and age_group not in meta["age_groups"]:
        return {"error": f"unknown age_group {age_group!r}; valid: {meta['age_groups']}"}

    times = silver.query_times(race, year, sex=sex, age_group=age_group, club=club)
    if not times:
        return {"error": "no finishers match those filters", "n": 0}

    if metric == "count":
        value: object = len(times)
    elif metric == "median":
        value = _fmt(statistics.median(times))
    elif metric == "mean":
        value = _fmt(statistics.mean(times))
    elif metric == "fastest":
        value = _fmt(min(times))
    else:  # slowest
        value = _fmt(max(times))

    return {
        "race": race, "year": year, "metric": metric, "sex": sex,
        "age_group": age_group, "club": club, "n": len(times), "value": value,
    }


def get_club_stats(club: str, race: str | None = None, year: int | None = None) -> dict:
    """Finisher counts (and fastest time) for clubs matching `club` by substring."""
    rows = silver.query_club(club, race=race, year=year)
    if not rows:
        return {"error": f"no club matching {club!r}"}
    names = sorted({r["club"] for r in rows})
    if len(names) > 1:
        return {"matched_clubs": names, "hint": "narrow the club name and retry"}
    times = [r["time_sec"] for r in rows]
    by_race: dict[str, int] = {}
    by_year: dict[int, int] = {}
    for r in rows:
        by_race[r["race"]] = by_race.get(r["race"], 0) + 1
        by_year[r["year"]] = by_year.get(r["year"], 0) + 1
    return {
        "club": names[0], "race": race, "year": year, "finishers": len(rows),
        "by_race": by_race, "by_year": dict(sorted(by_year.items())),
        "male": sum(r["sex"] == "M" for r in rows),
        "female": sum(r["sex"] == "F" for r in rows),
        "fastest": _fmt(min(times)),
    }


def list_columns() -> dict:
    """Schema and valid filter values (no PII) so the model picks real arguments."""
    meta = silver.query_meta()
    return {
        "table": "finishers",
        "filterable": ["race", "year", "sex", "age_group", "club"],
        "metrics": sorted(_METRICS),
        **meta,
        "note": "name and bib exist but are PII and never returned; query clubs via get_club_stats",
    }


# OpenAI function-calling schemas (the open, MCP-portable format — ADR 0003).
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "compute_stat",
            "description": "Compute one statistic (count, median, mean, fastest, slowest finish time) over Cork City Marathon finishers, optionally filtered by sex, age group, or club.",
            "parameters": {
                "type": "object",
                "properties": {
                    "race": {"type": "string", "enum": ["full", "half", "10k"]},
                    "year": {"type": "integer", "enum": [2024, 2025, 2026]},
                    "metric": {"type": "string", "enum": sorted(_METRICS)},
                    "sex": {"type": "string", "enum": ["M", "F"]},
                    "age_group": {"type": "string"},
                    "club": {"type": "string"},
                },
                "required": ["race", "year", "metric"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_club_stats",
            "description": "Finisher counts and fastest time for a running club (matched by substring), optionally for one race/year.",
            "parameters": {
                "type": "object",
                "properties": {
                    "club": {"type": "string"},
                    "race": {"type": "string", "enum": ["full", "half", "10k"]},
                    "year": {"type": "integer", "enum": [2024, 2025, 2026]},
                },
                "required": ["club"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_columns",
            "description": "List the schema and valid filter values (races, years, age groups) before querying.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

_DISPATCH = {
    "compute_stat": compute_stat,
    "get_club_stats": get_club_stats,
    "list_columns": list_columns,
}


def dispatch(name: str, args: dict) -> dict:
    fn = _DISPATCH.get(name)
    if fn is None:
        return {"error": f"unknown tool {name!r}"}
    try:
        return fn(**args)
    except TypeError as exc:
        return {"error": f"bad arguments for {name}: {exc}"}
