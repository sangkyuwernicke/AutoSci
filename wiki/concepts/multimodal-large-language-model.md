---
title: Multimodal Large Language Model
aliases:
  - MLLM
  - vision-language model
  - VLM
  - multimodal LLM
tags:
  - vision-language
  - multimodal
  - large-language-models
maturity: active
definition: A large language model extended to process and reason over non-text modalities (most commonly images, but also audio and video) by coupling a modality encoder with the LLM through an alignment mechanism.
key_papers:
  - "[[minigpt-enhancing-vision-language-understanding-advanced]]"
first_introduced: "2021 (Frozen / Tsimpoukelli et al.)"
date_updated: 2026-05-29
related_concepts:
  - "[[vision-language-alignment]]"
  - "[[two-stage-vision-language-pretraining]]"
---

## Definition

A multimodal large language model (MLLM) combines a pretrained LLM with one or more modality-specific encoders (e.g., a vision transformer for images) connected via an alignment module. The LLM serves as the reasoning and generation backbone; the encoder provides modality features; the alignment module (linear projection, Q-Former, cross-attention, etc.) bridges the two. The resulting system can answer questions about images, describe visual scenes, and generalize to open-ended visual tasks using the LLM's world knowledge.

## Key design axes

- **LLM backbone**: FLAN-T5, Vicuna/LLaMA, GPT-4 (closed). Stronger LLMs unlock richer emergent capabilities.
- **Visual encoder**: CLIP ViT, EVA-CLIP ViT-G, etc.
- **Alignment mechanism**: linear projection, Q-Former, gated cross-attention, MLP adapter.
- **Training regime**: freeze-all-align-only vs. end-to-end fine-tune vs. LoRA.

## Representative systems

| System | LLM | Alignment | Trainable params |
|---|---|---|---|
| Flamingo | Chinchilla 70B | Gated cross-attn | ~10B |
| BLIP-2 | FlanT5-XXL | Q-Former | ~188M |
| MiniGPT-4 | Vicuna-13B | Linear proj | ~5M |
| LLaVA | Vicuna-13B | Linear proj | ~5M |

## Key papers

- [[minigpt-enhancing-vision-language-understanding-advanced]] — demonstrates that LLM quality, not parameter count of the alignment module, is the primary driver of advanced multimodal capabilities
