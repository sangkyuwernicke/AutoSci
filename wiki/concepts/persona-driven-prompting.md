---
title: "Persona-Driven Prompting"
aliases:
  - persona prompting
  - persona-based prompting
  - trading persona injection
tags:
  - llm-agents
  - prompt-engineering
  - behavioral-ai
  - multi-agent-systems
maturity: emerging
definition: "A prompting technique that assigns distinct behavioral identities — defined by personality traits, risk tolerances, and decision styles — to LLM agents via system-level prompts, in order to elicit consistent, differentiated behaviors across tasks."
key_papers:
  - "[[persona-driven-llm-interaction-stock-market]]"
  - "[[tradinggpt-multi-agent-system-layered-memory]]"
first_introduced: "2023"
date_updated: 2026-05-29
related_concepts: []
linked_ideas: []
---

## Overview

Persona-driven prompting instantiates LLM agents with explicit behavioral profiles (e.g., Competitive/Adaptive/Strategic) derived from psychology or domain theory. Unlike generic role prompting, it anchors the persona in a specific theoretical framework (behavioral finance, Big Five personality model) to produce interpretable and consistent agent behaviors across varied scenarios.

## Key papers

- [[persona-driven-llm-interaction-stock-market]] — introduces the Competitive/Adaptive/Strategic trading persona framework and demonstrates persona consistency in both alignment tests and live simulations
- [[tradinggpt-multi-agent-system-layered-memory]] — earlier, coarser use: assigns agents discrete risk-preference characters (risk-seeking/neutral/averse) plus an industry subscope to diversify a multi-agent trading system's decisions

## Realized by

- [[persona-based-llm-trading-simulation]]
