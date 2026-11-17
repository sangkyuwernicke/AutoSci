# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                   model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0               catboost  firm      0.5403       0.5539  0.4884     0.4944     0.4638 0.1002  0.5355 -0.3015         0.5000     0.0011    0.3522    0.3687
1               catboost  full      0.4806       0.5452  0.4629     0.4910     0.4638 0.0976  0.5209 -0.3432         0.4444     0.0010    0.3753    0.4216
2                   lgbm  firm      0.5294       0.5515  0.4823     0.4957     0.4638 0.1070  0.5604 -0.2896         0.5417     0.0017    0.5299    0.3738
3                   lgbm  full      0.4947       0.5448  0.4634     0.4924     0.4638 0.1038  0.5384 -0.3279         0.5000     0.0016    0.5042    0.4452
4                  logit  firm      0.5296       0.5497  0.4821     0.4982     0.4638 0.1098  0.5813 -0.2804         0.5000     0.0018    0.5825    0.2851
5                  logit  full      0.5120       0.5497  0.4707     0.4985     0.4638 0.1100  0.5820 -0.2804         0.5000     0.0018    0.5865    0.2849
6                 MARKET     -         NaN          NaN     NaN        NaN        NaN 0.1149  0.6105 -0.3459         0.5139     0.0021    0.5996       NaN
7            EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.0903  0.5184 -0.2968         0.5000     0.0001    0.0459       NaN
8      KOSPI200_OFFICIAL     -         NaN          NaN     NaN        NaN        NaN 0.1283  0.6487 -0.3589         0.5556     0.0032    0.7726       NaN
9   KOSPI200_EW_OFFICIAL     -         NaN          NaN     NaN        NaN        NaN 0.0904  0.5300 -0.3155         0.0000     0.0000       NaN       NaN
10        KOSPI200_PROXY     -         NaN          NaN     NaN        NaN        NaN 0.1229  0.6172 -0.3381         0.4861     0.0029    0.6941       NaN
```

## Resolving power
72 test months x ~647 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.008 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base market=KOSPI top_n_mcap=0

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc    0.00000  0.30679  0.37995     0.38810        72    -0.00002     0.00002 0.37200 1.00000
1     logit  prec_k    0.00028  2.04364  0.02235     0.02275        72     0.00007     0.00056 0.02040 0.13410
2      lgbm     auc   -0.00668 -1.64450  0.94775     0.96191        72    -0.01422     0.00053 0.96660 1.00000
3      lgbm  prec_k   -0.00326 -0.68236  0.75139     0.72868        72    -0.01347     0.00709 0.74320 1.00000
4  catboost     auc   -0.00871 -1.99496  0.97506     0.97861        72    -0.01830     0.00089 0.96440 1.00000
5  catboost  prec_k   -0.00347 -0.60563  0.72665     0.77986        72    -0.01569     0.00882 0.72580 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.5384    0.5820 -0.0436 -0.1748 0.0898       0.7422        72
1  catboost  logit    0.5209    0.5820 -0.0611 -0.2133 0.0923       0.8026        72
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
KRWUSD              0.2199
VKOSPI              0.2056
TERM_SPREAD         0.2056
CPI_YOY             0.1767
BASE_RATE           0.0644
VOL_20D             0.0276
RET_3M              0.0193
RET_1M              0.0153
ROE                 0.0152
OPM                 0.0149

[BASE_RATE high vs low] rank corr=0.914, permutation p=0.0080, months high/low=31/41, sign flips=3/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0318   0.0237          1         1   -0.3994  -0.3215      False
RET_3M       0.0171   0.0207          2         2   -0.7159  -0.6673      False
ROE          0.0141   0.0157          3         5    0.3535   0.2698      False
RET_1M       0.0118   0.0178          4         3   -0.7182  -0.7247      False
OPM          0.0115   0.0171          5         4    0.5722   0.5336      False
PBR          0.0067   0.0132          6         7    0.6103   0.1723      False
OP_GROWTH    0.0063   0.0141          7         6    0.5692   0.5447      False
ROA          0.0055   0.0060          8        14    0.4427   0.4405      False

[TERM_SPREAD high vs low] rank corr=0.949, permutation p=0.1058, months high/low=36/36, sign flips=3/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0246   0.0298          1         1   -0.2957  -0.4196      False
RET_3M          0.0184   0.0199          2         2   -0.6527  -0.7090      False
OPM             0.0162   0.0132          3         5    0.5468   0.5567      False
RET_1M          0.0154   0.0151          4         4   -0.7025  -0.7431      False
ROE             0.0134   0.0167          5         3    0.2064   0.4061      False
OP_GROWTH       0.0127   0.0088          6         7    0.5489   0.5699      False
PBR             0.0108   0.0100          7         6    0.3648   0.3476      False
SALES_GROWTH    0.0099   0.0073          8         9    0.7539   0.4174      False

[CPI_YOY high vs low] rank corr=0.853, permutation p=0.0020, months high/low=36/36, sign flips=4/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0303   0.0241          1         1   -0.4471  -0.2928      False
RET_3M       0.0243   0.0140          2         2   -0.6857  -0.6938      False
ROE          0.0185   0.0116          3         5    0.3324   0.2826      False
RET_1M       0.0176   0.0128          4         4   -0.7532  -0.6790      False
OPM          0.0161   0.0132          5         3    0.5444   0.5491      False
PBR          0.0136   0.0072          6         7    0.0770   0.6347      False
OP_GROWTH    0.0135   0.0079          7         6    0.5427   0.5704      False
RET_12M      0.0128   0.0037          8        12   -0.5756   0.3688       True

Top macro x firm interactions (mean|phi_ij|*2):
                        value
CPI_YOY     PBR        0.0120
            DEBT_RATIO 0.0086
TERM_SPREAD PBR        0.0078
KRWUSD      DEBT_RATIO 0.0068
CPI_YOY     OPM        0.0066
KRWUSD      VOL_20D    0.0064
            RET_1M     0.0055
TERM_SPREAD ROE        0.0053

```