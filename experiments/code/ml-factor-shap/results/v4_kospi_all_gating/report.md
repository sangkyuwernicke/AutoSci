# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 target=direction margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
         model   fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost   firm      0.5362       0.5420  0.4881     0.4973     0.4642 0.1249  0.6496 -0.2699         0.5278    0.3387
1         lgbm   firm      0.5353       0.5437  0.4916     0.4951     0.4642 0.1322  0.6924 -0.2652         0.5694    0.2623
2        logit   firm      0.5333       0.5372  0.4849     0.4955     0.4642 0.1487  0.7488 -0.2758         0.5278    0.2777
3  macro_gated  gated      0.5285       0.5323  0.4897     0.4875     0.4642 0.1543  0.7566 -0.2628         0.5694    0.3611
4       MARKET      -         NaN          NaN     NaN        NaN        NaN 0.1149  0.6105 -0.3459            NaN       NaN
5  EW_UNIVERSE      -         NaN          NaN     NaN        NaN        NaN 0.0918  0.5247 -0.2966         0.5139       NaN
```

## Resolving power
72 test months x ~647 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.008 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=gating factor_set=base market=KOSPI top_n_mcap=0

## H1: macro_gated vs firm-only models (paired by month)
```
  macro_gated_vs  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0          logit     auc   -0.00493 -0.95383  0.82830     0.53354        72    -0.01525     0.00358 0.85500 1.00000
1          logit  prec_k   -0.00808 -1.39947  0.91699     0.71295        72    -0.02103     0.00329 0.90600 1.00000
2           lgbm     auc   -0.01142 -1.70843  0.95404     0.93370        72    -0.02452     0.00087 0.96400 1.00000
3           lgbm  prec_k   -0.00762 -0.96279  0.83054     0.81161        72    -0.02374     0.00810 0.81920 1.00000
4       catboost     auc   -0.00967 -1.41682  0.91955     0.79688        72    -0.02346     0.00186 0.94220 1.00000
5       catboost  prec_k   -0.00985 -1.21807  0.88639     0.83207        72    -0.02582     0.00577 0.88880 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.6924    0.7488 -0.0565 -0.2030 0.0960       0.7734        72
1  catboost  logit    0.6496    0.7488 -0.0993 -0.2516 0.0229       0.9410        72
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
           mean_abs_shap
PER               0.0475
PCR               0.0450
OPM               0.0295
VOL_20D           0.0244
GPOA              0.0209
RET_12M           0.0178
EV_EBITDA         0.0171
PBR               0.0166
RET_3M            0.0148
RET_1M            0.0142

[BASE_RATE high vs low] rank corr=0.615, permutation p=0.0020, months high/low=31/41, sign flips=2/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D    0.0197   0.0273          1         7   -0.2413  -0.0142      False
OPM        0.0195   0.0368          2         3    0.4096   0.6143      False
PCR        0.0155   0.0676          3         2    0.7755   0.7354      False
PER        0.0152   0.0723          4         1    0.7523   0.4187      False
RET_1M     0.0131   0.0147          5        14   -0.4762  -0.4683      False
RET_3M     0.0092   0.0188          6        12   -0.5793  -0.5287      False
PBR        0.0065   0.0243          7         8    0.6456   0.2533      False
GPOA       0.0055   0.0326          8         4   -0.7151  -0.7421      False

[TERM_SPREAD high vs low] rank corr=0.728, permutation p=0.0020, months high/low=36/36, sign flips=3/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
PER          0.0750   0.0204          1         4    0.4033   0.7183      False
PCR          0.0666   0.0237          2         2    0.6818   0.8047      False
OPM          0.0348   0.0239          3         1    0.6186   0.4594      False
GPOA         0.0286   0.0133          4         7   -0.6918  -0.7526      False
EV_EBITDA    0.0269   0.0073          5        10   -0.5659   0.0379       True
VOL_20D      0.0259   0.0221          6         3    0.0567  -0.2736       True
RET_12M      0.0231   0.0126          7         8   -0.4912  -0.6723      False
PBR          0.0228   0.0105          8         9    0.2485   0.5614      False

[CPI_YOY high vs low] rank corr=0.755, permutation p=0.0020, months high/low=36/36, sign flips=3/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
PCR        0.0566   0.0337          1         2    0.7814   0.5845      False
PER        0.0520   0.0434          2         1    0.5084   0.5167      False
OPM        0.0405   0.0182          3         3    0.6008   0.4929      False
GPOA       0.0324   0.0094          4         7   -0.7677  -0.5558      False
VOL_20D    0.0312   0.0168          5         4   -0.2475   0.0681       True
RET_12M    0.0297   0.0059          6        12   -0.7028  -0.3470      False
RET_3M     0.0247   0.0047          7        15   -0.5513  -0.5573      False
PBR        0.0230   0.0103          8         6    0.4670   0.2559      False

[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv
Regime centroids (last test fold):
          BASE_RATE  TERM_SPREAD  CPI_YOY    KRWUSD  VKOSPI
regime_0     1.3598       0.3588   1.4995 1137.2659 14.9807
regime_1     3.1774       0.0900   3.8698 1328.8161 17.8919
regime_2     0.6711       0.6226   1.2552 1166.2105 27.1000

Factor weights at first/last test month:
              PER     PBR    PCR  EV_EBITDA    ROE    ROA    OPM    GPOA  SALES_GROWTH  OP_GROWTH  DEBT_RATIO  QUICK_RATIO    ICR  RET_1M  RET_3M  RET_12M  VOL_20D
2019-12-31 0.0000 -0.0028 0.0000     0.0029 0.0000 0.0000 0.0118  0.0000       -0.0216    -0.0106     -0.0251       0.0288 0.0000 -0.0143  0.0240   0.0118   0.0424
2025-11-30 0.0181  0.0447 0.0319    -0.0002 0.0075 0.0324 0.0541 -0.0141        0.0071     0.0317      0.0166       0.0147 0.0047 -0.0253 -0.0452   0.0243   0.0137

```