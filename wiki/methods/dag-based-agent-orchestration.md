---
title: "DAG-Based Agent Orchestration"
aliases:
  - DAG planner orchestration
  - FinAgent DAG orchestration
tags:
  - multi-agent-systems
  - orchestration
  - dag
  - financial-ai
type: framework
source_papers:
  - "[[orchestration-framework-financial-agents-algorithmic-trading]]"
realizes_concepts:
  - "[[agentic-trading]]"
---

## Problem setting

Coordinating multiple heterogeneous LLM-based agent pools in a complex workflow (e.g., an algorithmic trading pipeline) where tasks have dependencies, data provenance must be tracked, and operations must be auditable. Naive point-to-point messaging or sequential chaining does not scale to many agents with intricate ordering requirements.

## Mechanism

A **DAG Planner** constructs a directed acyclic graph where:
- **Nodes** are typed invocations of agent pools, each declaring: input schemas and provenance, output artifacts and metrics, side effects, and pre/post-conditions.
- **Edges** encode (a) data flow (artifact dependencies), (b) control flow (rule checks and ordering), and (c) readiness constraints (e.g., Risk checks must complete before Execution).

The **Orchestrator** executes a constraint-aware topological schedule:
1. Validates preconditions for each node before dispatching.
2. Issues commands to agent pools via **Model Context Protocol (MCP)** — small control messages describing task type, declared inputs, policy flags, timeout, and retry budget.
3. Mediates peer communication via **Agent-to-Agent (A2A)** protocol — peer messages (ask, tell, propose, confirm) with role tags and context IDs.
4. Commits all inputs, prompts, tool calls, and outputs to a **Memory Agent** for audit and reuse.

## Procedure

1. Bottom-up specification of tasks and interfaces → DAG construction.
2. Topological sort determines execution order.
3. For each ready node: validate preconditions → dispatch via MCP → monitor via heartbeats → collect results.
4. Within each pool, a manager agent breaks the task into subtasks for subordinate agents; partial results merge before returning upstream.
5. All peer-to-peer exchanges log to Memory Agent with timestamps.
6. After all nodes complete, Orchestrator updates the plan for the next cycle based on memory logs.

## Assumptions

- Agent pool interfaces can be described by a schema (typed inputs/outputs).
- Data flow between pools is artifact-based (references to data stores, not in-line payloads).
- Execution-window returns and realized performance metrics are not exposed to any LLM prompt to prevent leakage.

## Limitations

- DAG is currently static; does not adapt dynamically to market regime shifts.
- MCP and A2A are described at the protocol level; actual standardization depends on the specific implementations used.
- Overhead of orchestration (latency from DAG scheduling, memory writes) may be significant for very high-frequency strategies.

## Tradeoff profile

- **Pro**: Explicit auditability of every decision step; modular swap-out of any agent pool; easy to extend to new asset classes by only changing schedules/rebalancing parameters.
- **Con**: Added complexity vs. simple sequential scripts; performance improvements over naive baselines are modest in short-window experiments; static DAG limits adaptability.

## Evaluated by

- [[orchestration-framework-financial-agents-algorithmic-trading]] — stock trading (7-stock, hourly) and BTC (minute-data) backtests.
