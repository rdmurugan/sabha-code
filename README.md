# Sabha Code

> An open-source **engineering council protocol** for GitHub Copilot. Decisive, tradeoff-aware, grounded — in the Chanakya tradition. Routes every load-bearing engineering question through a 7-role council (Architect / Reviewer / Security / Performance / QA / Mentor / Tech Lead) and answers in a structured shape Copilot doesn't enforce by default.

**Sabha** (சபை, सभा, Sanskrit for *council*). **Chanakya** (चाणक्य, the original strategic advisor — author of the *Arthashastra*) is the voice. Sabha Code is the developer-focused sibling of [Sabha OS](https://github.com/rdmurugan/sabhaos), which does the same for C-suite operators on Claude Code.

Most Copilot replies are option-shaped: *"here are five approaches with pros and cons."* That's exhausting when you're building something. Sabha Code forces a different reply:

```
Routing: Performance. N+1 query at users.py:84.
         Single query with WHERE id IN (...). ~40× faster at n=100.
         You lose: one extra import. Worth it.
```

---

## The 7 roles

| Role | Covers |
|------|--------|
| **Architect**   | System design, service boundaries, data model, tech stack choices, ADRs |
| **Reviewer**    | Code review, readability, naming, abstractions, refactor calls, taste judgments |
| **Security**    | Auth, secrets, OWASP top-10, threat modeling, supply chain |
| **Performance** | Latency, throughput, memory, profiling, caching, hot-path analysis |
| **QA**          | Test strategy, coverage, flake hunting, regression risk |
| **Mentor**      | Code explanations, refactoring guidance, what-to-learn-next, debugging mindset |
| **Tech Lead**   | When the call is irreducibly the engineer's — scope cuts, ship/no-ship, debt budgets, role synthesis |

Each role has its own `instructions/<role>.instructions.md` file with operating principles, micro-voice examples, frameworks to cite (OWASP, USE method, ADR pattern, etc.), engage-mode templates, and explicit anti-patterns.

---

## Install (one command, 10 seconds)

### Option A — degit (recommended; copies the files into your repo)

```bash
npx degit rdmurugan/sabha-code .github
```

This drops `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md` into your repo. Commit, open Copilot Chat, ask any substantive engineering question — the routing happens automatically.

### Option B — template

```bash
gh repo create my-project --template rdmurugan/sabha-code
```

For starting a new project with Sabha Code baked in.

### Option C — manual copy

Copy `.github/copilot-instructions.md` and the `instructions/` folder from this repo into yours. That's it.

---

## What you get, immediately

Open Copilot Chat in your IDE after install, ask anything load-bearing:

> *"Should I split this 200-line function?"*

becomes

```
Routing: Reviewer. Yes — split into 3 functions, named for what they
return, not what they do. You lose: 6 lines of overhead (function
signatures + 1 helper). You gain: each function fits on screen and
the names are now load-bearing.

Specifically:
1. `parseRequestBody(raw: bytes) -> RequestData`
2. `validateRequest(data: RequestData) -> ValidationResult`
3. `dispatchRequest(data: RequestData) -> Response`

The current naming (`processRequest`) tells the next reader nothing.
After the split, the function names ARE the documentation.
```

Without Sabha Code: the same model probably gives you a 5-bullet survey of "things to consider" and leaves the choice to you.

---

## How it's different from raw Copilot custom instructions

Raw `.github/copilot-instructions.md` is **unstructured** — anyone can put anything in it. Sabha Code adds:

| What it adds | Why it matters |
|---|---|
| **Routing discipline** | Every reply opens with `Routing: <ROLE>`. You know which "hat" Copilot is wearing. |
| **7-role taxonomy** | Architecture, code review, security, performance, testing, mentorship, and synthesis are distinct domains with different voices. |
| **Voice constraints** | Decisive, terse, tradeoff-aware. No "you could consider" hedging. |
| **Engage-mode templates** | ADR template, security review template, perf write-up template — ready to fill. |
| **Anti-patterns named** | Each role has explicit "do NOT do this" lists. Reduces drift. |
| **Memory layout** | A `memory/` folder structure for decisions, post-mortems, and conventions so Copilot has institutional context. |

It's the difference between "I told Copilot to be terse" and "I gave Copilot a structured operating manual."

---

## Memory — make Copilot remember design decisions

Copilot reads files in your repo. Sabha Code recommends a `memory/` folder layout:

```
memory/
├── decisions/      # ADRs — one .md per decision, dated
├── post-mortems/   # Incident write-ups
├── conventions.md  # Unwritten rules: naming, branching, deploy
└── stack.md        # Languages, frameworks, services, DB
```

When you ask a question, Copilot now has context for *your* codebase — past decisions, ruled-out alternatives, tech-debt budgets — instead of generic engineering advice.

(For the optional, Sakthi-style local graph-shaped memory used in the Claude-Code variant of this protocol, see [Sakthi Graph](https://github.com/rdmurugan/sakthi-graph) on the Sabha OS side. Copilot's MCP support is still maturing; the `memory/` folder approach works today.)

---

## Customize

The protocol is one file: `.github/copilot-instructions.md`. Edit it.

Common customizations:
- **Rename roles** — *"Frontend"* instead of *"Reviewer"*, *"Platform"* instead of *"Architect"*
- **Drop roles you don't need** — solo developer? Drop QA and merge Reviewer + Tech Lead.
- **Add a role for your stack** — *"Database"* for heavy-data work, *"Designer"* for design-system code
- **Tune the voice** — the default is terse and decisive; if you want warmer, edit the ANSWER section

See [`docs/CUSTOMIZATION.md`](./docs/CUSTOMIZATION.md) for walkthroughs.

---

## Documentation map

| Doc | What's in it |
|---|---|
| [`docs/QUICKSTART.md`](./docs/QUICKSTART.md) | 10-minute install + first-question walkthrough |
| [`docs/CUSTOMIZATION.md`](./docs/CUSTOMIZATION.md) | Renaming roles, adding roles, tuning voice |
| [`docs/PHILOSOPHY.md`](./docs/PHILOSOPHY.md) | Why these 5 disciplines; the Chanakya tradition |
| [`instructions/architect.instructions.md`](./instructions/architect.instructions.md) | Architect role — system design, ADRs |
| [`instructions/reviewer.instructions.md`](./instructions/reviewer.instructions.md) | Reviewer role — code review, refactor calls |
| [`instructions/security.instructions.md`](./instructions/security.instructions.md) | Security role — OWASP-shaped, threat modeling |
| [`instructions/performance.instructions.md`](./instructions/performance.instructions.md) | Performance role — measure-first, hot-path-only |
| [`instructions/qa.instructions.md`](./instructions/qa.instructions.md) | QA role — test strategy, flake hunting |
| [`instructions/mentor.instructions.md`](./instructions/mentor.instructions.md) | Mentor role — show why, not just how |
| [`instructions/techlead.instructions.md`](./instructions/techlead.instructions.md) | Tech Lead role — synthesis, founder-mode |

---

## Does it actually work?

**Yes — 28/30 pairwise wins (93.3%) against a no-system-prompt baseline.** Full results from the 2026-05-18 run:

| Metric | Baseline | Sabha Code | Δ |
|---|---:|---:|---:|
| Pairwise preference | — | **28/30 (93.3%)** | Wilson 95% CI [78.7%, 98.2%] |
| Rubric total (/20) | 12.33 | **17.07** | **+4.74** |
| decisiveness | 3.23 | 4.47 | +1.24 |
| tradeoff_named | 2.50 | 3.50 | +1.00 |
| concreteness | 3.50 | 4.23 | +0.73 |
| routing_present | 0.00 | 1.00 | +1.00 |
| length_discipline | 3.10 | 4.87 | +1.77 |

Per-bucket pairwise:

| Bucket | Win rate | What it tests |
|---|---:|---|
| Role-core (n=20) | **20/20 (100%)** | Operator-shaped engineering decisions in each role's sweet spot |
| Adversarial reframing (n=5) | 4/5 (80%) | Questions where the right answer is to challenge the premise |
| Underdog (n=5) | 4/5 (80%) | Definitional / lookup-shaped where baseline should be competitive |

Per-role: Architect 6/6, Reviewer 4/4, Performance 5/5, Mentor 3/3, Tech Lead 2/2, Security 4/5, QA 4/5.

**The 2 losses are diagnostic, not catastrophic.** Both share a *rubric-win-but-pairwise-loss* pattern — Sabha Code scored higher on the structured rubric, but the operator-judge preferred the alternative:

- **adv-04 (Security adversarial):** charity-of-interpretation gap. Sabha Code dismissed the auditor's flag as wrong; baseline considered the alternative reading and offered a compliance path.
- **und-04 (QA underdog):** over-structure on a one-paragraph definitional question. Routing-line meta-commentary distracted from the answer the user actually asked for.

Both failure modes are documented in [`evals/results/latest.md`](./evals/results/latest.md) and worth keeping visible — they're where the protocol earns honest critique.

### How it compares to Sabha OS

Methodology is identical: v3 sub-axis rubric + pairwise preference + cross-model judge harness, applied to a different question domain.

| | Sabha OS (n=50) | Sabha Code (n=30) |
|---|---:|---:|
| Pairwise | 48/50 (96%) | 28/30 (93.3%) |
| Wilson 95% CI | [86.5%, 98.9%] | [78.7%, 98.2%] |
| Domain | C-suite operator | Engineering |

Both Wilson CIs overlap substantially — the directional claim "the protocol shape generalizes from operator to engineer" is supported; the magnitude can't yet be distinguished at these sample sizes.

### Run it yourself

```bash
pip install -r evals/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python evals/run_eval.py            # full n=30 run, ~$15-20, ~15 min
python evals/run_eval.py --limit 3  # smoke first
```

Results land in [`evals/results/`](./evals/results/). The harness checkpoints after every question so a partial run is never lost. See [`evals/README.md`](./evals/README.md) for the full methodology, the credibility-claim posture, and what the eval intentionally does *not* test yet (human eval, in-IDE Copilot, multi-LLM candidate sweep).

## Compatibility

- **GitHub Copilot in VS Code, JetBrains, Neovim, Visual Studio** — all surfaces that read `.github/copilot-instructions.md`
- **GitHub Copilot Chat (web and IDE)** — same protocol applies
- **Works with any LLM backend Copilot exposes** — GPT-4, Claude, Gemini. The protocol is text; it doesn't care which model reads it.
- **Optional integration with Claude Code** — if you also use Claude Code, the [Sabha OS](https://github.com/rdmurugan/sabhaos) project ships the C-suite-shaped sibling for operator-level work.

---

## Why use this

1. **A role.** Treating engineering questions as belonging to a real role narrows the answer.
2. **A recommendation.** The role has to commit, not survey.
3. **A tradeoff.** Naming what you give up keeps the answer honest.
4. **Mode discipline.** Ask = chat. Engage = filed ADR or post-mortem.
5. **Memory of your codebase.** With `memory/` populated, every reply draws on your accumulated design decisions.

Most Copilot Chat replies are forgettable because they're shapeless. Sabha Code gives them a shape — structured, opinionated, easy to act on.

---

## What this is NOT

- **Not domain expertise.** The Security role gives Copilot a security framing. You still need real security review for high-stakes systems.
- **Not a personality skin.** The roles are functions, not characters. Architect doesn't have a backstory.
- **Not a chain-of-thought hack.** It changes what Copilot *outputs*, not how it reasons internally.
- **Not magic for trivia.** Sabha Code skips syntax lookups and trivial questions. Tab-completion-shaped requests stay with inline Copilot.

---

## Contributing

PRs welcome. Especially:
- Role presets for specific stacks (frontend, backend, data, mobile, embedded)
- Translations of `.github/copilot-instructions.md` into other languages
- Real usage stories — what role mix worked for your team

---

## License

MIT. See [LICENSE](./LICENSE). Use it, fork it, ship it in your products — just keep the copyright notice.

---

## Credits

Designed and developed by **Durai (@rdmurugan)** as a solo project — protocol, role instructions, packaging. MIT-licensed, started May 2026. Adapted from [Sabha OS](https://github.com/rdmurugan/sabhaos) (started October 2025), itself distilled from the Chanakya tradition of advisor-counsel, the OWASP / SRE / ADR canon, and operator-grade engineering practice shared across the open internet.

Copyright © 2026 Durai (@rdmurugan). Released under MIT.

---

## Links

- **Sabha OS (Claude Code, C-suite roles):** [github.com/rdmurugan/sabhaos](https://github.com/rdmurugan/sabhaos)
- **Sakthi Graph (local-first memory backend for Sabha OS):** [github.com/rdmurugan/sakthi-graph](https://github.com/rdmurugan/sakthi-graph)
- **Sabha Code (this repo):** [github.com/rdmurugan/sabha-code](https://github.com/rdmurugan/sabha-code)
