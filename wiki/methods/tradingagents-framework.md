---
name: TradingAgents Framework
slug: tradingagents-framework
tags:
  - multi-agent-systems
  - llm-agents
  - financial-trading
  - agentic-debate
  - role-specialization
type: system
source_papers:
  - "[[tradingagents-multi-agents-llm-financial-trading]]"
realizes_concepts:
  - "[[llm-multi-agent-financial-trading]]"
date_added: 2026-05-29
---

## Problem setting

Automated stock trading requires integrating diverse and noisy information sources (price history, financial statements, news, social media, macroeconomic indicators) and balancing risk against return — a task that exceeds the capacity of rule-based systems or single-agent LLMs to handle holistically.

## Mechanism

TradingAgents defines five functional teams that operate sequentially:

1. **Analyst Team** — four concurrent specialist agents independently gather and analyze fundamental data, social/sentiment data, news/macro data, and 60 technical indicators. Each produces a structured analysis report written to global shared state.
2. **Researcher Team** — one bullish and one bearish agent read analyst reports, then engage in $n$ rounds of natural-language debate. A facilitator agent arbitrates and records the consensus perspective as a structured state entry.
3. **Trader Agent** — reads analyst reports and the researcher debate outcome to generate a buy/sell/hold decision with a structured rationale report. Uses deep-thinking LLMs (e.g., o1-preview) for reasoning-intensive decision tasks.
4. **Risk Management Team** — three risk-profile agents (risk-seeking, neutral, risk-conservative) deliberate over the trader's proposed action; a fund manager reviews and finalizes the decision.

**Communication protocol:** All inter-agent information exchange uses structured state documents except during debate phases (researcher and risk-management deliberations), where focused natural-language dialogue is permitted. This hybrid design prevents context degradation over long decision horizons while preserving dialectical reasoning benefits.

**Backbone LLM selection:** Deep-thinking models for analysis and decision; fast models for data retrieval and formatting. All via API — no GPU dependency.

## Procedure

For each trading day:
1. Analyst agents query their respective data sources and write reports to global state.
2. Researcher agents retrieve analyst reports, debate for $n$ rounds, facilitator resolves and updates state.
3. Trader reads state, decides position (buy/sell/hold, size), writes decision + rationale to state.
4. Risk agents review trader decision, deliberate, fund manager approves or adjusts.
5. Approved trade is executed; metrics are computed.

## Assumptions

- Daily bar frequency (one decision per trading day).
- No look-ahead bias: agents access only data available at decision time.
- LLM API access (GPT-4o family + o1-preview or equivalent).
- Sufficient API budget for ≈11 LLM calls and 20+ tool calls per trading day.

## Limitations

- High per-day cost limits feasibility for intraday or HFT scenarios.
- Evaluated on a 3-month bull-market window; generalization untested.
- Relies on closed-source frontier models; behavior with open-source or domain-fine-tuned LLMs is uncharacterized.
- No portfolio-level optimization — each asset is traded independently.

## Tradeoff profile

| Dimension | TradingAgents | Rule-based |
|---|---|---|
| Cumulative return | Very high (23–27% / 3 mo) | Moderate or negative |
| Sharpe ratio | Very high (5.6–8.2) | Low to moderate |
| Maximum drawdown | Low–moderate (< 2.1%) | Low |
| Inference cost | High | Negligible |
| Explainability | High (full reasoning logs) | High (deterministic rules) |

## Evaluated by

- [[tradingagents-multi-agents-llm-financial-trading]]
