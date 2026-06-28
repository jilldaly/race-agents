# race-agents

One marathon dataset, 4 essential AI architectures of the 2026 AI agents stack.

Each  AI architectures answers questions / builds reports about the Cork City Marathon, but
each is built at a different rung of the stack — from a stateless fact-checker to
a four-specialist report synthesizer. The point is to show, on identical data,
what each architecture buys you and what it costs.

![Four AI architecture types, four starting stacks — the 2026 AI agents stack applied to marathon data](docs/architecture/AI_Agents_Processing_Marathon_Data.png)

## Why four  AI architectures

The numbers already exist: [`cork-city-marathon-analysis`](https://github.com/jilldaly/cork-city-marathon-analysis)
is the **deterministic ancestor** — a Python generator that turns official Cork
City Marathon results (2024–2026) into a fixed PDF analysis, and the source of
truth every agent here is validated against ([sample report](https://github.com/jilldaly/cork-city-marathon-analysis/blob/main/report_charts/analog_devices_cork_marathon_analysis.pdf)).
For one fixed report, deterministic code wins; agents earn their keep on
**variability** — different users, asking different things, for different
purposes. Same data, reframed around four users, each needing a different tier of
the 2026 stack (infographic above, made with NotebookLM):

| # | User — persona | What they need | Architecture tier |
|---|---|---|---|
| [01](agents/01-stateless)    | Journalist — quick fact-checker     | one grounded number, instantly, zero setup             | stateless tool caller |
| [02](agents/02-multistep)    | Analyst — data-cleaning assistant   | a repeatable, fault-tolerant pipeline with checkpoints | multistep workflow (LangGraph) |
| [03](agents/03-learning)     | Coach — proactive club dashboard    | memory of their club, tracked across seasons           | memory-first (pgvector) |
| [04](agents/04-multi-agent)  | Race director — report synthesizer  | the whole report, synthesized on demand                | multi-agent system |

The agents share **only** the bronze (raw) data layer, via the
[`racedata`](packages/racedata) package. Design rationale lives in
[`docs/four-agent-monorepo-plan.md`](docs/four-agent-monorepo-plan.md).

## Quickstart
```bash
brew install gh
python -m venv .venv && source .venv/bin/activate
make install
make test
```

## Status
Phase 0 (scaffold) complete: `racedata` built and tested. Agents land in
sequence — see the plan doc.
