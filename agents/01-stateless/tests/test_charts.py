"""Chart-tool tests: numbers behind the chart are right, it renders, no PII,
guardrails hold. No LLM, no network."""
import os

from backend import charts, tools


def test_gender_snapshot_numbers_and_render():
    out = charts.gender_chart("snapshot", 2026, "full")
    d = out["races"][0]
    assert (d["male"], d["female"], d["total"], d["pct_female"]) == (1615, 487, 2102, 23.2)
    assert not os.path.isabs(out["chart"])  # app-relative — no absolute path leak
    p = charts.OUTPUT_DIR / os.path.basename(out["chart"])
    assert p.exists() and p.stat().st_size > 1000


def test_gender_snapshot_all_races():
    out = charts.gender_chart("snapshot", 2026)
    by_race = {r["race"]: r["pct_female"] for r in out["races"]}
    assert by_race == {"full": 23.2, "half": 46.1, "10k": 61.1}


def test_gender_trend_series():
    out = charts.gender_chart("trend")  # all races combined
    assert [p["pct_female"] for p in out["series"]] == [44.8, 47.0, 46.4]
    assert (charts.OUTPUT_DIR / os.path.basename(out["chart"])).exists()


def test_gender_chart_guardrails():
    assert "error" in charts.gender_chart("nonsense")
    assert "error" in charts.gender_chart("snapshot", 2099)
    assert "error" in charts.gender_chart("snapshot", 2026, "marathon")


def test_snapshot_without_year_asks_not_assumes():
    # No silent default to 2026 — a year-less snapshot must nudge for clarification.
    out = charts.gender_chart("snapshot")
    assert "error" in out and "year" in out["error"]


def test_gender_chart_no_pii():
    out = charts.gender_chart("snapshot", 2026, "full")
    assert "name" not in str(out) and "bib" not in out


def test_gender_chart_registered_as_tool():
    assert "gender_chart" in tools._DISPATCH
    names = {s["function"]["name"] for s in tools.TOOL_SCHEMAS}
    assert "gender_chart" in names
