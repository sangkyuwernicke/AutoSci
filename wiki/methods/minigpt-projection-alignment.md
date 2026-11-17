---
name: MiniGPT-4 Projection Alignment
slug: minigpt-projection-alignment
type: training
tags:
  - vision-language
  - alignment
  - projection
  - multimodal
  - instruction-tuning
source_papers:
  - "[[minigpt-enhancing-vision-language-understanding-advanced]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[vision-language-alignment]]"
  - "[[two-stage-vision-language-pretraining]]"
date_updated: 2026-05-29
---

## Summary

MiniGPT-4 Projection Alignment is a two-stage training method for aligning a frozen visual encoder with a frozen advanced LLM using a single linear projection layer as the only trainable component.

## Stage 1: Large-scale pretraining

- **Datasets**: Conceptual Captions (CC3M + CC12M), SBU Captions, LAION (~5 M image-text pairs total)
- **Architecture**: ViT-G/14 (EVA-CLIP) → Q-Former (from BLIP-2) → linear projection → Vicuna-13B
- **Objective**: next-token prediction on ground-truth captions conditioned on visual soft prompt
- **Schedule**: 20,000 steps, batch size 256, ~10 hours on 4 × A100-80GB

## Stage 2: Curated fine-tuning

- **Dataset construction**: (1) prompt stage-1 model to generate long descriptions of 5,000 CC images; (2) clean with ChatGPT (remove repetition, fragments, non-English); (3) manual verification → ~3,500 pairs retained
- **Template**: `###Human: <Img><ImageFeature></Img> <Instruction> ###Assistant:`
- **Schedule**: 400 steps, batch size 12, ~7 minutes on 1 × A100
- **Loss masking**: no regression loss on the image-instruction prompt prefix

## Key design choices

- All vision encoder and LLM weights are frozen in both stages (only the ~5M-parameter projection layer is trained)
- Q-Former from BLIP-2 is reused without modification; ablations show it is not critical for advanced abilities
- Single linear layer outperforms deeper MLPs in limited-data stage-2 setting

## Realized concepts

- [[vision-language-alignment]]
- [[two-stage-vision-language-pretraining]]
