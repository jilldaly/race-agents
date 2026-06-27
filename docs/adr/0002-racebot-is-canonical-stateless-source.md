# ADR 0002 — `racebot` is the canonical stateless source

**Status:** accepted (Phase 0).

**Context.** Two earlier repos implement a stateless-ish agent over the same Cork
data: `racebot` (`~/dev/racebot`, a ~120-line stateless tool-caller with
statistical tools and a golden-number eval) and `race-report-agent` (a
schema-driven skill registry). Agent 01 here needs exactly one upstream to port
from, so the stateless patterns have a single source of truth and the same code
is not ported twice.

**Decision.**
1. `racebot` is the canonical upstream for `agents/01-stateless`. Its first-pass
   code is preserved in git tag `v1-stateless-firstpass` (see ADR 0001).
2. Port `racebot`'s `tools/`, agent loop, eval, and tests into agent 01, and
   repoint its silver builder at `racedata.get_bronze_store()`.
3. When a stateless pattern is in question — control/data plane split, tool
   schemas, statistical tools, eval harness — `racebot` decides, not
   `race-report-agent`. `race-report-agent` is treated as a parallel sibling, not
   an input to this repo.

**Consequences.** No double-porting of the stateless tier. `race-report-agent`'s
skill-registry ideas remain available as reference for agent 02 (multistep) but
do not feed agent 01. `racebot` should be kept readable until the port lands.
