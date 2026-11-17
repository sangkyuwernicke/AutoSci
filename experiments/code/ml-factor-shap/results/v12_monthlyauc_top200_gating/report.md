# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                  model   fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0              catboost   firm      0.5403       0.5539  0.4884     0.4944     0.4638 0.1002  0.5355 -0.3015         0.5000     0.0011    0.3522    0.3687
1                  lgbm   firm      0.5294       0.5515  0.4823     0.4957     0.4638 0.1070  0.5604 -0.2896         0.5417     0.0017    0.5299    0.3738
2                 logit   firm      0.5296       0.5497  0.4821     0.4982     0.4638 0.1099  0.5817 -0.2806         0.5000     0.0018    0.5841    0.2849
3           macro_gated  gated      0.5261       0.5461  0.4945     0.4941     0.4638 0.1209  0.6130 -0.2748         0.5556     0.0028    0.9301    0.3171
4                MARKET      -         NaN          NaN     NaN        NaN        NaN 0.1149  0.6105 -0.3459         0.5139     0.0021    0.5996       NaN
5           EW_UNIVERSE      -         NaN          NaN     NaN        NaN        NaN 0.0903  0.5184 -0.2968         0.5000     0.0001    0.0459       NaN
6     KOSPI200_OFFICIAL      -         NaN          NaN     NaN        NaN        NaN 0.1283  0.6487 -0.3589         0.5556     0.0032    0.7726       NaN
7  KOSPI200_EW_OFFICIAL      -         NaN          NaN     NaN        NaN        NaN 0.0904  0.5300 -0.3155         0.0000     0.0000       NaN       NaN
8        KOSPI200_PROXY      -         NaN          NaN     NaN        NaN        NaN 0.1229  0.6172 -0.3381         0.4861     0.0029    0.6941       NaN
```

## Resolving power
72 test months x ~647 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.008 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=gating factor_set=base market=KOSPI top_n_mcap=0

## H1: macro_gated vs firm-only models (paired by month)
```
  macro_gated_vs  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0          logit     auc   -0.00363 -1.77071  0.95955     0.94817        72    -0.00781     0.00035 0.96300 1.00000
1          logit  prec_k   -0.00410 -1.44646  0.92378     0.97379        72    -0.00931     0.00153 0.93420 1.00000
2           lgbm     auc   -0.00540 -1.40907  0.91841     0.85300        72    -0.01277     0.00183 0.92760 1.00000
3           lgbm  prec_k   -0.00160 -0.33582  0.63100     0.62168        72    -0.01076     0.00750 0.62480 1.00000
4       catboost     auc   -0.00781 -1.79849  0.96183     0.88940        72    -0.01598     0.00036 0.97000 1.00000
5       catboost  prec_k   -0.00035 -0.07370  0.52927     0.48903        72    -0.00979     0.00889 0.52440 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.5604    0.5817 -0.0212 -0.1066 0.0765       0.6552        72
1  catboost  logit    0.5355    0.5817 -0.0461 -0.1512 0.0566       0.8022        72
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
              mean_abs_shap
VOL_20D              0.0299
RET_3M               0.0256
OP_GROWTH            0.0170
RET_1M               0.0166
ROE                  0.0156
SALES_GROWTH         0.0109
RET_12M              0.0106
OPM                  0.0105
PCR                  0.0087
PBR                  0.0087

[BASE_RATE high vs low] rank corr=0.929, permutation p=0.0040, months high/low=31/41, sign flips=2/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0358   0.0251          1         2   -0.5303  -0.4393      False
RET_3M          0.0257   0.0258          2         1   -0.6924  -0.8340      False
RET_1M          0.0180   0.0158          3         4   -0.7544  -0.7796      False
ROE             0.0166   0.0149          4         5   -0.0290  -0.1093      False
OP_GROWTH       0.0156   0.0181          5         3    0.7821   0.7567      False
OPM             0.0116   0.0097          6         8    0.5603   0.6520      False
SALES_GROWTH    0.0102   0.0115          7         7    0.7892   0.7442      False
PBR             0.0099   0.0078          8        10    0.7844   0.6535      False

[TERM_SPREAD high vs low] rank corr=0.934, permutation p=0.0060, months high/low=36/36, sign flips=1/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0247   0.0347          1         1   -0.3912  -0.5484      False
RET_3M          0.0241   0.0274          2         2   -0.8259  -0.7314      False
OP_GROWTH       0.0177   0.0165          3         5    0.7579   0.7762      False
RET_1M          0.0150   0.0185          4         3   -0.7704  -0.7704      False
ROE             0.0148   0.0165          5         4   -0.0463  -0.0926      False
RET_12M         0.0110   0.0103          6         9   -0.7205  -0.7663      False
SALES_GROWTH    0.0109   0.0111          7         7    0.7422   0.7860      False
OPM             0.0098   0.0112          8         6    0.6547   0.5690      False

[CPI_YOY high vs low] rank corr=0.900, permutation p=0.0020, months high/low=36/36, sign flips=2/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0358   0.0236          1         1   -0.5751  -0.3799      False
RET_3M          0.0309   0.0206          2         2   -0.7606  -0.8217      False
RET_1M          0.0203   0.0132          3         4   -0.7852  -0.7706      False
OP_GROWTH       0.0194   0.0147          4         3    0.7710   0.7672      False
ROE             0.0186   0.0127          5         5   -0.2231   0.0532       True
RET_12M         0.0157   0.0056          6         8   -0.7882  -0.6613      False
SALES_GROWTH    0.0143   0.0077          7         7    0.7837   0.7568      False
PBR             0.0131   0.0044          8        10    0.8874   0.5071      False

[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv
Regime centroids (last test fold):
          BASE_RATE  TERM_SPREAD  CPI_YOY    KRWUSD  VKOSPI
regime_0     1.1620       0.4250   1.3906 1146.6183 17.8344
regime_1     3.1774       0.0900   3.8698 1328.8161 17.8919

Factor weights at first/last test month:
               PER    PBR    PCR  EV_EBITDA     ROE    ROA    OPM    GPOA  SALES_GROWTH  OP_GROWTH  DEBT_RATIO  QUICK_RATIO     ICR  RET_1M  RET_3M  RET_12M  VOL_20D
2019-12-31 -0.0109 0.0287 0.0378     0.0035 -0.0018 0.0791 0.0118  0.0198       -0.0128     0.0320     -0.0308       0.0014 -0.0337 -0.0273 -0.0588  -0.0490  -0.0169
2025-11-30  0.0077 0.0383 0.0247    -0.0039  0.0060 0.0495 0.0564 -0.0054       -0.0012     0.0378      0.0232       0.0186  0.0094 -0.0243 -0.0537   0.0381   0.0229

```