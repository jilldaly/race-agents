# ADR 0001 — One monorepo, shared bronze only

**Status:** accepted (Phase 0).

**Context.** Four agents demonstrate four tiers of the agent stack on one
dataset. They need different front ends, back ends, and dependencies, but should
not duplicate raw-data handling.

**Decision.**
1. One monorepo. Each agent is self-contained under `agents/NN-*` with its own
   deps, README, and Dockerfile; agents never import each other.
2. Share **only** the bronze layer, via a `racedata` package exposing a
   `BronzeStore` interface (`LocalStore` now, `ObjectStore` later). Silver/gold
   stay per-agent because how each agent builds them is the architecture being
   shown.
3. The repo reuses the existing `jilldaly/racebot` remote; the first-pass
   stateless code is preserved in git tag `v1-stateless-firstpass` and ported
   into agent 01 rather than carried as working-tree legacy.

**Consequences.** Hosting later is a config change (`BRONZE_BACKEND`,
OpenAI-compatible `base_url`), not a rewrite. Each agent deploys independently.
