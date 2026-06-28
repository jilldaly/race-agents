# ADR 0004 — Data plane per tier: SQLite at 01/02, Postgres from 03

**Status:** accepted (Phase 0).

**Context.**
The 2026 reference stack lists **Postgres** for the stateless tier
(`Provider SDK + MCP + Postgres`). But tier 01's data is static, small
(~9,809 rows), read-only, and not shared — the case where a server DB is
ceremony, the same way MCP is at 01 (ADR 0003). Tier 03 is memory-first and
needs **pgvector**, so Postgres is unavoidable there. We want the lower tiers
right-sized without making the eventual move to Postgres painful.

**Decision.**
1. **01 and 02 use SQLite** (stdlib `sqlite3`, file-based, zero server). 01 is
   read-only static silver; 02's LangGraph pipeline regenerates silver (single
   writer — fine for SQLite).
2. **03 and 04 use Postgres.** 03 needs pgvector; 04 needs concurrent
   multi-agent access. Postgres runs unbroken from 03 → 04.
3. **The DB is a queryable store, not the compute engine.** Tools `SELECT … WHERE
   …` and **Python/pandas computes the statistics** ("numbers from code"). This
   keeps the SQL surface tiny and nearly dialect-free, so SQLite→Postgres is
   close to a connection-string change.
4. **Each agent's DB access lives behind one small per-agent repository function**
   (`backend/silver.py`). No hand-written SQL scattered through the tools. Per
   THE ONE RULE this repository is **not shared** across agents — each owns its
   store, so swapping the engine is a one-file job, not a refactor.
5. **No heavy ORM at 01/02.** stdlib `sqlite3` matches the "ship in days"
   minimalism; the small per-agent rewrite at the Postgres tier is more honest
   than a shared abstraction.

**Why SQLite at 01/02 doesn't hurt the 03/04 comparison.**
- Dialect drift (placeholders, `percentile_cont`, date types) is avoided by
  computing stats in Python, not SQL.
- No native vector search in SQLite is irrelevant — 03 is Postgres+pgvector by
  design; that's the intended escalation, not pain.
- SQLite's single-writer limit only matters for the write-heavy tiers (03
  memory, 04 parallel agents), which use Postgres anyway.

**Consequences.**
- The 01→02 (file DB) → 03 (server DB + pgvector) progression is itself a
  teachable beat: prototype on SQLite, graduate to Postgres when the workflow
  needs vectors/concurrency.
- Accepted tradeoff: 02 is the "production standard" tier, and SQLite there reads
  as less-production than Postgres. We favour minimalism and keep the Postgres
  debut at 03 where it is load-bearing.
- Hosting stays cheap for 01/02 (a file ships with the app / object store); the
  managed-Postgres cost arrives only at 03.
