# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
                   model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0               catboost  firm      0.5344       0.5509  0.4782     0.4944     0.4638 0.0884  0.4870 -0.3098         0.4722    0.3909
1               catboost  full      0.4576       0.5450  0.4310     0.4935     0.4638 0.1076  0.5694 -0.2890         0.5000    0.4074
2                   lgbm  firm      0.5306       0.5497  0.4785     0.4931     0.4638 0.1021  0.5404 -0.2947         0.5000    0.3871
3                   lgbm  full      0.4742       0.5197  0.4406     0.4681     0.4638 0.0519  0.3453 -0.3195         0.4583    0.3566
4                  logit  firm      0.5350       0.5499  0.4862     0.4986     0.4638 0.1108  0.5866 -0.2804         0.5000    0.2875
5                  logit  full      0.5023       0.5367  0.4688     0.4920     0.4638 0.0909  0.4966 -0.3084         0.4722    0.2785
6                 MARKET     -         NaN          NaN     NaN        NaN        NaN 0.1149  0.6105 -0.3459            NaN       NaN
7            EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.0903  0.5184 -0.2968         0.5139       NaN
8      KOSPI200_OFFICIAL     -         NaN          NaN     NaN        NaN        NaN 0.1283  0.6487 -0.3589         0.5000       NaN
9   KOSPI200_EW_OFFICIAL     -         NaN          NaN     NaN        NaN        NaN 0.0904  0.5300 -0.3155         0.4861       NaN
10        KOSPI200_PROXY     -         NaN          NaN     NaN        NaN        NaN 0.1229  0.6172 -0.3381         0.5556       NaN
```

## Resolving power
72 test months x ~647 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.008 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base market=KOSPI top_n_mcap=0

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.01324 -2.36158  0.98953     0.87528        72    -0.02492    -0.00368 0.99900 1.00000
1     logit  prec_k   -0.00660 -1.91625  0.97032     0.94023        72    -0.01361    -0.00056 0.98600 1.00000
2      lgbm     auc   -0.02997 -4.20362  0.99996     0.99993        72    -0.04395    -0.01660 1.00000 1.00000
3      lgbm  prec_k   -0.02507 -3.97117  0.99992     0.99989        72    -0.03584    -0.01437 1.00000 1.00000
4  catboost     auc   -0.00596 -1.56243  0.93868     0.81687        72    -0.01309     0.00122 0.94840 1.00000
5  catboost  prec_k   -0.00090 -0.18865  0.57455     0.63511        72    -0.01104     0.00882 0.56980 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.3453    0.4966 -0.1513 -0.2876 0.0332       0.9500        72
1  catboost  logit    0.5694    0.4966  0.0727 -0.0377 0.2262       0.1068        72
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
VKOSPI              0.1708
CPI_YOY             0.1482
KRWUSD              0.1477
TERM_SPREAD         0.0955
BASE_RATE           0.0290
VOL_20D             0.0175
RET_3M              0.0133
ROE                 0.0122
OPM                 0.0102
RET_1M              0.0099

[BASE_RATE high vs low] rank corr=0.838, permutation p=0.0060, months high/low=31/41, sign flips=2/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0206   0.0145          1         2   -0.2675  -0.3954      False
RET_3M       0.0108   0.0149          2         1   -0.5988  -0.7384      False
ROE          0.0099   0.0137          3         3    0.2569   0.2012      False
RET_1M       0.0076   0.0115          4         5   -0.5799  -0.6078      False
OPM          0.0071   0.0123          5         4    0.4671   0.7789      False
OP_GROWTH    0.0052   0.0051          6         9    0.3436   0.6214      False
ROA          0.0044   0.0044          7        13    0.2319   0.2542      False
PBR          0.0036   0.0115          8         6    0.0115   0.4310      False

[TERM_SPREAD high vs low] rank corr=0.926, permutation p=0.2934, months high/low=36/36, sign flips=2/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0183   0.0159          1         1   -0.3616  -0.3297      False
RET_3M       0.0161   0.0103          2         2   -0.7165  -0.6463      False
ROE          0.0159   0.0082          3         3    0.2271   0.2434      False
OPM          0.0145   0.0056          4         5    0.7833   0.5234      False
RET_1M       0.0131   0.0066          5         4   -0.6628  -0.4945      False
PBR          0.0116   0.0047          6         6    0.3737   0.1746      False
RET_12M      0.0089   0.0031          7         9   -0.5047  -0.2975      False
OP_GROWTH    0.0070   0.0033          8         8    0.6000   0.4272      False

[CPI_YOY high vs low] rank corr=0.615, permutation p=0.0020, months high/low=36/36, sign flips=5/17
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D       0.0062   0.0281          1         1   -0.4099  -0.3374      False
ROE           0.0045   0.0196          2         3    0.2807   0.2266      False
RET_3M        0.0038   0.0225          3         2   -0.6344  -0.7454      False
DEBT_RATIO    0.0035   0.0053          4        15   -0.5738  -0.2623      False
OPM           0.0031   0.0170          5         5    0.5535   0.7901      False
RET_1M        0.0016   0.0181          6         4   -0.3470  -0.7519      False
ROA           0.0015   0.0073          7        12    0.3183   0.2428      False
PBR           0.0014   0.0148          8         6    0.1967   0.4051      False

Top macro x firm interactions (mean|phi_ij|*2):
                        value
CPI_YOY     PBR        0.0099
KRWUSD      GPOA       0.0069
CPI_YOY     RET_12M    0.0056
            RET_3M     0.0049
TERM_SPREAD RET_3M     0.0044
KRWUSD      OP_GROWTH  0.0042
CPI_YOY     DEBT_RATIO 0.0038
VKOSPI      RET_1M     0.0037

```