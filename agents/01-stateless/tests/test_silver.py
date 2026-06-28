"""Silver-layer tests: PII scrub removes personal data without changing any
aggregate (GDPR — the public deploy ships a name-free db)."""
import sqlite3

from backend import silver


def test_scrub_pii_removes_names_keeps_counts(tmp_path):
    db = tmp_path / "cork.db"
    silver.build_silver(db)

    con = sqlite3.connect(db)
    assert con.execute("SELECT COUNT(*) FROM finishers WHERE name != ''").fetchone()[0] > 0
    con.close()

    silver.scrub_pii(db)

    con = sqlite3.connect(db)
    # No personal data left.
    assert con.execute("SELECT COUNT(*) FROM finishers WHERE name != ''").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM finishers WHERE bib IS NOT NULL").fetchone()[0] == 0
    # Aggregates untouched (golden marathon 2026 count).
    assert con.execute(
        "SELECT COUNT(*) FROM finishers WHERE race='full' AND year=2026"
    ).fetchone()[0] == 2102
    con.close()
