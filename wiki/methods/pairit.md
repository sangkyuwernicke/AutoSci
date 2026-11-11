---
name: Pairit
slug: pairit
type: system
tags:
  - human-AI collaboration
  - experimental platform
  - randomized controlled trial
  - multimodal
source_papers:
  - "[[collaborating-ai-agents-field-experiment-teamwork]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[human-ai-collaboration]]"
date_updated: 2026-05-29
---

## Description

Pairit is a real-time collaborative workspace platform designed for randomized experiments on human-human and human-AI teaming. It enables researchers to assign participants to human-human or human-AI conditions, capture fine-grained interaction data (every keystroke, message, edit, API call), and run AI agents that have the full action repertoire available to human participants.

## Architecture

- **Task panel**: Collaborative ad-creation workspace with synchronized text editing (TipTap), image carousel (stock images), and DALL-E 3 image generation API.
- **Chat panel**: Real-time messaging with typing indicator; messages transmitted via WebSockets (Pusher).
- **AI agent**: OpenAI `gpt-4o-2024-08-06` with full UI context (current ad state, chat history, action log, screenshots of current image). Chain-of-thought prompting via OpenAI structured outputs. Agent is prompted every 10 seconds to decide whether to act.
- **Randomization**: On entry, participants are routed to human-human queue (wait for another participant) or human-AI queue (simulated 1–5 second wait, then paired with agent). Partner identity not revealed until post-task survey.
- **Data capture**: Time-stamped logs of all text edits (character-level), image actions, messages, and API calls. Each session produces a complete reconstruction of the collaboration workflow.

## Use in experiments

- Used by Ju & Aral (2025) to study 2,234 participants producing 11,024 ads, 182,607 messages, and 1,889,559 text edits in a 40-minute collaborative ad-creation task.
- Supports team-level randomization (human-human vs. human-AI) and within-AI randomization (prompt variants, model fine-tuning).
- Platform code and data available upon request; intended to be made freely available to academic researchers.

## Realized concepts

- [[human-ai-collaboration]] — the core phenomenon the platform is designed to study and enable

## Source papers

- [[collaborating-ai-agents-field-experiment-teamwork]]
