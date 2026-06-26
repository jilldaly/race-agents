# race-agents — project context

## What this is
A monorepo holding **four AI agents**, each demonstrating a different tier of the
2026 AI agents stack against the **same Cork City Marathon dataset**. It is a
portfolio piece with a Substack write-up planned, so every architectural choice
should stay explainable and citable (`docs/adr/`).

| Dir | Agent | Persona | Tier demonstrated |
|-----|-------|---------|-------------------|
| `agents/01-stateless`  | Journalist's Quick Fact-Checker     | stateless tool caller (models + tools) |
| `agents/02-multistep`  | Analyst's Data-Cleaning Assistant   | multistep workflow (orchestration + eval) |
| `agents/03-learning`   | Coach's Proactive Club Dashboard    | agent that learns (memory-first) |
| `agents/04-multi-agent`| Race Director's Report Synthesizer  | multi-agent system (full stack) |

Full design rationale: `docs/four-agent-monorepo-plan.md`.

## THE ONE RULE
The **only** thing the four agents share is the **bronze layer** (raw race
results) and the `racedata` package that reads it. Silver (cleaned tables) and
gold (reports) are **per-agent on purpose** — *how* each agent builds them IS the
architecture being demonstrated. Never factor silver/gold into a shared package.

## Agent isolation
Each agent has its own front end, back end, dependencies, README, and Dockerfile.
The only shared import is `racedata`. An agent must never import from another
agent. Keep each one independently runnable and independently deployable.

## The shared seam: `racedata`
`packages/racedata` exposes a `BronzeStore` interface with `LocalStore`
(filesystem, today) and `ObjectStore` (S3/GCS, for hosting later). Agents call
`get_bronze_store()`; the backend is chosen by `BRONZE_BACKEND` env, not by code.
Bronze is append-only and immutable — producers `put()`, agents only read. The
future scraper is just another producer behind the same interface.

## Status (Phase 0 — scaffold)
`racedata` package built and tested. Agent dirs are placeholders. Next: Phase 1
ports the old `racebot` stateless agent into `agents/01-stateless` (lift its
`tools/`, agent loop, eval, tests; repoint its silver builder at
`racedata.get_bronze_store()`). The old code lives in git tag
`v1-stateless-firstpass`.

## Architecture rules that carry across all agents
- **Control plane vs data plane**: the LLM only chooses which tool/node to call.
  DataFrames, chart PNGs, and raw scrapes never enter the model context — tools
  return compact JSON summaries.
- **Numbers from code, words from the model**: the LLM never does arithmetic and
  never invents a statistic; it narrates computed values.
- **OpenAI-compatible transport everywhere**: a raw `openai` client pointed at
  Ollama by default. Swapping to a hosted endpoint is a `base_url` + key change.
- All config is env-overridable; model pricing is never hardcoded; default cost
  is $0 (local Ollama).

## Data layers
- **bronze** `data/bronze/<race>/<year>/results_<distance>.pdf` (+ `meta.yaml`):
  raw, immutable, shared, gitignored (large; bucket is canonical once hosted).
- **silver / gold**: per-agent, regenerable, never committed.

## Commands
```bash
make install     # editable racedata + dev tools
make test        # pytest across packages/ and agents/
make lint        # ruff
```

## Apprenticeship note
Porting the old racebot code into agent 01 is a deliberate learning exercise —
guide and review diffs rather than writing the whole implementation, unless asked
to implement directly. Prompt for a JOURNAL.md entry after each session (blog raw
material).
