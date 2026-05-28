---
title: "Metocean Forecasting"
aliases:
  - metocean prediction
  - marine environmental forecasting
  - ocean weather forecasting
tags:
  - time-series-forecasting
  - oceanography
  - marine-science
  - multivariate-forecasting
maturity: active
definition: "Prediction of marine environmental variables — including significant wave height, wind speed, current speed, water temperature, and air pressure — from historical observations, typically for operational maritime safety and planning."
key_papers:
  - "[[metoformer-hq-multi-scale-horizon-adaptive]]"
date_updated: 2026-05-29
related_concepts: []
linked_ideas: []
---

## Definition

Metocean (meteorological + oceanographic) forecasting encompasses data-driven and physics-based prediction of marine environmental state variables from time-series measurements. Key variables include significant wave height (SWH), wind speed and direction, surface current speed and direction, water temperature, air temperature, and atmospheric pressure. These are typically measured at fixed coastal or offshore buoy stations at regular intervals (e.g., 30-minute cadence).

The task is challenging because metocean series exhibit: (1) concurrent periodicities across multiple time scales (hourly variability, tidal/diurnal cycles at ~12–24 h, synoptic weather patterns at ~48 h+); (2) pronounced non-stationarity from storm events and seasonal regimes; (3) complex nonlinear cross-variable coupling (wind drives waves and currents, tides modulate wave interaction).

## Intuition

Traditional numerical models (WAVEWATCH III, SWAN) solve governing physical equations and provide interpretable predictions, but require high computational cost and careful parameterization at local scales. Data-driven approaches learn forecast mappings directly from buoy observations, offering faster inference and flexibility for localized applications where historical data is available.

Multi-step (multi-horizon) forecasting of multiple variables simultaneously is the operationally relevant setting: maritime operations require forecasts at varying lead times (hours to days), and physically coupled variables should be predicted jointly.

## Variants

- **Single-variable fixed-horizon**: most ocean engineering deep learning work; focuses on SWH at 1–6 h ahead using LSTM/GRU.
- **Multivariate multi-step**: joint prediction of all metocean channels at multiple lead times; required for operational systems.
- **Spatial OOD generalization**: training on observed stations, forecasting at unseen test stations; critical for network-wide deployment.
- **Physics-informed hybrid**: numerical model post-processing or neural surrogates that incorporate physical constraints.

## Comparison

Versus general time-series benchmarks (ETTh, Exchange-rate, etc.): metocean data has stronger physical coupling among variables, stricter operational accuracy requirements for peak events, and spatial heterogeneity across buoy stations that makes OOD generalization a first-class concern.

## Known limitations

- Deep learning models lack explicit physical constraints, which may produce physically implausible forecasts during extreme events.
- Data sparsity at newly instrumented buoy sites limits transfer learning.
- Directional variables (wind/current direction) require circular encoding to avoid discontinuity artifacts.

## Open problems

- Spatio-temporal modeling across buoy networks (graph-based propagation of marine weather fronts).
- Reliable forecast calibration and uncertainty quantification for safety-critical maritime decisions.
- Evaluation under distributional shift (unseen storm regimes, seasonal extremes).

## Relationship to foundations

Builds on time-series forecasting, sequence modeling, and signal processing for multi-periodic data.

## Realized by

- [[horizon-adaptive-decoding]]

## My understanding

Metocean forecasting is a domain application of multivariate time-series forecasting with domain-specific challenges (concurrent periodicities, physical coupling, spatial OOD) that motivate specialized architectural choices beyond generic LTSF backbones.
