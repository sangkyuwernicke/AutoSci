# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 target=direction margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
         model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost  firm      0.5362       0.5420  0.4881     0.4973     0.4642 0.1249  0.6496 -0.2699         0.5278    0.3387
1     catboost  full      0.4918       0.5429  0.4832     0.5001     0.4642 0.1258  0.6599 -0.3069         0.5833    0.4449
2         lgbm  firm      0.5353       0.5437  0.4916     0.4951     0.4642 0.1322  0.6924 -0.2652         0.5694    0.2623
3         lgbm  full      0.5245       0.5385  0.4925     0.4931     0.4642 0.1075  0.5731 -0.3285         0.5139    0.3862
4        logit  firm      0.5333       0.5372  0.4849     0.4955     0.4642 0.1487  0.7488 -0.2758         0.5278    0.2777
5        logit  full      0.5053       0.5237  0.4784     0.4842     0.4642 0.1406  0.6861 -0.2823         0.5139    0.2412
6       MARKET     -         NaN          NaN     NaN        NaN        NaN 0.1149  0.6105 -0.3459            NaN       NaN
7  EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.0918  0.5247 -0.2966         0.5139       NaN
```

## Resolving power
72 test months x ~647 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.008 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base market=KOSPI top_n_mcap=0

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.01353 -2.64338  0.99495     0.98133        72    -0.02374    -0.00432 0.99920 1.00000
1     logit  prec_k   -0.01135 -2.32742  0.98860     0.98095        72    -0.02230    -0.00174 0.98860 1.00000
2      lgbm     auc   -0.00526 -1.11984  0.86672     0.59882        72    -0.01303     0.00200 0.91800 1.00000
3      lgbm  prec_k   -0.00200 -0.33820  0.63189     0.53602        72    -0.01282     0.00864 0.64620 1.00000
4  catboost     auc    0.00095  0.19915  0.42136     0.15622        72    -0.00886     0.00965 0.41520 1.00000
5  catboost  prec_k    0.00279  0.52083  0.30205     0.35923        72    -0.00796     0.01400 0.31600 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.5731    0.6861 -0.1130 -0.3164 0.0807       0.8676        72
1  catboost  logit    0.6599    0.6861 -0.0262 -0.2335 0.1980       0.5856        72
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
VKOSPI              0.3725
KRWUSD              0.1705
CPI_YOY             0.1275
TERM_SPREAD         0.1169
BASE_RATE           0.0421
OPM                 0.0417
PCR                 0.0345
VOL_20D             0.0307
PER                 0.0266
PBR                 0.0232

[BASE_RATE high vs low] rank corr=0.757, permutation p=0.0020, months high/low=31/41, sign flips=5/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D    0.0321   0.0281          1         4   -0.2284   0.0447       True
OPM        0.0240   0.0542          2         1    0.5548   0.6603      False
PER        0.0239   0.0279          3         5    0.6714   0.6439      False
RET_1M     0.0197   0.0215          4         9   -0.5025  -0.6385      False
PCR        0.0159   0.0482          5         2    0.7834   0.8456      False
RET_3M     0.0147   0.0212          6        10   -0.5951  -0.4905      False
PBR        0.0116   0.0316          7         3    0.5044   0.1117      False
GPOA       0.0073   0.0248          8         8   -0.0423  -0.7248      False

[TERM_SPREAD high vs low] rank corr=0.860, permutation p=0.0060, months high/low=36/36, sign flips=2/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
OPM             0.0540   0.0284          1         1    0.6810   0.5585      False
PCR             0.0504   0.0181          2         5    0.8201   0.8172      False
VOL_20D         0.0314   0.0282          3         2    0.0398  -0.2006       True
PBR             0.0306   0.0153          4         7    0.1561   0.4263      False
PER             0.0305   0.0218          5         3    0.6417   0.6915      False
EV_EBITDA       0.0254   0.0098          6         9   -0.5729  -0.0517      False
SALES_GROWTH    0.0248   0.0091          7        12    0.5920   0.2667      False
GPOA            0.0227   0.0119          8         8   -0.6272  -0.2474      False

[CPI_YOY high vs low] rank corr=0.892, permutation p=0.0100, months high/low=36/36, sign flips=2/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
OPM          0.0455   0.0370          1         1    0.6273   0.6355      False
PCR          0.0356   0.0330          2         2    0.8075   0.7877      False
PBR          0.0287   0.0173          3         6    0.2355   0.2748      False
VOL_20D      0.0279   0.0317          4         3   -0.0918  -0.0481      False
PER          0.0263   0.0259          5         4    0.6120   0.6897      False
RET_1M       0.0239   0.0175          6         5   -0.5914  -0.5943      False
GPOA         0.0219   0.0127          7        10   -0.5648  -0.3471      False
EV_EBITDA    0.0214   0.0138          8         9   -0.3753  -0.3561      False

Top macro x firm interactions (mean|phi_ij|*2):
                 value
VKOSPI  PBR     0.0168
KRWUSD  PBR     0.0136
        GPOA    0.0118
VKOSPI  OPM     0.0104
        RET_12M 0.0085
        RET_1M  0.0083
CPI_YOY PCR     0.0081
        PBR     0.0080

```