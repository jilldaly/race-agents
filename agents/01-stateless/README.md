# Agent 01 — Stateless Tool Caller
**Persona:** the Journalist's Quick Fact-Checker.

Single-turn Q&A over the Cork City Marathon results (Full / Half / 10K,
2024–2026): a raw `openai`-compatible client in a small Think-Act-Observe loop
that routes to deterministic Python tools. No framework, no vector DB, no
cross-session memory — every question is a blank slate.

**Stack:** Streamlit (single-turn) · OpenAI-compatible client → **Gemini free
tier** (`gemini-2.0-flash`, swappable via `base_url`) · function-calling tools
(ADR 0003) · read-only **SQLite** silver behind one `backend/silver.py`
repository (ADR 0004) · `racedata` for bronze.

## How it works
- **Control plane** (`backend/agent.py`, `router.py`): the LLM only chooses which
  tool to call; the loop — not the model — owns termination via `MAX_STEPS`.
- **Data plane** (`backend/tools.py`): `compute_stat`, `get_club_stats`,
  `list_columns`. Tools read via the repository and **compute statistics in
  Python** ("numbers from code"); bad arguments return `{"error": ...}`; PII
  (name, bib) is never returned.
- **Silver** (`backend/silver.py`): parses the two bronze PDF layouts (2026
  `Chip/Gun`; 2024/25 single `Time`) into SQLite. `time_sec` is chip (net).
- **Validated** against the deterministic ancestor
  ([`cork-city-marathon-analysis`](https://github.com/jilldaly/cork-city-marathon-analysis)):
  the golden eval reproduces the 2026 numbers exactly.

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ../../packages/racedata -r requirements.txt
cp .env.example .env          # add your free-tier GEMINI_API_KEY
streamlit run app.py
```

## Test & eval (no live LLM, no network)
```bash
pip install pytest
python -m pytest tests/        # tool golden/guardrail + loop control-flow (stub router)
python -m eval.golden          # golden gate: tools reproduce the golden numbers
```
The golden eval builds silver from the committed bronze and asserts the 2026
figures (full 2,102; half 4,309; 10K 3,396; medians 4:18:24 / 3:53:29 / 2:00:24 /
1:02:07; fastest 2:22:42) plus the full year-on-year counts. It runs in CI as the
required `golden-eval` gate.
