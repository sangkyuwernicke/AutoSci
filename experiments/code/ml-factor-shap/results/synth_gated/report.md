# Experiment report
data=synthetic trials=15 cost=0.002 top_q=0.2 margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
         model   fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost   firm      0.5928       0.5934  0.5936     0.6337     0.5023 0.2128  1.4192 -0.0962         0.9583    0.3525
1        dtree   firm      0.5654       0.5651  0.5639     0.5896     0.5023 0.1381  1.0024 -0.1109         0.9167    0.5277
2         lgbm   firm      0.5892       0.5897  0.5899     0.6285     0.5023 0.2045  1.3886 -0.0883         0.9792    0.3777
3        logit   firm      0.5933       0.5929  0.5924     0.6278     0.5023 0.1982  1.3476 -0.0921         0.9583    0.3184
4  macro_gated  gated      0.6025       0.6028  0.5971     0.6431     0.5023 0.2463  1.6519 -0.0902         0.9792    0.3553
5           rf   firm      0.5923       0.5928  0.5928     0.6389     0.5023 0.2410  1.6003 -0.0843         0.9792    0.3535
6        ridge   firm      0.5924       0.5950  0.5866     0.6309     0.5023 0.2089  1.3906 -0.0915         0.9375    0.3142
7          xgb   firm      0.5911       0.5910  0.5904     0.6292     0.5023 0.2045  1.3937 -0.0892         0.9583    0.3681
8       MARKET      -         NaN          NaN     NaN        NaN        NaN 0.0019  0.0807 -0.2526            NaN       NaN
9  EW_UNIVERSE      -         NaN          NaN     NaN        NaN        NaN 0.0019  0.0807 -0.2526         0.1458       NaN
```

## Resolving power
48 test months x ~300 stocks, positive rate 0.50: the mean monthly AUC of a model with no skill has s.e. ~0.005; AUC gaps below ~0.013 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=False macro_mode=raw macro_role=gating factor_set=base market=ALL top_n_mcap=0

## H1: macro_gated vs firm-only models (paired by month)
```
   macro_gated_vs  metric  mean_diff  t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0           logit     auc    0.00990 4.15858  0.00007     0.00022        48     0.00365     0.01645 0.00140 0.00081
1           logit  prec_k    0.01528 2.28943  0.01330     0.00364        48     0.00103     0.03090 0.01960 0.07977
2           ridge     auc    0.00779 2.98599  0.00224     0.00655        48     0.00070     0.01507 0.01340 0.01791
3           ridge  prec_k    0.01215 1.78732  0.04017     0.04302        48    -0.00243     0.02778 0.05820 0.13830
4           dtree     auc    0.03776 8.03781  0.00000     0.00000        48     0.02516     0.05040 0.00000 0.00000
5           dtree  prec_k    0.05347 5.44270  0.00000     0.00000        48     0.03264     0.07500 0.00000 0.00001
6              rf     auc    0.01005 3.18498  0.00129     0.00225        48     0.00143     0.01847 0.01300 0.01157
7              rf  prec_k    0.00417 0.58149  0.28184     0.28333        48    -0.01215     0.02083 0.32840 0.28184
8             xgb     auc    0.01178 3.63513  0.00034     0.00064        48     0.00344     0.02001 0.00280 0.00344
9             xgb  prec_k    0.01389 1.88982  0.03248     0.02459        48    -0.00208     0.03056 0.04880 0.13830
10           lgbm     auc    0.01314 4.02719  0.00010     0.00012        48     0.00470     0.02139 0.00140 0.00112
11           lgbm  prec_k    0.01458 1.96518  0.02766     0.01372        48    -0.00174     0.03229 0.03920 0.13830
12       catboost     auc    0.00946 2.75763  0.00413     0.00545        48     0.00045     0.01817 0.02180 0.02893
13       catboost  prec_k    0.00937 1.19745  0.11857     0.10492        48    -0.00764     0.02674 0.14320 0.23713
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b   diff   ci_lo  ci_hi  p_one_sided  n_months
0        rf  logit    1.6003    1.3476 0.2527  0.1074 0.4284       0.0004        48
1       xgb  logit    1.3937    1.3476 0.0461 -0.1272 0.2379       0.3060        48
2      lgbm  logit    1.3886    1.3476 0.0411 -0.1246 0.1910       0.3066        48
3  catboost  logit    1.4192    1.3476 0.0716 -0.0928 0.2725       0.2082        48
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
              mean_abs_shap
RET_3M               0.0932
SALES_GROWTH         0.0872
EV_EBITDA            0.0618
ROE                  0.0609
OP_GROWTH            0.0589
ROA                  0.0456
ICR                  0.0412
DEBT_RATIO           0.0364
GPOA                 0.0346
PCR                  0.0342

[BASE_RATE high vs low] rank corr=0.983, permutation p=0.0260, months high/low=24/24, sign flips=0/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M          0.0912   0.0952          1         1    0.9562   0.9096      False
SALES_GROWTH    0.0838   0.0905          2         2    0.9705   0.9119      False
EV_EBITDA       0.0566   0.0671          3         3    0.9607   0.9095      False
ROE             0.0561   0.0657          4         4    0.9582   0.8912      False
OP_GROWTH       0.0542   0.0636          5         5    0.9762   0.8881      False
ROA             0.0441   0.0471          6         6    0.9735   0.8685      False
ICR             0.0360   0.0464          7         7    0.9418   0.8673      False
DEBT_RATIO      0.0348   0.0379          8         9   -0.9517  -0.7855      False

[TERM_SPREAD high vs low] rank corr=0.980, permutation p=0.0045, months high/low=24/24, sign flips=0/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M          0.0922   0.0942          1         1    0.9119   0.9522      False
SALES_GROWTH    0.0866   0.0877          2         2    0.9171   0.9627      False
EV_EBITDA       0.0658   0.0579          3         3    0.9153   0.9519      False
ROE             0.0655   0.0563          4         4    0.8942   0.9541      False
OP_GROWTH       0.0623   0.0554          5         5    0.8969   0.9659      False
ICR             0.0455   0.0370          6         7    0.8712   0.9329      False
ROA             0.0454   0.0459          7         6    0.8732   0.9649      False
DEBT_RATIO      0.0383   0.0344          8         8   -0.8026  -0.9355      False

[CPI_YOY high vs low] rank corr=0.953, permutation p=0.0005, months high/low=24/24, sign flips=0/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M          0.1022   0.0843          1         1    0.9655   0.9069      False
SALES_GROWTH    0.0969   0.0774          2         2    0.9732   0.9257      False
EV_EBITDA       0.0581   0.0655          3         4    0.9488   0.9155      False
OP_GROWTH       0.0560   0.0618          4         5    0.9686   0.8973      False
ROE             0.0540   0.0678          5         3    0.9734   0.8850      False
ROA             0.0498   0.0414          6         7    0.9768   0.8569      False
ICR             0.0366   0.0459          7         6    0.9405   0.8672      False
DEBT_RATIO      0.0317   0.0410          8         8   -0.9496  -0.7971      False

[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv
Regime centroids (last test fold):
          BASE_RATE  TERM_SPREAD  CPI_YOY    KRWUSD  VKOSPI
regime_0     1.4037       0.6463   1.1108 1148.8624 27.1866
regime_1     3.1712      -0.1986   4.1424 1395.6164 25.2680

Factor weights at first/last test month:
               PER    PBR     PCR  EV_EBITDA    ROE    ROA    OPM   GPOA  SALES_GROWTH  OP_GROWTH  DEBT_RATIO  QUICK_RATIO    ICR  RET_1M  RET_3M  RET_12M  VOL_20D
2021-12-31 -0.0082 0.0676 -0.0002     0.0575 0.0726 0.0731 0.0427 0.0625        0.1656     0.0700     -0.0318       0.0362 0.0010 -0.0320  0.1481  -0.0043  -0.0372
2025-11-30  0.0964 0.1001  0.0612     0.0687 0.0877 0.0218 0.0606 0.0036        0.0182     0.0648     -0.0900       0.0908 0.0979  0.0250 -0.0657   0.0167  -0.0031

```