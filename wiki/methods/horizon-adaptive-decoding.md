---
name: "Horizon-Adaptive Query Decoding"
slug: horizon-adaptive-decoding
type: architecture
tags:
  - time-series-forecasting
  - transformer
  - multi-horizon
  - horizon-adaptive
  - randomized-training
source_papers:
  - "[[metoformer-hq-multi-scale-horizon-adaptive]]"
parent_methods: []
child_methods: []
realizes_concepts:
  - "[[metocean-forecasting]]"
date_updated: 2026-05-29
---

## Problem setting

Standard Transformer decoders for multi-step forecasting produce fixed-length output sequences where each position is decoded identically, without explicit conditioning on which lead time is being predicted. This causes the model to over-specialize to the fixed training horizon, degrading performance when inference horizons differ from the training horizon or when the model must produce consistent predictions across a range of lead times.

## Mechanism

**Horizon-Adaptive Query Decoding (HAQD)** replaces fixed decoder position embeddings with dynamic sinusoidal lead-time queries:

```
q_h = PE(h)  ∈ R^d
```

where PE(·) is a standard sinusoidal positional encoding and h is the horizon step index. The decoder cross-attends to encoder memory M ∈ R^{T×d} using q_h to produce step-specific context and output ŷ_h.

**Randomized-horizon training**: During training, the active prediction length H' is sampled from U{H_min(e), ..., H} each epoch. H_min is warmed up (held at H for early epochs) then linearly ramped to a lower minimum (e.g., from H_start=4 to H_final=1). Loss is computed only on the first H' decoded steps, optionally with horizon-dependent loss weights (e.g., linear decay 0.5).

## Procedure

1. Encode input sequence X ∈ R^{B×L×C_in} via Transformer encoder → memory M ∈ R^{B×T×d}.
2. For each training step, sample H' ~ U{H_min(e), ..., H}.
3. For h = 1, ..., H': compute q_h = PE(h), cross-attend to M, project to ŷ_h ∈ R^{B×C_out}.
4. Compute loss on (Ŷ_{:,1:H',:}, Y_{:,1:H',:}).
5. At inference: decode all H steps with lead-time-specific queries.

## Assumptions

- Positional encoding is a sufficient representation of lead-time identity for the decoder.
- Exposure to varied horizon lengths during training improves distribution over inference horizons without requiring explicit multi-task objectives.
- The encoder memory provides a shared representation that can be re-queried at arbitrary lead times within the trained range.

## Limitations

- Generalization is bounded by the maximum training horizon H; out-of-distribution inference at H' >> H is untested.
- Sinusoidal PE is fixed; learned lead-time embeddings may offer richer conditioning but add parameters.
- The randomized training schedule introduces a hyperparameter (H_min schedule) that requires tuning.

## Tradeoff profile

- **Benefit**: largest incremental gain in MetoFormer-HQ ablation (RMSE −5.74%, MAE −10.11% over the base without HAQD); improves horizon-wise consistency and peak-event detection (F1 0.9446).
- **Cost**: adds decoder query computation and horizon-sampling curriculum; minimal parameter overhead (only PE and query-norm clip).
- **Vs. fixed-horizon decoder**: more robust to variable operational lead times; no accuracy loss at the nominal training horizon.

## Evaluated by

- [[metoformer-hq-multi-scale-horizon-adaptive]]
