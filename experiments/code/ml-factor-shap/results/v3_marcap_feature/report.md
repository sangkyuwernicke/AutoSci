# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 target=direction margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
         model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost  firm      0.4913       0.5113  0.5183     0.5058     0.5200 0.1099  0.6727 -0.1656         0.3056    0.3848
1     catboost  full      0.4330       0.4794  0.4716     0.4955     0.5200 0.1389  0.7501 -0.2195         0.3889    0.4885
2         lgbm  firm      0.4928       0.5082  0.5138     0.5202     0.5200 0.1558  0.8197 -0.1683         0.4722    0.4438
3         lgbm  full      0.4830       0.5055  0.4987     0.5600     0.5200 0.1966  1.1081 -0.2046         0.5278    0.2810
4        logit  firm      0.5028       0.5132  0.5230     0.5237     0.5200 0.1883  0.9237 -0.1962         0.4722    0.3876
5        logit  full      0.4961       0.5089  0.5056     0.5176     0.5200 0.1871  0.8755 -0.1488         0.4167    0.4762
6       MARKET     -         NaN          NaN     NaN        NaN        NaN 0.2346  1.1450 -0.1455            NaN       NaN
7  EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.2851  1.3805 -0.1479         0.5278       NaN
```

## Resolving power
36 test months x ~80 stocks, positive rate 0.52: the mean monthly AUC of a model with no skill has s.e. ~0.011; AUC gaps below ~0.030 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base market=KOSPI top_n_mcap=100

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.00438 -0.58535  0.71897     0.79468        36    -0.01922     0.00950 0.71800 1.00000
1     logit  prec_k   -0.00605 -0.37953  0.64671     0.79660        36    -0.03490     0.02644 0.67420 1.00000
2      lgbm     auc   -0.00272 -0.21256  0.58355     0.37516        36    -0.02436     0.01588 0.58140 1.00000
3      lgbm  prec_k    0.03979  1.73965  0.04535     0.05460        36     0.00492     0.08440 0.01140 0.27213
4  catboost     auc   -0.03184 -1.91065  0.96787     0.97006        36    -0.06629    -0.00114 0.98040 1.00000
5  catboost  prec_k   -0.01029 -0.57339  0.71498     0.69310        36    -0.04183     0.02304 0.73640 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    1.1081    0.8755  0.2326 -0.3606 1.1886       0.2194        36
1  catboost  logit    0.7501    0.8755 -0.1254 -0.6467 0.3790       0.6832        36
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
KRWUSD              0.1633
CPI_YOY             0.1406
TERM_SPREAD         0.0584
VKOSPI              0.0572
BASE_RATE           0.0275
RET_3M              0.0238
PCR                 0.0187
RET_12M             0.0150
RET_1M              0.0147
OPM                 0.0132

[BASE_RATE high vs low] rank corr=0.880, permutation p=0.0040, months high/low=21/15, sign flips=3/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_12M    0.0218   0.0051          1         7   -0.6056  -0.7374      False
PCR        0.0196   0.0161          2         2    0.6137   0.7976      False
RET_3M     0.0186   0.0287          3         1   -0.6650  -0.8609      False
RET_1M     0.0182   0.0091          4         5   -0.6543  -0.8206      False
OPM        0.0158   0.0088          5         6   -0.6472  -0.8081      False
PER        0.0119   0.0131          6         3    0.5908   0.7977      False
GPOA       0.0090   0.0012          7        10   -0.6492  -0.2097      False
PBR        0.0075   0.0026          8         8    0.6457   0.8081      False

[TERM_SPREAD high vs low] rank corr=0.917, permutation p=0.0020, months high/low=18/18, sign flips=3/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M     0.0316   0.0139          1         5   -0.8617  -0.6139      False
PCR        0.0194   0.0168          2         2    0.7834   0.5729      False
PER        0.0145   0.0103          3         6    0.7636   0.5586      False
RET_1M     0.0139   0.0149          4         3   -0.8184  -0.5992      False
OPM        0.0118   0.0140          5         4   -0.7865  -0.6001      False
RET_12M    0.0115   0.0182          6         1   -0.7162  -0.5616      False
VOL_20D    0.0097   0.0054          7        10   -0.7582  -0.5535      False
PBR        0.0044   0.0065          8         8    0.7928   0.5947      False

[CPI_YOY high vs low] rank corr=0.924, permutation p=0.0040, months high/low=18/18, sign flips=3/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_12M    0.0162   0.0135          1         5   -0.5213  -0.7257      False
PCR        0.0147   0.0216          2         2    0.5380   0.7896      False
RET_1M     0.0131   0.0157          3         4   -0.5561  -0.8313      False
OPM        0.0123   0.0135          4         6   -0.5614  -0.7927      False
RET_3M     0.0122   0.0334          5         1   -0.5688  -0.8860      False
PER        0.0089   0.0159          6         3    0.5223   0.7784      False
GPOA       0.0066   0.0048          7         9   -0.5531  -0.4394      False
PBR        0.0058   0.0051          8         8    0.5514   0.8046      False

Top macro x firm interactions (mean|phi_ij|*2):
                     value
TERM_SPREAD RET_3M  0.0119
CPI_YOY     OPM     0.0094
TERM_SPREAD RET_1M  0.0034
KRWUSD      PBR     0.0034
BASE_RATE   RET_3M  0.0027
TERM_SPREAD VOL_20D 0.0023
VKOSPI      RET_12M 0.0018
            PCR     0.0016

```