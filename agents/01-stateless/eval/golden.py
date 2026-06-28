"""Golden eval — the verdict (deterministic, no LLM, no network).

Builds silver from the committed bronze PDFs and asserts the data-plane tools
reproduce the numbers anchored to the deterministic ancestor's report
(cork-city-marathon-analysis). 2026 is the gate (see docs/eval-strategy.md):
chip/net times, placeholder rows excluded, medians floored to whole seconds.

Run:  python -m eval.golden   (exit 0 = pass, 1 = fail)
"""
from __future__ import annotations

import os
import sys

from backend import charts, silver, tools

# (label, tool call, expected "value")
GOLDEN = [
    ("full 2026 finishers", dict(race="full", year=2026, metric="count"), 2102),
    ("half 2026 finishers", dict(race="half", year=2026, metric="count"), 4309),
    ("10k 2026 finishers", dict(race="10k", year=2026, metric="count"), 3396),
    ("full 2026 female median", dict(race="full", year=2026, metric="median", sex="F"), "4:18:24"),
    ("full 2026 male median", dict(race="full", year=2026, metric="median", sex="M"), "3:53:29"),
    ("full 2026 overall median", dict(race="full", year=2026, metric="median"), "3:57:09"),
    ("half 2026 median", dict(race="half", year=2026, metric="median"), "2:00:24"),
    ("10k 2026 median (chip)", dict(race="10k", year=2026, metric="median"), "1:02:07"),
    ("full 2026 fastest", dict(race="full", year=2026, metric="fastest"), "2:22:42"),
]

# Cross-check: full year-on-year finisher counts (deterministic ancestor trend).
GOLDEN += [
    ("full 2024 finishers", dict(race="full", year=2024, metric="count"), 1855),
    ("full 2025 finishers", dict(race="full", year=2025, metric="count"), 1944),
]

# Gender story tool. Charts can't be golden'd as pixels, so we assert the numbers
# the chart *encodes* (must match the source) plus a render smoke test. 2026
# all-races M/F = 5,258/4,549 reproduces the report exactly.
# (label, race, year, (male, female, total, pct_female))
GENDER_SNAPSHOT = [
    ("full 2026 gender", "full", 2026, (1615, 487, 2102, 23.2)),
    ("half 2026 gender", "half", 2026, (2322, 1987, 4309, 46.1)),
    ("10k 2026 gender", "10k", 2026, (1321, 2075, 3396, 61.1)),
    ("full 2024 gender", "full", 2024, (1467, 388, 1855, 20.9)),
]
# (label, race or None=all-races-combined, [pct_female per 2024,2025,2026])
GENDER_TREND = [
    ("female % trend, all races", None, [44.8, 47.0, 46.4]),
    ("female % trend, full", "full", [20.9, 21.6, 23.2]),
]


def _rendered(rel_path: str) -> bool:
    p = charts.OUTPUT_DIR / os.path.basename(rel_path)  # chart path is app-relative
    return p.exists() and p.stat().st_size > 1000


def main() -> int:
    silver.build_silver()  # from committed bronze; deterministic
    failures = total = 0

    for label, call, expected in GOLDEN:
        got = tools.compute_stat(**call).get("value")
        ok = got == expected
        print(f"  [{'ok' if ok else 'FAIL'}] {label}: got {got!r}, want {expected!r}")
        failures += not ok
        total += 1

    for label, race, year, exp in GENDER_SNAPSHOT:
        out = charts.gender_chart("snapshot", year, race)
        d = out["races"][0]
        got = (d["male"], d["female"], d["total"], d["pct_female"])
        ok = got == exp and _rendered(out["chart"])
        print(f"  [{'ok' if ok else 'FAIL'}] {label}: got {got}, want {exp}, rendered={_rendered(out['chart'])}")
        failures += not ok
        total += 1

    for label, race, exp in GENDER_TREND:
        out = charts.gender_chart("trend", race=race)
        got = [p["pct_female"] for p in out["series"]]
        ok = got == exp and _rendered(out["chart"])
        print(f"  [{'ok' if ok else 'FAIL'}] {label}: got {got}, want {exp}, rendered={_rendered(out['chart'])}")
        failures += not ok
        total += 1

    print(f"\n{total - failures}/{total} golden checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
