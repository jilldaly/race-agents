# Agent 02 — Multistep Workflow
**Persona:** The Analyst's Data-Cleaning Assistant.

Autonomously runs the bronze->silver->gold pipeline with retry logic, parallel
race processing, robust statistics (median/MAD, bootstrap CIs), and a
human-approval checkpoint before the gold report.

**Stack:** Streamlit + approval gate · **LangGraph** state machine · per-run
silver + trace logs · `racedata` for bronze.
