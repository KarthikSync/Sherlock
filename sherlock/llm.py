from __future__ import annotations

import os
import sys
from typing import Any


_BASE_URL = "https://openrouter.ai/api/v1"
_DEFAULT_MODEL = "openai/gpt-4o-mini"


def summarize(finding: dict[str, Any]) -> str | None:
    """
    Generate a one-sentence hypothesis for a case using OpenRouter.

    Returns None (with a stderr warning) if the key is absent or the call fails.
    Requires: pip install sherlock[llm]
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print(
            "Warning: OPENROUTER_API_KEY not set — skipping LLM summarization.",
            file=sys.stderr,
        )
        return None

    try:
        from openai import OpenAI
    except ImportError:
        print(
            "Warning: openai package not installed — run `pip install sherlock[llm]`.",
            file=sys.stderr,
        )
        return None

    model = os.environ.get("OPENROUTER_MODEL", _DEFAULT_MODEL)
    client = OpenAI(api_key=api_key, base_url=_BASE_URL)

    prompt = (
        f"In one sentence, explain why {finding['service']} {finding['metric']} "
        f"is anomalous. Observed value: {finding['value']}. "
        f"Threshold: {finding['threshold']}. Severity: {finding['severity']}."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        print(f"Warning: LLM call failed ({exc}) — skipping summarization.", file=sys.stderr)
        return None
