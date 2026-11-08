# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
         model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost  firm      0.4847       0.4856  0.4521     0.4531     0.4548 0.1949  0.9228 -0.1520         0.3611    0.3972
1     catboost  full      0.4916       0.4813  0.4558     0.4432     0.4548 0.1651  0.7634 -0.2531         0.3333    0.4037
2         lgbm  firm      0.4838       0.4828  0.4531     0.4360     0.4548 0.1803  0.9143 -0.1574         0.3889    0.3540
3         lgbm  full      0.4798       0.4758  0.4505     0.4431     0.4548 0.1906  0.9132 -0.1741         0.4722    0.3623
4        logit  firm      0.4947       0.4966  0.4555     0.4621     0.4548 0.2321  0.9410 -0.2107         0.4444    0.2232
5        logit  full      0.4898       0.4966  0.4530     0.4621     0.4548 0.2321  0.9410 -0.2107         0.4444    0.2232
6       MARKET     -         NaN          NaN     NaN        NaN        NaN 0.2352  1.1489 -0.1424            NaN       NaN
7  EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.2813  1.3639 -0.1536         0.5833       NaN
```

## Resolving power
36 test months x ~80 stocks, positive rate 0.45: the mean monthly AUC of a model with no skill has s.e. ~0.011; AUC gaps below ~0.030 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=regime factor_set=base market=KOSPI top_n_mcap=100

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
1     logit  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
2      lgbm     auc   -0.00698 -1.64386  0.94542     0.87746        36    -0.01503    -0.00026 0.97880 1.00000
3      lgbm  prec_k    0.00714  0.77666  0.22129     0.25053        36    -0.00995     0.02448 0.20500 0.88516
4  catboost     auc   -0.00427 -0.40619  0.65646     0.65963        36    -0.02541     0.01642 0.65140 1.00000
5  catboost  prec_k   -0.00998 -0.44926  0.67199     0.71074        36    -0.04957     0.03168 0.68000 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.9132    0.9410 -0.0278 -0.3284 0.3527       0.5290        36
1  catboost  logit    0.7634    0.9410 -0.1776 -0.7202 0.3024       0.7592        36
```

## H3: SHAP
```
Global mean|SHAP| (top 10):
             mean_abs_shap
RET_3M              0.0608
PCR                 0.0460
GPOA                0.0358
VKOSPI              0.0351
OP_GROWTH           0.0303
TERM_SPREAD         0.0243
DEBT_RATIO          0.0241
QUICK_RATIO         0.0219
RET_12M             0.0215
RET_1M              0.0211

[BASE_RATE high vs low] rank corr=0.806, permutation p=0.0060, months high/low=21/15, sign flips=4/16
             imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M         0.0642   0.0613          1         1   -0.8540  -0.8904      False
PCR            0.0430   0.0526          2         2    0.5774   0.8334      False
OP_GROWTH      0.0374   0.0245          3         4   -0.7571  -0.8599      False
GPOA           0.0370   0.0369          4         3   -0.7839  -0.7004      False
DEBT_RATIO     0.0357   0.0133          5         8    0.0539   0.6873      False
QUICK_RATIO    0.0328   0.0117          6        11    0.8085   0.6197      False
RET_12M        0.0322   0.0111          7        13   -0.7325  -0.7146      False
PER            0.0271   0.0127          8         9   -0.6721  -0.7855      False

[TERM_SPREAD high vs low] rank corr=0.788, permutation p=0.0040, months high/low=18/18, sign flips=5/16
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M          0.0531   0.0729          1         1   -0.8568  -0.8588      False
PCR             0.0452   0.0488          2         2    0.8007   0.5582      False
GPOA            0.0321   0.0418          3         4   -0.7125  -0.7911      False
OP_GROWTH       0.0217   0.0423          4         3   -0.8312  -0.7688      False
OPM             0.0177   0.0249          5        10   -0.7269  -0.2644      False
SALES_GROWTH    0.0154   0.0248          6        11   -0.5079   0.1101       True
RET_1M          0.0142   0.0308          7         8    0.5215  -0.7447       True
DEBT_RATIO      0.0119   0.0409          8         5    0.5278   0.1372      False

[CPI_YOY high vs low] rank corr=0.718, permutation p=0.0020, months high/low=18/18, sign flips=5/16
             imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M         0.0782   0.0478          1         1   -0.8643  -0.8517      False
PCR            0.0524   0.0416          2         2    0.5491   0.8173      False
GPOA           0.0451   0.0288          3         3   -0.7955  -0.7044      False
OP_GROWTH      0.0449   0.0191          4         4   -0.7763  -0.8280      False
DEBT_RATIO     0.0445   0.0082          5        11    0.1862   0.4849      False
QUICK_RATIO    0.0412   0.0068          6        13    0.8156   0.6136      False
RET_12M        0.0393   0.0075          7        12   -0.7257  -0.6981      False
RET_1M         0.0331   0.0118          8         7   -0.7574   0.5924       True

Top macro x firm interactions (mean|phi_ij|*2):
                       value
TERM_SPREAD RET_3M    0.0076
VKOSPI      PBR       0.0033
            RET_1M    0.0028
            RET_3M    0.0025
TERM_SPREAD OP_GROWTH 0.0024
VKOSPI      OP_GROWTH 0.0021
BASE_RATE   GPOA      0.0020
VKOSPI      ROA       0.0019

```