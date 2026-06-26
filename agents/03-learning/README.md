# Agent 03 — Agent that Learns
**Persona:** The Coach's Proactive Club Dashboard.

Memory-first: named memory blocks the agent reads/overwrites each turn, plus
pgvector retrieval of past analyses. Tracks specific clubs across 2024–2026 and
carries preferences across sessions.

**Stack:** dashboard UI · raw SDK + memory tools · **Postgres + pgvector**
(docker-compose) · `racedata` for bronze.
