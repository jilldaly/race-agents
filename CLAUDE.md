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
`racedata` package built and tested. Agent dirs are placeholders.

**`racebot` is the canonical upstream for the stateless tier.** Agent 01 is built
by porting `racebot` (`~/dev/racebot`, git tag `v1-stateless-firstpass`) into
`agents/01-stateless`: lift its `tools/`, agent loop, eval, and tests, and
repoint its silver builder at `racedata.get_bronze_store()`. When a stateless
pattern is in question — control/data plane split, tool schemas, the statistical
tools, the eval harness — `racebot` is the source of truth, not
`race-report-agent`. Next: Phase 1 executes that port. See
`docs/adr/0002-racebot-is-canonical-stateless-source.md`.

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

## Build mode — Claude Code builds this
Claude Code implements the agents directly and autonomously: write the code, run
the tests, commit. Do **not** hand work back as an exercise or stop at guidance —
that apprenticeship split belongs to the sibling `race-report-agent` repo, not
here. Pause for input only when an architectural decision is genuinely ambiguous;
otherwise build it.

## Decision tracking — this repo is blog raw material
The Substack write-up is about *how it was built*, so every architecture and code
decision must leave a trail:
- **`JOURNAL.md`** — append an entry at the end of every working session: date,
  Claude model used, what was built, decisions made, what was hard. This is the
  narrative spine of the blog; never skip it after a significant change.
- **`docs/adr/`** — for any decision that changes structure, an interface, or a
  dependency, add a numbered ADR (context → decision → consequences). Cite the
  ADR number from the matching JOURNAL entry and the commit message.
- If a choice can't be justified in one paragraph, it isn't ready to commit.
