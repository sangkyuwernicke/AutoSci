"""S0 (single-agent) and S3 (minimal TradingAgents-style scaffold) decision paths.

Pilot Spec: experiments/pilot/kospi-information-diet-vs-reasoning-scaffold.yaml

S0: one LLM call, all channel content in one prompt -> BUY/SELL/HOLD + fraction.

S3: a *minimal reimplementation* of TradingAgents' role structure (not the
published repo, per the Pilot Spec's cost-bounding note): 4 parallel analyst
calls (fundamental/news/technical/macro-flow), each given only its relevant
slice of the context string, then 1 combined bull/bear debate call, then 1
trader call, then 1 combined risk-team + manager call. 4 + 1 + 1 + 1 = 7 LLM
calls per decision, matching the Pilot Spec's cost estimate.

Both paths use the project's existing OpenAI-compatible LLM_BASE_URL /
LLM_API_KEY / LLM_MODEL (same backbone across S0 and S3 — no fine-tuning,
fixed backbone, so any performance difference is attributable to scaffold
structure, not model choice).
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field

import requests

RATE_LIMIT_BACKOFF_S = (2, 5, 10)  # seconds, one entry per retry attempt on HTTP 429


@dataclass(frozen=True)
class AgentDecision:
    action: str
    position_fraction: float
    rationale: str
    parse_ok: bool
    n_llm_calls: int
    n_parse_failures: int
    trace: list[str] = field(default_factory=list)  # one short line per stage, for the qualitative check


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return json.loads(text)


def _call_llm(system: str, user: str, temperature: float, max_tokens: int, timeout_s: int) -> str:
    """Call the LLM backend, retrying on HTTP 429 (rate limit) with backoff.

    The project's LLM_BASE_URL routes through a shared provider (OpenRouter)
    that rate-limits aggressively under back-to-back calls — confirmed live
    during pilot debugging (every failure in an early sanity run was a 429,
    not a JSON parse problem). Retrying 429 here, separately from
    `_call_json`'s parse-failure retry, keeps `parse_failure_rate` measuring
    what it's meant to measure (prompt/formatting adherence), not transient
    exogenous rate-limiting.
    """
    base_url = os.environ["LLM_BASE_URL"].rstrip("/")
    api_key = os.environ["LLM_API_KEY"]
    model = os.environ["LLM_MODEL"]

    last_error: requests.exceptions.HTTPError | None = None
    for attempt, backoff_s in enumerate((0, *RATE_LIMIT_BACKOFF_S)):
        if backoff_s:
            time.sleep(backoff_s)
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=timeout_s,
        )
        if response.status_code == 429:
            last_error = requests.exceptions.HTTPError(f"429 rate-limited (attempt {attempt + 1})", response=response)
            continue
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]

    raise last_error


def _call_json(
    system: str, user: str, temperature: float, max_tokens: int, timeout_s: int, max_retries: int
) -> tuple[dict | None, int, int]:
    """Call the LLM expecting strict JSON. Returns (parsed_or_None, n_calls, n_failures)."""
    n_calls = 0
    n_failures = 0
    for _ in range(max_retries + 1):
        n_calls += 1
        try:
            raw = _call_llm(system, user, temperature, max_tokens, timeout_s)
            return _extract_json(raw), n_calls, n_failures
        except Exception as error:  # noqa: BLE001 - pilot diagnostic, any parse/API failure counted and retried
            n_failures += 1
            if os.environ.get("PILOT_DEBUG"):
                print(f"[DEBUG parse-failure] {type(error).__name__}: {error} | raw={raw[:300]!r}" if "raw" in dir() else f"[DEBUG parse-failure] {type(error).__name__}: {error} (no raw text — call itself failed)")
            continue
    return None, n_calls, n_failures


def _slice_context(context: str, header_keyword: str) -> str:
    """Extract the '[... header_keyword ...]' block from a channels.py-built context string."""
    lines = context.splitlines()
    capture = False
    captured: list[str] = []
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            if header_keyword.lower() in line.lower():
                capture = True
                captured.append(line)
                continue
            elif capture:
                break
        elif capture:
            captured.append(line)
    return "\n".join(captured) if captured else f"(no '{header_keyword}' block present in this diet condition)"


S0_SYSTEM = (
    "You are a single-agent KOSPI equity trading decision system. You will be given "
    "market context for one stock on one trading day. Respond with STRICT JSON only, "
    "no markdown fences, no commentary outside the JSON object, in exactly this shape:\n"
    '{"action": "BUY" | "SELL" | "HOLD", "position_fraction": <float 0.0-1.0>, '
    '"rationale": "<one short sentence>"}\n'
    "position_fraction is the target fraction of this name's allocation slot to hold. "
    "This is a long-only system: SELL means reduce toward 0.0, never short."
)

ANALYST_SYSTEM_TEMPLATE = (
    "You are the {role} analyst on a KOSPI trading desk. You will be given only your "
    "specialty's slice of today's information for one stock. Respond with STRICT JSON "
    "only, no markdown fences, in exactly this shape:\n"
    '{{"stance": "bullish" | "bearish" | "neutral", "analysis": "<one short sentence '
    'referencing specific content from your input, not a generic statement>"}}'
)

DEBATE_SYSTEM = (
    "You are facilitating a bull/bear research debate on a KOSPI trading desk. You will "
    "be given four analyst reports. Produce a short bull case, a short bear case, and a "
    "resolution. Respond with STRICT JSON only, no markdown fences, in exactly this shape:\n"
    '{"bull_case": "<one sentence>", "bear_case": "<one sentence>", '
    '"resolution": "bullish" | "bearish" | "neutral", "resolution_rationale": "<one sentence>"}'
)

TRADER_SYSTEM = (
    "You are the trader on a KOSPI trading desk. You will be given four analyst reports "
    "and a debate resolution. Propose a trade. Respond with STRICT JSON only, no markdown "
    "fences, in exactly this shape:\n"
    '{"action": "BUY" | "SELL" | "HOLD", "position_fraction": <float 0.0-1.0>, '
    '"rationale": "<one short sentence referencing the debate resolution>"}'
)

RISK_MANAGER_SYSTEM = (
    "You are the risk team + fund manager on a KOSPI trading desk, reviewing the trader's "
    "proposed action. You may approve it as-is or adjust position_fraction down (never up) "
    "if the analyst reports show conflicting signals. This is long-only: never propose SELL "
    "below 0.0 fraction. Respond with STRICT JSON only, no markdown fences, in exactly this "
    "shape:\n"
    '{"action": "BUY" | "SELL" | "HOLD", "position_fraction": <float 0.0-1.0>, '
    '"rationale": "<one short sentence stating whether/why you adjusted the trader\'s proposal>"}'
)


def _finalize(
    parsed: dict | None,
    n_calls: int,
    n_failures: int,
    fallback_action: str,
    fallback_fraction: float,
    trace: list[str],
) -> AgentDecision:
    if parsed is None:
        trace.append("FINAL: fallback (parse/API failure)")
        return AgentDecision(
            action=fallback_action,
            position_fraction=fallback_fraction,
            rationale="fallback (parse/API failure)",
            parse_ok=False,
            n_llm_calls=n_calls,
            n_parse_failures=n_failures,
            trace=trace,
        )
    action = str(parsed.get("action", fallback_action)).upper()
    if action not in {"BUY", "SELL", "HOLD"}:
        action = fallback_action
    fraction = min(max(float(parsed.get("position_fraction", fallback_fraction)), 0.0), 1.0)
    rationale = str(parsed.get("rationale", ""))
    trace.append(f"FINAL: {action} frac={fraction:.2f} — {rationale}")
    return AgentDecision(
        action=action,
        position_fraction=fraction,
        rationale=rationale,
        parse_ok=True,
        n_llm_calls=n_calls,
        n_parse_failures=n_failures,
        trace=trace,
    )


def run_s0(context: str, llm_cfg: dict, exec_cfg: dict) -> AgentDecision:
    parsed, calls, failures = _call_json(
        S0_SYSTEM, context, llm_cfg["temperature"], llm_cfg["max_tokens"], llm_cfg["request_timeout_s"], exec_cfg["max_llm_retries"]
    )
    trace = [f"S0 single-call: parse_ok={parsed is not None}"]
    return _finalize(parsed, calls, failures, exec_cfg["fallback_action"], exec_cfg["fallback_position_fraction"], trace)


def run_s3(context: str, llm_cfg: dict, exec_cfg: dict) -> AgentDecision:
    total_calls = 0
    total_failures = 0
    trace: list[str] = []

    analyst_specs = [
        ("fundamental", "DART disclosures"),
        ("news", "news"),
        ("technical", "Price/Technical"),
        ("macro-flow", "Investor net-flow"),
    ]
    reports: dict[str, dict] = {}
    for role, keyword in analyst_specs:
        slice_text = _slice_context(context, keyword)
        parsed, calls, failures = _call_json(
            ANALYST_SYSTEM_TEMPLATE.format(role=role),
            slice_text,
            llm_cfg["temperature"],
            llm_cfg["analyst_max_tokens"],
            llm_cfg["request_timeout_s"],
            exec_cfg["max_llm_retries"],
        )
        total_calls += calls
        total_failures += failures
        report = parsed or {"stance": "neutral", "analysis": "(fallback: analyst call failed)"}
        reports[role] = report
        trace.append(f"analyst[{role}] input_present={'no ' not in slice_text[:4]} stance={report.get('stance')}")

    reports_text = "\n".join(f"- {role}: stance={r.get('stance')}, analysis={r.get('analysis')}" for role, r in reports.items())

    debate_parsed, calls, failures = _call_json(
        DEBATE_SYSTEM, reports_text, llm_cfg["temperature"], llm_cfg["analyst_max_tokens"], llm_cfg["request_timeout_s"], exec_cfg["max_llm_retries"]
    )
    total_calls += calls
    total_failures += failures
    debate = debate_parsed or {"resolution": "neutral", "resolution_rationale": "(fallback: debate call failed)"}
    trace.append(f"debate: resolution={debate.get('resolution')} — {debate.get('resolution_rationale')}")

    trader_input = reports_text + f"\n\nDebate resolution: {debate.get('resolution')} — {debate.get('resolution_rationale')}"
    trader_parsed, calls, failures = _call_json(
        TRADER_SYSTEM, trader_input, llm_cfg["temperature"], llm_cfg["max_tokens"], llm_cfg["request_timeout_s"], exec_cfg["max_llm_retries"]
    )
    total_calls += calls
    total_failures += failures
    if trader_parsed:
        trace.append(f"trader proposal: {trader_parsed.get('action')} frac={trader_parsed.get('position_fraction')}")
        risk_input = trader_input + f"\n\nTrader proposal: {json.dumps(trader_parsed)}"
    else:
        trace.append("trader proposal: FAILED (fallback)")
        risk_input = trader_input + "\n\nTrader proposal: (failed — propose HOLD 0.0 for review)"

    risk_parsed, calls, failures = _call_json(
        RISK_MANAGER_SYSTEM, risk_input, llm_cfg["temperature"], llm_cfg["max_tokens"], llm_cfg["request_timeout_s"], exec_cfg["max_llm_retries"]
    )
    total_calls += calls
    total_failures += failures

    return _finalize(risk_parsed, total_calls, total_failures, exec_cfg["fallback_action"], exec_cfg["fallback_position_fraction"], trace)


def run_scaffold(scaffold: str, context: str, llm_cfg: dict, exec_cfg: dict) -> AgentDecision:
    if scaffold == "S0":
        return run_s0(context, llm_cfg, exec_cfg)
    if scaffold == "S3":
        return run_s3(context, llm_cfg, exec_cfg)
    raise ValueError(f"unknown scaffold condition '{scaffold}'")
