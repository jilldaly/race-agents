# ADR 0005 — Charts are deterministic tools (render to disk, return reference + numbers)

**Status:** accepted (Phase 1).

**Context.**
Agent 01 should return story visualizations matching the deterministic Cork report
(the golden source). But two tier-01 rules pull against that: chart **pixels must
never enter the model context** (control/data plane split, ADR 0003), and **numbers
come from code, not the model**. A chart is also not pixel-comparable, so naively
returning images would put a whole capability outside the golden gate. We needed a
way to surface charts that keeps the control/data plane intact and keeps charts
**gradeable**.

**Decision.**
1. A chart is a normal function-calling **tool** that renders a matplotlib PNG to a
   gitignored `output/` dir and returns a **compact JSON reference**: the numbers it
   plots + the file path + a one-line caption. The model receives only that
   reference (a path string + numbers), never the pixels.
2. The **Streamlit app** renders the PNG from the trace; the model narrates from the
   numbers that travelled with it.
3. Charts are graded by the **numbers they encode** — asserted against the golden
   source in `eval/golden.py` — plus a **render smoke test** (valid, non-empty PNG).
   No pixel-diffing. Same computation feeds the plot and the assertion, so a chart
   cannot drift from the verified figures.
4. Plotting logic is **adapted from the report `.py` files**; data flows through the
   **silver repository** (`silver.load_frame`, ADR 0004), not the report's own
   loader. Report schema (`Full`/`sec`) is mapped to silver (`full`/`time_sec`).
5. Scope is capped at **story archetypes** (gender, age-group, club; each
   snapshot + 2024–26 trend), chosen by the question — not BI-style free
   exploration. Comprehensive deep-dives belong to tiers 03/04.

**Consequences.**
- Control/data plane stays intact; "numbers from code" holds for charts too.
- Charts live under the same required `golden-eval` gate as stats.
- Agent 01 gains `matplotlib`/`numpy`/`pandas` (allowed under per-agent isolation;
  it fattens the "lean" agent — a conscious trade for visualization).
- The pattern is reused unchanged across the three story tools.
