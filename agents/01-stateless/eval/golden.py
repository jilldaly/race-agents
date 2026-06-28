"""Golden eval — the verdict (deterministic, no LLM, no network).

Builds silver from the committed bronze PDFs and asserts the data-plane tools
reproduce the numbers anchored to the deterministic ancestor's report
(cork-city-marathon-analysis). 2026 is the gate (see docs/eval-strategy.md):
chip/net times, placeholder rows excluded, medians floored to whole seconds.

Run:  python -m eval.golden   (exit 0 = pass, 1 = fail)
"""
from __future__ import annotations

import sys

from backend import silver, tools

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


def main() -> int:
    silver.build_silver()  # from committed bronze; deterministic
    failures = 0
    for label, call, expected in GOLDEN:
        got = tools.compute_stat(**call).get("value")
        ok = got == expected
        print(f"  [{'ok' if ok else 'FAIL'}] {label}: got {got!r}, want {expected!r}")
        failures += not ok
    total = len(GOLDEN)
    print(f"\n{total - failures}/{total} golden checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
