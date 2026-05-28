---
title: "Collaborating with AI Agents: A Field Experiment on Teamwork, Productivity, and Performance"
slug: collaborating-ai-agents-field-experiment-teamwork
arxiv: "2503.18238"
venue: arXiv.org
year: 2025
tags:
  - human-AI collaboration
  - field experiment
  - teamwork
  - productivity
  - AI agents
  - delegation
  - diversity collapse
  - jagged frontier
importance: 4
date_added: 2026-05-29
source_type: tex
s2_id: a6592233f89114439705adf7244e0fb80bd96e72
tldr: A large-scale randomized field experiment on the Pairit platform finds that human-AI teams are 50% more productive but exhibit a jagged frontier of quality (better text, worse images) and diversity collapse, mediated by task-oriented communication, delegation, and AI recognition.
contribution_type:
  - analysis
  - system
datasets: []
code_url: ""
cited_by: []
---

## Problem & Context

Prior work on AI productivity gains (Noy & Zhang 2023, Brynjolfsson et al. 2023) treats AI as a passive chatbot or individual-level tool, not as a full collaborator in a shared workspace. These studies cannot capture how teamwork dynamics—communication patterns, delegation decisions, and awareness of partner identity—shape outcomes when AI agents take autonomous actions alongside humans. There was no platform enabling randomized controlled experiments where AI agents perform the full complement of collaborative actions (messaging, text editing, image selection, image generation) while researchers capture every time-stamped interaction.

## Key idea

Collaborating with an AI agent reshapes teamwork in three specific ways: (1) communication becomes more **task-oriented** and less interpersonal; (2) humans **delegate** more work to AI and perform fewer direct edits; (3) **recognition** of the AI partner amplifies both effects. Together these form a **delegation workflow** that drives productivity gains and a jagged-frontier quality profile (AI-strength tasks improve; AI-weakness tasks do not). These mechanisms also cause **diversity collapse**: teams that delegate more produce outputs that are more similar to each other.

## Method

**Pairit platform**: A bespoke web platform enabling real-time human-AI or human-human collaboration on ad-creation tasks. The AI agent uses OpenAI `gpt-4o-2024-08-06` with full multimodal context (text, images, UI state, action history). The AI can send messages, edit ad copy (headline, primary text, description), select from stock images, and generate new images via DALL-E 3 API—the same action set as a human partner (minus ad submission). Chain-of-thought prompting is used to guide agent behavior; the agent is triggered every 10 seconds.

**Lab experiment**: 2,234 participants recruited via Prolific (US representative), randomized to human-human (HH) or human-AI (HAI) teams. Teams had 40 minutes to create as many ads as possible for a think-tank annual report. Dataset: 11,024 ads, 182,607 messages, 1,889,559 text edits, 62,119 image edits, 10,074 AI-generated images. Message categories labeled by GPT-4o-mini into task-oriented (content/process) and interpersonal (social/emotional).

**Human evaluation**: 1,195 Prolific raters scored ad text quality, image quality, and predicted click likelihood on 7-point Likert scales (3+ ratings per ad).

**Field experiment**: 2,000 sampled ads (stratified by team type and predicted click score) ran as X (Twitter) ad campaigns from Jan 21–Feb 9, 2025, generating 4.93M impressions and 7,546 clicks across 400 campaigns. Outcomes: CTR, CPC, VTR, VTD (via DocSend unique links).

**Analysis**: OLS for lab outcomes; mixed-effects models with campaign random effects for field outcomes; mediation analysis via sequential regressions; interaction models for recognition effects.

## Experiment & Results

**Productivity**: HAI teams submitted 50% more ads per worker per unit time than HH teams (p<0.001), with higher ad-copy completion rates.

**Quality (jagged frontier)**: HAI teams produced higher text quality (p<0.05) but lower image quality (p<0.01); estimated click likelihood was indistinguishable across conditions—consistent with a jagged frontier where LLMs excel at text but not at visual-quality prediction.

**Output diversity**: HAI teams produced significantly less diverse outputs (cosine distance to condition centroid β=−0.094, p<0.001), consistent with diversity collapse.

**Field performance**: No direct HAI effect on CPC, CTR, or VTD. Text quality increased CTR by 0.007% (p<0.05) and extended VTD by ~4% per rating point (p=0.051). Image quality reduced CPC by $0.29 (2.5%; p<0.05). The quality trade-offs offset each other, yielding similar overall field performance across team types.

**Communication**: HAI teams sent 62% more messages overall; 25% more task-oriented, 18% fewer interpersonal messages.

**Delegation**: HAI teams made 62% fewer direct copy edits; delegated 58% of work to AI vs. 50% in HH teams (17% increase, p<0.001).

**Recognition**: 94.5% of HAI participants correctly identified their partner as AI vs. 57.6% in HH teams. Correct recognizers sent more messages (+11.5, p<0.001), more task-oriented (+0.061, p<0.001), less interpersonal (−0.059, p<0.01), and delegated more (+0.056, p<0.05).

**Mechanism mediation**: Task-oriented communication improved text/image quality and productivity in HAI teams but not HH teams; interpersonal communication reduced quality in HAI teams. Delegation improved text quality (β=0.302, p<0.001) and click ratings (β=0.178, p<0.01) but not image quality (β=0.132, n.s.) in HAI teams—consistent with the jagged frontier. Delegation reduced output diversity (β=−0.083, p<0.001).

## Limitations

- No human-alone baseline: cannot isolate AI's marginal contribution vs. coordination costs.
- Mediation analyses are post-hoc and correlational; causal pathway from recognition → behavior cannot be fully disentangled from personality/AI-comfort confounds.
- Vision models (gpt-4o) not optimized for image-quality prediction; image quality effects may change as models improve.
- Single-task, single-session context (ad creation, 40 min); long-term collaboration dynamics unexplored.
- Generalizability limited to multi-modal creative tasks with iterative structure; may not extend to high-stakes or deep-expertise domains.

## Open questions

- How do delegation workflow dynamics evolve over repeated or longitudinal human-AI collaborations?
- Can targeted fine-tuning or specialized vision models close the image-quality gap on the jagged frontier?
- Do multi-AI or multi-human-AI team configurations change the mechanisms found in dyadic settings?
- How does output diversity collapse affect downstream creative quality at scale?
- What training or interface designs can preserve human creative variation while capturing AI efficiency gains?

## My take

This is a methodologically rigorous contribution: randomized, large-scale, with both lab and field validation, and a platform that enables unprecedented measurement granularity. The three-mechanism framework (task-orientation, delegation, recognition) is a clean and portable explanatory structure. The finding that recognition itself shapes behavior—not just team type—is particularly important for practitioners. The jagged frontier extending to field performance metrics (text quality → CTR; image quality → CPC) is a useful operationalization for applied settings. Main caveat: the 2025 gpt-4o capabilities define the jagged frontier—future work will need to re-calibrate as vision capabilities improve. The diversity collapse finding warrants serious attention given scale effects in organizational deployment.

## Related

- [[jagged-frontier]] — foundational concept operationalized and extended to field performance
- [[human-ai-collaboration]] — core concept studied through agentic dyadic setting
- [[diversity-collapse]] — empirically documented mechanism in HAI teams
- [[delegation-workflow]] — new concept introduced as integrating mechanism
- [[pairit]] — platform method enabling the experiment
