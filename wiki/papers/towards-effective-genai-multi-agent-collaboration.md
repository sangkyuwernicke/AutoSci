---
title: "Towards Effective GenAI Multi-Agent Collaboration: Design and Evaluation for Enterprise Applications"
slug: towards-effective-genai-multi-agent-collaboration
arxiv: "2412.05449"
venue: NeurIPS 2024 Workshop
year: 2024
tags:
  - multi-agent-systems
  - llm-agents
  - enterprise-ai
  - benchmarking
  - agent-coordination
importance: 3
date_added: 2026-05-28
source_type: tex
tldr: Proposes a hierarchical multi-agent collaboration (MAC) framework for enterprise applications with inter-agent communication, payload referencing, and dynamic routing, achieving 90% goal success rates and validated via assertion-based benchmarking across three domains.
contribution_type:
  - system
  - benchmark
  - analysis
datasets:
  - MAC-Enterprise-Benchmark
code_url: "https://github.com/aws-samples/multiagent-collab-scenario-benchmark"
cited_by: []
---

## Problem & Context

Real-world enterprise tasks are often too complex for a single LLM agent to handle reliably. While multi-agent systems (MAS) research dates to the 1980s–1990s, the GenAI era has renewed interest in how LLM-powered agents can collaborate. Prior work (ChatDev, MetaGPT, CAMEL, AutoGen) focuses on general-purpose multi-agent coordination, but enterprise applications impose additional requirements: latency sensitivity, tool-call correctness, reliability, and the need for fast, scalable evaluation during development. Existing benchmarks designed for single agents rely on static gold-truth trajectories, which penalize equivalent-but-different valid solutions—a gap that grows worse with multiple agents.

## Key idea

The paper introduces a MAC (Multi-Agent Collaboration) framework built around a centralized hierarchical agent topology: a supervisor agent delegates to specialist agents via a unified `send_message` tool, supporting parallel communication. Two key optimizations reduce overhead: (1) **payload referencing**, which tags large static content blocks (especially code) with identifiers so the supervisor can reference rather than re-generate them; and (2) **dynamic agent routing**, a fast classifier (≥90% accuracy, ~350 ms) that bypasses full supervisor orchestration when a request is simple enough to route directly to a specialist agent. For evaluation, the paper introduces **assertion-based benchmarking**: handcrafted scenarios with user-side and system-side assertions judged by an LLM, avoiding dependence on single-trajectory gold labels.

## Method

The MAC framework models inter-agent communication as a tool call (`send_message` with `recipient` and `content` parameters), allowing the supervisor agent to leverage the LLM's native function-calling capability. Incoming specialist messages are wrapped in XML-style tags (`<message from="$AGENT">`). Parallel communication is enabled by dispatching `send_message` calls concurrently. Payload referencing works by tagging detected structured content (e.g., code blocks) with unique IDs on the way in to the supervisor, then expanding reference tags on the way out to specialist agents—reducing output tokens by ~30% in code-heavy tasks. Dynamic routing uses a fast LLM-based classifier (Claude 3.0 Haiku) or a rule-based Lex classifier to decide per-turn whether to engage the supervisor at all; routing overhead is 600–800 ms end-to-end vs. full orchestration.

For evaluation, three enterprise domains are used (Travel, Mortgage, Software Development) with 30 scenarios each (90 total). Each scenario provides a description, an initial problem statement, and a list of assertions. A user simulator (LLM grounded on the scenario) drives the conversation; an action simulator handles tool calls. An LLM judge (GPT-4o) then evaluates each assertion and computes Goal Success Rate (GSR) at the user-side, system-side, and overall levels.

## Experiment & Results

**Coordination mode** (Claude 3.5 Sonnet 20241022 for all agents): overall GSR = 90% across all three domains. Single-agent baseline shows up to 37% absolute GSR regression in Software (0.53 vs. 0.90), confirming that specialization matters. Using Claude 3.0 Sonnet as specialists causes a significant drop in Software (0.77) but not in Travel/Mortgage, while Haiku 3.5 recovers Software performance (0.87).

**Payload referencing** ablation (Software domain): enabling payload referencing improves overall GSR from 0.73 → 0.90 (+23% relative) and reduces average communication overhead from 48.78 s → 35.44 s per turn (−27% relative), driven by a 30% reduction in supervisor output tokens (539 → 374 avg tokens/communication).

**Routing mode** (Claude 3.0 Haiku classifier): classification accuracy 90–92%, false switch rate ≤3%, classification latency ~344–378 ms, turn-level routing overhead 627–751 ms end-to-end. End-to-end GSR with routing: Travel 0.85, Mortgage 0.95 with Supervisor GSR = 1.00 in both, indicating routing correctly escalates when needed.

**Comparison with open-source framework (OSF)**: MAC coordination mode vs. an OSF (ReAct-style prompting, extended for multi-turn): MAC achieves 87–90% GSR vs. OSF 40–63% (Claude) / 33–43% (GPT-4o mini), highlighting the advantage of native function-calling over ReAct prompting in enterprise settings.

## Limitations

- Dataset of 90 scenarios (30/domain) is hand-crafted and relatively small; automated curation would enable faster iteration.
- Software Development domain shows high latency (avg user-perceived turn latency 168 s), suggesting further optimization of the orchestration is needed for real-time use.
- The coordination mode is synchronous; asynchronous communication is listed as future work.
- Payload referencing is currently limited to code blocks; extending to other large static payloads (e.g., documents, images) is future work.
- The study relies on Claude models; generalization to other LLM families is not validated.

## Open questions

- How does MAC performance scale as agent team size grows beyond 2–3 layers?
- Can the assertion-based benchmarking framework be automatically curated (rather than hand-crafted)?
- What is the optimal routing policy when requests span multiple specialist agents?
- How does MAC behave under adversarial or ambiguous user inputs?

## My take

A solid engineering report from AWS Bedrock that addresses a real enterprise gap: how to get LLM multi-agent systems to work reliably enough for deployment. The assertion-based benchmarking methodology is the most broadly reusable contribution—it sidesteps the gold-trajectory problem and scales naturally to multi-agent settings. The payload referencing trick is clever but domain-specific (primarily code). The paper's honest treatment of latency tradeoffs and the honest comparison with an OSF strengthen its credibility. Importance is limited by scope (AWS-specific framework, relatively small benchmark) but the open-sourced dataset and evaluation code add lasting value.

## Related

- [[multi-agent-collaboration]] — core concept introduced/operationalized
- [[assertion-based-benchmarking]] — evaluation method introduced
- [[dynamic-agent-routing]] — optimization method introduced
