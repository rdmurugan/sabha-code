# Changelog

All notable changes to Sabha Code will be documented here. Format follows [Keep a Changelog](https://keepachangelog.com/).

> **Origin:** project conceived 2026-05-18 as the developer-focused sibling of [Sabha OS](https://github.com/rdmurugan/sabhaos). First public release same day.

## [0.4.0] — 2026-05-18 (voice reframing — Chanakya references removed)

### Changed

Removed all "Chanakya tradition" framing from the user-facing docs and the protocol file. Sabha Code now leads with the voice characteristics directly — **decisive, terse, concrete, tradeoff-aware, grounded** — without a borrowed archetype.

**Why:** the Chanakya framing carried two costs that didn't pay back for the developer audience:
1. **Cognitive load.** Asking developers to read about a 4th-century BCE strategist before they can install a Copilot config is friction without a payoff. The voice principles are useful on their own.
2. **Risk of being misread as ceremony.** The protocol's value is the structured discipline (routing + 5 voice characteristics + ask/engage mode). Tying it to a tradition invited the reading that the tradition itself is the value, which it isn't.

**What stayed:** the name *Sabha* (Sanskrit/Tamil for *council*) remains — it's the product name and a clean one-word metaphor for the protocol's whole shape (you're not asking an oracle; you're convening a council). The 7-role structure, the v3 sub-axis rubric, the eval results — all unchanged.

**Files updated:**
- `README.md` — tagline reframed; "Why Sabha and Chanakya" framing replaced with the voice characteristics named directly; Credits section no longer cites Chanakya as the source tradition
- `.github/copilot-instructions.md` — header, §3 title, and footer all reframed to "operator-grade discipline" instead of "Chanakya tradition"
- `docs/PHILOSOPHY.md` — "Why Sabha and Chanakya?" section rewritten to "Why 'Sabha'? (the only ceremonial word)" — keeps the council metaphor; drops the archetype

**No code changes.** The 7 role instruction files, the eval harness, the evaluation results, and the install path are unchanged. The 2026-05-18 eval numbers (28/30 pairwise, +4.74 rubric Δ) still describe the current protocol exactly — the rebrand is messaging, not mechanism.

The relationship to [Sabha OS](https://github.com/rdmurugan/sabhaos) (which retains its own Chanakya framing for the C-suite audience) is preserved as "the developer-focused sibling of Sabha OS." Sabha OS readers who prefer the Chanakya tradition framing keep it there; Sabha Code reads cleaner for the developer audience.

## [0.3.0] — 2026-05-18 (eval results)

### First live eval results

Ran the n=30 eval harness from v0.2.0 against the v3 sub-axis rubric. Anthropic candidate (Claude Sonnet 4.6), Anthropic judge (Claude Opus 4.7).

**Headline:** 28/30 pairwise wins for Sabha Code (93.3%, Wilson 95% CI [78.7%, 98.2%]). Rubric total +4.74 (12.33 baseline → 17.07 Sabha Code).

**Per-bucket:**
- Role-core (n=20): **20/20 = 100%** — protocol works exactly where designed
- Adversarial reframing (n=5): 4/5 = 80%
- Underdog (n=5): 4/5 = 80%

**Per-role (all 7):** Architect 6/6, Reviewer 4/4, Performance 5/5, Mentor 3/3, Tech Lead 2/2, Security 4/5, QA 4/5.

**The 2 losses, documented honestly:**

- `adv-04` (Security adversarial — auditor flagged SHA-512 vs HMAC-SHA-256). Sabha Code scored 19 on rubric, baseline 16. Pairwise went to baseline — judge cited charity-of-interpretation: baseline considered the alternative reading (bare SHA vs HMAC) while Sabha Code dismissed the auditor as wrong. Real signal: the protocol's discipline can become rigidity when the premise itself is ambiguous.
- `und-04` (QA underdog — "explain test-the-contract in one paragraph"). Sabha Code scored 14, baseline 11. Pairwise went to baseline — judge cited the routing-line meta-commentary as distracting from a clean one-paragraph definitional answer. Real signal: Sabha Code over-structures lookup-shaped questions, which is exactly what the protocol's "skip for" rules say *not* to do.

Both losses are *rubric-wins-but-pairwise-losses*. Pattern is consistent: structured technically-correct replies that operator-judge preferred to be looser or more accommodating. Two backlog items follow:

1. Add a "charity-of-interpretation" rule to Security and CLC-equivalent role instructions: when the user reports an external flag (auditor, reviewer, regulator), consider what the flag *might* be trying to say, not just whether it's literally correct.
2. Strengthen the "skip for" enforcement in `.github/copilot-instructions.md` for clearly-definitional questions — the model can detect "explain X briefly" patterns and skip the routing line.

### Per-axis lifts (notable vs Sabha OS)

`length_discipline` was Sabha Code's strongest axis (+1.77), which inverts the Sabha OS pattern where length_discipline was the hardest axis. Two hypotheses:

1. The developer-shaped instructions ask for terse engineering replies more explicitly than C-suite instructions ("real APIs, real file paths, performance numbers when relevant").
2. The eval bumped `max_tokens` from 1200 → 2000, removing the truncation artifact that hurt Sabha OS replies but giving Sabha Code more room to *not* fill it.

Worth re-running Sabha OS with the same max_tokens bump to test hypothesis 2 cleanly.

### Comparison to Sabha OS

Methodology is identical (v3 sub-axis rubric, pairwise judge, cross-model judge harness, role-core + adversarial + underdog bucket structure).

| | Sabha OS (n=50) | Sabha Code (n=30) |
|---|---:|---:|
| Pairwise | 48/50 (96%) | 28/30 (93.3%) |
| Wilson 95% CI | [86.5%, 98.9%] | [78.7%, 98.2%] |
| Domain | C-suite / operator | Engineering |

CIs overlap substantially. **The directional claim "the protocol shape generalizes from operator to engineer" is supported.** The magnitude can't yet be distinguished at these sample sizes — both could be 90-96%, both could be tighter or looser. Need more N or a cross-model judge run to discriminate further.

### Results filed

- [`evals/results/2026-05-18.json`](./evals/results/2026-05-18.json) — machine-readable full record (252 KB; replies, scores, sub-criteria, pairwise rationales for all 30 questions)
- [`evals/results/2026-05-18.md`](./evals/results/2026-05-18.md) — rendered report (canonical for human reading)
- [`evals/results/latest.md`](./evals/results/latest.md) — refreshed pointer
- [`evals/results/smoke.json`](./evals/results/smoke.json) + `.md` — 3-question warm-up run from before the full eval

### Cross-model judge run — still pending

Default judge was Anthropic (in-family). The `--judge-provider openai` and `--judge-provider google` paths are wired in v0.2.0 but not yet exercised. A cross-family judge run would defeat ~80% of the remaining in-family-bias critique. Run command when an OpenAI or Google API key is available:

```bash
pip install 'openai>=1.0'
export OPENAI_API_KEY=sk-...
python evals/run_eval.py \
  --judge-provider openai --judge-model gpt-5 \
  --out-name 2026-MM-DD-openai-judge
```

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

- **`.github/copilot-instructions.md`** — the protocol; this IS Sabha Code. Routing-at-top-of-reply discipline, structured voice (decisive / terse / concrete / tradeoff-aware / grounded), ask/engage mode discipline, grounding rules.
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
  - `docs/PHILOSOPHY.md` — the 5 disciplines, what Sabha Code is and isn't
- **Install paths documented:** `npx degit`, `gh repo create --template`, manual copy.
- **MIT License.** Copyright Durai Rajamanickam (@rdmurugan).
- **No code dependencies.** Pure markdown protocol. Works with any Copilot-supported IDE and any LLM Copilot uses (GPT-4 / Claude / Gemini).

### Relationship to Sabha OS

Sabha Code is the developer-focused sibling of [Sabha OS](https://github.com/rdmurugan/sabhaos) (started October 2025). Same protocol shape — *route, recommend, name the tradeoff, mode discipline, ground in memory* — adapted to engineering questions and GitHub Copilot's distribution surface. The two projects are independent but complementary: Sabha OS for C-suite/operator decisions in Claude Code, Sabha Code for engineering decisions in Copilot.
