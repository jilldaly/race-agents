"""Silver layer for agent 01: parse bronze result PDFs into a read-only SQLite db.

The DB is a queryable *store*, not a compute engine (ADR 0004): callers read rows
through the small repository functions here and compute statistics in Python.
Bronze PDFs are read via racedata.get_bronze_store(); silver is rebuilt, never
hand-edited. `time_sec` is chip (net) time where available, else the single
published time.

Two bronze layouts exist and are detected per-PDF from the header row:
  - 2026:    "Bib Pos. Name Club Sex AG Chip Gun"  (two times; 10k swaps to Gun Chip)
  - 2024/25: "Rank Bib Name Club Sex AG Time"      (one time, leading "Rank.")
A row is a finisher only if it carries a full result tail (sex, age-group, time);
placeholder rows without an age-group (e.g. the timing provider's "Contact
POPUPRACES" entries in the 10k) are therefore not counted.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Iterable

import pdfplumber

from racedata import get_bronze_store

SILVER_DB = Path(__file__).resolve().parent.parent / "data" / "silver" / "cork.db"

# 2026 layout: "<bib> [pos] <who> <sex_rank>. <sex> <ag> <chip> <gun>".
# Bib/pos are one token in the 10k (no space) and two elsewhere; we don't need
# them for statistics, so the leading group is flexible.
_ROW_CHIPGUN = re.compile(
    r"^(?P<lead>\d+(?:\s+\d+)?)\s+(?P<who>.+?)\s+"
    r"(?P<sex_rank>\d+)\.\s+(?P<sex>[MF])\s+(?P<ag>\S+)\s+"
    r"(?P<t1>\d{1,2}:\d{2}:\d{2})\s+(?P<t2>\d{1,2}:\d{2}:\d{2})$"
)
# 2024/25 layout: "<rank>. <bib> <who> <sex_rank>. <sex> <ag> <time>".
# The age-group can be multi-word ("F Juvenile") and the single time may be
# sub-hour MM:SS (10k) or H:MM:SS, so both groups are flexible.
_ROW_TIME = re.compile(
    r"^(?P<rank>\d+)\.\s+(?P<bib>\d+)\s+(?P<who>.+?)\s+"
    r"(?P<sex_rank>\d+)\.\s+(?P<sex>[MF])\s+(?:(?P<ag>.+?)\s+)?"
    r"(?P<time>\d{1,2}:\d{2}(?::\d{2})?)$"
)


def _to_sec(t: str) -> int:
    parts = [int(x) for x in t.split(":")]
    if len(parts) == 2:  # MM:SS (sub-hour, e.g. 10k)
        m, s = parts
        return m * 60 + s
    h, m, s = parts  # H:MM:SS
    return h * 3600 + m * 60 + s


def _split_name_club(who: str) -> tuple[str, str]:
    """Surname is an ALL-CAPS word; the club (if any) follows it.

    Name is up to and including the last all-letters uppercase token (e.g.
    VILLAMOR); the remainder is the club. Tokens with dots (A.C.) are not treated
    as the surname, so 'Andrea AZA VILLAMOR Glanmire A.C.' splits correctly.
    """
    toks = who.split()
    last_caps = -1
    for i, t in enumerate(toks):
        if t.isupper() and "." not in t and any(c.isalpha() for c in t):
            last_caps = i
    if last_caps < 0:
        return who, ""
    return " ".join(toks[: last_caps + 1]), " ".join(toks[last_caps + 1 :])


def _is_header(low: str) -> bool:
    return all(w in low for w in ("bib", "name", "sex", "ag"))


def parse_pdf(fh, race: str, year: int) -> list[dict]:
    """Parse one bronze result PDF into normalised row dicts (both layouts)."""
    rows: list[dict] = []
    layout: str | None = None
    chip_first = True
    with pdfplumber.open(fh) as pdf:
        for page in pdf.pages:
            for line in (page.extract_text() or "").splitlines():
                s = line.strip()
                if s[:1].isdigit() is False and _is_header(s.lower()):
                    low = s.lower()
                    if "chip" in low and "gun" in low:
                        layout = "chipgun"
                        chip_first = low.index("chip") < low.index("gun")
                    elif "time" in low:
                        layout = "time"
                    continue

                if layout == "chipgun":
                    m = _ROW_CHIPGUN.match(s)
                    if not m:
                        continue
                    chip, gun = (m["t1"], m["t2"]) if chip_first else (m["t2"], m["t1"])
                    chip_sec, gun_sec = _to_sec(chip), _to_sec(gun)
                    lead = m["lead"].split()
                    bib = int(lead[0])
                    pos = int(lead[1]) if len(lead) > 1 else None
                    who = m["who"]
                elif layout == "time":
                    m = _ROW_TIME.match(s)
                    if not m:
                        continue
                    chip_sec = _to_sec(m["time"])
                    gun_sec = None
                    bib = int(m["bib"])
                    pos = int(m["rank"])
                    who = m["who"]
                else:
                    continue

                name, club = _split_name_club(who.strip())
                rows.append(
                    {
                        "race": race,
                        "year": year,
                        "bib": bib,
                        "pos": pos,
                        "name": name,          # PII — never surfaced to the LLM
                        "club": club,
                        "sex": m["sex"],
                        "age_group": (m["ag"] or "").strip(),
                        "sex_rank": int(m["sex_rank"]),
                        "chip_sec": chip_sec,
                        "gun_sec": gun_sec,
                        "time_sec": chip_sec,  # chip (net) where available
                    }
                )
    return rows


def _all_rows() -> Iterable[dict]:
    store = get_bronze_store()
    for ref in store.list_races():
        if ref.race != "cork":
            continue
        with store.open(ref) as fh:
            yield from parse_pdf(fh, ref.distance, ref.year)


def build_silver(db_path: Path = SILVER_DB) -> int:
    """Rebuild the silver SQLite db from bronze. Returns row count."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.execute(
        """CREATE TABLE finishers (
            race TEXT, year INTEGER, bib INTEGER, pos INTEGER,
            name TEXT, club TEXT, sex TEXT, age_group TEXT, sex_rank INTEGER,
            chip_sec INTEGER, gun_sec INTEGER, time_sec INTEGER
        )"""
    )
    # One finisher per (race, year, bib): some 2024/25 PDFs list a runner in both
    # an overall ranking and an age-group ranking. Keep the age-group-bearing row.
    best: dict[tuple, dict] = {}
    for r in _all_rows():
        key = (r["race"], r["year"], r["bib"])
        cur = best.get(key)
        if cur is None or (not cur["age_group"] and r["age_group"]):
            best[key] = r
    rows = list(best.values())
    con.executemany(
        """INSERT INTO finishers VALUES
           (:race,:year,:bib,:pos,:name,:club,:sex,:age_group,:sex_rank,
            :chip_sec,:gun_sec,:time_sec)""",
        rows,
    )
    con.commit()
    con.close()
    return len(rows)


# --- repository: the only place that issues SQL (ADR 0004) ------------------
# Tools call these; they never write SQL themselves. PII (name, bib) is never
# returned. Statistics are computed in Python by the caller, not in SQL.

def _connect(db_path: Path = SILVER_DB) -> sqlite3.Connection:
    if not db_path.exists():
        build_silver(db_path)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def query_times(
    race: str,
    year: int,
    *,
    sex: str | None = None,
    age_group: str | None = None,
    club: str | None = None,
    db_path: Path = SILVER_DB,
) -> list[int]:
    """Chip times (seconds) for the filtered finishers — the read for time stats."""
    sql = "SELECT time_sec FROM finishers WHERE race=? AND year=?"
    args: list = [race, year]
    for col, val in (("sex", sex), ("age_group", age_group), ("club", club)):
        if val is not None:
            sql += f" AND {col}=?"
            args.append(val)
    con = _connect(db_path)
    try:
        return [r["time_sec"] for r in con.execute(sql, args)]
    finally:
        con.close()


def query_meta(db_path: Path = SILVER_DB) -> dict:
    """Valid filter values (no PII) for list_columns / validation."""
    con = _connect(db_path)
    try:
        col = lambda q: [r[0] for r in con.execute(q)]
        return {
            "races": col("SELECT DISTINCT race FROM finishers ORDER BY race"),
            "years": col("SELECT DISTINCT year FROM finishers ORDER BY year"),
            "sexes": ["M", "F"],
            "age_groups": col(
                "SELECT DISTINCT age_group FROM finishers WHERE age_group<>'' ORDER BY age_group"
            ),
            "n_clubs": con.execute(
                "SELECT COUNT(DISTINCT club) FROM finishers WHERE club<>''"
            ).fetchone()[0],
        }
    finally:
        con.close()


def query_club(
    club_like: str, *, race: str | None = None, year: int | None = None,
    db_path: Path = SILVER_DB,
) -> list[dict]:
    """Finisher records for clubs matching `club_like` (case-insensitive substring)."""
    sql = "SELECT race, year, sex, age_group, club, time_sec FROM finishers WHERE club<>'' AND club LIKE ?"
    args: list = [f"%{club_like}%"]
    if race is not None:
        sql += " AND race=?"
        args.append(race)
    if year is not None:
        sql += " AND year=?"
        args.append(year)
    con = _connect(db_path)
    try:
        return [dict(r) for r in con.execute(sql, args)]
    finally:
        con.close()


if __name__ == "__main__":
    n = build_silver()
    print(f"built {SILVER_DB} with {n} rows")
