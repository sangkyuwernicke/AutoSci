---
title: "Generative AI Agents for Knowledge Work Augmentation in Finance"
slug: generative-ai-agents-knowledge-work-augmentation
arxiv: ""
venue: "Annual Review of Control, Robotics, and Autonomous Systems"
year: 2025
tags:
  - generative-ai
  - llm-agents
  - finance
  - multi-agent-systems
  - planning
  - human-ai-collaboration
  - knowledge-work
  - autonomy
importance: 3
date_added: 2026-05-29
source_type: pdf
s2_id: ""
tldr: "A survey and framework paper connecting generative AI agent architectures to the specific challenges of knowledge work augmentation in finance, proposing a levels-of-autonomy taxonomy and human–AI collaboration architecture."
contribution_type:
  - survey
  - application
  - system
datasets: []
cited_by: []
---

## Problem & Context

Finance is primarily knowledge work—skilled humans cognitively process heterogeneous information (documents, databases, emails, market data) to deliver products and services. Automating or augmenting this work is uniquely challenging due to: (a) high operational complexity spanning diverse products, clients, and geographies; (b) risk-sensitive tasks where failures carry high costs; (c) strict regulatory constraints; (d) rich implicit domain knowledge acquired through experience; and (e) dynamic environments where market conditions and regulations change rapidly.

Prior to the generative AI era, software agents lacked the ability to handle the natural language and multimodal inputs that dominate knowledge work. Traditional AI planning (PDDL-based) required labor-intensive domain model engineering and could not bridge the gap between human language and formal specifications. LLM-based reasoning (chain-of-thought, ReAct) improved language understanding but sacrificed formal guarantees. No prior work had systematically connected the architecture of generative AI agents to the operational realities of financial knowledge work.

## Key idea

The paper argues that generative AI agents—agents that leverage LLMs and other foundation models alongside classical AI methods (planning, search, learning)—are now tractable for augmenting finance knowledge work. The key insight is that a **hybrid approach** combining LLMs with classical AI planning (PDDL-based) provides the best of both worlds: the language understanding and knowledge of LLMs with the formal guarantees (validity, optimality, constraint satisfaction) of symbolic AI planners. The paper also introduces a three-dimensional **levels of autonomy** framework (flexibility, proactivity, supervision) and a **human–AI architecture** that allows controlled, progressive increase of agent autonomy in risk-sensitive domains.

## Method

The paper is a survey and framework contribution; there is no single empirical method. It organizes the agent framework around five pillars:

1. **Reasoning and Planning**: Categorizes approaches as open-loop vs. closed-loop and implicit vs. explicit world model. Advocates for hybrid LLM + PDDL planners to get correctness guarantees needed for regulated finance tasks.

2. **Execution Monitoring and Self-Correction**: Describes the three-step self-correction loop (evaluate → reflect → correct). Notes that intrinsic self-correction (without external feedback) degrades performance; external feedback (e.g., unit tests, human review) enables reliable correction. Recommends framing deployment as continual learning from human feedback rather than a leap to fully autonomous agents.

3. **Learning**: Three paradigms—learning from instruction/demonstration (in-context learning), learning from observation (skill discovery from logs), and learning from experience (self-directed curriculum, skill retention for reuse).

4. **Tool Use**: Tool-calling capabilities enable agents to overcome LLM parametric knowledge limitations by connecting to live financial databases, APIs, and software systems for both information retrieval and execution.

5. **Multiagent Communication and Coordination**: Surveys role assignment (fixed vs. dynamic), communication topology (chain, hierarchy, publish–subscribe, fully connected), and mixed settings involving agents from different organizations with potentially conflicting objectives. Structured prompts, structured outputs, and predefined communication patterns outperform naive free-form LLM debate.

**Levels of Autonomy Framework**: A five-level taxonomy along three dimensions—(1) *flexibility* (handling underspecified tasks), (2) *proactivity* (goal identification), and (3) *supervision* (degree of human oversight/confirmation required). The supervision dimension is the primary scale for practical deployment decisions in finance.

## Experiment & Results

This is a survey/framework paper with no new empirical experiments. The authors review and synthesize results from referenced works:
- Chain-of-thought self-consistency improves over single-chain reasoning (cited work: ~3–10% improvement on standard benchmarks).
- LLMs alone fail on planning tasks with constraints, time, or cost reasoning (cited evaluation on planning benchmarks).
- Hybrid LLM + PDDL planners (e.g., LLM-based PDDL generation followed by classical planning) improve both performance and provide formal guarantees.
- Multiagent systems with structured communication (MetaGPT, MAC-SQL, etc.) outperform single-agent baselines on code generation and data querying tasks.
- Self-correction without external feedback often degrades performance; code self-debugging with external feedback (unit tests) succeeds.

## Limitations

- The paper is primarily conceptual/survey; no empirical evaluation of the proposed frameworks on real financial tasks.
- The levels-of-autonomy framework is descriptive rather than operational—no concrete metrics or thresholds for moving between levels.
- The hybrid LLM+PDDL approach requires domain model creation, which remains an open challenge (the paper acknowledges this as a research direction).
- The mixed multiagent setting (cross-organizational agents with competing goals) is identified as largely unexplored territory.
- No treatment of model security, adversarial robustness, or data privacy constraints that are particularly critical in finance.

## Open questions

- How do we automatically generate and validate correct PDDL domain models from natural language financial regulations and SOPs?
- What continual learning mechanisms allow agents to update behavior from human feedback in long-term memory without catastrophic forgetting?
- How can multiagent systems be designed for mixed settings where agents represent different organizations with conflicting objectives and need to negotiate?
- What monitoring and evaluation modules best detect agent failures in risk-sensitive financial workflows?
- How should agents be progressively granted more autonomy (moving up the supervision levels) based on demonstrated reliability?

## My take

A well-structured survey that successfully bridges the generative AI agents literature and the specific operational constraints of financial knowledge work. The levels-of-autonomy framework is a useful practical contribution for practitioners thinking about deployment. The advocacy for hybrid LLM+planning over pure LLM reasoning is well-motivated for regulated domains. The paper's main limitation is that it remains largely conceptual—the research directions it identifies (especially PDDL generation, continual learning from human feedback, and mixed multiagent negotiation) are genuinely hard open problems. Best read as an informed roadmap from practitioners at JPMorgan AI Research rather than as empirical science.

## Related

- [[agent-autonomy-levels]]
- [[llm-ai-planning-hybrid]]
