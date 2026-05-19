"""LLM-as-judge for Sabha OS evals.

Scores a reply on five axes (decisiveness, tradeoff-named, concreteness,
routing-present, length-discipline) using a single Claude call per reply.

Also does pairwise preference: given two replies to the same question,
which would an operator find more useful?
"""

from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass, asdict
from typing import Callable, Optional, TypeVar

from anthropic import (
    Anthropic,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    RateLimitError,
)

try:
    from anthropic import InternalServerError
except ImportError:  # older SDK
    InternalServerError = APIStatusError  # type: ignore[assignment,misc]

try:
    from anthropic import OverloadedError
except ImportError:  # older SDK — fall through to status-code matching
    OverloadedError = None  # type: ignore[assignment]


T = TypeVar("T")

# HTTP status codes that are worth retrying.
_RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 529}

# Class names that should always be retried, regardless of whether the SDK
# version exposes them at the top level. Match by name so import variations
# across SDK versions don't silently break detection.
_RETRY_EXC_NAMES = {
    "OverloadedError",
    "RateLimitError",
    "APIConnectionError",
    "APITimeoutError",
    "APIResponseValidationError",
    "InternalServerError",
}


def _status_code_of(exc: BaseException) -> Optional[int]:
    """Pull the HTTP status code off an anthropic exception via multiple paths."""
    sc = getattr(exc, "status_code", None)
    if sc:
        return sc
    response = getattr(exc, "response", None)
    if response is not None:
        sc = getattr(response, "status_code", None)
        if sc:
            return sc
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        sc = body.get("status_code") or body.get("status")
        if isinstance(sc, int):
            return sc
    return None


def _is_retryable(exc: BaseException) -> bool:
    """Return True for errors a retry might recover from. Defensive: match by
    class name AND isinstance AND status code, so SDK import quirks don't drop
    real retryable errors on the floor (which is the bug that bit us on 1.2.1)."""
    # 1. Class-name match (independent of which SDK version is installed).
    if type(exc).__name__ in _RETRY_EXC_NAMES:
        return True

    # 2. isinstance against whatever the SDK exposes.
    if isinstance(exc, (RateLimitError, APIConnectionError, APITimeoutError)):
        return True
    if OverloadedError is not None and isinstance(exc, OverloadedError):
        return True

    # 3. Status code match — works even on APIStatusError instances of unknown
    #    concrete class.
    if isinstance(exc, APIStatusError):
        sc = _status_code_of(exc)
        if sc in _RETRY_STATUS:
            return True

    return False


def with_retry(
    fn: Callable[[], T],
    max_attempts: int = 10,
    base_delay: float = 2.0,
    max_single_delay: float = 30.0,
    label: str = "",
) -> T:
    """Run `fn` with jittered exponential backoff on transient API errors.

    Defaults: 10 attempts, base 2s, cap single delay at 30s. Worst-case wait
    across 9 retries: 2 + 4 + 8 + 16 + 30 + 30 + 30 + 30 + 30 ≈ 180s (3 min).
    Anthropic API overload windows are usually under 2 minutes; this should
    ride them out.
    """
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            retryable = _is_retryable(exc)
            tag = f"[{label}] " if label else ""
            if not retryable:
                print(
                    f"    {tag}attempt {attempt + 1}/{max_attempts} hit "
                    f"non-retryable {type(exc).__name__}; raising.",
                    flush=True,
                )
                raise
            if attempt == max_attempts - 1:
                print(
                    f"    {tag}giving up after {max_attempts} attempts on "
                    f"{type(exc).__name__}.",
                    flush=True,
                )
                raise
            raw_delay = base_delay * (2 ** attempt)
            delay = min(raw_delay, max_single_delay) + random.uniform(0, base_delay)
            print(
                f"    {tag}attempt {attempt + 1}/{max_attempts} hit "
                f"{type(exc).__name__}; sleeping {delay:.1f}s...",
                flush=True,
            )
            time.sleep(delay)
    raise RuntimeError("unreachable")


JUDGE_RUBRIC = """\
You are an experienced operator scoring a reply to a business question. Use the
v3 sub-axis rubric below. Be strict — most replies should NOT score 5/5.

Three composite axes (decisiveness, tradeoff_named, length_discipline) are each
made of 5 binary sub-criteria. Award 1 point per sub-criterion that is clearly
met; award 0 if it's absent or only partially met. This forces the rubric to
discriminate between strong and very-strong replies (a problem with the v1/v2
rubric, where 75-80% of Sabha replies hit ceiling on these axes).

Sub-axes:

1. DECISIVENESS sub-criteria (each 0 or 1; sum = decisiveness, 0-5):
   d1. made_clear_recommendation       — single committed path (not "you could do A or B")
   d2. stated_confidence_or_conditions — names confidence level OR conditions under which the recommendation would flip
   d3. named_alternative_rejected      — explicitly says what option is being rejected
   d4. committed_specific_next_move    — concrete next action (verb + object), not just opinion
   d5. avoided_hedging_language        — no "maybe", "possibly", "depending on", "it depends" as load-bearing words

2. TRADEOFF_NAMED sub-criteria (each 0 or 1; sum = tradeoff_named, 0-5):
   t1. named_what_is_given_up          — explicit "you lose X"
   t2. quantified_the_cost             — dollars, hours, percentage, opportunity, where possible
   t3. named_who_is_affected           — specific actor/team/customer cohort
   t4. stated_time_horizon             — when does the tradeoff matter (now, Q3, end of year)
   t5. gave_reasoning_to_accept        — "worth it because Z" clearly stated

3. CONCRETENESS (0-5 integer, holistic):
   0 = entirely abstract ("consider your options")
   3 = some specifics but mostly generic
   5 = real vendors, numbers, dates, file paths, named entities throughout

4. ROUTING_PRESENT (0 or 1, binary):
   1 if the reply opens with a "Routing: <ROLE>" line; 0 otherwise.

5. LENGTH_DISCIPLINE sub-criteria (each 0 or 1; sum = length_discipline, 0-5):
   l1. no_three_paragraph_windup       — reply gets to the recommendation in the first 1-2 paragraphs
   l2. no_padding_phrases              — no "Great question", "Let me think about this", "There are many ways..."
   l3. no_unnecessary_disclaimers      — no "I'm just an AI" or "consult a professional" boilerplate (caveats specific to the question are fine)
   l4. no_redundancy                   — does not restate the same idea in two forms
   l5. every_paragraph_advances        — each paragraph adds new information or moves toward action

Return STRICT JSON with this shape and nothing else:

{
  "decisiveness_sub": {
    "d1_made_clear_recommendation": 0|1,
    "d2_stated_confidence_or_conditions": 0|1,
    "d3_named_alternative_rejected": 0|1,
    "d4_committed_specific_next_move": 0|1,
    "d5_avoided_hedging_language": 0|1
  },
  "tradeoff_named_sub": {
    "t1_named_what_is_given_up": 0|1,
    "t2_quantified_the_cost": 0|1,
    "t3_named_who_is_affected": 0|1,
    "t4_stated_time_horizon": 0|1,
    "t5_gave_reasoning_to_accept": 0|1
  },
  "concreteness": <int 0-5>,
  "routing_present": <int 0 or 1>,
  "length_discipline_sub": {
    "l1_no_three_paragraph_windup": 0|1,
    "l2_no_padding_phrases": 0|1,
    "l3_no_unnecessary_disclaimers": 0|1,
    "l4_no_redundancy": 0|1,
    "l5_every_paragraph_advances": 0|1
  },
  "rationale": "<one sentence explaining where the reply lost the most sub-criteria>"
}
"""


PAIRWISE_RUBRIC = """\
You are an experienced operator. You will see a business question and two
replies labeled A and B. Pick the one a busy operator would find more useful
— more decisive, more tradeoff-aware, more concrete, less padding.

Return STRICT JSON with this shape and nothing else:

{
  "winner": "A" | "B" | "tie",
  "rationale": "<one sentence>"
}

Note: there is no "right answer" to the question. You are judging the *reply*,
not the underlying decision.
"""


@dataclass
class JudgeScore:
    """v3 score record. Composite axes (decisiveness, tradeoff_named,
    length_discipline) are sums of their 5 binary sub-criteria. Concreteness
    and routing_present remain holistic/binary as before.

    Backward compatibility: the composite top-level fields are still present
    so aggregation code that read v2 records keeps working. The sub-criteria
    dicts are new; they let later analysis slice by what specifically
    succeeded or failed.
    """

    decisiveness: int                  # 0-5, sum of 5 binary sub-criteria
    tradeoff_named: int                # 0-5, sum of 5 binary sub-criteria
    concreteness: int                  # 0-5, holistic
    routing_present: int               # 0 or 1
    length_discipline: int             # 0-5, sum of 5 binary sub-criteria
    rationale: str
    decisiveness_sub: Optional[dict] = None
    tradeoff_named_sub: Optional[dict] = None
    length_discipline_sub: Optional[dict] = None
    rubric_version: str = "v3"

    @property
    def total(self) -> int:
        return (
            self.decisiveness
            + self.tradeoff_named
            + self.concreteness
            + self.length_discipline
        )  # routing_present is reported separately; not summed.


@dataclass
class PairwiseResult:
    winner: str  # "sabha", "baseline", or "tie"
    rationale: str


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a reply, robust to surrounding text."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object in judge reply: {text[:200]}")
    return json.loads(match.group(0))


def _sum_sub(sub: dict) -> int:
    """Sum a sub-criteria dict's 0/1 values. Tolerant of missing keys
    (counts them as 0). Caps at 5 so a malformed judge response can't
    blow up downstream totals."""
    if not isinstance(sub, dict):
        return 0
    total = 0
    for v in sub.values():
        try:
            total += 1 if int(v) >= 1 else 0
        except (TypeError, ValueError):
            continue
    return min(total, 5)


def score_reply(
    client, question: str, reply: str, judge_model: str
) -> JudgeScore:
    """Score a single reply against the v3 sub-axis rubric. Returns JudgeScore.

    Accepts any judge `client` that exposes the Anthropic-style
    `messages.create(model, max_tokens, system, messages)` shape. The
    cross-model judge harness wraps OpenAI/Google clients to match this
    interface, so this function doesn't need to know which provider's
    underneath.
    """
    response = with_retry(
        lambda: client.messages.create(
            model=judge_model,
            max_tokens=800,  # v3 rubric returns more fields; needs more room
            system=JUDGE_RUBRIC,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n---\n\nReply:\n{reply}\n\n---\n\n"
                        "Score this reply against the v3 sub-axis rubric. "
                        "Return JSON only."
                    ),
                }
            ],
        ),
        label="judge:score",
    )
    text = response.content[0].text
    data = _extract_json(text)

    # v3 path (preferred): sum sub-criteria into composite axes
    d_sub = data.get("decisiveness_sub")
    t_sub = data.get("tradeoff_named_sub")
    l_sub = data.get("length_discipline_sub")

    if d_sub is not None or t_sub is not None or l_sub is not None:
        # v3 grader response
        decisiveness = _sum_sub(d_sub) if d_sub else int(data.get("decisiveness", 0))
        tradeoff = _sum_sub(t_sub) if t_sub else int(data.get("tradeoff_named", 0))
        length = _sum_sub(l_sub) if l_sub else int(data.get("length_discipline", 0))
    else:
        # v2 fallback (no sub-criteria returned by judge)
        decisiveness = int(data.get("decisiveness", 0))
        tradeoff = int(data.get("tradeoff_named", 0))
        length = int(data.get("length_discipline", 0))

    return JudgeScore(
        decisiveness=decisiveness,
        tradeoff_named=tradeoff,
        concreteness=int(data.get("concreteness", 0)),
        routing_present=int(data.get("routing_present", 0)),
        length_discipline=length,
        rationale=str(data.get("rationale", "")),
        decisiveness_sub=d_sub,
        tradeoff_named_sub=t_sub,
        length_discipline_sub=l_sub,
        rubric_version="v3" if (d_sub or t_sub or l_sub) else "v2-fallback",
    )


def pairwise_preference(
    client,
    question: str,
    sabha_reply: str,
    baseline_reply: str,
    judge_model: str,
    seed: Optional[int] = None,
) -> PairwiseResult:
    """Pairwise judge with order randomization to avoid position bias."""
    rng = random.Random(seed)
    sabha_first = rng.random() < 0.5
    if sabha_first:
        reply_a, reply_b = sabha_reply, baseline_reply
        label_map = {"A": "sabha", "B": "baseline"}
    else:
        reply_a, reply_b = baseline_reply, sabha_reply
        label_map = {"A": "baseline", "B": "sabha"}

    response = with_retry(
        lambda: client.messages.create(
            model=judge_model,
            max_tokens=300,
            system=PAIRWISE_RUBRIC,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n---\n\n"
                        f"Reply A:\n{reply_a}\n\n---\n\n"
                        f"Reply B:\n{reply_b}\n\n---\n\n"
                        "Pick. Return JSON only."
                    ),
                }
            ],
        ),
        label="judge:pairwise",
    )
    text = response.content[0].text
    data = _extract_json(text)
    raw = str(data["winner"]).strip().upper()
    if raw in ("A", "B"):
        winner = label_map[raw]
    else:
        winner = "tie"
    return PairwiseResult(winner=winner, rationale=str(data.get("rationale", "")))


def serialize(obj) -> dict:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    raise TypeError(f"Cannot serialize {type(obj)}")
