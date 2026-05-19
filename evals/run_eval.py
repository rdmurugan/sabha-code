"""Sabha Code eval harness.

Adapted from the Sabha OS harness (github.com/rdmurugan/sabhaos). Same
v3 sub-axis rubric + pairwise judge methodology, applied to the
developer-shaped Sabha Code protocol.

The eval simulates what a Copilot-equivalent LLM produces with vs without
the Sabha Code protocol loaded as a system prompt. The candidate model
is invoked via the Anthropic API by default, but the protocol is text —
the same eval can be run on any LLM exposed via this harness's provider
adapters.

Usage:
    pip install -r evals/requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    python evals/run_eval.py
    python evals/run_eval.py --limit 5                  # smoke test
    python evals/run_eval.py --judge-provider openai    # cross-model judge
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Optional

import yaml
from anthropic import Anthropic


# Bootstrap: put this directory on sys.path so `judge` and `judge_clients`
# import the same way the Sabha OS harness does.
sys.path.insert(0, str(Path(__file__).parent))
from judge import (  # noqa: E402
    JudgeScore,
    PairwiseResult,
    pairwise_preference,
    score_reply,
    with_retry,
)


REPO_ROOT = Path(__file__).parent.parent
QUESTIONS_PATH = REPO_ROOT / "evals" / "questions.yaml"
PROTOCOL_PATH = REPO_ROOT / ".github" / "copilot-instructions.md"
INSTRUCTIONS_DIR = REPO_ROOT / "instructions"
RESULTS_DIR = REPO_ROOT / "evals" / "results"

DEFAULT_CANDIDATE_MODEL = "claude-sonnet-4-6"
DEFAULT_JUDGE_MODEL = "claude-opus-4-7"
CONDITIONS = ("baseline", "sabha_code")


# Map question-tagged role → instruction filename. Lowercase, no extension.
ROLE_TO_INSTRUCTION = {
    "Architect": "architect",
    "Reviewer": "reviewer",
    "Security": "security",
    "Performance": "performance",
    "QA": "qa",
    "Mentor": "mentor",
    "Tech Lead": "techlead",
    "TechLead": "techlead",  # tolerate both writings
}


def load_protocol() -> str:
    """The .github/copilot-instructions.md file IS Sabha Code."""
    return PROTOCOL_PATH.read_text()


def load_role_instructions(role: Optional[str]) -> str:
    """Return the role-specific instruction file content, or '' if no match.

    In Copilot, the per-role file at instructions/<role>.instructions.md
    loads based on the `applyTo` frontmatter. The eval harness simulates
    activation by appending the file's content to the system prompt for
    the matching role.
    """
    if not role:
        return ""
    slug = ROLE_TO_INSTRUCTION.get(role)
    if not slug:
        return ""
    path = INSTRUCTIONS_DIR / f"{slug}.instructions.md"
    if not path.exists():
        return ""
    return f"\n\n---\n# ROLE INSTRUCTION FILE: {role.upper()}\n---\n\n" + path.read_text()


def generate_reply(
    candidate_client,
    model: str,
    question: str,
    condition: str,
    protocol_system: str,
    role: Optional[str] = None,
) -> str:
    """Run the candidate model under the given condition.

    `baseline` = no system prompt (vanilla LLM).
    `sabha_code` = the Sabha Code protocol + the matching role instruction
                    file loaded as system prompt.
    """
    kwargs = {
        "model": model,
        "max_tokens": 2000,  # bumped from sabha-os 1200 default to avoid truncation
        "messages": [{"role": "user", "content": question}],
    }
    if condition == "sabha_code":
        kwargs["system"] = protocol_system + load_role_instructions(role)
    response = with_retry(
        lambda: candidate_client.messages.create(**kwargs),
        label=f"gen:{condition}",
    )
    return response.content[0].text


def run_question(
    candidate_client,
    judge_client,
    candidate_model: str,
    judge_model: str,
    protocol_system: str,
    question: dict,
    seed: int,
) -> dict:
    qid = question["id"]
    prompt = question["prompt"]
    print(f"  [{qid}] generating...", flush=True)

    replies: dict[str, str] = {}
    for condition in CONDITIONS:
        replies[condition] = generate_reply(
            candidate_client,
            candidate_model,
            prompt,
            condition,
            protocol_system,
            role=question.get("role"),
        )

    print(f"  [{qid}] judging...", flush=True)
    scores: dict[str, JudgeScore] = {}
    for condition in CONDITIONS:
        scores[condition] = score_reply(
            judge_client, prompt, replies[condition], judge_model
        )

    pairwise: PairwiseResult = pairwise_preference(
        judge_client,
        prompt,
        sabha_reply=replies["sabha_code"],
        baseline_reply=replies["baseline"],
        judge_model=judge_model,
        seed=seed,
    )

    role_instructions_loaded = bool(load_role_instructions(question.get("role")))
    return {
        "id": qid,
        "role": question.get("role"),
        "category": question.get("category"),
        "role_instructions_loaded": role_instructions_loaded,
        "prompt": prompt,
        "replies": replies,
        "scores": {
            cond: {
                "decisiveness": s.decisiveness,
                "tradeoff_named": s.tradeoff_named,
                "concreteness": s.concreteness,
                "routing_present": s.routing_present,
                "length_discipline": s.length_discipline,
                "total": s.total,
                "rationale": s.rationale,
                "decisiveness_sub": s.decisiveness_sub,
                "tradeoff_named_sub": s.tradeoff_named_sub,
                "length_discipline_sub": s.length_discipline_sub,
                "rubric_version": s.rubric_version,
            }
            for cond, s in scores.items()
        },
        "pairwise": {
            # rename the result key from generic 'sabha' to 'sabha_code'
            # for clarity in the sabha-code repo, but the judge logic is
            # the same.
            "winner": (
                "sabha_code" if pairwise.winner == "sabha"
                else pairwise.winner
            ),
            "rationale": pairwise.rationale,
        },
    }


def aggregate(records: list[dict]) -> dict:
    per_condition = {cond: {} for cond in CONDITIONS}
    axes = ["decisiveness", "tradeoff_named", "concreteness",
            "routing_present", "length_discipline", "total"]
    for cond in CONDITIONS:
        for axis in axes:
            vals = [r["scores"][cond][axis] for r in records]
            per_condition[cond][axis] = round(sum(vals) / len(vals), 2)

    pairwise = {"sabha_code": 0, "baseline": 0, "tie": 0}
    for r in records:
        w = r["pairwise"]["winner"]
        if w in pairwise:
            pairwise[w] += 1
        else:
            pairwise["tie"] += 1

    return {
        "per_condition": per_condition,
        "pairwise": pairwise,
        "n": len(records),
    }


def render_markdown(meta: dict, summary: dict, records: list[dict]) -> str:
    s = summary
    b = s["per_condition"]["baseline"]
    sc = s["per_condition"]["sabha_code"]
    pw = s["pairwise"]
    n = s["n"]
    rate = pw["sabha_code"] / n * 100 if n else 0

    lines = [
        f"# Sabha Code — eval results ({meta['run_date']})",
        "",
        f"- **Candidate model:** `{meta['candidate_model']}`",
        f"- **Judge model:** `{meta.get('judge_provider', 'anthropic')}:{meta['judge_model']}`",
        f"- **Question set:** v1 ({n} questions)",
        f"- **Rubric version:** {meta.get('rubric_version', 'v3')}",
        "",
        "## Summary",
        "",
        "| Metric | Baseline | Sabha Code | Δ |",
        "|---|---:|---:|---:|",
    ]
    for axis_key, label in [
        ("decisiveness", "decisiveness"),
        ("tradeoff_named", "tradeoff named"),
        ("concreteness", "concreteness"),
        ("routing_present", "routing present"),
        ("length_discipline", "length discipline"),
        ("total", "total"),
    ]:
        delta = sc[axis_key] - b[axis_key]
        lines.append(f"| {label} | {b[axis_key]} | {sc[axis_key]} | {delta:+.2f} |")
    lines.extend([
        "",
        "### Pairwise preference",
        "",
        f"- **Sabha Code preferred:** {pw['sabha_code']} / {n} ({rate:.1f}%)",
        f"- **Baseline preferred:** {pw['baseline']} / {n} ({pw['baseline']/n*100:.1f}%)" if n else "",
        f"- **Tie:** {pw['tie']} / {n}" if n else "",
        "",
        "## Per-question results",
        "",
        "| id | role | role instr loaded | pairwise winner | Sabha Code total | Baseline total |",
        "|---|---|---|---|---:|---:|",
    ])
    for r in records:
        rl = "✓" if r.get("role_instructions_loaded") else "—"
        sc_total = r["scores"]["sabha_code"]["total"]
        b_total = r["scores"]["baseline"]["total"]
        winner = r["pairwise"]["winner"]
        winner_md = f"**{winner}**"
        lines.append(
            f"| `{r['id']}` | {r.get('role', '—')} | {rl} | {winner_md} | "
            f"{sc_total} | {b_total} |"
        )
    return "\n".join(lines) + "\n"


def load_questions(limit: Optional[int]) -> list[dict]:
    data = yaml.safe_load(QUESTIONS_PATH.read_text())
    qs = data["questions"]
    return qs[:limit] if limit else qs


def save_checkpoint(records: list[dict], basename: str, meta: dict):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary = aggregate(records)
    path = RESULTS_DIR / f"{basename}.json"
    path.write_text(json.dumps(
        {"meta": meta, "summary": summary, "records": records},
        indent=2,
    ))
    md_path = RESULTS_DIR / f"{basename}.md"
    md_path.write_text(render_markdown(meta, summary, records))
    (RESULTS_DIR / "latest.md").write_text(render_markdown(meta, summary, records))


def load_checkpoint(basename: str) -> tuple[list[dict], Optional[dict]]:
    path = RESULTS_DIR / f"{basename}.json"
    if not path.exists():
        return [], None
    data = json.loads(path.read_text())
    return data.get("records", []), data.get("meta")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Sabha Code eval.")
    parser.add_argument("--candidate-model", default=DEFAULT_CANDIDATE_MODEL)
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Judge model. If omitted, defaults per --judge-provider.",
    )
    parser.add_argument(
        "--judge-provider",
        choices=["anthropic", "openai", "google"],
        default="anthropic",
        help=(
            "Which provider hosts the judge model. Default 'anthropic'. "
            "Use 'openai' or 'google' to defeat in-family bias."
        ),
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-name", default=None)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip questions already completed in the output file.",
    )
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set. Export it and re-run.", file=sys.stderr)
        return 1
    candidate_client = Anthropic()

    from judge_clients import build_judge_client, default_judge_model  # noqa: E402
    judge_client = build_judge_client(args.judge_provider)
    judge_model = args.judge_model or default_judge_model(args.judge_provider) or DEFAULT_JUDGE_MODEL

    protocol_system = load_protocol()
    questions = load_questions(args.limit)

    run_date = dt.date.today().isoformat()
    basename = args.out_name or run_date
    meta = {
        "run_date": run_date,
        "candidate_model": args.candidate_model,
        "judge_provider": args.judge_provider,
        "judge_model": judge_model,
        "rubric_version": "v3",
        "project": "sabha-code",
    }

    if args.resume:
        existing, existing_meta = load_checkpoint(basename)
        done_ids = {r["id"] for r in existing}
        records: list[dict] = list(existing)
        if existing_meta:
            meta["run_date"] = existing_meta.get("run_date", run_date)
        if done_ids:
            print(
                f"Resuming '{basename}': {len(done_ids)} of {len(questions)} "
                f"questions already complete; will skip those."
            )
    else:
        records = []
        done_ids = set()

    print(
        f"Running {len(questions)} questions "
        f"(candidate={args.candidate_model}, "
        f"judge={args.judge_provider}:{judge_model}, rubric=v3)..."
    )

    for i, q in enumerate(questions, start=1):
        if q["id"] in done_ids:
            print(f"[{i}/{len(questions)}] {q['id']} (cached, skipping)")
            continue
        print(f"[{i}/{len(questions)}] {q['id']}")
        rec = run_question(
            candidate_client=candidate_client,
            judge_client=judge_client,
            candidate_model=args.candidate_model,
            judge_model=judge_model,
            protocol_system=protocol_system,
            question=q,
            seed=args.seed + i,
        )
        records.append(rec)
        save_checkpoint(records, basename, meta)

    summary = aggregate(records)
    json_path = RESULTS_DIR / f"{basename}.json"
    md_path = RESULTS_DIR / f"{basename}.md"
    latest_md = RESULTS_DIR / "latest.md"

    print(f"\nDone. Wrote:\n  {json_path}\n  {md_path}\n  {latest_md}")
    pw = summary["pairwise"]
    print(
        f"Pairwise preference: sabha_code={pw['sabha_code']} "
        f"baseline={pw['baseline']} tie={pw['tie']} (n={summary['n']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
