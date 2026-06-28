# race-agents

Four AI agents, one marathon dataset, four tiers of the 2026 AI agents stack.

Each agent answers questions / builds reports about the Cork City Marathon, but
each is built at a different rung of the stack — from a stateless fact-checker to
a four-specialist report synthesizer. The point is to show, on identical data,
what each architecture buys you and what it costs.

![Four agent types, four starting stacks — the 2026 AI agents stack applied to marathon data](docs/architecture/AI_Agents_Processing_Marathon_Data.png)

| Agent | Persona | Architecture |
|-------|---------|--------------|
| [`agents/01-stateless`](agents/01-stateless)   | Journalist's Quick Fact-Checker    | stateless tool caller |
| [`agents/02-multistep`](agents/02-multistep)   | Analyst's Data-Cleaning Assistant  | multistep workflow (LangGraph) |
| [`agents/03-learning`](agents/03-learning)     | Coach's Proactive Club Dashboard   | memory-first (pgvector) |
| [`agents/04-multi-agent`](agents/04-multi-agent)| Race Director's Report Synthesizer | multi-agent system |

The agents share **only** the bronze (raw) data layer, via the
[`racedata`](packages/racedata) package. Design rationale lives in
[`docs/four-agent-monorepo-plan.md`](docs/four-agent-monorepo-plan.md).

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
make install
make test
```

## Status
Phase 0 (scaffold) complete: `racedata` built and tested. Agents land in
sequence — see the plan doc.
