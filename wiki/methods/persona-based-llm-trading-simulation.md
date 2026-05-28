---
name: "Persona-Based LLM Trading Simulation"
slug: persona-based-llm-trading-simulation
type: protocol
tags:
  - llm-agents
  - multi-agent-systems
  - financial-ai
  - persona-prompting
  - simulation
source_papers:
  - "[[persona-driven-llm-interaction-stock-market]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[persona-driven-prompting]]"
code_repo: ""
date_updated: 2026-05-29
---

## Problem setting

How to design a multi-LLM agent trading environment where agents maintain distinct, theoretically grounded behavioral profiles and interact under different incentive structures for group decision-making.

## Mechanism

Three LLM instances are each assigned a distinct trading persona (Competitive, Adaptive, Strategic) via system-level prompt injection derived from behavioral finance theory (prospect theory, Big Five personality dimensions). Agents interact with a simulated stock market (Polygon price data + Marketaux news) with discrete buy/sell/wait/check actions. In the collaborative phase, agents first submit independent decisions, then observe peers' decisions over up to 4 rounds, deciding each round to KEEP their choice or SUPPORT a peer's. Two incentive variants are compared: (1) round-based bonus (decaying from 20% to 0% for consensus speed) and (2) influence-based bonus ($10 flat to the agent whose choice is selected).

## Procedure

1. Define three persona prompt templates encoding risk tolerance and decision style.
2. Run alignment tests: 20 hypothetical scenarios per persona varying risk and opportunity levels; record decision boundaries.
3. Deploy agents individually into simulated stock market (6-month period, tech sector NASDAQ, $100k starting balance); run 3 simulation seeds per persona.
4. Run collaborative simulation: per trading day, collect independent decisions → 4-round consensus protocol → random selection of final decision → equal profit sharing. Run under both incentive conditions plus no-persona baseline, 3 seeds each.
5. Compare portfolio valuations across solo, round-bonus, and influence-bonus conditions.

## Assumptions

- Small LLM (3B parameters) is sufficient to exhibit meaningful persona-driven behavioral differences.
- Simulated market with historical price + news adequately proxies real market dynamics for behavioral comparison.
- Equal profit sharing + bonus incentives are sufficient to operationalize consensus and influence motivations.

## Limitations

- Relies on a single small model family (LLaMA 3.2 3B); generalizability to larger models unknown.
- Six-month trading window; long-term dynamics untested.
- Portfolio value only; risk-adjusted returns not measured.

## Tradeoff profile

- Simple to implement (prompt-only persona definition, no fine-tuning)
- Interpretable agent behaviors via behavioral finance grounding
- Limited by model capability ceiling and simulation fidelity

## Evaluated by

- [[persona-driven-llm-interaction-stock-market]]
