---
title: "Autonomous Agents for Collaborative Task under Information Asymmetry"
slug: autonomous-agents-collaborative-task-under-information
arxiv: "2406.14928"
venue: "NeurIPS 2024"
year: 2024
tags:
  - multi-agent-systems
  - information-asymmetry
  - llm-agents
  - social-networks
  - benchmark
importance: 4
date_added: 2026-05-29
source_type: tex
tldr: "iAgents mirrors human social networks in agent networks to resolve information asymmetry in collaborative tasks via InfoNav reasoning and mixed memory, evaluated on the new InformativeBench benchmark."
contribution_type:
  - system
  - benchmark
  - method
datasets:
  - InformativeBench
  - FriendsTV
  - NP
  - Schedule
code_url: "https://github.com/thinkwee/iAgents"
cited_by: []
---

## Problem & Context

Multi-agent systems (MAS) driven by LLMs have achieved strong performance on tasks where all agents share the same information pool. However, real-world multi-person collaboration operates under *information asymmetry*: each person—and thus each agent acting on their behalf—can access only their own private data. Previous LLM-MAS designs (e.g., ChatDev, MetaGPT, AgentVerse) assume a shared context within a virtual entity (company, hospital) and break down when each agent holds disjoint private information. Collecting all private data into one place is both a privacy violation and impractical for dynamic human information.

The research question is therefore: how can a network of agents, each bound to its human user's private context, collaboratively resolve tasks that require aggregating information from multiple users?

## Key idea

iAgents (Informative Multi-Agent Systems) maps the human social network directly into an agent network. Rather than forming a single virtual entity with shared context, each human user is assigned a personal agent that holds only that user's private information. When a task requires information from multiple humans, agents proactively exchange the relevant pieces of information—subject to privacy constraints—using two mechanisms:

1. **InfoNav** — a plan-and-track reasoning mechanism that makes the agent's information needs explicit. Before each communication turn the agent states what rationales are still *unknown* and updates the plan as new facts arrive. A final "consensus check" reconciles partial plans from both sides.
2. **Mixed Memory** — human information is stored in two complementary stores: *Clear Memory* (structured, SQL-style exact retrieval) and *Fuzzy Memory* (embedding-based ANN retrieval over session summaries). Agents reactively adjust their queries to each store.

Recursive communication lets Bob's agent spawn a sub-dialogue with Charlie's agent while conversing with Alice's agent, enabling information to diffuse across the social network.

## Method

**Problem formulation.** Given a question Q whose required rationales R are distributed across users' private information (I1, I2), two agents (A1, A2) must communicate (C) to build R = R1 ∪ R2 and answer Q.

**InfoNav pipeline:**
- *Initialise plan*: prompt the agent to enumerate all unknown rationales needed to answer Q.
- *Fill plan during communication*: each received utterance updates rationale status from unknown → known and inserts the retrieved value as a filled placeholder.
- *Consensus reasoning*: after communication ends, both agents cross-check their completed plans, discard conflicting rationales, and jointly infer the answer.

**Mixed Memory:**
- Clear Memory (MemC): stores original chat messages in a structured database; supports SQL keyword queries spanning multiple sessions.
- Fuzzy Memory (MemF): stores GPT-4-generated session summaries; retrieves via OpenAI text-embedding-3-small + approximate nearest-neighbour (FAISS).
- Retrieval action: `Act(query) = SQL(MemC) + ANN(MemF)`. Agents adjust query parameters (context window, topk) reactively based on communication progress.

**Recursive communication:** agents can open new sub-communication threads within their social subnetwork at any point, allowing multi-hop information diffusion.

**Implements:** [[infonav]], [[informative-multi-agent-system]] (iAgents framework).

## Experiment & Results

**Benchmark — InformativeBench** (5 datasets, 2 task categories):
- *Needle-Oriented*: find a piece of information distributed across two agents' private stores.
  - NP (Needle in Persona): modified SPC dialogues; agents find a shared/opposite persona.
  - FriendsTV: reconstructed Friends Season 1 social network (140 characters, 588 relationships, ~70 k messages); two combined FriendsQA questions as needles.
- *Reasoning-Oriented (Schedule)*: distributed schedule data; agents solve algorithmic problems (Easy/Medium/Hard) over it.

**Main results (Table 1, iAgents full model):**

| LLM | Schedule Easy | Schedule Medium | Schedule Hard | NP | FriendsTV |
|---|---|---|---|---|---|
| GPT-4 | 56.67% | 51.00% | 22.80% | 64.00% | 57.94% |
| GPT-3.5 | 36.67% | 18.00% | 12.25% | 51.00% | 35.71% |
| Claude Sonnet | 43.33% | 17.44% | 18.66% | 50.00% | 34.13% |
| Gemini 1.0 | 26.67% | 22.33% | 14.40% | 40.00% | 28.57% |

Average across all tasks: ~50.48% with GPT-4. Hardest task (Schedule Hard): only 22.8%.

**Ablation (Table 2, GPT-3.5 base):**
- Removing InfoNav: NP drops from 51% → 39%, Schedule Easy 36.67% → 10%.
- Removing Recursive Communication (FriendsTV): 35.71% → 23.02% (−12.7%).
- Removing Fuzzy Memory (FriendsTV): 35.71% → 29.37%.
- Removing Clear Memory (FriendsTV): 35.71% → 33.33%.

InfoNav is most critical for reasoning tasks; recursive communication is most critical for large social networks; mixed memory provides compounding gains.

**Real-world analysis:** Anonymizing character names drops FriendsTV by ~3.2 pp (prior knowledge helps but is not decisive); adding privacy-preserving utterance constraints costs ~4.8 pp (tension between collaboration and privacy).

## Limitations

- **Privacy trade-off**: full collaboration requires sharing user information; privacy-preserving utterances reduce performance. Access-control at the input level remains unsolved.
- **Network modeling**: agent communication is triggered by task-relevance only; nuanced social network topology (history, trust) is not modeled.
- **Human-agent interaction**: real deployments need human-in-the-loop verification steps; the framework currently targets full autonomy.
- **Cost**: ~30,000 input tokens per task; high cost for large social networks.
- **LLM capability ceiling**: even with GPT-4, the hardest reasoning task achieves only 22.8%.

## Open questions

- Can lightweight edge-deployed models handle privacy-sensitive information in L3 privacy mode without compromising task performance?
- How should agents model trust, social norms, and communication history within the social network topology?
- What human-AI interaction paradigms allow users to control agent communication without micro-managing every exchange?
- Can model-unlearning techniques reduce prior-knowledge distraction in benchmarks using publicly known content (e.g., Friends)?

## My take

iAgents reframes the role of LLM agents from intra-system collaborators to inter-personal proxies, which is a conceptually clean and practically important shift. The InfoNav mechanism is the most novel contribution — making the information-need state explicit in natural-language plans is an elegant generalization of dialogue state tracking. The mixed memory design is pragmatic and well-ablated. InformativeBench fills a real evaluation gap. The main limitation is that the privacy and scalability analysis is still surface-level; the framework is a proof of concept rather than a deployable system. NeurIPS 2024.

## Related

- [[informative-multi-agent-system]] — the iAgents paradigm introduced by this paper
- [[infonav]] — the InfoNav reasoning mechanism introduced here
- [[information-asymmetry-multi-agent-systems]] — the central concept addressed
