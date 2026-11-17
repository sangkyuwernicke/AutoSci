# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 target=direction margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
         model   fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost   firm      0.4913       0.5113  0.5183     0.5058     0.5200 0.1099  0.6727 -0.1656         0.3056    0.3848
1         lgbm   firm      0.4928       0.5082  0.5138     0.5202     0.5200 0.1558  0.8197 -0.1683         0.4722    0.4438
2        logit   firm      0.5028       0.5132  0.5230     0.5237     0.5200 0.1883  0.9237 -0.1962         0.4722    0.3876
3  macro_gated  gated      0.4910       0.5087  0.5070     0.5260     0.5200 0.1780  0.8846 -0.1653         0.5000    0.3972
4       MARKET      -         NaN          NaN     NaN        NaN        NaN 0.2346  1.1450 -0.1455            NaN       NaN
5  EW_UNIVERSE      -         NaN          NaN     NaN        NaN        NaN 0.2851  1.3805 -0.1479         0.5278       NaN
```

## Resolving power
36 test months x ~80 stocks, positive rate 0.52: the mean monthly AUC of a model with no skill has s.e. ~0.011; AUC gaps below ~0.030 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=gating factor_set=base market=KOSPI top_n_mcap=100

## H1: macro_gated vs firm-only models (paired by month)
```
  macro_gated_vs  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0          logit     auc   -0.00448 -0.58779  0.71977     0.90128        36    -0.01780     0.00707 0.75360 1.00000
1          logit  prec_k    0.00236  0.14607  0.44235     0.62963        36    -0.01955     0.02650 0.43220 1.00000
2           lgbm     auc    0.00049  0.05034  0.48007     0.31787        36    -0.01783     0.01818 0.48440 1.00000
3           lgbm  prec_k    0.00579  0.26820  0.39506     0.30563        36    -0.03573     0.04545 0.38480 1.00000
4       catboost     auc   -0.00252 -0.30941  0.62058     0.55860        36    -0.01954     0.01331 0.61380 1.00000
5       catboost  prec_k    0.02020  1.11008  0.13727     0.10652        36    -0.01799     0.05754 0.15380 0.82361
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.8197    0.9237 -0.1041 -0.7480 0.4871       0.6470        36
1  catboost  logit    0.6727    0.9237 -0.2510 -1.0294 0.4068       0.7792        36
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
            mean_abs_shap
RET_3M             0.0741
RET_1M             0.0601
RET_12M            0.0539
PCR                0.0501
PER                0.0414
OPM                0.0406
GPOA               0.0264
OP_GROWTH          0.0262
DEBT_RATIO         0.0238
VOL_20D            0.0210

[BASE_RATE high vs low] rank corr=0.907, permutation p=0.0599, months high/low=21/15, sign flips=5/17
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M        0.0804   0.0690          1         1   -0.8866  -0.9012      False
RET_1M        0.0787   0.0392          2         4   -0.8785  -0.7599      False
RET_12M       0.0729   0.0322          3         5   -0.8678  -0.5922      False
PCR           0.0549   0.0438          4         3    0.8196   0.8090      False
OPM           0.0517   0.0244          5         6   -0.4347  -0.6482      False
PER           0.0377   0.0472          6         2    0.2260   0.6721      False
DEBT_RATIO    0.0312   0.0148          7        10   -0.2488   0.5720       True
GPOA          0.0300   0.0239          8         7   -0.7738  -0.8719      False

[TERM_SPREAD high vs low] rank corr=0.900, permutation p=0.0359, months high/low=18/18, sign flips=5/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M       0.0657   0.0856          1         1   -0.8856  -0.8990      False
PCR          0.0466   0.0540          2         4    0.8004   0.8165      False
PER          0.0432   0.0400          3         6    0.6648   0.1822      False
RET_1M       0.0422   0.0823          4         2   -0.7666  -0.8855      False
RET_12M      0.0362   0.0757          5         3   -0.6558  -0.8675      False
OPM          0.0342   0.0464          6         5   -0.6727  -0.2987      False
OP_GROWTH    0.0237   0.0290          7         9    0.8693   0.8126      False
GPOA         0.0209   0.0340          8         7   -0.8510  -0.7808      False

[CPI_YOY high vs low] rank corr=0.863, permutation p=0.0160, months high/low=18/18, sign flips=5/17
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M        0.0890   0.0622          1         1   -0.9084  -0.8765      False
RET_1M        0.0847   0.0397          2         4   -0.8905  -0.7648      False
RET_12M       0.0777   0.0342          3         6   -0.8676  -0.6540      False
PCR           0.0535   0.0471          4         2    0.8139   0.7978      False
OPM           0.0428   0.0379          5         5   -0.1820  -0.7305      False
PER           0.0418   0.0414          6         3    0.1543   0.7144      False
GPOA          0.0369   0.0181          7         9   -0.7898  -0.8495      False
DEBT_RATIO    0.0311   0.0175          8        10   -0.0436   0.0670       True

[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv
Regime centroids (last test fold):
          BASE_RATE  TERM_SPREAD  CPI_YOY    KRWUSD  VKOSPI
regime_0     3.1774       0.0900   3.8698 1328.8161 17.8919
regime_1     0.7500       0.6296   2.4221 1153.8188 20.8038

Factor weights at first/last test month:
              PER     PBR    PCR  EV_EBITDA     ROE     ROA     OPM    GPOA  SALES_GROWTH  OP_GROWTH  DEBT_RATIO  QUICK_RATIO     ICR  RET_1M  RET_3M  RET_12M  VOL_20D
2022-12-31 0.0145  0.0103 0.0161     0.0075 -0.0053 -0.0149 -0.0009 -0.0105        0.0088     0.0138      0.0139      -0.0010 -0.0047 -0.0462 -0.0520  -0.0248   0.0009
2025-11-30 0.0676 -0.0295 0.1029    -0.0657  0.1240 -0.1460 -0.0312 -0.0847       -0.0084     0.0541      0.0172       0.0120  0.0821 -0.0371 -0.0880  -0.0384  -0.0199

```