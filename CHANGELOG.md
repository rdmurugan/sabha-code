# Changelog

All notable changes to Sabha Code will be documented here. Format follows [Keep a Changelog](https://keepachangelog.com/).

> **Origin:** project conceived 2026-05-18 as the developer-focused sibling of [Sabha OS](https://github.com/rdmurugan/sabhaos). First public release same day.

## [0.1.0] — 2026-05-18

### Initial release

- **`.github/copilot-instructions.md`** — the protocol; this IS Sabha Code. Routing-at-top-of-reply discipline, Chanakya voice, ask/engage mode discipline, grounding rules.
- **7 role instruction files** in `instructions/`:
  - `architect.instructions.md` — system design, ADRs, tech stack
  - `reviewer.instructions.md` — code review, naming, refactor calls
  - `security.instructions.md` — OWASP-shaped, threat modeling
  - `performance.instructions.md` — measure-first, hot-path-only
  - `qa.instructions.md` — test strategy, flake hunting
  - `mentor.instructions.md` — show why, not just how
  - `techlead.instructions.md` — synthesis, founder-mode calls
- **Documentation:**
  - `README.md` — pitch + install + 7-role table + how it differs from raw Copilot custom instructions
  - `docs/QUICKSTART.md` — 10-min install, including `memory/` folder setup with worked example
  - `docs/CUSTOMIZATION.md` — renaming roles, voice tuning, `applyTo` per-file routing
  - `docs/PHILOSOPHY.md` — the 5 disciplines, the Chanakya tradition, what it's NOT
- **Install paths documented:** `npx degit`, `gh repo create --template`, manual copy.
- **MIT License.** Copyright Durai Rajamanickam (@rdmurugan).
- **No code dependencies.** Pure markdown protocol. Works with any Copilot-supported IDE and any LLM Copilot uses (GPT-4 / Claude / Gemini).

### Relationship to Sabha OS

Sabha Code is the developer-focused sibling of [Sabha OS](https://github.com/rdmurugan/sabhaos) (started October 2025). Same protocol shape — *route, recommend, name the tradeoff, mode discipline, ground in memory* — adapted to engineering questions and GitHub Copilot's distribution surface. The two projects are independent but complementary: Sabha OS for C-suite/operator decisions in Claude Code, Sabha Code for engineering decisions in Copilot.
