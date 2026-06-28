# Eval strategy — golden is the verdict, judges are sensors

Evaluation is infrastructure here, not an afterthought. (O'Reilly's 2026 stack
survey: 89% of teams have observability but only 52% have evals — a 37-point gap.
"Most teams skip eval until something breaks in production. By then they're
debugging blind." We don't.)

## Two axes

**Axis 1 — Deterministic golden baseline = the verdict.**
- LLM-free, network-free. A stub router scripts the tool calls; the *real* tool
  observations are asserted against numbers from the human-validated sample
  report (`racebot/sample_report/cork_2026_report.pdf`).
- Anchored golden numbers from that report:
  - Marathon 2026 — 2,102 finishers; fastest 2:22:42; median 3:57:09; female
    median 4:18:24.
  - Half 2026 — 4,309 finishers; median 2:00:24.
  - 10K 2026 — 3,398 finishers; median 1:04:11.
  - All races — 9,809 finishers (5,260 M / 4,549 F).
- This is the source of truth. Numbers must reproduce **exactly**. No LLM gets
  to override it.

**Axis 2 — LLM-as-judge / trace evals = sensors.**
- LLM judges score *quality* and *flow* at the orchestration tiers (02 node
  outputs, 04 handoffs). They catch silent mid-pipeline failures ("wrong tool at
  step 3 ruins steps 4–12").
- They are **sensor data, never verdicts** (O'Reilly *Agentic Code Review*:
  "Treat AI review as sensor data, never as verdicts"). A judge can flag, never
  bless. If a judge passes but the golden gate fails, the golden gate wins.

## The trust rule

The person who clicks merge owns what ships; a green check from an LLM is
"borrowed confidence" unless a deterministic gate earned it. So **the golden
baseline is the gate that must be green to merge; judges only triage attention.**
That is how this solo, green-field project earns trust without a human reading
every diff — numbers are proven by reproduction, not by the model's say-so.

## Per-tier eval

| Tier | Golden (verdict) | Judge / trace (sensor) | Human gate |
|---|---|---|---|
| 01 stateless | golden-question eval (ported from racebot `eval/golden.py`) | — | review + merge |
| 02 multistep | same golden numbers after pipeline rebuild | LLM-judge per node before proceeding | approval gate before gold report |
| 03 learning | golden numbers + memory-retrieval correctness | judge: was the right past analysis recalled? | review |
| 04 multi-agent | Data-Engineer silver must hit golden numbers | LLM-judge on every agent handoff | review of final report |

## Cadence (maps to O'Reilly stack Layer 5)

- **Fast PR check** — golden eval runs in CI on every push/PR. Required gate
  (`.github/workflows/ci.yml`, job `golden-eval`).
- **Nightly regression** — full golden suite + judge evals across tiers (added
  as agents land).
- **Production monitoring** — deferred: green-field, no users yet. Wire when
  there is traffic.

## The gold target

The sample report (`racebot/sample_report/cork_2026_report.pdf`, 22 pp) is the
**example of the output the agents produce dynamically** — a cover + four
sections (Overall Marathon 2026, Marathon Trend 2024–26, All Clubs Overall, All
Clubs Trend), per-race stat tables, finish-time histograms, age-group and gender
trends, and finish-time box plots. Tier 04's job is to generate this report
end-to-end; every golden number above is lifted from it, so "does the agent
reproduce the report's numbers" is the falsifiable bar for the whole repo.
