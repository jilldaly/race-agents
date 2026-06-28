# ADR 0002 — Golden source is the deterministic analysis; agents built fresh

**Status:** accepted (Phase 0).

**Context.**
A deterministic Python report generator already turns the official Cork City
Marathon results (2024–2026) into a fixed, human-validated PDF analysis
([`cork-city-marathon-analysis`](https://github.com/jilldaly/cork-city-marathon-analysis)).
Its numbers are reproducible and checked. The agents here must not silently
diverge from those numbers — but each agent's *architecture* is the thing being
demonstrated, so we also don't want to inherit one fixed implementation.

**Decision.**
1. The deterministic analysis is the **golden source of truth**. Its published
   report (`analog_devices_cork_marathon_analysis.pdf`) anchors the golden-eval
   numbers every tier is checked against (see `docs/eval-strategy.md`).
2. Each agent is **built fresh** for its tier from the architecture specs
   (`docs/architecture/`) — not ported wholesale from any single prior
   implementation. *How* an agent computes the numbers is the architecture on
   display; *which* numbers it must reach is fixed by the golden source.
3. The only shared seam stays the bronze layer (`racedata`, ADR 0001); silver and
   gold are per-agent.

**Consequences.**
- Correctness is falsifiable without coupling agents to one codebase: the golden
  eval is the gate, the deterministic report is the reference.
- Each tier is free to use the data plane, framework, and tools its architecture
  calls for (ADRs 0003, 0004), so long as it reproduces the golden numbers.
