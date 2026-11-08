---
title: "Global Correlation-Network Centrality Agent for KOSPI Regime Detection"
slug: global-correlation-network-centrality-agent-kospi
status: failed
origin: "ideate: Claude Phase 2 brainstorm candidate (Path E, cross-domain transfer) — transfer econophysics correlation-network / minimal-spanning-tree methods (e.g. Song et al. 2011, 'Evolution of worldwide stock markets, correlation structure and correlation-based graphs') into an LLM-agent monitoring role that tracks KOSPI's centrality within a rolling multi-index global correlation network."
origin_gaps:
  - "[[agentic-trading]]"
  - "[[llm-multi-agent-financial-trading]]"
tags:
  - kospi
  - cross-market-correlation
  - correlation-network
  - econophysics-transfer
target_venue: ""
novelty_score: ""
priority: 1
pilot_result: ""
failure_reason: "[filter] Requires building and maintaining a multi-index (5-10 global indices) rolling correlation-network / minimal-spanning-tree pipeline for a benefit that [[global-linkage-channel-ablation-blanket-index]]'s D6b concentration-weighted signal likely captures more directly and cheaply for KOSPI specifically: the empirical driver of KOSPI's global linkage is documented to be two concentrated stocks (Samsung Electronics, SK Hynix) tied to a single mechanism (AI-hyperscaler capex), not a diffuse network effect requiring 5-10-index correlation-graph machinery. Deprioritized as future/robustness work (e.g. a network-centrality early-warning signal for regime shifts) rather than pursued as a standalone idea now, given the higher implementation cost and unclear marginal novelty over the already-scoped concentration-weighted channel."
linked_experiments: []
date_proposed: 2026-09-21
date_resolved: 2026-09-21
---

## Motivation

Econophysics literature (e.g. correlation-based graphs and minimal spanning trees across world market indices) shows that global equity market correlation structure has both slow (globalization) and fast (crisis-driven) dynamics, and that a market's position/centrality within such a network can shift rapidly around stress events. One could build an LLM agent that maintains a rolling correlation network across major global indices (S&P 500, NASDAQ-100, SOX, Nikkei, VIX, DXY) plus KOSPI, and surfaces a "systemic coupling" alert when KOSPI's centrality or eigenvector position shifts — a more general signal than a single pairwise KOSPI-NASDAQ correlation number.

## Hypothesis

A network-centrality signal (KOSPI's position within a rolling multi-index global correlation network) would provide earlier or more robust detection of KOSPI's global-linkage regime shifts than a single pairwise KOSPI-NASDAQ correlation series.

## Approach sketch

Construct a rolling correlation matrix across 6-10 major global indices plus KOSPI; compute a minimal spanning tree or eigenvector-centrality score for KOSPI at each time step; feed the resulting centrality/coupling score as an input channel to a KOSPI trading agent; compare its regime-detection timeliness and channel value against the simpler pairwise KOSPI-NASDAQ correlation signal.

## Novelty argument

General multi-index network-centrality methods are well established in econophysics (Song et al. 2011 and related work) but have not been applied inside an LLM trading-agent pipeline for KOSPI. However, the specific mechanism actually driving KOSPI's global linkage in the current empirical setting is concentrated in two stocks tied to one theme (AI-capex), not diffuse across a broad index network — so the added generality of a full network-centrality pipeline is unlikely to outperform the much cheaper concentration-weighted signal already scoped in [[global-linkage-channel-ablation-blanket-index]]'s D6b, at substantially higher data-collection and engineering cost.

## Target venue

N/A — eliminated at Phase 3 first-pass filter.

## Risks

Higher implementation cost (5-10-index data pipeline, network-construction machinery) without a clear marginal-novelty case over the concentration-weighted channel already scoped in the sibling idea.

## Pilot results

N/A — eliminated at Phase 3 first-pass filter.

## Lessons learned

(empty)
