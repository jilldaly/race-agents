# ADR 0003 — Tool transport per tier: function-calling now, MCP where it earns its keep

**Status:** accepted (Phase 0).

**Context.**
The 2026 reference stack this repo demonstrates — The AI Engineer "Pick Your
Stack" infographic and O'Reilly's *The AI Agents Stack (2026 edition)* — lists
**MCP** in both the stateless (`Provider SDK + MCP + Postgres`) and multistep
(`LangGraph + MCP + eval`) stacks. MCP is part of the canonical stack from tier
01 up, and we will not pretend otherwise.

Two layers are easy to conflate:

- **Function-calling** — the provider API mechanism by which the model emits a
  structured tool call (name + JSON args). This is *how the model invokes a
  tool*. racebot (our canonical 01) already uses it:
  `client.chat.completions(..., tools=TOOL_SCHEMAS)` reading `msg.tool_calls`.
- **MCP (Model Context Protocol)** — a client/server protocol for *hosting and
  discovering* tools (and resources/prompts) over a standard interface. This is
  *how tools are served and shared*. With MCP the model still uses
  function-calling; an MCP client translates the call to an MCP server.

So the real question is **not** "function-calling vs MCP" — 01 uses
function-calling regardless — but "do we also stand up an MCP server for these
tools?"

**Decision.**
1. Tiers **01 and 02** use **raw function-calling** with the open tool schema.
   No MCP server.
2. Tiers **03 and 04** introduce **MCP** where it is load-bearing: 03 to expose
   shared memory/retrieval tools, 04 to give the multi-agent system a real
   tool/resource boundary alongside A2A handoffs.
3. Tool schemas stay **MCP-portable** — promoting a tool to an MCP server later
   is a wrapping change, not a rewrite.

**Why we deviate from the reference stack at 01/02 (deliberately).**
- **THE ONE RULE negates MCP's main payoff here.** MCP's biggest win is reuse
  across processes/hosts/agents. This repo keeps tools/silver/gold **per-agent**
  on purpose (only bronze is shared) — that separation *is* the architecture
  being demonstrated. There is no cross-agent tool reuse for MCP to standardize
  at 01/02.
- **No external consumer yet.** Nothing outside the agent (Claude Desktop,
  another team's client) consumes these tools. MCP's portability tax buys
  nothing until a second consumer exists.
- **01 is the "simplest path / ship in days" tier.** A separate MCP server
  process cuts against the "~120 lines you can read" minimalism that is the
  point of tier 01.
- **Better blog narrative.** "Here is exactly where MCP earns its tax (04), and
  why 01 doesn't need it yet" is more honest and more useful than wiring every
  box from the diagram.

**Consequences.**
- Any agent can adopt MCP the moment a second consumer or a shared-tool boundary
  appears; the open schemas make that cheap.
- When we do (tiers 03/04): per the stack article, 82% of audited MCP servers
  were path-traversal-vulnerable — enforce authorization at the tool-execution
  layer and validate all inputs server-side (see future guardrails ADR).
- The deviation is documented, so the write-up can defend "we read the stack and
  chose where each layer earns its keep" rather than cargo-culting it.
