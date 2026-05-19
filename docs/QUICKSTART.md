# Quickstart — Sabha Code in 10 minutes

For developers who use GitHub Copilot in any IDE (VS Code, JetBrains, Neovim, Visual Studio) and want a structured engineering council layered on top.

**Setup time:** ~10 minutes (most of it: deciding what to put in `memory/`).
**Required:** GitHub Copilot subscription, any IDE with Copilot installed.

---

## Step 1 — Drop the files into your repo

The fastest install is `degit` (a tool that copies a folder from a GitHub repo without dragging the whole git history):

```bash
cd /path/to/your/repo
npx degit rdmurugan/sabha-code .github
```

This copies `.github/copilot-instructions.md` and the `instructions/` folder into your repo. That's it.

If you don't have npx:

```bash
git clone --depth 1 https://github.com/rdmurugan/sabha-code.git /tmp/sabha-code
cp -r /tmp/sabha-code/.github/* .github/
cp -r /tmp/sabha-code/instructions ./instructions
rm -rf /tmp/sabha-code
```

Or just `gh repo create my-project --template rdmurugan/sabha-code` if you're starting a new repo from scratch.

---

## Step 2 — Commit and open Copilot Chat

```bash
git add .github/
git commit -m "Add Sabha Code engineering council protocol"
git push
```

Open Copilot Chat in your IDE. Copilot should now read `.github/copilot-instructions.md` automatically on every chat in this repo.

---

## Step 3 — Verify it's working

Ask any substantive engineering question. For example:

> *"Should I add a Redis cache to this endpoint, or is the DB query fast enough?"*

You should see a reply that opens with `Routing: Performance.` (or another role) and that names a specific tradeoff. If you instead see a generic 5-bullet list of "things to consider," Copilot didn't pick up the protocol — see "Troubleshooting" below.

---

## Step 4 — Populate `memory/` (optional but powerful)

Sabha Code reads files from `memory/` if you have them. Create the folder structure:

```bash
mkdir -p memory/{decisions,post-mortems}
touch memory/conventions.md memory/stack.md
```

### `memory/stack.md` — your tech stack

Edit `memory/stack.md` with one paragraph:

```markdown
# Stack

- **Language:** TypeScript (Node 20+) for backend; Python 3.12 for data work
- **Framework:** Fastify on backend; React + Vite on frontend
- **DB:** Postgres 15 (main), Redis (cache + queues)
- **Deploy:** Vercel (frontend), Render (backend), Neon (DB)
- **CI:** GitHub Actions
- **Test:** Vitest (TS), pytest (Python), Playwright (E2E)
```

Now when you ask *"should we add Redis?"* — Copilot already knows you have Redis.

### `memory/conventions.md` — your unwritten rules

```markdown
# Conventions

## Naming
- Files: kebab-case for TS, snake_case for Python
- DB columns: snake_case (Postgres convention)
- React components: PascalCase

## Branching
- `main` is always deployable
- Feature branches: `feat/<short-description>`
- Fix branches: `fix/<issue-number>`

## Code review
- 2 approvals required for shared infra
- Solo approval OK for feature work behind a flag

## Testing
- New endpoints require integration tests
- Frontend changes require Storybook entries
- E2E only for revenue-affecting flows
```

When you ask *"should I write a test for X?"* — Copilot now applies your conventions, not generic advice.

### `memory/decisions/<YYYY-MM-DD>-<slug>.md` — ADRs

Every time you make a load-bearing decision, write a short ADR:

```markdown
# ADR: Postgres over MongoDB

- **Status:** accepted
- **Date:** 2026-05-18

## Context
Choosing a primary DB for the user/order/event data.

## Decision
Postgres 15.

## Tradeoff
We give up MongoDB's flexible schema for early-stage iteration.
We gain: ACID transactions, mature tooling, less ops complexity.

## Alternatives considered
- MongoDB — rejected for transaction guarantees
- DynamoDB — rejected for lock-in

## Revisit when
We hit a real Postgres-specific limit (>5K req/s sustained, multi-region writes).
```

Copilot now has institutional memory. When you later ask *"should we migrate off Postgres?"*, the answer is informed by *why* you chose it in the first place.

---

## Step 5 — Use it for real work

Try Sabha Code on five different question shapes to see how the different roles answer:

| Question | Expected routing |
|---|---|
| *"Should I split this 200-line function?"* | Reviewer |
| *"Where's the bottleneck in this endpoint?"* | Performance |
| *"Is this PR ready to merge?"* | Reviewer or Security (depends on the diff) |
| *"How should I structure this new service?"* | Architect |
| *"This test keeps flaking. What do I do?"* | QA |
| *"What should I learn next about distributed systems?"* | Mentor |
| *"We're behind schedule. Cut features or extend?"* | Tech Lead |

If the routing feels off for your work, customize the role table in `.github/copilot-instructions.md` (see [`docs/CUSTOMIZATION.md`](./CUSTOMIZATION.md)).

---

## Troubleshooting

### "Copilot doesn't seem to follow the protocol"

- **Confirm the file exists:** `ls .github/copilot-instructions.md`
- **Confirm Copilot reads it:** ask explicitly *"What system instructions are loaded for this repo?"*
- **Confirm your IDE version:** Copilot custom instructions require recent versions of the Copilot extension
- **Try a fresh chat session:** old chat threads may not pick up new instructions

### "The routing line isn't appearing"

- The model is reading the instructions but ignoring the format. Add an even more emphatic line at the top of `.github/copilot-instructions.md`: *"YOU MUST open every substantive reply with `Routing: <ROLE>` on its own line."*

### "I want some files to have different routing"

Use the `applyTo` frontmatter in `instructions/*.instructions.md`:

```markdown
---
applyTo: "**/*.test.ts,**/*.spec.ts"
---

# Only loaded when working on test files
```

See [Copilot's instructions docs](https://docs.github.com/en/copilot/customizing-copilot/) for the latest syntax.

### "Can I use this with Claude Code instead?"

Yes — use [Sabha OS](https://github.com/rdmurugan/sabhaos) for Claude Code. It's the C-suite-shaped sibling of this project, designed for operator/founder work rather than developer work.

---

## What to do next

- **Customize the roles:** see [`docs/CUSTOMIZATION.md`](./CUSTOMIZATION.md)
- **Read the philosophy:** see [`docs/PHILOSOPHY.md`](./PHILOSOPHY.md)
- **Contribute a preset:** if you build a working customization for a specific stack (frontend-heavy, data-platform, embedded, etc.), PR it back as an example
- **Pair with Sabha OS:** if you also handle non-engineering decisions (pricing, hiring, strategy), install [Sabha OS](https://github.com/rdmurugan/sabhaos) for Claude Code

---

**Sabha Code · MIT License · [github.com/rdmurugan/sabha-code](https://github.com/rdmurugan/sabha-code)**
