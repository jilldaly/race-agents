# Agent 01 — Stateless Tool Caller
**Persona:** The Journalist's Quick Fact-Checker.

Single-turn Q&A over the Cork data: raw `openai` SDK + function tools in a small
think-act-observe loop. No framework, no vector DB, no cross-session memory.

**Stack:** Streamlit (single-turn) · raw OpenAI-compatible client · function-calling
tools (ADR 0003) · read-only static **SQLite** silver behind one `backend/silver.py`
repository function (ADR 0004) · `racedata` for bronze.

**Build note:** built fresh from `docs/architecture/Repo_1_The_Stateless_Tool_Caller.md`
and the per-tier ADRs. Silver is built from bronze via `racedata.get_bronze_store()`;
the golden eval validates the numbers against the deterministic ancestor
([`cork-city-marathon-analysis`](https://github.com/jilldaly/cork-city-marathon-analysis)).
