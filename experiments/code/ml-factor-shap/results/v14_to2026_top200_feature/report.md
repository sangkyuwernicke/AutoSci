# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                   model        fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0               catboost   Firm-only      0.5394       0.5570  0.4825     0.4917     0.4589 0.0806  0.4482 -0.2999         0.5366    -0.0005   -0.1339    0.3573
1               catboost  Firm+Macro      0.4835       0.5512  0.4702     0.4877     0.4589 0.0672  0.3926 -0.3415         0.5000    -0.0015   -0.4055    0.4106
2                   lgbm   Firm-only      0.5344       0.5539  0.4775     0.4921     0.4589 0.0757  0.4278 -0.3022         0.5366    -0.0008   -0.2205    0.3748
3                   lgbm  Firm+Macro      0.4864       0.5358  0.4500     0.4787     0.4589 0.0537  0.3433 -0.3321         0.4878    -0.0026   -0.7281    0.3959
4                  logit   Firm-only      0.5323       0.5504  0.4791     0.4926     0.4589 0.0898  0.4869 -0.2851         0.5000     0.0002    0.0581    0.2707
5                  logit  Firm+Macro      0.4988       0.5503  0.4617     0.4932     0.4589 0.0911  0.4928 -0.2848         0.5000     0.0003    0.0795    0.2657
6                 MARKET           -         NaN          NaN     NaN        NaN        NaN 0.1518  0.6071 -0.3459         0.5244     0.0065    1.1261       NaN
7            EW_UNIVERSE           -         NaN          NaN     NaN        NaN        NaN 0.0669  0.3974 -0.2965         0.5000    -0.0016   -0.5969       NaN
8      KOSPI200_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.1780  0.6490 -0.3589         0.5610     0.0090    1.2929       NaN
9   KOSPI200_EW_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.0849  0.4578 -0.3155         0.0000     0.0000       NaN       NaN
10        KOSPI200_PROXY           -         NaN          NaN     NaN        NaN        NaN 0.1640  0.6170 -0.3425         0.4878     0.0079    1.2064       NaN
```

fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in metrics.csv).

## Resolving power
82 test months x ~648 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.007 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base market=KOSPI top_n_mcap=0

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.00010 -0.38624  0.64984     0.84202        82    -0.00060     0.00028 0.63540 1.00000
1     logit  prec_k    0.00061  1.23485  0.11023     0.12075        82    -0.00043     0.00183 0.13000 0.66137
2      lgbm     auc   -0.01807 -3.24996  0.99916     0.99952        82    -0.03309    -0.00660 1.00000 1.00000
3      lgbm  prec_k   -0.01335 -3.25479  0.99917     0.99754        82    -0.02220    -0.00445 0.99820 1.00000
4  catboost     auc   -0.00586 -1.84402  0.96558     0.95830        82    -0.01196    -0.00016 0.97680 1.00000
5  catboost  prec_k   -0.00402 -1.07711  0.85768     0.86076        82    -0.01116     0.00299 0.86940 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo   ci_hi  p_one_sided  n_months
0      lgbm  logit    0.3433    0.4928 -0.1495 -0.2624 -0.0244       0.9904        82
1  catboost  logit    0.3926    0.4928 -0.1002 -0.2076  0.0017       0.9730        82
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
VKOSPI              0.2476
KRWUSD              0.1918
TERM_SPREAD         0.1617
CPI_YOY             0.1598
BASE_RATE           0.0513
VOL_20D             0.0239
PBR                 0.0198
ROE                 0.0162
RET_3M              0.0142
OPM                 0.0131

[BASE_RATE high vs low] rank corr=0.902, permutation p=0.0160, months high/low=33/49, sign flips=2/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0168   0.0282          1         1   -0.4176  -0.4605      False
ROE          0.0093   0.0207          2         3    0.3261   0.2799      False
PBR          0.0076   0.0279          3         2    0.4681   0.4337      False
RET_3M       0.0072   0.0191          4         4   -0.6667  -0.7337      False
OPM          0.0067   0.0173          5         5    0.5040   0.6084      False
RET_1M       0.0054   0.0160          6         6   -0.5234  -0.7607      False
OP_GROWTH    0.0036   0.0125          7         8    0.4245   0.6695      False
PCR          0.0027   0.0109          8        10    0.3745   0.5663      False

[TERM_SPREAD high vs low] rank corr=0.875, permutation p=0.0060, months high/low=41/41, sign flips=4/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
PBR        0.0280   0.0115          1         5    0.6402   0.2071      False
VOL_20D    0.0278   0.0194          2         1   -0.4541  -0.4312      False
ROE        0.0201   0.0121          3         3    0.2539   0.3202      False
OPM        0.0156   0.0105          4         7    0.5858   0.5660      False
RET_3M     0.0138   0.0148          5         2   -0.7288  -0.6885      False
RET_1M     0.0120   0.0115          6         4   -0.7726  -0.5802      False
PCR        0.0086   0.0066          7        11    0.5667   0.4045      False
RET_12M    0.0083   0.0073          8         9   -0.4688  -0.3919      False

[CPI_YOY high vs low] rank corr=0.674, permutation p=0.0020, months high/low=41/41, sign flips=4/17
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D       0.0253   0.0219          1         1   -0.4419  -0.4401      False
PBR           0.0223   0.0172          2         2    0.1808   0.7343      False
RET_3M        0.0184   0.0102          3         6   -0.7106  -0.7114      False
DEBT_RATIO    0.0172   0.0011          4        17   -0.5319  -0.2984      False
ROE           0.0166   0.0156          5         3    0.2554   0.3214      False
OPM           0.0144   0.0117          6         4    0.5224   0.6261      False
OP_GROWTH     0.0138   0.0041          7         8    0.5279   0.6447      False
RET_1M        0.0125   0.0110          8         5   -0.6417  -0.7608      False

Top macro x firm interactions (mean|phi_ij|*2):
                        value
CPI_YOY     PBR        0.0159
KRWUSD      PBR        0.0129
VKOSPI      PBR        0.0110
CPI_YOY     DEBT_RATIO 0.0084
KRWUSD      VOL_20D    0.0072
TERM_SPREAD PBR        0.0068
CPI_YOY     RET_12M    0.0054
TERM_SPREAD RET_3M     0.0051

```