---
title: Vision-Language Alignment
aliases:
  - visual feature alignment
  - multimodal alignment
  - cross-modal alignment
tags:
  - vision-language
  - multimodal
  - alignment
maturity: active
definition: The process of mapping visual representations into the semantic space of a language model so that the LLM can condition its generation on visual input without requiring task-specific architectural changes.
key_papers:
  - "[[minigpt-enhancing-vision-language-understanding-advanced]]"
first_introduced: "2021 (Frozen / Tsimpoukelli et al.)"
date_updated: 2026-05-29
related_concepts:
  - "[[multimodal-large-language-model]]"
  - "[[two-stage-vision-language-pretraining]]"
---

## Definition

Vision-language alignment refers to learning a mapping between a pretrained visual encoder's output space and the input token space of a pretrained language model. The goal is to enable an LLM—which processes discrete or continuous token sequences—to condition its outputs on visual signals without retraining the vision or language backbone. Alignment strategies range from lightweight linear projections (MiniGPT-4) to Q-Former bottlenecks (BLIP-2) to gated cross-attention layers (Flamingo).

## Why it matters

Large language models acquire broad world knowledge and instruction-following capabilities through pretraining and RLHF. If visual features can be faithfully projected into the LLM's representation space, the LLM's existing capabilities can be repurposed for vision-conditioned tasks (captioning, VQA, code generation from sketches) without expensive task-specific fine-tuning.

## Key approaches

- **Linear projection** (MiniGPT-4): a single trainable layer maps Q-Former output to Vicuna's embedding dimension. Simplest; works well when the LLM is powerful enough to interpret soft prompts.
- **Q-Former bottleneck** (BLIP-2): a learned transformer queries the visual encoder with a fixed set of query tokens, producing a compact cross-modal representation fed to the LLM.
- **Gated cross-attention** (Flamingo): interleaves cross-attention layers with existing LLM layers; requires billions of image-text pairs and partial LLM fine-tuning.

## Key papers

- [[minigpt-enhancing-vision-language-understanding-advanced]] — shows one linear projection layer is sufficient when the LLM is sufficiently capable (Vicuna-13B)

## Realized by

- [[minigpt-projection-alignment]]
