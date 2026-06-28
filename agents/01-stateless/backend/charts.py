"""Chart tools: deterministic *story* visualizations for the stateless agent.

Each chart renders a matplotlib PNG to ``output/`` (gitignored) and returns a
compact JSON reference — the numbers it plots, plus the file path and a one-line
caption. The model never receives pixels (control/data plane split, ADR 0003): it
narrates from the numbers and the Streamlit app displays the PNG. Numbers come
from code.

Plotting is adapted from the deterministic Cork report (the golden source); data
comes from the silver repository (`silver.load_frame`), not the report's own
loader. The report uses capitalised race names and a `sec` column; here races are
`full`/`half`/`10k` and time is `time_sec`.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: render to file, never to a window
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from backend import silver  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
YEARS = (2024, 2025, 2026)
RACE_ORDER = ("full", "half", "10k")
RACE_LABEL = {"full": "Marathon", "half": "Half Marathon", "10k": "10K"}
C_MALE = "#3b6fb0"
C_FEMALE = "#d06b9c"


def _frame() -> pd.DataFrame:
    return pd.DataFrame(silver.load_frame())


def _save(fig, name: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / name, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return f"output/{name}"  # app-relative — never leak absolute server paths/usernames


def _style(ax, title="", xlabel="", ylabel="", grid_axis="y"):
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, alpha=0.25, linestyle="--")
    ax.tick_params(labelsize=8)


def _gender_counts(sub) -> dict:
    m = int((sub["sex"] == "M").sum())
    f = int((sub["sex"] == "F").sum())
    total = m + f
    return {
        "male": m,
        "female": f,
        "total": total,
        "pct_female": round(100 * f / total, 1) if total else 0.0,
        "pct_male": round(100 * m / total, 1) if total else 0.0,
    }


# ── Gender ───────────────────────────────────────────────────────────────────
def gender_chart(
    mode: str = "snapshot", year: int | None = None, race: str | None = None
) -> dict:
    """Gender (male/female) story chart + the numbers behind it.

    mode='snapshot': gender split of finishers for a year — all races, or one race
    if `race` is given. mode='trend': female participation % across 2024–2026 — all
    races combined, or one race if given.
    """
    if mode not in ("snapshot", "trend"):
        return {"error": f"mode must be 'snapshot' or 'trend', got {mode!r}"}
    if race is not None and race not in RACE_ORDER:
        return {"error": f"unknown race {race!r}; valid: {list(RACE_ORDER)}"}
    df = _frame()
    if mode == "snapshot":
        if year is None:
            return {"error": "specify a year for a snapshot: 2024, 2025, or 2026"}
        if year not in YEARS:
            return {"error": f"unknown year {year!r}; valid: {list(YEARS)}"}
        return _gender_snapshot(df, year, race)
    return _gender_trend(df, race)


def _gender_snapshot(df, year: int, race: str | None) -> dict:
    races = [race] if race else list(RACE_ORDER)
    rows = []
    for r in races:
        sub = df[(df["race"] == r) & (df["year"] == year)]
        rows.append({"race": r, **_gender_counts(sub)})

    fig, ax = plt.subplots(figsize=(max(3.5, 1.7 * len(races) + 1.5), 4))
    for i, d in enumerate(rows):
        ax.bar(i, d["male"], color=C_MALE, width=0.55)
        ax.bar(i, d["female"], bottom=d["male"], color=C_FEMALE, width=0.55)
        if d["male"] > 30:
            ax.text(i, d["male"] / 2, f"{d['male']:,}\n({d['pct_male']:.0f}%)",
                    ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        if d["female"] > 30:
            ax.text(i, d["male"] + d["female"] / 2, f"{d['female']:,}\n({d['pct_female']:.0f}%)",
                    ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([RACE_LABEL[d["race"]] for d in rows], fontsize=9)
    ax.legend(handles=[mpatches.Patch(color=C_MALE, label="Male"),
                       mpatches.Patch(color=C_FEMALE, label="Female")],
              fontsize=8, loc="upper right")
    scope = RACE_LABEL[race] if race else "by race"
    _style(ax, title=f"Gender split {scope} — {year}", ylabel="Finishers")
    fig.tight_layout()
    path = _save(fig, f"gender_snapshot_{year}_{race or 'all'}.png")
    return {
        "mode": "snapshot", "year": year, "race": race, "races": rows,
        "chart": path, "caption": f"Gender split of finishers, {year}.",
    }


def _gender_trend(df, race: str | None) -> dict:
    label = RACE_LABEL[race] if race else "all races"
    pts = []
    for y in YEARS:
        sub = df[df["year"] == y] if race is None else df[(df["year"] == y) & (df["race"] == race)]
        pts.append({"year": y, **_gender_counts(sub)})

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot([p["year"] for p in pts], [p["pct_female"] for p in pts],
            marker="o", linewidth=2.5, markersize=8, color=C_FEMALE)
    for p in pts:
        ax.annotate(f"{p['pct_female']:.1f}%", (p["year"], p["pct_female"]),
                    textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9)
    ax.axhline(50, color="grey", linestyle=":", alpha=0.5)
    ax.set_xticks(list(YEARS))
    ax.set_ylim(0, 70)
    _style(ax, title=f"Female participation % — {label} (2024–2026)",
           xlabel="Year", ylabel="% female")
    fig.tight_layout()
    path = _save(fig, f"gender_trend_{race or 'all'}.png")
    return {
        "mode": "trend", "race": race, "series": pts,
        "chart": path, "caption": f"Female share of finishers, {label}, 2024–2026.",
    }
