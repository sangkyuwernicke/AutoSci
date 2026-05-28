---
title: "Persona-Driven LLM Interaction in Stock Market Simulations"
slug: persona-driven-llm-interaction-stock-market
arxiv: ""
venue: "ACL Workshop (FinNLP 2025)"
year: 2025
tags:
  - llm-agents
  - multi-agent-systems
  - financial-ai
  - persona-prompting
  - stock-trading
  - behavioral-finance
importance: 2
date_added: 2026-05-29
source_type: pdf
s2_id: ""
tldr: "Assigns Competitive, Adaptive, and Strategic personas to LLaMA 3.2 3B agents trading in a simulated stock market, finding that influence-based incentives for multi-agent consensus outperform round-based consensus and no-persona baselines."
contribution_type:
  - analysis
  - application
datasets: []
code_url: ""
cited_by: []
---

## Problem & Context

LLM-based financial decision-making agents lack well-studied mechanisms for encoding distinct risk tolerances and trading personalities. Prior work (FinBERT, FinLLM surveys) shows LLMs can process financial text, but how behavioral finance archetypes — e.g., loss-averse vs. risk-seeking profiles — translate into controllable agent behavior in dynamic markets is underexplored. Similarly, the interaction dynamics among multiple LLM trading agents under different incentive structures (consensus vs. influence) had not been systematically investigated before this paper.

## Key idea

The paper proposes **persona-driven prompting** for LLM trading agents: three behavioral personas (Competitive, Adaptive, Strategic) derived from behavioral finance archetypes (Kahneman prospect theory, Big Five personality model) are injected as system-level prompts to LLaMA 3.2 3B. The study then introduces a two-incentive multi-agent collaboration protocol — round-based bonuses rewarding early consensus and influence-based bonuses rewarding the agent whose decision is ultimately selected — to study how persona-aligned agents negotiate and adapt under different incentive structures.

## Method

Three LLaMA 3.2 3B instances are assigned distinct personas via prompts:
- **Competitive**: high risk tolerance, impulsive, reacts to short-term momentum
- **Adaptive**: moderate risk tolerance, flexible, context-sensitive
- **Strategic**: low risk tolerance, patient, long-term focused

**Stage 1 (Alignment tests)**: 20 hypothetical scenarios per test varying risk level (Extreme → Low) and opportunity level (High → Low). Measures decision boundary shifts per persona.

**Stage 2 (Individual simulation)**: Agents trade technology-sector NASDAQ stocks over a simulated period using live-ish data from Polygon API (prices) and Marketaux (news). Starting balance $100,000. Actions: BUY, SELL, WAIT, CHECK. 3 simulation runs each.

**Stage 3 (Collaborative simulation)**: Three agents make initial independent decisions, then observe each other's choices for up to 4 rounds. Two incentive conditions:
- *Round-based bonus*: decreasing bonus (20%→15%→10%→0%) for early consensus
- *Influence-based bonus*: flat $10 bonus to the agent whose decision is selected

Final decision is randomly sampled among the consensus choice. Profits shared equally. Baseline: no-persona agents with a generic trading objective.

All experiments run CPU-only on LLaMA 3.2 3B (~200 hours total).

## Experiment & Results

**Persona alignment tests**: All three personas displayed consistent patterns across the 20 risk and 20 opportunity scenarios. Competitive consistently chose the risky option regardless of reliability. Strategic never invested under risk. Adaptive made context-sensitive, nuanced choices (only investing in low-risk, high-opportunity combos).

**Individual simulation**:
- Competitive: 95.1% trade frequency, avg. 0.4 info checks/day, avg. profit $8,869.28 (most volatile)
- Adaptive: 52.7% trade frequency, avg. 1.5 info checks/day, avg. profit $1,263.50
- Strategic: 16.3% trade frequency, avg. 0.8 info checks/day, avg. profit $461.44

**Collaborative simulation**:
- Influence-based bonus group: highest returns, outperforming all solo traders
- Round-based bonus group: lower profits than solo Competitive; early consensus pressure reduced deliberation quality
- No-persona baseline: worst performance in both setups

Key finding: individual incentives (influence bonus) elicit stronger per-agent contributions and better group outcomes than collective-speed incentives (round bonus). Persona framing is necessary for distinct reasoning.

## Limitations

- LLaMA 3.2 3B is a small model; results may not generalize to larger, more capable LLMs.
- Six-month simulated trading window may not capture long-term strategies or full market cycles.
- Only three personas evaluated; broader persona taxonomy could reveal richer dynamics.
- Performance measured solely by portfolio value; risk-adjusted metrics (Sharpe ratio, max drawdown) not reported.
- No real-world validation; results remain in simulated environments.
- Potential overreliance on AI trading without human oversight carries systemic risk.

## Open questions

- Do similar persona-driven incentive structures transfer to larger LLMs (GPT-4, Claude)?
- Can the influence-based bonus protocol be generalized to non-financial multi-agent tasks?
- What is the optimal number and diversity of personas for wisdom-of-the-crowd effects?
- How does the 4-round consensus horizon interact with market volatility?

## My take

A modest but clear contribution: demonstrates that even a tiny 3B LLM can maintain behavioral personas in a financial simulation, and that influence-based incentives outperform consensus-pressure incentives in multi-agent deliberation. The study is preliminary (small model, simple environment), but the incentive protocol design is novel and could inspire follow-up work with stronger models. The connection to behavioral finance theory (Kahneman, Big Five) adds interpretability. Main weakness is that portfolio value is the only success metric — risk-adjusted returns would strengthen conclusions.

## Related

- [[tradingagents-multi-agents-llm-financial]] — builds a more sophisticated multi-role trading firm with structured communication
- [[multi-agent-collaboration]] — foundational concept for the collaborative stage
- [[persona-driven-prompting]] — core concept introduced/operationalized here
