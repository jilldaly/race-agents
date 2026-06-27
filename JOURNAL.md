# race-agents Build Journal

Append-only log of how race-agents was built — what was created each session,
what decisions were made, and what was learned. Raw material for the Substack
write-up on building the four-tier agent stack. Add an entry at the end of every
working session.

---

## 2026-06-27 — Build mode set: Claude Code builds, decisions tracked

**Agent:** Claude (Opus 4.8) via Claude Code · **Human:** Jill Daly

**Session summary:**
Set the working contract for this repo before implementation starts. Reversed the
apprenticeship model used in `race-report-agent`: here Claude Code builds the
agents directly and autonomously rather than guiding from the sidelines. Made the
blog the explicit reason for disciplined decision tracking, and named `racebot`
as the single canonical upstream for the stateless tier.

**Key decisions:**
- **Build mode = Claude Code builds it** (not apprenticeship). Pause only on
  genuinely ambiguous architecture; otherwise write, test, commit. (CLAUDE.md
  "Build mode" section.)
- **Decision tracking is mandatory** — JOURNAL entry per session + an ADR for any
  structural/interface/dependency change, cross-referenced from commits. The repo
  exists partly to be blogged about, so the trail is a deliverable, not overhead.
- **`racebot` is canonical for the stateless tier** — agent 01 ports from
  `racebot` (tag `v1-stateless-firstpass`), and `racebot` is the source of truth
  over `race-report-agent` for any stateless pattern. (ADR 0002.)

**Files changed:**
CLAUDE.md (Status + new "Build mode" and "Decision tracking" sections, replacing
the apprenticeship note), docs/adr/0002-racebot-is-canonical-stateless-source.md
(new), JOURNAL.md (new).

**Next:** Phase 1 — port `racebot` into `agents/01-stateless`.
