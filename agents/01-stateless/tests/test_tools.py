"""Tool-layer tests: golden numbers reproduce, guardrails hold, no PII leaks."""
from backend import tools


def test_golden_subset():
    assert tools.compute_stat("full", 2026, "count")["value"] == 2102
    assert tools.compute_stat("full", 2026, "median", sex="F")["value"] == "4:18:24"
    assert tools.compute_stat("half", 2026, "median")["value"] == "2:00:24"


def test_guardrails_return_errors():
    assert "error" in tools.compute_stat("marathon", 2026, "count")
    assert "error" in tools.compute_stat("full", 2026, "avg")
    assert "error" in tools.compute_stat("full", 2099, "count")


def test_no_pii_in_results():
    stat = tools.compute_stat("full", 2026, "count")
    club = tools.get_club_stats("Togher A.C.")
    for out in (stat, club):
        assert "name" not in out and "bib" not in out


def test_ambiguous_club_lists_candidates():
    out = tools.get_club_stats("A.C.")
    assert "matched_clubs" in out and len(out["matched_clubs"]) > 1
