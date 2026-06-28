# Build prompts

Paste-ready prompts for driving the race-agents build with Claude Code. They
assume the `CLAUDE.md` contract is loaded, but each restates the load-bearing
rules so it survives a fresh context window:

- **Claude Code builds it** — write the code, run the tests, commit. Not handed
  back as an exercise.
- **Track decisions** — JOURNAL entry per session, ADR per structural/interface
  change (this repo is blog raw material).
- **The deterministic analysis is the golden source** — each agent is built fresh
  for its tier and validated against its numbers (ADR 0002).

The four phase prompts are **sequential** — run one phase at a time; each ends
green (`make test`) and committed before the next.

---

## Phase 1 — build agent 01 (stateless tool caller)

```
Build agents/01-stateless fresh from docs/architecture/Repo_1_The_Stateless_Tool_Caller.md
and the per-tier ADRs. Don't port a prior implementation wholesale — this tier's
architecture is the point.

- Single-turn, zero-memory Think-Act-Observe loop; OpenAI-compatible client
  (Ollama default, Claude swappable via base_url).
- Raw function-calling tools (compute_stat, get_club_stats, list_columns) with the
  open, MCP-portable schema (ADR 0003). No MCP server at this tier.
- Data plane: read-only static SQLite silver; all access behind one
  backend/silver.py repository function, no hand-written SQL scattered through
  tools (ADR 0004). Stats computed in Python ("numbers from code").
- Build silver from bronze via racedata.get_bronze_store().
- Guardrails: argument clamping, intent/scope classification, PII never reaches
  the model context.
- Golden eval (eval/golden.py): assert tool observations reproduce the
  deterministic ancestor's numbers (cork-city-marathon-analysis); this lights up
  the golden-eval CI gate.
- Self-contained: own pyproject, README, Dockerfile, Streamlit single-turn app.py.
  Only shared import is racedata; never import from other agents.
- Build directly — write code, run `make test`, fix until green. Then a JOURNAL
  entry + an ADR for any structural choice; open a small PR.
```

## Phase 2 — agent 02 (multistep / LangGraph)

```
Build agents/02-multistep per docs/architecture/Repo_2_The_Multistep_Workflow.md.
This is the orchestration + eval + fault-tolerance tier.

- LangGraph state machine running bronze→silver→gold: retries on the bronze
  fetch, parallel race processing, conditional routing, a human-in-the-loop
  approval gate before the gold report, and a self-criticism node.
- It regenerates its OWN silver through the pipeline (do not reuse agent 01's
  silver — that difference is the architecture being shown).
- Implement robust statistical tools (bootstrap CI, permutation test, robust
  estimators); agent 02 owns its own copy.
- Trace-level eval: an LLM-judge node validates each step's output before
  proceeding.
- Self-contained (own deps/README/Dockerfile); only shared import is racedata.
- Build directly, test, then JOURNAL entry + ADR(s) for the orchestration and
  eval choices. Commit on a branch.
```

## Phase 3 — agent 03 (memory-first / pgvector)

```
Build agents/03-learning per docs/architecture/Repo_3_The_Agent_that_Learns.md.
This is the memory-first tier: a personalised club analyst across 2024–2026.

- Three memory tiers: in-context state blocks, pgvector retrieval, cross-session
  persistence. update_memory + search_historical_context tools.
- Proactive: on a returning user, recall their club/preferences and surface
  trends without being re-asked.
- Layers memory ON TOP of its own silver; pgvector via docker-compose in the
  agent dir. Self-contained; only shared import is racedata.
- Build directly, test, JOURNAL entry + ADR for the memory architecture and the
  context-pollution strategy. Commit on a branch.
```

## Phase 4 — agent 04 (multi-agent)

```
Build agents/04-multi-agent per docs/architecture/Repo_4_The_Multi_Agent_System.md.
Full-stack tier: autonomously generate the multi-page Cork 2026 report.

- Four specialists: Controller/Editor, Data Engineer (owns bronze→silver +
  emits a YAML data dictionary), Statistician (robust estimators, bootstrap CI,
  permutation tests), Visualizer (sandboxed charting).
- Controller decouples planning from execution and delegates in parallel.
- Trace-level eval on every handoff (LLM judge between agents); guardrails
  enforced per-agent at the tool layer.
- This agent's Data Engineer is what produces silver here. Self-contained; only
  shared import is racedata.
- Build directly, test, JOURNAL entry + ADRs for the coordination protocol and
  handoff-eval design. Commit on a branch.
```

---

## Reusable — start and end of every session

```
Session start: read CLAUDE.md and the latest JOURNAL.md entry, summarise where we
are, and tell me the next buildable step before writing code.
```

```
Session end: append a JOURNAL.md entry (date, Claude model, what was built,
decisions made, what was hard), add/update any ADRs for decisions made this
session, and stage a branch commit that references them. This repo is blog raw
material — don't skip the trail.
```
