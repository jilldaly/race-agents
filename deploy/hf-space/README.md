---
title: Cork Marathon Fact-Checker
emoji: 🏃
colorFrom: blue
colorTo: pink
sdk: docker
app_port: 8501
pinned: false
license: mit
---

# Cork City Marathon — quick fact-checker

A stateless tool-calling agent that answers natural-language questions about the
Cork City Marathon results (Full / Half / 10K, 2024–2026). It computes every
statistic in code and draws story charts (gender split, trends) — the model only
narrates the numbers, it never invents them.

Ask things like *"What % of 2026 marathon finishers were female?"* or *"Show the
gender split of the 2026 races."*

Privacy: this app uses only **aggregated, name-free** race data — no individual
runners' names or bib numbers are stored or shown.
