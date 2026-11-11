# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 target=direction margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
         model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost  firm      0.4852       0.4995  0.4947     0.5097     0.5177 0.1800  0.9338 -0.1662         0.4722    0.4553
1     catboost  full      0.4467       0.5000  0.4770     0.5091     0.5177 0.1689  0.9188 -0.1868         0.4722    0.4621
2         lgbm  firm      0.4976       0.5101  0.5127     0.5176     0.5177 0.1780  1.0193 -0.1290         0.4722    0.3974
3         lgbm  full      0.5228       0.5091  0.5206     0.5714     0.5177 0.2859  1.4245 -0.2060         0.6389    0.3234
4        logit  firm      0.4920       0.5083  0.5171     0.5030     0.5177 0.1589  0.7788 -0.2020         0.4722    0.3899
5        logit  full      0.5030       0.5012  0.5103     0.5151     0.5177 0.2064  0.8817 -0.2090         0.4722    0.3640
6       MARKET     -         NaN          NaN     NaN        NaN        NaN 0.2352  1.1489 -0.1424            NaN       NaN
7  EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.2822  1.3707 -0.1519         0.5833       NaN
```

## Resolving power
36 test months x ~81 stocks, positive rate 0.52: the mean monthly AUC of a model with no skill has s.e. ~0.011; AUC gaps below ~0.030 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base market=KOSPI top_n_mcap=100

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.00702 -0.53363  0.70152     0.67096        36    -0.02477     0.01193 0.77480 1.00000
1     logit  prec_k    0.01208  0.56280  0.28858     0.29050        36    -0.02752     0.05438 0.27180 1.00000
2      lgbm     auc   -0.00102 -0.07637  0.53022     0.37516        36    -0.02462     0.02013 0.51680 1.00000
3      lgbm  prec_k    0.05378  2.09026  0.02196     0.01003        36     0.00798     0.10619 0.00860 0.13178
4  catboost     auc    0.00043  0.03628  0.48563     0.55247        36    -0.01386     0.01519 0.47260 1.00000
5  catboost  prec_k   -0.00057 -0.03183  0.51261     0.39668        36    -0.02973     0.02807 0.50020 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b   diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    1.4245    0.8817 0.5428 -0.0790 1.6043       0.0460        36
1  catboost  logit    0.9188    0.8817 0.0371 -0.4522 0.6729       0.4004        36
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
CPI_YOY             0.1056
KRWUSD              0.0940
VKOSPI              0.0530
TERM_SPREAD         0.0316
RET_3M              0.0201
BASE_RATE           0.0195
PCR                 0.0102
RET_1M              0.0090
OPM                 0.0048
PER                 0.0027

[BASE_RATE high vs low] rank corr=0.654, permutation p=0.0020, months high/low=21/15, sign flips=9/16
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M       0.0196   0.0191          1         1   -0.6609  -0.8622      False
PCR          0.0116   0.0075          2         2    0.6765   0.8226      False
RET_1M       0.0110   0.0058          3         4   -0.6508  -0.7580      False
OPM          0.0061   0.0027          4         5   -0.6402  -0.8120      False
ROE          0.0031   0.0006          5         8   -0.6124   0.2650       True
ROA          0.0022   0.0002          6        11   -0.5844  -0.2019      False
PBR          0.0020   0.0002          7        12    0.6356   0.2209      False
OP_GROWTH    0.0013   0.0009          8         6    0.6370   0.8012      False

[TERM_SPREAD high vs low] rank corr=0.813, permutation p=0.0020, months high/low=18/18, sign flips=8/16
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M       0.0235   0.0152          1         1   -0.8396  -0.6152      False
PCR          0.0102   0.0096          2         2    0.8167   0.6239      False
RET_1M       0.0095   0.0082          3         3   -0.7586  -0.6074      False
PER          0.0049   0.0000          4        12    0.5732      NaN       True
OPM          0.0042   0.0052          5         4   -0.7906  -0.5919      False
ROE          0.0015   0.0027          6         5   -0.0363  -0.5717      False
OP_GROWTH    0.0012   0.0011          7         8    0.7830   0.5896      False
ROA          0.0007   0.0020          8         6   -0.3706  -0.5394      False

[CPI_YOY high vs low] rank corr=0.831, permutation p=0.0040, months high/low=18/18, sign flips=8/16
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M       0.0133   0.0254          1         1   -0.5724  -0.8511      False
PCR          0.0083   0.0115          2         2    0.5812   0.8272      False
RET_1M       0.0071   0.0105          3         3   -0.5667  -0.7678      False
OPM          0.0045   0.0048          4         5   -0.5538  -0.7962      False
ROE          0.0023   0.0018          5         6   -0.5375  -0.1225      False
ROA          0.0018   0.0009          6         8   -0.5054  -0.4129      False
PBR          0.0017   0.0008          7         9    0.5517   0.4495      False
OP_GROWTH    0.0010   0.0013          8         7    0.5528   0.7904      False

Top macro x firm interactions (mean|phi_ij|*2):
                       value
TERM_SPREAD RET_3M    0.0086
            RET_1M    0.0057
KRWUSD      RET_3M    0.0024
            ROA       0.0020
CPI_YOY     PBR       0.0019
KRWUSD      OPM       0.0019
BASE_RATE   OP_GROWTH 0.0017
            RET_3M    0.0015

```