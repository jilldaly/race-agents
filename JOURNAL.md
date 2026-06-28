# race-agents Build Journal

Append-only log of how race-agents was built — what was created each session,
what decisions were made, and what was learned. Raw material for the Substack
write-up on building the four-tier agent stack. Add an entry at the end of every
working session.

---

## 2026-06-27 — Build mode set: Claude Code builds, decisions tracked

**Agent:** Claude (Opus 4.8) via Claude Code · **Human:** Jill Daly

**Session summary:**
Set the working contract for this repo before implementation starts. Claude Code
builds the agents directly and autonomously rather than guiding from the
sidelines. Made the blog the explicit reason for disciplined decision tracking,
and named the deterministic analysis as the golden source agents are validated
against.

**Key decisions:**
- **Build mode = Claude Code builds it** (not guidance-only). Pause only on
  genuinely ambiguous architecture; otherwise write, test, commit. (CLAUDE.md
  "Build mode" section.)
- **Decision tracking is mandatory** — JOURNAL entry per session + an ADR for any
  structural/interface/dependency change, cross-referenced from commits. The repo
  exists partly to be blogged about, so the trail is a deliverable, not overhead.
- **Golden source = the deterministic analysis** (`cork-city-marathon-analysis`) —
  each agent is built fresh for its tier and validated against its numbers, rather
  than inheriting a prior implementation. (ADR 0002.)

**Files changed:**
CLAUDE.md (Status + new "Build mode" and "Decision tracking" sections),
docs/adr/0002-golden-source-and-build-fresh.md (new), JOURNAL.md (new).

**Next:** Phase 1 — build `agents/01-stateless`.

---

## 2026-06-28 — Tool transport, eval strategy, golden CI gate

**Agent:** Claude (Opus 4.8) via Claude Code · **Human:** Jill Daly

**Session summary:**
Locked three architecture decisions and the trust story before agent 01 lands,
and tied each to the source material so the blog has citations. Confirmed the
sample report is the example of the dynamic output the agents produce.

**Key decisions:**
- **Tool transport per tier (ADR 0003).** The reference stack we demonstrate
  (The AI Engineer "Pick Your Stack"; O'Reilly *AI Agents Stack 2026*) puts MCP
  at 01/02. We deliberately defer it: 01/02 use raw function-calling with the
  open, MCP-portable tool schema; MCP is introduced at 03/04 where a real
  tool/resource boundary exists. Rationale: THE ONE RULE keeps tools per-agent
  (no reuse for MCP to standardize), no external consumer yet, and 01 is the
  "ship in days" minimal tier. Fixed the Repo_1 spec to stop claiming MCP.
- **Eval strategy: golden = verdict, judges = sensors** (`docs/eval-strategy.md`).
  The deterministic golden baseline (reproduces sample-report numbers, LLM-free)
  is the merge gate; LLM-judge/trace evals are sensor data that can flag but
  never bless. Maps to O'Reilly's three-tier eval cadence and *Agentic Code
  Review*'s "AI review is sensor data, not verdicts."
- **Golden eval wired as a required CI gate** (`.github/workflows/ci.yml`, job
  `golden-eval`) — runs once agent 01 lands, pending until then. Action: mark
  `golden-eval` as a required status check in branch protection.

**Why this matters (green-field framing):** no users yet, so production
monitoring and blast-radius tiering are deferred. The live application of
agentic code review is *reflexive* — the loop is "Claude builds, Jill reviews +
merges," so the golden gate is how trust is earned without reading every diff.

**The gold target:** confirmed the deterministic ancestor's report
(`analog_devices_cork_marathon_analysis.pdf`, 22 pp) is the example of the dynamic
output — four sections (Overall 2026,
Marathon Trend 2024–26, All Clubs Overall, All Clubs Trend), per-race stat
tables, finish-time histograms, age/gender trends, box plots. Golden numbers
(Marathon 2,102 / female median 4:18:24; 9,809 total) are lifted from it.

**References (blog raw material):**
- O'Reilly — *Agentic Code Review*: https://www.oreilly.com/radar/agentic-code-review/
- O'Reilly — *The AI Agents Stack (2026 edition)*: https://www.oreilly.com/radar/the-ai-agents-stack-2026-edition/

**Files changed:** docs/adr/0003-tool-transport-per-tier.md (new),
docs/eval-strategy.md (new),
docs/architecture/Repo_1_The_Stateless_Tool_Caller.md (MCP wording),
.github/workflows/ci.yml (golden gate), JOURNAL.md.

**Next:** Phase 1 — build agents/01-stateless (its golden eval lights up the CI
gate).

---

## 2026-06-28 — Data plane per tier (ADR 0004)

**Agent:** Claude (Opus 4.8) via Claude Code · **Human:** Jill Daly

**Session summary:**
Settled the data-plane question for all four tiers and the access pattern, after
weighing Postgres vs SQLite vs parquet against the O'Reilly stateless stack
(which prescribes Postgres).

**Key decisions (ADR 0004):**
- **SQLite at 01 and 02; Postgres from 03.** 01's data is static, small,
  read-only — a server DB is ceremony there (same reasoning as the MCP deferral,
  ADR 0003). 03 needs pgvector, so Postgres debuts there and runs through 04.
- **DB = store, not compute engine.** Tools `SELECT … WHERE …`; Python/pandas
  computes the stats. Keeps the SQL surface tiny and near dialect-free, so the
  SQLite→Postgres move is ~a connection-string change.
- **One small per-agent repository function** (`backend/silver.py`) fronts all DB
  access — no hand-written SQL scattered through tools, not shared across agents
  (THE ONE RULE). stdlib `sqlite3`, no heavy ORM at 01/02.

**Why SQLite won't hurt the 03/04 comparison:** dialect drift avoided by
computing in Python; no vector search in SQLite is irrelevant (03 is pgvector by
design); single-writer limit only matters for the write-heavy tiers, which use
Postgres anyway. Accepted tradeoff: 02 ("production standard") with SQLite reads
slightly less-production than Postgres — we favour minimalism.

**Decision lineage worth noting for the blog:** 01's two right-sizing calls
(function-calling not MCP; SQLite not Postgres) share one spine — *the reference
stack is a general default; this data is static/small/read-only, so both are
over-provisioned here, and each earns its keep at the exact later tier (MCP and
Postgres+pgvector at 03/04).* That consistency is the portfolio's argument.

**Files changed:** docs/adr/0004-data-plane-per-tier.md (new),
docs/four-agent-monorepo-plan.md (parquet → SQLite), JOURNAL.md.

**Next:** Phase 1 — build agents/01-stateless.

---

## 2026-06-28 — Intent + source of truth; agents built fresh

**Agent:** Claude (Opus 4.8) via Claude Code · **Human:** Jill Daly

**Session summary:**
Connected the repo to its purpose and finalised the source-of-truth model. The
four agents are four *users* with four needs (README "Why four agents"), built on
the same data the deterministic analysis already covers.

**Key decisions:**
- **Golden source = the deterministic analysis** (`cork-city-marathon-analysis`).
  ADR 0002 now states this; all sample-report references point to its published
  report (`analog_devices_cork_marathon_analysis.pdf`).
- **Agents are built fresh per tier**, validated against the golden numbers — the
  Phase 1 instructions across CLAUDE.md, build-prompts, the plan, and agent 01's
  README reflect this, and fold in ADRs 0003/0004 (function-calling, SQLite,
  repository function).
- **README "Why four agents"** (minimal): a deterministic-ancestor nod + a
  user → need → tier table; infographic (made with NotebookLM) as the anchor.

**Files changed:** README.md, docs/eval-strategy.md, ADR 0002 (replaced with
golden-source-and-build-fresh), ADR 0001/0003 reworded, CLAUDE.md,
docs/build-prompts.md, docs/four-agent-monorepo-plan.md, agents/01-stateless/README.md,
JOURNAL.md.

**Next:** Phase 1 — build agents/01-stateless.

---

## 2026-06-28 — Phase 1: silver builder + a finisher-counting rule

**Agent:** Claude (Opus 4.8) via Claude Code · **Human:** Jill Daly

**Session summary:**
Started Phase 1. Built the silver layer for agent 01 (`backend/silver.py`):
parses the bronze result PDFs into a read-only SQLite db via
`racedata.get_bronze_store()`. The bronze has **two layouts**, detected per-PDF
from the header: 2026 (`Bib Pos. … Chip Gun`, with the 10k swapping to `Gun
Chip`) and 2024/25 (`Rank … Time`, single time column, age-band codes). `time_sec`
is chip (net) where available.

**Decisions:**
- **A finisher is a row with a complete result tail** (sex + age-group + time).
  Placeholder rows the timing provider inserts without an age-group (e.g. "Contact
  POPUPRACES" in the 10k) are therefore **not counted**. Net effect: 10k 2026 =
  **3,396**, two fewer than the ancestor's published 3,398 — accepted as the clean
  athlete count (Jill's call). We do *not* hard-filter on the name; the
  complete-record rule is the definition.

**Validated (2026, exact against the golden source):** full 2,102; half 4,309;
full female median 4:18:24; full male median 3:53:29; half overall median 2:00:24.

**Open data questions (next):**
- **2024/25 counts are short** (e.g. full 1,835 vs golden 1,944) — the 2024/25
  layout needs more parser work (10k times likely lack the hour field; possible
  wrapped rows / age-band sub-headers).
- **10k 2026 median, chip vs gun:** chip (net) gives 1:02:07; the ancestor's
  published 1:04:11 was computed on *gun* time (a known inconsistency in the
  source report). Decision needed: stay chip-consistent (and update the golden
  number) or match the report's gun-based figure.

**Next:** settle the two data questions, finish the 2024/25 parser, then tools +
golden eval + agent loop + UI.

---

## 2026-06-28 — Phase 1 complete: agent 01 (stateless tool caller)

**Agent:** Claude (Opus 4.8) via Claude Code · **Human:** Jill Daly

**Session summary:**
Built agent 01 end-to-end on `feat/phase-1-stateless`. Stateless single-turn
fact-checker: control plane routes to deterministic tools, numbers come from code.

**What was built:**
- **silver** — both bronze layouts parsed to read-only SQLite; full exact all
  years, 2026 all races + medians exact.
- **tools** — `compute_stat` / `get_club_stats` / `list_columns` with
  function-calling schemas, arg guardrails, no PII; stats in Python.
- **golden eval** — LLM-free, 11/11 pass; lights the CI `golden-eval` gate (now
  real, since bronze is committed).
- **control plane** — Think-Act-Observe loop (loop owns termination via
  MAX_STEPS); router defaults to **Gemini free tier** (`gemini-2.0-flash`) via
  the OpenAI-compatible endpoint; system prompt enforces numbers-from-tools,
  param reporting, scope, no PII.
- **UI / packaging** — Streamlit single-turn app (shows the tool trace),
  pyproject, Dockerfile, README, `.env.example`; 7/7 unit tests via stub router.

**Decisions applied:** chip-consistent 10k median (1:02:07); 2026 is the golden
gate; placeholder rows excluded (finisher = complete record); bronze committed;
default control plane = Gemini free tier (reconciled CLAUDE.md / plan / build-prompts).

**Open / follow-ups:** 2024/25 half & 10k counts within ~0.3% of eyeballed trend
figures (not authoritative); a few scruffy 2024/25 age-group labels; live Gemini
run needs a key (loop verified via stub). 2026 — the gate — is exact.

**Next:** open the Phase 1 PR; then live-test with a Gemini key; then Phase 2.
