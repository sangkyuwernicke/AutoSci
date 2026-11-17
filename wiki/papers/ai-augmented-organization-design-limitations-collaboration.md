---
title: "AI-augmented Organization Design: Limitations of the Collaboration Model between Domain and AI Experts"
slug: ai-augmented-organization-design-limitations-collaboration
arxiv: ""
venue: "경영정보학연구 (Korea Information Systems Review)"
year: 2025
tags:
  - ai-augmented-organization
  - human-ai-collaboration
  - organizational-design
  - domain-expert
  - intermediary-role
  - case-study
importance: 2
date_added: 2026-05-29
source_type: pdf
s2_id: ""
tldr: "Literature review and two-firm case study of why domain-expert/AI-expert collaboration fails in AI-augmented organizations, proposing a data-strategist intermediary role to bridge technical and domain gaps."
contribution_type:
  - analysis
  - application
datasets: []
code_url: ""
cited_by: []
---

## Problem & Context

Organizations adopting AI systems increasingly require tight collaboration between domain experts (who hold field knowledge) and AI experts (who hold technical competence). Prior cross-functional collaboration literature identifies clear goals, role clarity, trust, communication, and conflict management as success factors. However, that literature was developed for conventional inter-departmental teams and has not been validated for the distinctive challenges of AI-augmented organizations, where black-box opacity, data-quality dependencies, legacy-system integration, and rapidly shifting technical possibilities all co-exist. Empirical, case-grounded analyses of where and why the existing collaboration model breaks down have been sparse.

## Key idea

The authors argue that standard cross-functional collaboration models are insufficient for AI-augmented organizations because they fail to address: (1) the technical-complexity/domain-specificity gap between AI and domain experts; (2) communication breakdown caused by mismatched vocabularies and feedback loops; (3) trust erosion from AI black-box opacity; and (4) leadership models that cannot simultaneously command both technical and domain depth. They propose a third-party "intermediary" (중간자) role that goes beyond project champion/PM to act as a **data strategist** — someone who bridges data-infrastructure design, pilot validation, conflict mediation, and goal alignment throughout the full project lifecycle.

## Method

Mixed qualitative method combining systematic literature review and two-firm case study.

**Literature review**: Searched Elsevier, Springer, ScienceDirect, Google Scholar, and arXiv for work on AI adoption, cross-functional collaboration, and domain-expert/AI-expert interaction (2020–2024). Screened by title + abstract for relevance; focused on collaboration mechanisms and barriers.

**Case study**: Two Korean companies selected for contrasting outcomes:
- **Company A** (media/journalism): Fragmented collaboration team structure; AI journalist team + reporters with project-level external devs. AI news writing and curation projects. Outcome: goal mismatch, trust failure, performance shortfall.
- **Company B** (manufacturing): Integrated AI task force for smart factory/anomaly detection. Outcome: goal alignment, trust built via PoC/pilot, project success.

Data: in-depth interviews with domain experts and AI experts, supplemented by internal documents.

Analysis: comparative case analysis mapping collaboration barriers from literature to observed company behaviors.

## Experiment & Results

No quantitative experiments. Key qualitative findings:

**Company A (fragmented team) — failure factors**:
- Communication breakdown: AI team used technical jargon reporters couldn't parse; reporters' feedback was too vague for technical implementation.
- Trust deficit: reporters feared AI would replace creative writing; AI outputs failed initial quality expectations, no structured trust-building program.
- Lack of long-term roadmap: short-term efficiency focus left no strategic vision for AI integration.
- Goal misalignment: AI team prioritized technical efficiency, reporters prioritized editorial quality; conflict persisted until a shared compromise framework was improvised.

**Company B (integrated team) — success factors**:
- Clear role assignment: AI team leader matched domain experts and AI experts to projects by R&R fit; roles explicitly defined pre-project.
- Mutual learning: AI experts embedded in domain teams for 1–3 months to acquire field knowledge; reciprocal knowledge exchange formalized.
- Trust building: PoC and pilot tests conducted early to validate technical feasibility and let domain experts observe AI behavior; partially resolved black-box concerns.
- Conflict mediation: AI team leader served as a knowledgeable mediator who anticipated conflicts before they escalated.
- Practical PM: flexible scheduling, online collaboration tools, stage-gate performance tracking (design → development → test → deployment → ROI).

**Proposed intermediary role (data strategist)** — five core elements:
1. Data-centric strategy design (collect/analyze field data, set data direction with AI experts)
2. Data coordination and integration management (quality, consistency, legacy-system compatibility)
3. Data-based trust building (PoC/pilot validation at project outset)
4. Data-utilization coordination (translate domain field needs into data specs for AI algorithms)
5. Resource allocation optimization (balance resources across data collection, preprocessing, analysis)

## Limitations

- Only two case firms, both Korean; limited cross-industry and cross-cultural generalizability.
- Qualitative/exploratory only; no quantitative validation of the intermediary role's effect on outcome.
- Role design is prescriptive but lacks concrete implementation guidance (training programs, authority structures, organizational reconfigurations needed to embed the intermediary).
- Barriers to introducing the intermediary role (vertical organizational hierarchy, inertia of existing practices) are acknowledged but not analyzed in depth.

## Open questions

- What specific competencies (technical vs. domain depth ratio) does an effective data-strategist intermediary need?
- How does the intermediary role scale across organizations of different sizes and sectors?
- What quantitative metrics (productivity gains, ROI, communication-efficiency scores, trust indices) can validate the model?
- How should organizations overcome hierarchical resistance to inserting a new third-party coordination layer?
- Does the model generalize beyond Korean corporate culture?

## My take

A well-grounded exploratory study that puts a useful name on a practitioner-known phenomenon: the person in the middle who makes AI projects work. The data-strategist framing is a modest but helpful extension of the "project champion" concept — it makes the data infrastructure ownership explicit. The two-case comparison is clean and illustrative. The main weakness is scale; two cases from one country with no quantitative validation leave the model firmly in the hypothesis-generation stage. The framework would benefit from large-N validation and from tighter operationalization of what distinguishes a data strategist from a senior data scientist or a business analyst.

## Related

- [[cross-functional-collaboration-model]]
- [[ai-augmented-organization]]
- [[data-strategist-intermediary]]
