# Agent 01 — Stateless Tool Caller
**Persona:** The Journalist's Quick Fact-Checker.

Single-turn Q&A over the Cork data: raw `openai` SDK + function tools in a small
think-act-observe loop. No framework, no vector DB, no cross-session memory.

**Stack:** Streamlit (single-turn) · raw OpenAI-compatible client · static silver
parquet (read-only) · `racedata` for bronze.

**Build note:** port from the old racebot first pass (git tag
`v1-stateless-firstpass`) — lift `tools/`, the agent loop, `eval/`, `tests/`, and
repoint the silver builder at `racedata.get_bronze_store()`.
