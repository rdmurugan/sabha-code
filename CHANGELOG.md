# Changelog

All notable changes to Sabha Code will be documented here. Format follows [Keep a Changelog](https://keepachangelog.com/).

> **Origin:** project conceived 2026-05-18 as the developer-focused sibling of [Sabha OS](https://github.com/rdmurugan/sabhaos). First public release same day.

## [0.2.0] — 2026-05-18

### Added — reproducible eval harness

- **`evals/run_eval.py`** — adapted from the Sabha OS harness. Runs each question under two conditions (baseline / sabha_code), scores both with the v3 sub-axis rubric, runs pairwise preference, writes JSON + Markdown results to `evals/results/`. Same checkpoint-after-each-question + `--resume` ergonomics as upstream.
- **`evals/judge.py`** — the v3 sub-axis rubric reused verbatim from Sabha OS. Decisiveness, tradeoff_named, and length_discipline each decomposed into 5 binary sub-criteria; concreteness stays holistic (0-5); routing_present stays binary.
- **`evals/judge_clients.py`** — `--judge-provider {anthropic,openai,google}` adapter pattern reused from Sabha OS. Defeats in-family bias when a non-Anthropic API key is available.
- **`evals/questions.yaml`** — 30 developer-shaped questions across 7 roles and 3 credibility-stress buckets:
  - **Role-core (n=20):** Sabha Code's sweet spot, 2-6 questions per role
  - **Adversarial reframing (n=5):** where the right answer is to challenge the premise (k8s for a 3-person startup, "optimize 200ms p50 to 50ms", auditor flagging HMAC-SHA-256 as insecure, etc.)
  - **Underdog (n=5):** definitional / lookup-shaped where baseline should be competitive (event sourcing vs CQRS, OAuth 2 vs OIDC, etc.)
- **`evals/README.md`** — methodology, run instructions, credibility-claim posture, and what the eval intentionally does *not* test yet (human eval, in-IDE Copilot, multi-LLM candidate sweep).
- **`evals/requirements.txt`** — `anthropic`, `PyYAML`, optional cross-model SDKs noted.

### Methodology lineage

This eval inherits Sabha OS's eval discipline (50-question, 4-bucket, v3 sub-axis rubric + pairwise + cross-model judge harness). The Sabha OS run on 2026-05-18 reported 48/50 pairwise (96%, Wilson 95% CI [86.5%, 98.9%]) for the C-suite-shaped protocol on Claude Code. Sabha Code's first eval run is **pending** — methodology shipped, results to be filed when the run completes.

### What's NOT in v0.2.0

- No live eval results yet — harness shipped, first run is the user's call
- No actual in-IDE Copilot run — the eval simulates via the candidate LLM API (which is what Copilot does under the hood anyway, just without the inline IDE integration)
- No human-judged validation — future work, in BACKLOG of upstream Sabha OS
- No multi-LLM candidate sweep — currently Anthropic-only candidate; running Sabha Code through OpenAI/Google as candidates would test cross-model generalization (sensible to add because Copilot is multi-LLM)

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
