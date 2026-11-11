"""Single-agent (O0) LLM trading decision call.

Pilot Spec: experiments/pilot/global-linkage-channel-ablation-blanket-index.yaml

Uses the project's existing OpenAI-compatible LLM_BASE_URL / LLM_API_KEY / LLM_MODEL
(same backbone already used by mcp__llm-review — no fine-tuning, fixed backbone
across all three conditions per the harness's model-backbone control).
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

import requests

SYSTEM_PROMPT = (
    "You are a single-agent KOSPI equity trading decision system. You will be given "
    "market context for one stock on one trading day. Respond with STRICT JSON only, "
    "no markdown fences, no commentary outside the JSON object, in exactly this shape:\n"
    '{"action": "BUY" | "SELL" | "HOLD", "position_fraction": <float 0.0-1.0>, '
    '"rationale": "<one short sentence>"}\n'
    "position_fraction is the target fraction of this name's allocation slot to hold "
    "(0.0 = fully out, 1.0 = fully in). This is a long-only system: SELL means reduce "
    "toward 0.0, never short."
)


@dataclass(frozen=True)
class AgentDecision:
    action: str
    position_fraction: float
    rationale: str
    parse_ok: bool


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return json.loads(text)


def call_llm(context: str, temperature: float, max_tokens: int, timeout_s: int) -> str:
    base_url = os.environ["LLM_BASE_URL"].rstrip("/")
    api_key = os.environ["LLM_API_KEY"]
    model = os.environ["LLM_MODEL"]

    response = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=timeout_s,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"]


def decide(
    context: str,
    temperature: float,
    max_tokens: int,
    timeout_s: int,
    max_retries: int,
    fallback_action: str,
    fallback_position_fraction: float,
) -> AgentDecision:
    """Get one trading decision, retrying once on parse failure, else fall back."""
    last_error: Exception | None = None
    for _ in range(max_retries + 1):
        try:
            raw = call_llm(context, temperature, max_tokens, timeout_s)
            parsed = _extract_json(raw)
            action = str(parsed["action"]).upper()
            if action not in {"BUY", "SELL", "HOLD"}:
                raise ValueError(f"invalid action '{action}'")
            fraction = float(parsed["position_fraction"])
            fraction = min(max(fraction, 0.0), 1.0)
            rationale = str(parsed.get("rationale", ""))
            return AgentDecision(action=action, position_fraction=fraction, rationale=rationale, parse_ok=True)
        except Exception as error:  # noqa: BLE001 - pilot diagnostic, any parse/API failure triggers fallback
            last_error = error
            continue

    return AgentDecision(
        action=fallback_action,
        position_fraction=fallback_position_fraction,
        rationale=f"fallback (parse/API failure: {last_error})",
        parse_ok=False,
    )
