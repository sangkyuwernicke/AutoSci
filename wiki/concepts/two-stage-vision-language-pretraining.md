---
title: Two-Stage Vision-Language Pretraining
aliases:
  - two-stage multimodal training
  - coarse-to-fine multimodal alignment
tags:
  - vision-language
  - training
  - alignment
  - instruction-tuning
maturity: active
definition: A training paradigm for multimodal models that separates (1) large-scale noisy pretraining for cross-modal knowledge acquisition from (2) small-scale curated fine-tuning to restore natural language generation quality and instruction-following behavior.
key_papers:
  - "[[minigpt-enhancing-vision-language-understanding-advanced]]"
first_introduced: "2023 (MiniGPT-4)"
date_updated: 2026-05-29
related_concepts:
  - "[[vision-language-alignment]]"
  - "[[multimodal-large-language-model]]"
---

## Definition

Two-stage vision-language pretraining addresses a fundamental tension: large-scale image-caption datasets provide broad visual knowledge but contain noisy, short, or stylistically inconsistent text that degrades the LLM's language generation quality when used for alignment fine-tuning. The solution is to separate training into:

1. **Stage 1 (Pretraining)**: Train on millions of image-text pairs to establish cross-modal feature alignment. The model learns to associate visual concepts with language, but may produce fragmented or repetitive outputs.
2. **Stage 2 (Curated fine-tuning)**: Fine-tune on a small, high-quality dataset (hundreds to thousands of pairs) using a conversational template. Restores language generation naturalness and enables instruction-following.

## Key properties

- Stage 2 requires orders of magnitude less compute than stage 1 (7 min vs. 10 h in MiniGPT-4).
- Stage 2 data quality matters more than quantity; manual curation and LLM-assisted cleaning are important.
- The split preserves the benefits of large-scale pretraining while avoiding language degradation.

## Relation to NLP precedent

Analogous to GPT-3 → InstructGPT/ChatGPT: pretraining acquires broad capabilities; RLHF/instruction fine-tuning aligns output style and instruction-following. MiniGPT-4 adapts this pattern to the multimodal domain without RLHF, relying on data curation instead.

## Key papers

- [[minigpt-enhancing-vision-language-understanding-advanced]] — introduced and demonstrated this two-stage recipe for vision-language alignment

## Realized by

- [[minigpt-projection-alignment]]
