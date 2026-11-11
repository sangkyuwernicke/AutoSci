---
title: "Orchestration Framework for Financial Agents: From Algorithmic Trading to Agentic Trading"
slug: orchestration-framework-financial-agents-algorithmic-trading
arxiv: "2512.02227"
venue: "NeurIPS 2023 (workshop)"
year: 2024
tags:
  - multi-agent-systems
  - financial-ai
  - algorithmic-trading
  - llm-agents
  - agent-orchestration
importance: 3
date_added: 2026-05-29
source_type: tex
tldr: "Proposes FinAgent Orchestration, a multi-agent framework that maps every component of a traditional algorithmic trading pipeline to dedicated agent pools coordinated via DAG planning, MCP control messages, and A2A peer communication."
contribution_type:
  - system
  - application
datasets: []
code_url: "https://github.com/Open-Finance-Lab/AgenticTrading"
cited_by: []
---

## Problem & Context

Traditional algorithmic trading (AT) systems follow a rigid pipeline — data ingestion, signal generation, portfolio construction, execution, and evaluation — typically stitched together by files and scripts, with manual handoffs between research and production. Building and maintaining such a system requires a professional team over years. The field lacked a principled, auditable architecture that unifies the research and operations phases under a single, agent-native control surface.

Concurrent work (FinRL-Meta, FinCon, FinMem, TradingAgents, RDAgents) demonstrated that LLM-based agents can handle individual stages such as signal generation, memory, and dialogue, but no unified orchestration framework existed that treated the entire AT pipeline — from data to execution — as a coordinated multi-agent system.

## Key idea

The key idea is to **replace every component of the classic AT pipeline with a corresponding agent pool**, and coordinate them using:
1. A **DAG Planner + Orchestrator** that encodes task ordering and data dependencies as a directed acyclic graph.
2. **Model Context Protocol (MCP)** for top-down vertical control messages (orchestrator → agent pools).
3. **Agent-to-Agent (A2A)** protocol for horizontal peer communication among agent pools.
4. A **Memory Agent** that persists states, prompts, tool calls, and decisions across cycles for auditability and reuse.

This "FinAgent Orchestration" framework aims to democratize financial intelligence: once instantiated, the same pipeline runs on both equities and BTC by changing only schedules and rebalancing rules.

## Method

**Agent pool mapping**: Each AT function maps to a dedicated pool — Data Agents, Alpha Agents, Risk Agents, Portfolio Agents, Backtest/Evaluation Agents, Execution Agents, Audit Agents, and a Memory Agent. Within each pool, a manager agent breaks tasks into subtasks delegated to subordinate agents.

**DAG-based control**: The Orchestrator constructs a typed DAG. Nodes are typed invocations of agent pools declaring inputs (with schemas and provenance), outputs (artifacts and metrics), side effects, and pre/post-conditions. Edges encode data flow, control flow, and readiness constraints.

**Dual-protocol communication**: MCP exposes each agent pool as a tool-like endpoint with a unified request-response schema; A2A carries peer messages (ask, tell, propose, confirm) with role tags and context IDs among pools and with the Memory Agent.

**Leakage prevention**: All numerical signal construction, backtesting, and return mapping are handled by tool-based modules, not LLMs. Evaluation-window data and realized returns are never exposed to any LLM prompt.

**LLM backends**: Different agents use different LLM backends (GPT-4o, Llama3, FinGPT), with domain-specific prompts.

## Experiment & Results

Two homegrown backtesting experiments share the same pipeline; only data sources, schedules, and rebalancing rules differ.

**Stock trading (7-stock universe: AAPL, MSFT, GOOGL, JPM, TSLA, NVDA, META)**
- Period: 09/2022–12/2024 (hourly data); out-of-sample test window 04/2024–12/2024
- Results: Total return 20.42%, annualized volatility 11.83%, Sharpe 2.63, max drawdown −3.59%
- vs. S&P 500 (SPY): 16.60% return, Sharpe 1.86; vs. equal-weighted benchmark: 47.46% return, Sharpe 3.37
- The agentic strategy achieves lower volatility and smallest max drawdown among all comparators, consistent with DAG gating enforcing risk and portfolio checks before execution.

**BTC/USDT trading (minute data)**
- Period: 05/2025–08/2025; 17-day out-of-sample window 07/27–08/13/2025
- Results: Total return 8.39%, Sharpe 0.378, max drawdown −2.80%, volatility 24.23%
- vs. Buy-and-Hold: 3.80% return, Sharpe 0.170, max drawdown −5.26%
- XGBoost predictor trained on 100+ microstructure features with rolling walk-forward; 17 trades total (~1.04/day), average holding time 16.07 hours, win rate 64.7%.

Both experiments show that risk-controlled, orchestrated execution trades off some upside for tighter risk profiles.

## Limitations

- **Small scale**: Only 7 stocks + BTC; results from a single instantiation over short windows should not be generalized.
- **No adaptive planning**: The DAG is static; the planner does not currently respond to regime shifts.
- **Equal-weight outperforms**: The equally-weighted benchmark beats the agentic strategy on total return (47.46% vs. 20.42%), suggesting the risk-control gating may be overly conservative.
- **BTC window is very short**: 17 days is too short to draw statistically reliable conclusions.
- **No ablation**: The contribution of each agent pool component is not isolated; no ablation study on gating, memory, or messaging is provided.
- **LLM leakage risks**: While the authors claim to prevent evaluation-window leakage, the LLM-guided signal design process is not fully mechanistically verified.

## Open questions

- How does the framework perform over longer horizons and across more asset classes?
- What is the marginal contribution of each agent pool? Can ablations isolate memory vs. orchestration vs. risk gating?
- How should the DAG adapt dynamically to regime changes?
- Can A2A communication protocols be standardized for interoperability with third-party agent frameworks?

## My take

This is a proof-of-concept systems paper that makes a compelling architectural argument: treating the AT pipeline as a DAG of coordinated agent pools with explicit protocols (MCP + A2A) is a natural next step from script-based pipelines. The dual-protocol design and memory auditability are thoughtful. However, the empirical results are weak — the framework does not beat a naive equal-weighted benchmark on return, the evaluation windows are very short, and there are no ablations. The value is in the reference architecture rather than demonstrated performance gains.

## Related

- [[trading-agents-multi-agents-llm-financial]] — TradingAgents: a related multi-agent LLM trading framework
- [[fincon]] — hierarchical agent collaboration with verbal reinforcement for trading decisions
- [[finmem]] — layered memory and role profiles for financial agents
