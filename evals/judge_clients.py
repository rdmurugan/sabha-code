"""Cross-model judge clients for the Sabha OS eval.

The judge step is the highest-leverage credibility lever: defeating
in-family bias by having a different model family score the candidate's
output. This module provides a thin adapter so the existing `judge.py`
functions (`score_reply`, `pairwise_preference`) can run against
Anthropic, OpenAI, or Google models without changes to the calling code.

Design contract: every adapter exposes a `.messages.create(model,
max_tokens, system, messages)` shape and returns an object with a
`.content[0].text` field. That's the minimum Anthropic-style API the
judge code in `judge.py` uses. Each provider's native SDK is wrapped
just enough to match.

Usage from `run_eval.py`:

    from evals.judge_clients import build_judge_client
    judge_client = build_judge_client(provider="anthropic")  # or "openai", "google"
    score = score_reply(judge_client, question, reply, judge_model)
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Any, List, Optional, Sequence


SUPPORTED_PROVIDERS = ("anthropic", "openai", "google")

# Sensible default judge model per provider.
DEFAULT_JUDGE_MODEL = {
    "anthropic": "claude-opus-4-7",
    "openai": "gpt-5",          # placeholder; substitute the actual model id available
    "google": "gemini-2.0-pro",  # placeholder; substitute the actual model id available
}


# ────────────────────────────────────────────────────────────────────────────
# The Anthropic-shaped response objects the judge.py code expects.
# We construct these manually for OpenAI / Google adapters so the calling
# code stays unchanged.
# ────────────────────────────────────────────────────────────────────────────


@dataclass
class _TextBlock:
    text: str


@dataclass
class _Response:
    content: Sequence[_TextBlock]


# ────────────────────────────────────────────────────────────────────────────
# Anthropic adapter — pass-through (native client already matches the shape)
# ────────────────────────────────────────────────────────────────────────────


def _build_anthropic_client():
    try:
        from anthropic import Anthropic
    except ImportError:
        _die_missing("anthropic", "anthropic>=0.40")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        _die_no_key("ANTHROPIC_API_KEY")
    return Anthropic()


# ────────────────────────────────────────────────────────────────────────────
# OpenAI adapter — wraps openai.OpenAI to match the Anthropic shape
# ────────────────────────────────────────────────────────────────────────────


class _OpenAIMessagesShim:
    """Mimics `anthropic.Anthropic().messages` for OpenAI."""

    def __init__(self, openai_client):
        self._client = openai_client

    def create(self, *, model: str, max_tokens: int, system: str, messages: list):
        # OpenAI chat messages put `system` inline as a role=system message.
        oai_messages = [{"role": "system", "content": system}]
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            oai_messages.append({"role": role, "content": content})

        # OpenAI v1+ SDK; using Responses-style if available, falling back to
        # chat.completions which is the durable shape.
        resp = self._client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=oai_messages,
        )
        text = resp.choices[0].message.content or ""
        return _Response(content=[_TextBlock(text=text)])


class _OpenAIClient:
    def __init__(self, openai_client):
        self.messages = _OpenAIMessagesShim(openai_client)


def _build_openai_client():
    try:
        from openai import OpenAI
    except ImportError:
        _die_missing("openai", "openai>=1.0")
    if not os.environ.get("OPENAI_API_KEY"):
        _die_no_key("OPENAI_API_KEY")
    return _OpenAIClient(OpenAI())


# ────────────────────────────────────────────────────────────────────────────
# Google (Gemini) adapter — wraps google.generativeai
# ────────────────────────────────────────────────────────────────────────────


class _GoogleMessagesShim:
    """Mimics `anthropic.Anthropic().messages` for Google Generative AI."""

    def __init__(self, genai_module):
        self._genai = genai_module

    def create(self, *, model: str, max_tokens: int, system: str, messages: list):
        # Google's generative_ai uses a different conversation shape; we
        # collapse the conversation into a single user prompt prefixed with
        # the system instructions. For pure judging (one-shot scoring), this
        # is equivalent.
        user_blob = system + "\n\n" + "\n\n".join(
            (m.get("content", "") if isinstance(m, dict) else str(m))
            for m in messages
        )
        model_obj = self._genai.GenerativeModel(model)
        resp = model_obj.generate_content(
            user_blob,
            generation_config={"max_output_tokens": max_tokens, "temperature": 0.0},
        )
        text = getattr(resp, "text", "") or ""
        return _Response(content=[_TextBlock(text=text)])


class _GoogleClient:
    def __init__(self, genai_module):
        self.messages = _GoogleMessagesShim(genai_module)


def _build_google_client():
    try:
        import google.generativeai as genai
    except ImportError:
        _die_missing("google.generativeai", "google-generativeai>=0.7")
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        _die_no_key("GOOGLE_API_KEY (or GEMINI_API_KEY)")
    genai.configure(api_key=key)
    return _GoogleClient(genai)


# ────────────────────────────────────────────────────────────────────────────
# Public factory
# ────────────────────────────────────────────────────────────────────────────


def build_judge_client(provider: str):
    """Return an Anthropic-shaped client for the named provider.

    Provider values: 'anthropic', 'openai', 'google'.
    Raises SystemExit with a helpful message if the SDK or API key is
    missing for the requested provider.
    """
    provider = provider.lower()
    if provider not in SUPPORTED_PROVIDERS:
        sys.exit(
            f"ERROR: unknown judge provider '{provider}'. "
            f"Supported: {', '.join(SUPPORTED_PROVIDERS)}"
        )
    if provider == "anthropic":
        return _build_anthropic_client()
    if provider == "openai":
        return _build_openai_client()
    if provider == "google":
        return _build_google_client()
    raise RuntimeError("unreachable")


def default_judge_model(provider: str) -> str:
    return DEFAULT_JUDGE_MODEL.get(provider.lower(), "")


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────


def _die_missing(import_name: str, pip_name: str) -> None:
    sys.exit(
        f"ERROR: judge provider needs the `{import_name}` Python package "
        f"(not installed in this env).\n\n"
        f"    pip install '{pip_name}'\n\n"
        f"Or install the eval extras:\n\n"
        f"    pip install -r evals/requirements.txt\n"
    )


def _die_no_key(env_var: str) -> None:
    sys.exit(
        f"ERROR: judge provider needs `{env_var}` set in the environment.\n\n"
        f"    export {env_var}=...\n"
    )
