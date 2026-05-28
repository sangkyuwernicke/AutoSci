---
title: "LLM-Based Collaboration Analysis"
aliases:
  - LLM-augmented qualitative coding
  - automated IPA coding
tags:
  - collaboration-analysis
  - qualitative-coding
  - llm-evaluation
  - human-ai-collaboration
type: analysis
source_papers:
  - "[[chatcollab-exploring-collaboration-between-humans-ai]]"
realizes_concepts:
  - "[[human-ai-collaborative-teaming]]"
date_updated: 2026-05-29
---

## Summary

An automated pipeline for quantifying collaboration dynamics in multi-agent (human or AI) team interactions by classifying each conversational turn with a large language model according to a chosen social-science coding framework. The paper instantiates this with Bales' Interaction Process Analysis (IPA) 12-category framework and GPT-4 Turbo, achieving 78.1% agreement and 72.9% Cohen's Kappa vs. human coders.

## How it works

1. **Data collection**: Record full chat transcripts from ChatCollab runs (or analogous multi-agent system logs) to markdown files.
2. **Preprocessing**: Parse transcripts into per-turn structured CSV using Python + regex; each row captures speaker, role, timestamp, and message.
3. **Classification**: For each message, prompt an LLM (GPT-4 Turbo) with:
   - The full Bales' IPA framework description (12 categories + "None of the Above")
   - Up to 2 turns of prior context and 2 turns of subsequent context
   - A concise categorization instruction optimized via iterative prompt engineering with human verification
4. **Aggregation**: Sum per-category counts per agent-role and per experimental condition; compute percentage differences from control.

## Key properties

- Framework-agnostic: any qualitative coding framework can substitute Bales' IPA.
- Single-coded per message (one best-fitting category); multi-coding is a future extension.
- Human validation loop was used during prompt development to calibrate IPA label wording.

## When to use

Use when measuring how role definitions or social convention prompts affect observable interaction patterns in AI or mixed human-AI teams. Particularly suited to comparing experimental conditions in controlled multi-agent chat environments.

## Source papers

- [[chatcollab-exploring-collaboration-between-humans-ai]] — introduced and validated this method
