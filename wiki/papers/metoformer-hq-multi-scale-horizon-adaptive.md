---
title: "MetoFormer-HQ: Multi-scale and Horizon-Adaptive Transformer for Multivariate Metocean Forecasting"
slug: metoformer-hq-multi-scale-horizon-adaptive
arxiv: ""
venue: ""
year: 2026
tags:
  - time-series-forecasting
  - transformer
  - metocean
  - multivariate-forecasting
  - patch-embedding
  - horizon-adaptive
importance: 3
date_added: 2026-05-29
source_type: tex
tldr: "MetoFormer-HQ augments a patch-based Transformer with multi-scale patch embedding, gated channel interaction, and horizon-adaptive query decoding to achieve robust multi-step multivariate metocean forecasting on Korean coastal buoy data."
contribution_type:
  - method
  - application
datasets:
  - Korean Coastal Buoy (KHOA OceanGrid)
cited_by: []
---

## Problem & Context

Metocean time series (significant wave height, wind speed, current speed, water temperature, air pressure, and directional variables) collected from coastal buoy networks require accurate multi-step forecasting for offshore renewable energy planning, ship routing, and coastal hazard mitigation. These series exhibit concurrent periodicities across multiple scales (hourly, tidal/diurnal at ~12-24 h, synoptic at ~48 h+), pronounced non-stationarity from weather systems, and complex nonlinear cross-variable coupling.

Numerical wave models (WAVEWATCH III, SWAN) provide physically interpretable predictions but are constrained by computational cost and sensitivity to initial/boundary conditions for localized, rapidly-updated operations. Data-driven approaches using deep learning have become attractive complements. Prior deep learning work focuses mainly on single targets (often significant wave height alone), fixed lead times, and either purely channel-independent or indiscriminate cross-variable mixing — leaving multivariate, multi-step, flexible-horizon settings underexplored.

Patch-based Transformers (e.g., PatchTST) offer an efficient backbone for long-horizon forecasting, but a generic single-scale, fixed-horizon patch design leaves three gaps for metocean use: (1) a single patch resolution cannot capture concurrent multi-scale periodicities; (2) channel-independent processing misses physical coupling among waves, winds, and currents; (3) fixed-horizon training leads to over-specialization at a single lead time.

## Key idea

MetoFormer-HQ addresses these three gaps with three incrementally added modules on top of a patch-based Transformer backbone: (i) **Multi-scale patch embedding (MSPE)** captures concurrent periodicities by tokenizing the input at three temporal scales (2 h/1 h, 12 h/4 h, 48 h/12 h receptive-field/stride on 30-min data) and concatenating scale-aware tokens; (ii) **Gated channel interaction (GCI)** performs conservative cross-variable reweighting using squeeze-and-excitation-style pooled descriptors and a learnable residual gate, stabilizing noisy cross-channel coupling without aggressive mixing; (iii) **Horizon-adaptive query decoding (HAQD)** with randomized-horizon training conditions the decoder on sinusoidal lead-time queries for step-specific predictions, while exposing the model to randomly sampled horizon lengths during training to reduce fixed-horizon over-specialization.

## Method

**Backbone**: Patch-based Transformer with reversible instance normalization (RevIN) applied per-channel before tokenization. Input window L=720 (15 days at 30-min resolution), horizon H=6 (3 hours).

**MSPE**: Three scale branches with (patch_length, stride) ∈ {(4,2), (24,8), (96,24)}. Each branch maps patches via a learnable projection to d-dim tokens, adds a scale embedding, and concatenates all tokens into a unified sequence fed to the encoder.

**GCI**: Before patch embedding, computes average- and max-pooled temporal descriptors per channel, passes them through a shared MLP, and produces per-channel weights via sigmoid. A learnable scalar gate (temperature-controlled sigmoid) controls residual mixing in additive mode: X̃ = X + α·X_att.

**HAQD**: Decoder uses sinusoidal positional encodings as horizon queries q_h = PE(h) for each step h. The decoder attends to encoder memory using q_h and produces step-specific predictions. Randomized-horizon training samples H' ~ Uniform{H_min(e), ..., H} each epoch, with H_min linearly ramped from H_start=4 to H_final=1 after warmup.

**Training**: Adam + OneCycle LR schedule, 50 epochs, batch size 128. d_model=128, 8 attention heads, 3 encoder layers, 2 decoder layers, FF dim 512, dropout 0.1. Early stopping patience 5 on validation RMSE.

**Input channels**: Cin=30 (6 numeric metocean + 4 directional encoded as (sin,cos) + 18 cyclical time features + 2 location features). Output: Cout=10 (6 numeric + 4 directional targets).

## Experiment & Results

**Dataset**: Korean Coastal Buoy (KHOA OceanGrid), 2018–2025, 18 stations at 30-min resolution (2,088,455 rows total). Spatial out-of-distribution (OOD) evaluation: training on 16 stations, validation and test on separate unseen stations. Three coastal regions tested (East, South, West).

**Baselines**: DLinear, NLinear, N-HiTS, and the patch-based Transformer backbone (BASE).

**Overall (East OOD, mean ± std over 3 seeds)**:
- HQ: RMSE 3.2071±0.0414, MAE 1.5952±0.1001, R² 0.7542
- BASE: RMSE 3.4025±0.0043, MAE 1.7747±0.0137, R² 0.7139
- N-HiTS: RMSE 4.5830±1.0453, MAE 2.5419±0.7039, R² 0.6417
- HQ vs BASE: −5.74% RMSE, −10.11% MAE
- HQ vs N-HiTS: −30.02% RMSE, −37.24% MAE

**Ablation chain** (East OOD): BASE→MS adds RMSE +0.0253 but MAE −0.0737 (multi-scale trade-off under spatial OOD); MS→MSG recovers RMSE (−0.0262) with GCI as conservative regularizer; MSG→HQ gives the largest gain (RMSE −0.1945, MAE −0.1267, R² +0.0295) confirming HAQD dominates.

**Regional OOD (South, West)**: HQ best or near-best across all three regions. South: HQ RMSE 7.3978, MAE 2.7375, R² 0.8324. West: R² 0.6744 (highest in core models).

**Extended horizon (recursive rollout, East)**: HQ best through t+24 on all metrics. Baseline models degrade severely (N-HiTS R² reaches 0.00 at t+13–24; NLinear/DLinear reach negative R² at t+25–36). MetoFormer variants maintain positive R² across all buckets.

**Horizon-wise RMSE** (East): HQ 2.4722 (t+1) to 3.7392 (t+6), consistently below BASE (2.8094 to 3.8467).

**Peak-event (90th percentile)**: HQ F1 0.9446; HQ-R F1 0.9458.

**Hard channels**: HQ-R (robust Huber loss variant) achieves the best average hard-feature R² (0.6013) vs HQ (0.5766), particularly for wave height R² 0.6988 vs 0.6507.

## Limitations

- Evaluation limited to Korean coastal buoys (KHOA OceanGrid); generalizability to other ocean basins and sensor networks is unverified.
- No comparison against recent spatio-temporal graph or physics-informed neural baselines (e.g., GraphCast, neural ODE for ocean).
- Spatial OOD is limited to single held-out stations; performance at stations with very different regimes (e.g., open-ocean vs. fjord) is not characterized.
- HAQD horizon flexibility is bounded by training H=6; truly arbitrary-length forecasting (beyond the training horizon distribution) is not demonstrated.
- GCI gate shifts are modest and scenario-conditional gains are small, suggesting the channel interaction mechanism provides stability rather than accuracy gains.
- No multi-buoy spatio-temporal modeling; each station is treated independently in the current framework.

## Open questions

- Can multi-buoy spatio-temporal modeling (e.g., graph-based encoding of buoy proximity) improve regional OOD performance?
- Does HAQD's randomized-horizon training benefit other multi-step forecasting domains (e.g., financial, energy) where horizon requirements are variable?
- How does MetoFormer-HQ compare against large pretrained time-series foundation models (e.g., TimesFM, Chronos) on buoy data?
- What is the minimum training data size for reliable spatial OOD transfer with HAQD?

## My take

MetoFormer-HQ is a well-motivated domain-specific adaptation of PatchTST for multivariate ocean forecasting. The ablation design is rigorous and cleanly isolates each component's contribution. The main finding — that horizon-adaptive decoding dominates over multi-scale tokenization and gated channel interaction — is informative and actionable for future work. The spatial OOD evaluation protocol is a strength rarely seen in ocean ML papers. The paper is an application paper with solid engineering contributions; the individual modules (MSPE, GCI, HAQD) are combinations of known ideas rather than fundamentally new primitives.

## Related

- PatchTST / patch-based Transformer forecasting (backbone)
- [[metocean-forecasting]] (domain context)
- [[horizon-adaptive-decoding]] (HAQD method)
