# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
          model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0      catboost  firm      0.4954       0.4980  0.4514     0.4781     0.4548 0.2509  1.0608 -0.1669         0.5000    0.4380
1      catboost  full      0.5096       0.5042  0.4668     0.4609     0.4548 0.2483  1.1157 -0.1883         0.4722    0.4725
2         dtree  firm      0.4840       0.4891  0.4479     0.4383     0.4548 0.2285  0.9508 -0.1878         0.5556    0.3122
3         dtree  full      0.5014       0.5050  0.4601     0.4783     0.4548 0.2570  1.0353 -0.2053         0.5556    0.3447
4          lgbm  firm      0.4891       0.4963  0.4427     0.4387     0.4548 0.1759  0.8798 -0.1995         0.4444    0.4314
5          lgbm  full      0.4669       0.4880  0.4327     0.4482     0.4548 0.2385  1.0918 -0.1738         0.5278    0.3904
6         logit  firm      0.4998       0.4936  0.4610     0.4545     0.4548 0.1967  0.8356 -0.1914         0.3889    0.3492
7         logit  full      0.4934       0.4935  0.4641     0.4527     0.4548 0.1993  0.8425 -0.1927         0.3889    0.3455
8            rf  firm      0.4948       0.4855  0.4566     0.4324     0.4548 0.1867  0.9398 -0.1540         0.4722    0.3028
9            rf  full      0.4964       0.4883  0.4573     0.4467     0.4548 0.2198  1.0428 -0.1810         0.5000    0.2977
10        ridge  firm      0.4992       0.4983  0.4533     0.4530     0.4548 0.2262  0.9388 -0.1914         0.4167    0.2886
11        ridge  full      0.4678       0.4984  0.4311     0.4530     0.4548 0.2262  0.9388 -0.1914         0.4167    0.2886
12          xgb  firm      0.4746       0.4923  0.4313     0.4320     0.4548 0.1563  0.8027 -0.1618         0.3611    0.3994
13          xgb  full      0.4881       0.4972  0.4448     0.4398     0.4548 0.1347  0.7113 -0.1822         0.4722    0.4720
14       MARKET     -         NaN          NaN     NaN        NaN        NaN 0.2352  1.1489 -0.1424            NaN       NaN
15  EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.2813  1.3639 -0.1536         0.5833       NaN
```

## H1: full (firm+macro) minus firm-only, paired by month
```
       model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months
0      logit     auc   -0.00017 -0.43008  0.66511     0.56234        36
1      logit  prec_k   -0.00185 -0.57193  0.71449     0.50000        36
2      ridge     auc    0.00007  0.52113  0.30278     0.24772        36
3      ridge  prec_k    0.00000      NaN      NaN         NaN        36
4      dtree     auc    0.01593  1.26649  0.10685     0.17663        36
5      dtree  prec_k    0.04001  1.90308  0.03264     0.03728        36
6         rf     auc    0.00278  0.86207  0.19726     0.26454        36
7         rf  prec_k    0.01425  1.25838  0.10829     0.16868        36
8        xgb     auc    0.00480  0.54653  0.29409     0.29600        36
9        xgb  prec_k    0.00776  0.42610  0.33632     0.45694        36
10      lgbm     auc   -0.00824 -1.05191  0.84997     0.89277        36
11      lgbm  prec_k    0.00953  0.47304  0.31956     0.22959        36
12  catboost     auc    0.00614  0.54624  0.29418     0.30685        36
13  catboost  prec_k   -0.01716 -0.69275  0.75348     0.68464        36
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0        rf  logit    1.0428    0.8425  0.2003 -0.2208 0.7829       0.1722        36
1       xgb  logit    0.7113    0.8425 -0.1312 -0.4387 0.1783       0.7932        36
2      lgbm  logit    1.0918    0.8425  0.2493 -0.1593 0.7946       0.1192        36
3  catboost  logit    1.1157    0.8425  0.2732 -0.3165 0.7445       0.1600        36
```

## H3: SHAP
```
Global mean|SHAP| (top 10):
              mean_abs_shap
RD_INTENSITY         0.0966
VKOSPI               0.0703
RET_6M               0.0685
RET_3M               0.0532
PCR                  0.0521
GPOA                 0.0465
DEBT_RATIO           0.0452
BASE_RATE            0.0398
OP_GROWTH            0.0374
PER                  0.0373

[BASE_RATE high vs low] rank corr=0.872, permutation p=0.0160, months high/low=21/15, sign flips=9/23
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_6M          0.1005   0.0339          1         3   -0.8852  -0.8769      False
RD_INTENSITY    0.0800   0.1156          2         1    0.1732   0.6362      False
PCR             0.0781   0.0262          3         5    0.7155   0.7392      False
GPOA            0.0672   0.0248          4         6   -0.6985  -0.8084      False
RET_3M          0.0668   0.0404          5         2   -0.8824  -0.8590      False
DEBT_RATIO      0.0600   0.0312          6         4   -0.0443   0.1002       True
PER             0.0566   0.0174          7         7   -0.6283  -0.5089      False
OP_GROWTH       0.0566   0.0172          8         8   -0.7576  -0.6391      False

[TERM_SPREAD high vs low] rank corr=0.930, permutation p=0.1677, months high/low=18/18, sign flips=9/23
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RD_INTENSITY    0.1095   0.0802          1         3    0.5980  -0.0866       True
RET_3M          0.0391   0.0725          2         4   -0.8656  -0.8813      False
RET_6M          0.0380   0.1076          3         1   -0.8639  -0.8867      False
DEBT_RATIO      0.0292   0.0668          4         6    0.0934  -0.0516       True
GPOA            0.0270   0.0720          5         5   -0.7574  -0.6856      False
PCR             0.0262   0.0866          6         2    0.7505   0.7056      False
OP_GROWTH       0.0189   0.0615          7         8   -0.6595  -0.7705      False
PER             0.0180   0.0626          8         7   -0.5335  -0.6461      False

[CPI_YOY high vs low] rank corr=0.856, permutation p=0.0040, months high/low=18/18, sign flips=10/23
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_6M          0.1111   0.0345          1         3   -0.8862  -0.8668      False
PCR             0.0925   0.0204          2         6    0.6983   0.7550      False
RD_INTENSITY    0.0806   0.1092          3         1   -0.0983   0.6467       True
RET_3M          0.0761   0.0356          4         2   -0.8791  -0.8748      False
GPOA            0.0755   0.0236          5         5   -0.6696  -0.7610      False
DEBT_RATIO      0.0707   0.0253          6         4   -0.0401   0.0966       True
PER             0.0664   0.0142          7         8   -0.6591  -0.5381      False
OP_GROWTH       0.0648   0.0156          8         7   -0.7806  -0.6530      False

Top macro x firm interactions (mean|phi_ij|*2):
                             value
TERM_SPREAD RET_3M          0.0121
VKOSPI      CAPEX_INTENSITY 0.0113
TERM_SPREAD PCR             0.0092
VKOSPI      RD_INTENSITY    0.0081
            GPOA            0.0064
TERM_SPREAD PER             0.0060
            PBR             0.0057
VKOSPI      RET_6M          0.0057

```