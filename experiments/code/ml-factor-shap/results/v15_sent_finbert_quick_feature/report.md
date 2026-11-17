# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                   model        fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0               catboost   Firm-only      0.5116       0.5014  0.5122     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
1               catboost  Firm+Macro      0.4544       0.4922  0.4834     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
2                  dtree   Firm-only      0.5026       0.5107  0.4998     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
3                  dtree  Firm+Macro      0.4798       0.5009  0.4968     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
4                   lgbm   Firm-only      0.4903       0.5006  0.4908     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
5                   lgbm  Firm+Macro      0.4536       0.5051  0.4802     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
6                  logit   Firm-only      0.4762       0.5048  0.4845     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
7                  logit  Firm+Macro      0.4966       0.5048  0.4994     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
8                     rf   Firm-only      0.4991       0.5082  0.4967     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
9                     rf  Firm+Macro      0.4689       0.5105  0.4755     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
10                 ridge   Firm-only      0.4917       0.5133  0.5184     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
11                 ridge  Firm+Macro      0.4756       0.5133  0.4953     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
12                   xgb   Firm-only      0.5003       0.4979  0.4986     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
13                   xgb  Firm+Macro      0.4352       0.4837  0.4527     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
14                MARKET           -         NaN          NaN     NaN        NaN        NaN 0.2346  1.1450 -0.1455         0.5833     0.0058    1.1032       NaN
15           EW_UNIVERSE           -         NaN          NaN     NaN        NaN        NaN 0.2059  1.0792 -0.1500         0.5833     0.0037    1.1719       NaN
16     KOSPI200_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.2768  1.2236 -0.1724         0.6389     0.0090    1.3818       NaN
17  KOSPI200_EW_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.1617  1.0836 -0.0982         0.0000     0.0000       NaN       NaN
18        KOSPI200_PROXY           -         NaN          NaN     NaN        NaN        NaN 0.2514  1.0575 -0.1701         0.5556     0.0076    1.0420       NaN
```

fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in metrics.csv).

## Resolving power
36 test months x ~91 stocks, positive rate 0.50: the mean monthly AUC of a model with no skill has s.e. ~0.010; AUC gaps below ~0.028 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=False macro_mode=raw macro_role=feature factor_set=base sentiment=finbert market=KOSPI top_n_mcap=100

## H1: full (firm+macro) minus firm-only, paired by month
```
       model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0      logit     auc    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
1      logit  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
2      ridge     auc    0.00007  0.70620  0.24237     0.25733        36    -0.00010     0.00032 0.29080 1.00000
3      ridge  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
4      dtree     auc   -0.00977 -1.26949  0.89368     0.86120        36    -0.02448     0.00258 0.93380 1.00000
5      dtree  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
6         rf     auc    0.00232  0.53619  0.29761     0.15371        36    -0.00508     0.00946 0.25400 1.00000
7         rf  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
8        xgb     auc   -0.01411 -1.15801  0.87265     0.84254        36    -0.03926     0.00838 0.87860 1.00000
9        xgb  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
10      lgbm     auc    0.00459  0.48108  0.31673     0.47217        36    -0.01321     0.02509 0.34200 1.00000
11      lgbm  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
12  catboost     auc   -0.00919 -0.66749  0.74558     0.67656        36    -0.03568     0.01645 0.74080 1.00000
13  catboost  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b   diff   ci_lo  ci_hi  p_one_sided  n_months
0        rf  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.4898        36
1       xgb  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.6152        36
2      lgbm  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.6798        36
3  catboost  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.5610        36
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
               mean_abs_shap
KRWUSD                0.2697
VKOSPI                0.1996
CPI_YOY               0.1464
RET_3M                0.1328
RET_1M                0.1014
TERM_SPREAD           0.0817
SENT_MEAN_3M          0.0740
NEWS_COUNT_1M         0.0626
SENT_MEAN_1M          0.0626
GPOA                  0.0624

[BASE_RATE high vs low] rank corr=0.371, permutation p=0.0020, months high/low=21/15, sign flips=10/23
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M          0.0523   0.2446          1         1   -0.9547  -0.8614      False
RET_1M          0.0476   0.1759          2         2   -0.8725  -0.7512      False
RET_12M         0.0238   0.1000          3        17   -0.8801  -0.0103      False
GPOA            0.0235   0.1167          4        13   -0.7937  -0.4464      False
PBR             0.0226   0.0831          5        21    0.8418  -0.0480       True
VOL_20D         0.0219   0.1179          6        12   -0.7998  -0.1933      False
SENT_MEAN_3M    0.0204   0.1489          7         3   -0.7475  -0.5806      False
OPM             0.0143   0.1280          8         8   -0.7623   0.2339       True

[TERM_SPREAD high vs low] rank corr=0.461, permutation p=0.0020, months high/low=18/18, sign flips=8/23
               imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M           0.2116   0.0532          1         1   -0.8509  -0.9522      False
RET_1M           0.1513   0.0508          2         2   -0.7369  -0.8741      False
SENT_MEAN_3M     0.1291   0.0188          3         7   -0.5832  -0.7411      False
SENT_MEAN_1M     0.1235   0.0014          4        20    0.3237  -0.1509       True
NEWS_COUNT_1M    0.1210   0.0038          5        14   -0.4545  -0.2894      False
DEBT_RATIO       0.1143   0.0040          6        13    0.3811   0.0177      False
PCR              0.1119   0.0079          7        10    0.6559   0.7729      False
OPM              0.1097   0.0136          8         8    0.1412  -0.7664       True

[CPI_YOY high vs low] rank corr=0.438, permutation p=0.0020, months high/low=18/18, sign flips=8/23
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M          0.0553   0.2096          1         1   -0.9508  -0.8484      False
RET_1M          0.0538   0.1484          2         2   -0.8796  -0.7277      False
RET_12M         0.0216   0.0894          3        16   -0.8663  -0.1133      False
PBR             0.0203   0.0753          4        21    0.8214   0.0635      False
GPOA            0.0201   0.1046          5         9   -0.7808  -0.4859      False
VOL_20D         0.0197   0.1041          6        10   -0.8007  -0.2517      False
SENT_MEAN_3M    0.0173   0.1306          7         3   -0.7412  -0.5892      False
OPM             0.0131   0.1102          8         8   -0.7693   0.1403       True

Top macro x firm interactions (mean|phi_ij|*2):
                   value
CPI_YOY OPM       0.0496
KRWUSD  ROE       0.0475
CPI_YOY RET_12M   0.0356
        RET_3M    0.0331
KRWUSD  OP_GROWTH 0.0315
        VOL_20D   0.0303
        GPOA      0.0271
CPI_YOY VOL_20D   0.0270

```