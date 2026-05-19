# Philosophy

Most Copilot Chat replies are *option-shaped*. You ask "should I do X?" and get "well, here are five ways to think about it." That's exhausting when you're trying to ship something. You don't need a survey — you need a recommendation, the tradeoff, and the next move.

Sabha Code forces five disciplines on every load-bearing reply.

## 1. A role

Real engineering questions have real domains. *"Should I add a Redis cache?"* is a Performance question. *"Should I split this function?"* is a Reviewer question. *"Is this auth check sufficient?"* is a Security question. Generic AI replies blur these — Sabha Code makes the model commit to a domain before opening its mouth. That commitment alone narrows the answer.

## 2. A recommendation

A senior engineer says *"do this."* A junior engineer says *"here are the tradeoffs."* The differentiator is conviction earned from experience. Sabha Code makes the role *recommend*. The engineer can override — they always can — but the default output is a decision, not a menu.

## 3. A tradeoff

The fastest way to spot a bad recommendation is to make the recommender name what they're giving up. *"Do X. You lose Y. Worth it because Z."* If a role can't name the Y, the recommendation isn't ready.

## 4. Mode discipline

Two modes, only two. **Ask** is a chat reply — code review, design questions, debugging help, refactor suggestions. **Engage** is a document — ADR, post-mortem, design doc, security review. Most engineering questions are ask-mode. Sabha Code defaults to ask, and only escalates to engage when the decision is big enough to revisit later.

This stops the dreaded "I asked a one-line question and got back a 500-line essay."

## 5. Memory — the codebase as institutional knowledge

A protocol that forgets your last decision is a *generic* protocol. Sabha Code is built around a `memory/` folder that holds ADRs, post-mortems, conventions, and the stack. Copilot reads these on every chat. Three decisions in, your Architect role knows your DB choice. Ten decisions in, your Performance role knows which optimizations the team has already tried. A year in, your council has the institutional memory of a real engineering team — and it's all in your repo, visible, versionable, transferable.

This is the difference between renting opinions and building an asset.

---

## Why "Sabha" and "Chanakya"?

**Sabha** (सभा, सपை). Sanskrit/Tamil for *assembly* or *council*. In the *Mahabharata*, the *Sabha Parva* describes the assembly hall where strategy gets debated and decisions get made. The metaphor is precise: you're not asking an oracle, you're convening a council. The council has roles. Each role has a domain and a voice. The council can disagree. The engineer — the architect, the shipper — makes the final call.

**Chanakya** (चाणक्य, 4th century BCE). The archetype the council embodies. Author of the *Arthashastra* — the original treatise on statecraft, economics, and strategy. The architect behind Chandragupta Maurya's rise. Sabha's voice is shaped by his disposition: decisive, tradeoff-aware, allergic to flattery, comfortable naming hard truths. Applied to engineering, this is the senior engineer who tells you the bug is in your assumption, not your code — and tells you which assumption.

Sabha Code is the developer-focused sibling of [Sabha OS](https://github.com/rdmurugan/sabhaos). Same protocol shape; different role set; different surface (GitHub Copilot vs Claude Code).

The protocol doesn't replace your judgment. It improves the inputs and remembers what you've already decided.

---

## What Sabha Code is *not*

- **Not a chain-of-thought hack.** It changes what the model *outputs*, not how it reasons internally.
- **Not domain expertise.** The Security role gives Copilot security framing. You still need real security review for high-stakes systems (paid pentest, formal threat model, real auditors).
- **Not a personality skin.** The roles aren't characters. They're job functions. Architect doesn't have a backstory. Architect has a domain.
- **Not magic for trivia.** Sabha Code skips syntax lookups and trivial questions. Asking *"what's the Python list comprehension syntax?"* will not produce `Routing: Mentor.` That would be ridiculous.
- **Not GitHub Copilot in disguise.** It's a structured operating manual layered on top of Copilot. Copilot still does the underlying work; Sabha Code shapes how Copilot replies.

---

## When Sabha Code works best

- **Mid-sized teams (3-30 engineers)** where institutional knowledge is real but not all in one head
- **Mature codebases** with accumulated decisions worth referencing
- **High-stakes systems** where naming the tradeoff explicitly matters (financial, healthcare, security-critical)
- **Engineers who are tired of "you could consider..." replies** and want a decisive sparring partner
- **Open-source projects** where the same protocol can be installed by every contributor

## When Sabha Code is overkill

- **Solo prototypes / weekend hacks** — when there's no team to keep aligned, the protocol overhead isn't worth it
- **Pure tutorial / learning environments** — Mentor role on its own may be useful, but the full council is over-structured
- **Tab-completion-shaped work** — let inline Copilot handle it; Sabha Code is for chat-shaped questions

You can keep Sabha Code installed and just not invoke it — by default it only fires on substantive questions. Trivia, syntax lookups, and trivial code generation skip the protocol entirely.

---

## The single sentence

**Sabha Code makes GitHub Copilot answer engineering questions like a senior engineer on your team — decisive, tradeoff-aware, grounded in your codebase's accumulated decisions — instead of like a hedging research assistant.**
