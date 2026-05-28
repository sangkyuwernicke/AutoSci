---
title: "Agentic Trading"
aliases:
  - agentic trading system
  - FinAgent orchestration
tags:
  - financial-ai
  - multi-agent-systems
  - algorithmic-trading
  - llm-agents
maturity: emerging
definition: "A paradigm that replaces components of traditional algorithmic trading pipelines with coordinated LLM-based agent pools, organized via DAG planning and explicit inter-agent communication protocols, to achieve modularity, observability, and auditability in automated trading."
key_papers:
  - "[[orchestration-framework-financial-agents-algorithmic-trading]]"
first_introduced: "2024"
date_updated: 2026-05-29
related_concepts: []
linked_ideas: []
---

## Definition

Agentic trading is an evolution of algorithmic trading (AT) in which each functional stage of the AT pipeline — data ingestion, alpha signal generation, risk management, portfolio construction, execution, backtesting, and attribution — is implemented as a dedicated agent (or agent pool) powered by large language models, rather than as hardcoded scripts or model-only pipelines. These agents are coordinated by an orchestrator following a directed acyclic graph (DAG) plan, communicate via standardized protocols (e.g., MCP for vertical control, A2A for peer messaging), and share state through a persistent memory agent.

## Intuition

Traditional AT systems are hard to modify, hard to audit, and require large engineering teams because their components are tightly coupled through file-based interfaces and manual handoffs. Agentic trading raises the abstraction level: each agent pool is a reusable, tool-augmented module with a declared interface, and the orchestrator provides a visible plan of what runs when and in what order. This makes the system more transparent, more modular, and more amenable to iterative refinement.

## Variants

- **Single-agent trading**: One LLM agent that handles multiple roles without explicit orchestration (simpler but less modular).
- **Multi-agent trading with flat topology**: Multiple agents with no explicit DAG; relies on ad-hoc messaging (e.g., TradingAgents).
- **Orchestrated agentic trading**: Full DAG-based orchestration with dual-protocol communication (MCP + A2A), as in FinAgent Orchestration.

## Comparison

Compared to pure algorithmic trading, agentic trading adds language-model reasoning for signal design, memory-backed context persistence, and explicit auditability. Compared to standard multi-agent systems, agentic trading applies the multi-agent pattern specifically to the AT pipeline with domain-specific gating (risk constraints, drawdown limits) and leakage prevention.

## Known limitations

- Empirical evidence of outperforming classical AT is limited so far; existing benchmarks show risk-control improvement but not return improvement vs. naive baselines.
- LLM-based alpha design is hard to verify for absence of test-window data leakage.
- Evaluation windows in published work are very short.

## Open problems

- How to design adaptive DAG plans that respond to market regime shifts.
- Standardization of A2A message schemas across different agent frameworks.
- Rigorous empirical comparison against classical AT over long horizons and diverse market conditions.

## Relationship to foundations

Draws on multi-agent reinforcement learning foundations, DAG scheduling theory, and LLM tool-use frameworks.

## Realized by

- [[dag-based-agent-orchestration]]

## My understanding

Agentic trading is an exciting architectural direction but is still in proof-of-concept stage as of 2024. The modularity and auditability benefits are real, but the performance advantages over classical baselines remain to be demonstrated.
