# Customization

Sabha Code is one protocol file + 7 role files. Everything you'd want to change lives in those 8 markdown files.

## Renaming or removing roles

The role table in `.github/copilot-instructions.md` is the source of truth. Edit it directly.

**Example — solo developer, monolith codebase:**

| Role | Covers |
|------|--------|
| **Builder** | Architecture + code review + refactor calls |
| **Security** | Auth, secrets, OWASP |
| **Performance** | Latency, throughput |
| **Tech Lead** | Ship-or-don't, scope cuts |

You don't need 7 roles when 4 cover your decision domains. Collapse what makes sense.

**Example — frontend-heavy work:**

| Role | Covers |
|------|--------|
| **Architect** | Component structure, state management |
| **Designer** | UX, accessibility, design system fit |
| **Performance** | Bundle size, render perf, LCP/FID/CLS |
| **Reviewer** | Code review |
| **QA** | Test strategy |
| **Mentor** | Onboarding, learning paths |

Rename `Security` → `Designer` if you don't need security as a primary role. Or keep both — Copilot just ignores the unused one.

After editing, also update or delete the corresponding `instructions/<role>.instructions.md` files.

## Tuning the voice

Find the `ANSWER` section in `.github/copilot-instructions.md`. The defaults:

- Decisive (recommend, don't survey)
- Terse over verbose
- Concrete over abstract
- Tradeoff-aware

To make it warmer:
- Replace `Terse over verbose` with `Conversational but on-point`
- Replace `Recommend, don't survey` with `Recommend, then sketch one alternative`

To make it more exploratory (useful for greenfield work):
- Replace `Decisive` with `Decisive after surfacing 2-3 options`
- Add `Default to asking clarifying questions when the constraint isn't obvious`

To make it more aggressive (useful for code review on legacy code):
- Add `Don't soften feedback. If the function does four things, say so directly.`

Both work — they just change the texture.

## Adding domain knowledge

If your work has heavy domain content (a specific framework, an internal library, a unique architecture), add a section to `.github/copilot-instructions.md`:

```markdown
## Domain context

Our backend is Fastify + tRPC. Don't suggest Express patterns.
Our DB layer uses Prisma; don't suggest raw SQL unless the question
is explicitly about Postgres internals.
Our queue is BullMQ on Redis; don't suggest SQS or Kafka.
```

Keep it under 500 words. Bigger context goes in `memory/stack.md` or `memory/conventions.md`.

## Per-file routing with `applyTo`

GitHub Copilot supports per-file instruction loading via the `applyTo` frontmatter. Use it to specialize roles:

```markdown
---
applyTo: "**/*.test.ts,**/*.spec.ts,**/__tests__/**"
---

# QA role — only loaded when working in test files
```

Or:

```markdown
---
applyTo: "infra/**,terraform/**,k8s/**"
---

# Infrastructure-specific Architect role
```

Multiple instruction files can apply to overlapping paths; Copilot loads all that match.

## Memory layout

The default suggested layout:

```
memory/
├── decisions/      # ADRs
├── post-mortems/   # Incident write-ups
├── conventions.md  # Unwritten rules
└── stack.md        # Tech stack
```

You can extend with whatever your team needs:

```
memory/
├── decisions/
├── post-mortems/
├── conventions.md
├── stack.md
├── domain.md       # business / product domain glossary
├── learning/       # personal "things I learned" notes
├── performance/    # perf investigations
├── security/       # threat models, security reviews
└── debt.md         # technical debt register
```

Sabha Code's protocol mentions `memory/` but doesn't enforce the layout. Use what fits.

## Multiple Sabha Codes per monorepo

If you have a monorepo with distinct sub-projects (e.g., backend + frontend + data pipeline), you can put `.github/copilot-instructions.md` at the repo root *and* per-package instruction files via `applyTo`:

```
.github/copilot-instructions.md       # the main protocol
.github/instructions/
├── frontend.instructions.md          # applyTo: "frontend/**"
├── backend.instructions.md           # applyTo: "backend/**"
└── data-pipeline.instructions.md     # applyTo: "data/**"
```

## Disabling Sabha Code temporarily

Several ways:

1. **`/explain` or other Copilot slash commands** — these tend to bypass custom instructions
2. **`@workspace` queries that explicitly ask for a survey** — *"give me 5 options for X"* will usually override the routing
3. **Delete or rename `.github/copilot-instructions.md`** — full opt-out
4. **Just write differently** — Sabha Code skips trivia and syntax lookups by design; ask *"what's the syntax for Y?"* and you'll get a plain answer

## Sharing customizations

If you build a great preset for a specific stack (Rails, Django, Next.js, Rust+Axum, Go+Echo) or domain (game dev, embedded, ML training pipelines, scientific computing), please PR it as `examples/<stack>.copilot-instructions.md` so others can use it as a starting point.

## Differences from Sabha OS

Sabha Code is the developer-focused sibling of [Sabha OS](https://github.com/rdmurugan/sabhaos). The structural differences:

| | Sabha OS | Sabha Code |
|---|---|---|
| Audience | Founders, C-suite operators | Developers |
| Surface | Claude Code (plugin) | GitHub Copilot (`.github/` files) |
| Roles | CFO/CMO/CIO/CAIO/CSO/CXO/CHRO/CLC/CEO | Architect/Reviewer/Security/Performance/QA/Mentor/Tech Lead |
| Memory | MCP-based (Sakthi Graph, etc.) | File-based (`memory/` folder) |
| LLM backend | Anthropic only | Multi-LLM (whatever Copilot uses) |
| Eval | LLM-as-judge, 50-question harness | Reuses Sabha OS's methodology (developer-shaped eval in BACKLOG) |

If you use both Claude Code and GitHub Copilot, install both. They're complementary — Sabha OS for non-engineering decisions (pricing, hiring, strategy), Sabha Code for engineering work.
