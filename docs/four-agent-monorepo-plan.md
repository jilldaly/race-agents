# Four-Agent Monorepo — design & build plan

One repo, four agents, each demonstrating a different tier of the 2026 AI
agents stack against the same Cork City Marathon data. The four map directly to
your architecture docs and the infographic personas:

| # | Agent (dir) | Persona | Stack tier it demonstrates |
|---|---|---|---|
| 01 | `stateless` | The Journalist's Quick Fact-Checker | Stateless tool caller — models + tools only |
| 02 | `multistep` | The Analyst's Data-Cleaning Assistant | Multistep workflow — orchestration + eval + fault tolerance |
| 03 | `learning` | The Coach's Proactive Club Dashboard | Agent that learns — memory-first, cross-session |
| 04 | `multi-agent` | The Race Director's Report Synthesizer | Multi-agent system — the full stack |

Decisions locked in for this plan: **one monorepo**, a **shared `racedata`
package with a pluggable bronze store**, and **`racebot` as the canonical source
of truth for the stateless tier**, ported into agent 01 (see ADR 0002).

## The one rule that shapes everything

Each agent has its **own front end, own back end, own dependencies, own
Dockerfile, own README**. The *only* thing they share is the **bronze layer**
(raw race results) and the small package that reads it. Silver (cleaned tables)
and gold (reports) are deliberately **not** shared — each agent builds its own,
because *how* it does that is the architecture being demonstrated:

- 01 reads a pre-built static silver parquet (read-only, zero pipeline).
- 02 regenerates silver through a LangGraph pipeline with retries + HITL.
- 03 layers pgvector memory on top of silver.
- 04 has a dedicated Data-Engineer sub-agent produce silver for the others.

Sharing silver would erase the very differences the repo exists to show.

## Repository layout

```
race-agents/                      # suggested name (yours to pick — see below)
├── README.md                     # portfolio narrative: the 4 tiers, one dataset
├── pyproject.toml                # workspace-level dev tooling (ruff, pytest)
├── .gitignore
│
├── packages/
│   └── racedata/                 # the ONLY shared code
│       ├── pyproject.toml        # installable: `pip install -e packages/racedata`
│       ├── racedata/
│       │   ├── store.py          # BronzeStore protocol (abstract interface)
│       │   ├── local_store.py    # filesystem impl — the PDFs you have today
│       │   ├── object_store.py   # S3 / GCS / R2 impl — for scraping + hosting
│       │   ├── manifest.py       # registry of race/year/distance + meta.yaml
│       │   └── scrape.py         # future scraper — writes INTO the bronze store
│       └── tests/
│
├── data/
│   └── bronze/                   # canonical raw layer (local dev)
│       └── cork/<year>/results_{full,half,10k}.pdf
│
├── agents/
│   ├── 01-stateless/
│   │   ├── README.md  pyproject.toml  Dockerfile
│   │   ├── app.py                # Streamlit single-turn chat
│   │   ├── backend/              # tools/, agent loop, silver builder
│   │   ├── eval/                 # golden questions (LLM-free)
│   │   └── tests/
│   ├── 02-multistep/
│   │   ├── README.md  pyproject.toml  Dockerfile
│   │   ├── app.py                # Streamlit + human-approval checkpoint
│   │   ├── backend/              # LangGraph nodes, retry logic, robust stats
│   │   └── tests/
│   ├── 03-learning/
│   │   ├── README.md  pyproject.toml  Dockerfile  docker-compose.yml  # app + pgvector
│   │   ├── app.py                # club dashboard UI
│   │   ├── backend/              # memory blocks, pgvector retrieval
│   │   └── tests/
│   └── 04-multi-agent/
│       ├── README.md  pyproject.toml  Dockerfile
│       ├── app.py                # report request UI / service
│       ├── backend/              # controller + data-engineer + statistician + visualizer
│       └── tests/
│
├── docs/
│   ├── architecture/             # your 4 arch md files, moved here
│   ├── infographic.png
│   └── adr/                      # architecture decision records (one per big call)
│
└── .github/workflows/ci.yml      # matrix: test each agent + racedata independently
```

## The shared boundary: `racedata` and the bronze store

This package is the seam that lets "local PDFs now → scraped + cloud-hosted
later" be a **config change, not a rewrite**. Every agent imports it; none of
them know where bronze actually lives.

```python
# racedata/store.py
class BronzeStore(Protocol):
    def list_races(self) -> list[RaceRef]: ...                 # what's available
    def open(self, race, year, distance) -> BinaryIO: ...      # read raw bytes
    def put(self, race, year, distance, data: bytes): ...      # scraper writes here

def get_bronze_store() -> BronzeStore:
    # BRONZE_BACKEND=local (default) | s3 | gcs
    ...
```

`LocalStore` points at `data/bronze/` (the PDFs you already have). `ObjectStore`
points at an S3/GCS/R2 bucket. The future `scrape.py` is just another *producer*
that calls `store.put(...)` — every consuming agent is unchanged whether the
bronze came from a download or a live scrape. Bronze is immutable: producers
add, agents only read.

`manifest.py` carries the `meta.yaml` convention (race, year, distance,
source URL, fetched-at, checksum) so provenance survives the move to scraping.

## Per-agent stack at a glance

| | Front end | Back end / framework | LLM transport | State store | New deps vs 01 |
|---|---|---|---|---|---|
| **01 stateless** | Streamlit, single-turn | raw `openai` SDK + function tools, `while` loop | OpenAI-compatible (Ollama local) | static silver parquet | — |
| **02 multistep** | Streamlit + approval gate | **LangGraph** state machine, retry/parallel nodes | same | silver regenerated per run; trace logs | langgraph |
| **03 learning** | dashboard | raw SDK + memory blocks + retrieval | same | **Postgres + pgvector** | pgvector, psycopg |
| **04 multi-agent** | report UI / service | controller + 3 specialists, A2A handoffs | same | per-agent + shared blackboard | (orchestration) |

Everything talks to the model through the **same OpenAI-compatible client**, so
swapping Ollama for a hosted open-weight endpoint later is a `base_url` + key
change — no agent rewrite.

## Build sequence (phased, each phase ships something runnable)

**Phase 0 — scaffold the monorepo.** Create the tree above. Move the 4 arch docs
and infographic into `docs/`. Build `racedata` wrapping the current local PDFs;
define `BronzeStore`, `LocalStore`, and the manifest. Write its tests. Nothing
agent-facing yet, but bronze access is now abstracted.

**Phase 1 — refactor `racebot` → `agents/01-stateless`.** Lift its working
`tools/`, agent loop, silver builder, eval, and tests in. The one change: its
silver builder now reads bronze via `racedata.get_bronze_store()` instead of a
hardcoded path. Archive the old `racebot` repo (README pointer to its new home).
This is your apprenticeship-friendly worked example for the porting pattern.

**Phase 2 — `agents/02-multistep`.** New back end on LangGraph: bronze→silver→gold
pipeline with retry loops, parallel race processing, robust stats (median/MAD,
bootstrap CIs), and a human-approval checkpoint before the gold report. Evals on
every node.

**Phase 3 — `agents/03-learning`.** Memory-first: pgvector via docker-compose,
named memory blocks, `update_memory` / `search_historical_context` tools,
cross-session club tracking across 2024–2026.

**Phase 4 — `agents/04-multi-agent`.** Controller + Data-Engineer + Statistician
+ Visualizer, A2A handoffs, trace-level eval on each handoff, guardrails per
sub-agent (the Visualizer can't scrape, etc.). Output: the full report artifact.

**Phase 5 — scraping + hosting** (below).

## Hosting path (you raised this for "later")

The architecture is already hosting-ready because of two choices: each agent is
self-contained with its own Dockerfile, and bronze + LLM are both behind
swappable interfaces.

- **Bronze:** flip `BRONZE_BACKEND=local` → `s3`/`gcs`/`r2`. Same code.
- **LLM:** Ollama doesn't host cheaply. For hosted demos, point the same
  OpenAI-compatible client at a hosted open-weight endpoint (Groq, Together,
  OpenRouter, Fireworks) via `base_url` + key — or run Ollama on a GPU VM.
- **Where each app can run:** 01 and 02 are stateless web apps → Streamlit
  Community Cloud, Hugging Face Spaces, Fly.io, Render, or Railway. 03 and 04
  need Postgres/pgvector → add managed PG (Supabase, Neon, or RDS). CI builds a
  per-agent image so each deploys independently.

Because agents are isolated, you can host them one at a time as each is ready,
and a problem in one never blocks the others.

## A few open choices to confirm as we go

- **Repo name** — `race-agents`, `agent-stack-lab`, `marathon-agents`, or
  `race-agent-stack`. I lean `race-agents`: short, accurate, room to grow.
- **Bronze in git or not** — the PDFs are large and currently gitignored. I'd
  keep them out of git and treat the object-store bucket as canonical once
  scraping lands; for local dev, a `make fetch-bronze` pulls them down. (Git-LFS
  is the alternative if you want them versioned in-repo.)
- **Python packaging** — a light workspace (uv or a top-level pyproject) so
  `racedata` installs editable into each agent's venv, while each agent still
  pins its own framework deps independently.

## Why this satisfies your constraints

Different front and back ends per agent → enforced by full per-agent isolation.
Share only bronze → the *only* shared import is `racedata`; silver/gold are
per-agent on purpose. Scrape later → the scraper is just another bronze
producer behind the same interface. Host later → bronze and LLM are both
config-swappable, and every agent already containerizes on its own.
