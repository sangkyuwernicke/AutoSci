---
title: "SLM-Mod: Small Language Models Surpass LLMs at Content Moderation"
slug: slm-mod-small-language-models-surpass
arxiv: ""
venue: "NAACL 2025"
year: 2025
tags:
  - content-moderation
  - small-language-models
  - fine-tuning
  - community-norms
  - nlp
  - reddit
importance: 3
date_added: 2026-05-29
source_type: tex
s2_id: ""
tldr: Fine-tuned small language models (<15B parameters) outperform zero-shot LLMs by 11.5% accuracy and 25.7% recall on community-specific Reddit content moderation, with additional cross-community transfer capability.
contribution_type:
  - benchmark
  - analysis
datasets:
  - Reddit-Comment-Removals
code_url: "https://github.com/AGoyal0512/SLM-Mod"
cited_by: []
---

## Problem & Context

Content moderation on online platforms is a critical and growing challenge. Current computational approaches rely on narrow definitions of abuse (e.g., toxicity, hate speech) that ignore the contextual and community-specific nature of norm violations. Large language models (LLMs) have been explored for content moderation, but they are expensive to query in real-time, cannot be easily fine-tuned for specific communities, and rely on closed-source APIs with inconsistent behavior. The field lacked a systematic comparison between fine-tuned small language models (SLMs) and zero-shot or few-shot LLMs for community-specific moderation tasks, including cross-community generalization.

## Key idea

Fine-tuned SLMs (under 15B parameters) consistently outperform much larger zero-shot LLMs at community-specific content moderation. By training subreddit-specific LoRA-adapted models on 8,000 balanced comments per community, SLMs achieve higher accuracy and substantially higher recall than GPT-4o and Command R+. Moreover, SLMs trained on one community can generalize to moderate other communities (cross-domain moderation), acting as "meta-experts" for new or resource-limited communities. The paper also documents GPT-4o's instability across versions—a 10.7% performance degradation between May and August 2024 releases—as a strong argument for open-source alternatives.

## Method

**Data**: 150K comments sampled from Chandrasekharan et al.'s (2018) Reddit comment removals dataset across 15 popular subreddits; 10K per subreddit (5K moderated, 5K unmoderated), 80/20 train/test split.

**SLMs evaluated**: Llama-3.1-8b, Gemma-2-9b, Mistral-NeMo-Instruct (4-bit quantized). Each is fine-tuned with LoRA (rank 16, α=32, 1 epoch, 8K balanced samples, lr=2e-4, AdamW).

**LLMs evaluated**: GPT-4o, GPT-4o-mini, Cohere Command R+ (zero-shot and 2/4-shot ICL).

**Task**: Given a comment, its preceding context, and subreddit rules, classify whether the comment violates norms (binary decision: True/False). Rule-based prompting following Kumar et al. (2024).

**Evaluation**: Balanced distribution (accuracy, precision, recall) and imbalanced distribution (1%, 5%, 10% moderated; AUC over 30 seeds). Cross-domain evaluation: models trained on one subreddit tested on another. Cross-domain factors: correlation analysis using Pearson r between (relative size, description similarity, rule similarity) and cross-domain accuracy.

## Experiment & Results

**In-domain (balanced)**:
- SLMs outperform LLMs by average 11.5% accuracy; Mistral-NeMo (77.87%), Gemma-2-9b (77.2%), Llama-3.1-8b (72.5%) vs. GPT-4o and GPT-4o-mini (both 65.8%).
- SLMs achieve 25.7% higher average recall (Mistral: 77.7%, Gemma: 77.5%, Llama: 71.5%) while LLMs lead in precision (Command R+: 85.5% average).
- Best SLM accuracy: r/changemyview (90.97%); worst: r/AskReddit (60.4%).

**Imbalanced evaluation**:
- Mistral-NeMo outperforms GPT-4o at all imbalance levels: AUC 0.792/0.785/0.781 vs. 0.698/0.687/0.683 at 1%/5%/10% on r/changemyview.

**In-context learning**:
- 2-shot and 4-shot ICL for LLMs yields only marginal gains (<4%) for GPT-4o and GPT-4o-mini. Command R+ gains >4% in some cases but still underperforms SLMs.

**Cross-domain**:
- Best cross-domain SLM outperforms best LLM: +6.5% for r/IAmA, +11.6% for r/askscience, +0.1% for r/movies.
- "Meta-experts" (models trained on r/changemyview, r/nba, r/movies) achieve 64.6–67.8% average cross-domain accuracy.
- No statistically significant correlation between relative subreddit size and cross-domain performance. Only 2 significant correlations for description similarity, 2 for rule similarity (out of 42 tested).

**GPT-4o instability**: Between May and August 2024 releases, recall dropped from 55.7% to 44.7%, accuracy from 67.7% to 65.8%; 10.7% of correctly moderated comments were no longer moderated.

## Limitations

1. Only 15 subreddits (popular ones); findings may not generalize to niche or smaller communities.
2. Text-only moderation; multimodal content (images, videos) is excluded.
3. Data from a single historical period (May 2016–Feb 2017); community norms evolve over time.
4. Continual adaptation of models to temporal norm drift is not addressed.
5. Fine-tuned SLMs are more aggressive (higher false positives on short comments), creating a precision/recall trade-off.

## Open questions

- What drives cross-community generalizability beyond size, topic, and rule similarity?
- Can mixture-of-experts (MoE) over SLMs specialized for different community clusters improve moderation?
- How do continual pretraining and domain-adaptive pretraining (DAPT) maintain SLM accuracy as community norms evolve?
- Can cross-platform (not just cross-subreddit) transfer be achieved with SLMs?

## My take

A well-executed empirical study that challenges the default assumption that bigger (LLM) is better for specialized NLP tasks. The key insight—fine-tuning enables community-norm alignment that off-the-shelf LLMs cannot easily replicate even with few-shot prompting—is practically important for platform moderation design. The GPT-4o instability finding is a useful cautionary data point. The cross-domain analysis is somewhat exploratory (only 4 significant correlations found out of 42 tests), leaving the "what predicts cross-domain success?" question open. Overall a solid, reproducible benchmark contribution for the community-specific moderation space.

## Related

- [[community-specific-content-moderation]]
- [[cross-community-content-moderation]]
- [[lora-fine-tuning-content-moderation]]
