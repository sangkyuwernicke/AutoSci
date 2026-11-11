---
title: "Large Language Model based Multi-Agents: A Survey of Progress and Challenges"
slug: large-language-model-based-multi-agents
arxiv: "2402.01680"
venue: "arXiv"
year: 2024
tags:
  - multi-agent-systems
  - llm-agents
  - survey
  - agent-communication
  - agent-profiling
  - collective-intelligence
importance: 4
date_added: 2026-05-29
source_type: tex
s2_id: ""
tldr: "A comprehensive survey of LLM-based multi-agent systems covering the taxonomy (environment interface, agent profiling, communication, capability acquisition), major application domains (problem-solving and world simulation), open-source frameworks, and key challenges."
contribution_type:
  - survey
datasets:
  - MMLU
  - GSM8K
  - StrategyQA
cited_by: []
---

## Problem & Context

Single LLM-based agents have demonstrated strong planning and reasoning capabilities, but they struggle with complex tasks requiring collaborative specialization. Multi-agent systems based on LLMs (LLM-MA) address this by distributing work across multiple agents with distinct roles, leveraging collective intelligence rather than a single monolithic planner. Before this survey, the rapidly growing body of LLM-MA work (spanning AI, social science, psychology, and policy) lacked a unifying taxonomy and comprehensive overview. Researchers from diverse disciplines were building systems independently without a shared vocabulary or architectural blueprint.

## Key idea

The survey proposes a four-dimensional taxonomy to characterize LLM-MA systems: (1) **Agents-Environment Interface** — how agents perceive and act within sandbox, physical, or environment-free settings; (2) **Agent Profiling** — how agent roles are defined (pre-defined, model-generated, or data-derived); (3) **Agent Communication** — paradigms (cooperative, debate, competitive), structures (layered, decentralized, centralized, shared message pool), and content; and (4) **Agent Capability Acquisition** — how agents learn via feedback from environment, other agents, humans, or through memory, self-evolution, and dynamic generation. Applications are organized into two streams: **problem-solving** (software development, embodied agents, science experiments, science debate) and **world simulation** (societal, game, psychological, economic, policy).

## Method

This is a survey paper. The authors systematically reviewed LLM-MA literature, organized works along the four-dimensional taxonomy, and produced a comprehensive summary table of existing systems. Three major open-source frameworks are analyzed in detail: **MetaGPT** (SOP-embedded workflow), **CAMEL** (inception prompting for autonomous cooperation), and **AutoGen** (customizable natural-language and code-driven agent orchestration). Datasets and benchmarks for both problem-solving and world simulation tasks are catalogued.

## Experiment & Results

As a survey, there are no original experimental results. The paper counts research papers across problem-solving and world simulation categories at 3-month intervals to document rapid growth in the field. Key quantitative observations: debate-based multi-agent approaches (e.g., Du et al.) improve factuality on reasoning tasks; MetaGPT's SOP-driven layered communication reduces hallucination vs. unstructured multi-agent debate. The survey includes a comprehensive taxonomy table covering ~30+ systems across environments, profiling methods, communication structures, feedback types, and agent adjustment strategies.

## Limitations

- Coverage is a snapshot; the field moves faster than any static survey can track (mitigated by open-source GitHub repository).
- No quantitative meta-analysis comparing systems across a shared benchmark.
- Ethics and risk section is minimal (only one line in the source).
- Evaluation benchmarks are incomplete: science-team experiments, economic modeling, and disease propagation simulation lack standardized benchmarks.
- Most existing systems operate in text-only environments; multi-modal settings remain underexplored.

## Open questions

- How do hallucinations cascade in interconnected multi-agent networks, and how can they be detected/mitigated system-wide?
- What are the scaling laws governing LLM-MA performance as the number of agents grows?
- How can collective intelligence emerge beyond simple memory and self-evolution — via coordinated multi-agent training?
- What agent orchestration strategies best balance communication cost with task performance?
- How should comprehensive benchmarks for world simulation (economic, epidemiological) be designed?

## My take

This survey arrived at a pivotal moment when LLM-MA research was fragmenting across disciplines. The four-dimensional taxonomy is pedagogically clean and provides a useful vocabulary. The distinction between problem-solving vs. world simulation as application streams is particularly clarifying. The survey's main weakness is that it is primarily descriptive — it stops short of proposing design principles or quantitative evaluations that would make the taxonomy actionable. Still, as a community-organizing reference it is high-value, especially given the open-source repository that keeps it alive post-publication.

## Related

- [[towards-effective-genai-multi-agent-collaboration-design-and-evaluation-for-enterprise-applications]] — practical enterprise-focused multi-agent design evaluation
- [[tradingagents-multi-agents-llm-financial-trading-framework]] — domain-specific LLM-MA application in finance
