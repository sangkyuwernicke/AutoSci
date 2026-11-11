# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 target=direction margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
         model   fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost   firm      0.4852       0.4995  0.4947     0.5097     0.5177 0.1800  0.9338 -0.1662         0.4722    0.4553
1         lgbm   firm      0.4976       0.5101  0.5127     0.5176     0.5177 0.1780  1.0193 -0.1290         0.4722    0.3974
2        logit   firm      0.4920       0.5082  0.5171     0.5030     0.5177 0.1589  0.7788 -0.2020         0.4722    0.3899
3  macro_gated  gated      0.4917       0.5032  0.5056     0.5173     0.5177 0.1906  0.9207 -0.1787         0.5556    0.3918
4       MARKET      -         NaN          NaN     NaN        NaN        NaN 0.2352  1.1489 -0.1424            NaN       NaN
5  EW_UNIVERSE      -         NaN          NaN     NaN        NaN        NaN 0.2822  1.3707 -0.1519         0.5833       NaN
```

## Resolving power
36 test months x ~81 stocks, positive rate 0.52: the mean monthly AUC of a model with no skill has s.e. ~0.011; AUC gaps below ~0.030 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=gating factor_set=base market=KOSPI top_n_mcap=100

## H1: macro_gated vs firm-only models (paired by month)
```
  macro_gated_vs  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0          logit     auc   -0.00496 -0.60780  0.72638     0.87922        36    -0.01788     0.00627 0.78040 1.00000
1          logit  prec_k    0.01432  0.92218  0.18137     0.07032        36    -0.00924     0.04037 0.12940 1.00000
2           lgbm     auc   -0.00690 -0.84858  0.79906     0.79824        36    -0.02160     0.00801 0.83000 1.00000
3           lgbm  prec_k   -0.00034 -0.01685  0.50667     0.46122        36    -0.03114     0.03083 0.50300 1.00000
4       catboost     auc    0.00370  0.42662  0.33613     0.45983        36    -0.01211     0.02055 0.33440 1.00000
5       catboost  prec_k    0.00765  0.49869  0.31056     0.24192        36    -0.01953     0.03523 0.30000 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b   diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    1.0193    0.7788 0.2405 -0.2987 0.7504       0.1774        36
1  catboost  logit    0.9338    0.7788 0.1550 -0.3305 0.6398       0.2630        36
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
              mean_abs_shap
RET_3M               0.0939
PCR                  0.0482
RET_12M              0.0470
GPOA                 0.0416
PER                  0.0394
RET_1M               0.0385
OP_GROWTH            0.0356
OPM                  0.0323
DEBT_RATIO           0.0263
SALES_GROWTH         0.0243

[BASE_RATE high vs low] rank corr=0.900, permutation p=0.0100, months high/low=21/15, sign flips=2/16
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M       0.1188   0.0658          1         1   -0.9337  -0.8973      False
RET_12M      0.0705   0.0199          2         7   -0.8008  -0.6047      False
GPOA         0.0591   0.0211          3         4   -0.9226  -0.8708      False
PCR          0.0578   0.0364          4         2    0.8725   0.8043      False
RET_1M       0.0553   0.0205          5         6   -0.8399  -0.7762      False
OP_GROWTH    0.0487   0.0207          6         5    0.9183   0.9101      False
OPM          0.0439   0.0180          7         8   -0.0585  -0.5564      False
PER          0.0429   0.0348          8         3    0.4025   0.4810      False

[TERM_SPREAD high vs low] rank corr=0.906, permutation p=0.0100, months high/low=18/18, sign flips=3/16
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M       0.0711   0.1223          1         1   -0.8888  -0.9363      False
PCR          0.0407   0.0571          2         5    0.8094   0.8743      False
PER          0.0368   0.0422          3         8    0.5031   0.3806      False
GPOA         0.0267   0.0598          4         3   -0.8543  -0.9236      False
RET_12M      0.0262   0.0726          5         2   -0.6470  -0.8107      False
OP_GROWTH    0.0238   0.0503          6         6    0.8941   0.9170      False
OPM          0.0230   0.0432          7         7   -0.6032   0.0763       True
RET_1M       0.0222   0.0594          8         4   -0.7765  -0.8497      False

[CPI_YOY high vs low] rank corr=0.885, permutation p=0.0020, months high/low=18/18, sign flips=3/16
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M       0.1243   0.0691          1         1   -0.9359  -0.8916      False
RET_12M      0.0741   0.0247          2         5   -0.8166  -0.6451      False
RET_1M       0.0623   0.0193          3         8   -0.8559  -0.7793      False
GPOA         0.0603   0.0261          4         4   -0.9216  -0.8535      False
PCR          0.0568   0.0410          5         2    0.8756   0.8067      False
OP_GROWTH    0.0516   0.0225          6         7    0.9154   0.8976      False
OPM          0.0427   0.0235          7         6    0.1794  -0.7110       True
PER          0.0417   0.0373          8         3    0.3653   0.5216      False

[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv
Regime centroids (last test fold):
          BASE_RATE  TERM_SPREAD  CPI_YOY    KRWUSD  VKOSPI
regime_0     3.1774       0.0900   3.8698 1328.8161 17.8919
regime_1     0.7500       0.6296   2.4221 1153.8188 20.8038

Factor weights at first/last test month:
              PER     PBR    PCR  EV_EBITDA     ROE     ROA     OPM    GPOA  SALES_GROWTH  OP_GROWTH  DEBT_RATIO  QUICK_RATIO     ICR  RET_1M  RET_3M  RET_12M
2022-12-31 0.0122  0.0086 0.0110     0.0095 -0.0031 -0.0128  0.0032 -0.0095        0.0106     0.0174      0.0120      -0.0003 -0.0067 -0.0406 -0.0499  -0.0141
2025-11-30 0.0553 -0.0163 0.0784    -0.0518  0.1406 -0.1723 -0.0067 -0.0690       -0.0154     0.0603      0.0125       0.0016  0.0622 -0.0343 -0.0903  -0.0211

```