# Sabha Code evals

Does loading the Sabha Code protocol actually produce better engineering replies than a vanilla LLM? This folder ships a reproducible harness to answer that question.

Adapted from the [Sabha OS eval methodology](https://github.com/rdmurugan/sabhaos/blob/main/docs/EVALS.md) — same v3 sub-axis rubric + pairwise judge + cross-model judge harness — applied to developer-shaped questions and the Copilot protocol layout.

> **Where the source-of-truth lives.** Raw data lives in `results/`. When numbers in human-written summaries conflict with the JSON, the JSON wins.

---

## What this eval tests

For each question:

1. **Baseline reply** — the candidate LLM (Claude Sonnet 4.6 by default) generates an answer with **no system prompt** at all.
2. **Sabha Code reply** — the same LLM generates an answer with `.github/copilot-instructions.md` loaded as the system prompt, plus the matching role's `instructions/<role>.instructions.md` appended.

Both replies are scored by an LLM-as-judge (Claude Opus 4.7 by default) on the v3 sub-axis rubric, plus a pairwise preference: *"Which would a busy engineer find more useful?"*

The eval is honest about what it doesn't test:

- **We do not run on actual Copilot.** Copilot's API isn't exposed to third parties. We approximate by running the protocol-as-text through the Anthropic API — which is what Copilot does under the hood anyway, just without the inline IDE integration. This is a real simulation, not a perfect one.
- **In-family judge bias.** Default Anthropic-judges-Anthropic. The `--judge-provider {openai,google}` flag exists to defeat this when a non-Anthropic API key is available.
- **No human-judged validation yet.** All judgments are LLM-judged. Future work.

---

## Question set v1 (n=30)

Mirror of the sabha-os methodology, applied to developer questions:

| Bucket | n | Purpose |
|---|---:|---|
| **Role-core** | 20 | Operator-shaped engineering decisions in each role's sweet spot |
| **Adversarial reframing** | 5 | Where the right answer is to challenge the premise; tests where Sabha Code's discipline becomes rigidity |
| **Underdog** | 5 | Definitional / lookup-shaped questions where baseline should be competitive |

Per-role distribution (n=30 total):

| Role | n |
|---|---:|
| Architect | 6 |
| Reviewer | 4 |
| Security | 5 |
| Performance | 5 |
| QA | 5 |
| Mentor | 3 |
| Tech Lead | 2 |

See [`questions.yaml`](./questions.yaml) for the full set.

---

## Methodology

### v3 sub-axis rubric

Three composite axes (`decisiveness`, `tradeoff_named`, `length_discipline`) are each scored as the sum of 5 binary sub-criteria. This defeats the saturation problem that flattened earlier rubrics — at v1/v2, 75-80% of Sabha replies hit ceiling on decisiveness, so the rubric stopped discriminating. v3 forces the judge to score discrete properties.

Two axes stay holistic:
- `concreteness` (0-5)
- `routing_present` (0 or 1)

Total composite score is /20. See `judge.py` for the exact prompt.

### Pairwise preference

Per question, the judge sees both replies (A/B order randomized) and picks the one a busy engineer would prefer. This is more robust than rubric scores; the rubric can saturate but pairwise forces a choice.

### Cross-model judge

`--judge-provider {anthropic,openai,google}` swaps the judge model family. Defeats in-family bias — by far the largest credibility concern in any LLM eval. Each provider needs its own API key + SDK.

---

## Running the eval

### Install dependencies

```bash
pip install -r evals/requirements.txt
```

### Anthropic-only run (default, continuity with prior sabha-os methodology)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python evals/run_eval.py
```

Expected wall time: ~10-15 min for n=30.
Expected cost: ~$15-20.

### Smoke first (recommended)

```bash
python evals/run_eval.py --limit 3 --out-name smoke
```

Three questions, ~$2, ~2 min. Confirms the harness works end-to-end before the full run.

### Cross-model judge (when you have a non-Anthropic key)

```bash
pip install 'openai>=1.0'
export OPENAI_API_KEY=sk-...
python evals/run_eval.py \
  --judge-provider openai --judge-model gpt-5 \
  --out-name YYYY-MM-DD-openai-judge
```

```bash
pip install 'google-generativeai>=0.7'
export GOOGLE_API_KEY=...
python evals/run_eval.py \
  --judge-provider google --judge-model gemini-2.0-pro \
  --out-name YYYY-MM-DD-google-judge
```

A *credible* eval cycle does at least one Anthropic + one cross-family judge. Numbers that hold across both judges are dramatically stronger than either alone.

### Resume after a transient failure

```bash
python evals/run_eval.py --resume
```

Checkpoint-after-each-question means a partial run is never lost. Resume picks up where it left off.

---

## Results

Once you've run the eval, results land in:

- `results/<date>.json` — machine-readable
- `results/<date>.md` — rendered report
- `results/latest.md` — always points at the most recent run

A run is bundled with a stable basename (default: today's ISO date; override with `--out-name`).

---

## What a "credible run" looks like

Per the methodology Sabha OS established, a credible Sabha Code run reports:

1. **Pairwise win rate with a Wilson 95% CI** — not a bare percentage
2. **Per-bucket breakdown** — role-core vs adversarial vs underdog
3. **Per-role distribution** — which roles do the protocol help most/least
4. **Catalogued losses** — every question Sabha Code loses, with the judge's rationale, traceable to either a real protocol weakness or a known artifact
5. **Cross-model judge corroboration** — does the result hold under a non-Anthropic judge

A run that reports only the headline percentage is not credible. The buckets, losses, and CI are what survive scrutiny.

---

## What's NOT in this eval (yet)

- **Human-judged validation.** 5-10 real engineers rating reply pairs blind. The single strongest piece of credibility evidence, but project-shaped (recruiting + comp). Future work.
- **Actual Copilot in IDE.** The eval simulates via the candidate LLM API. Real Copilot includes inline-completion and tool-use mechanics this eval doesn't exercise.
- **Multi-LLM candidate sweep.** Currently the candidate is Anthropic-only. Running Sabha Code through OpenAI / Google as candidates would test cross-model generalization — sensible to add because Copilot is multi-LLM by design.

These are documented as future work, not pretended away.

---

## Reproducibility

- All questions are committed
- All harness code is committed
- All API parameters (temperature, max_tokens, seed) are pinned in `run_eval.py`
- Results JSON contains the full reply text for both conditions — re-judging with a different rubric or judge is a `regrade.py` script away (see how sabha-os handles this)
- Run dates and rubric versions stamped in every result file

If the numbers in this eval folder are wrong, anyone with an API key can re-run and prove it. That's the standard.

---

## Related

- [Sabha OS eval methodology](https://github.com/rdmurugan/sabhaos/blob/main/docs/EVALS.md) — the upstream methodology this eval inherits
- [Sabha OS results](https://github.com/rdmurugan/sabhaos/tree/main/evals/results) — for comparison against the C-suite protocol's measured effects
- [v3 rubric details](https://github.com/rdmurugan/sabhaos/blob/main/evals/judge.py) — the same `judge.py` is used here
