# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                   model        fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0               catboost   Firm-only      0.5307       0.5451  0.4771     0.4875     0.4594 0.0583  0.3616 -0.3704         0.5472     0.0013    0.4461    0.3707
1               catboost  Firm+Macro      0.4871       0.5426  0.4520     0.4886     0.4594 0.0577  0.3593 -0.3808         0.5472     0.0013    0.4177    0.3678
2                   lgbm   Firm-only      0.5281       0.5436  0.4721     0.4869     0.4594 0.0556  0.3508 -0.3801         0.5660     0.0011    0.3711    0.3793
3                   lgbm  Firm+Macro      0.4986       0.5307  0.4488     0.4781     0.4594 0.0311  0.2499 -0.3822         0.5189    -0.0009   -0.3280    0.3810
4                  logit   Firm-only      0.5246       0.5375  0.4717     0.4847     0.4594 0.0548  0.3489 -0.4205         0.5000     0.0010    0.3379    0.2920
5                  logit  Firm+Macro      0.5060       0.5375  0.4637     0.4845     0.4594 0.0546  0.3476 -0.4201         0.5000     0.0010    0.3404    0.2956
6                 MARKET           -         NaN          NaN     NaN        NaN        NaN 0.1012  0.4774 -0.3459         0.5377     0.0057    1.2550       NaN
7            EW_UNIVERSE           -         NaN          NaN     NaN        NaN        NaN 0.0462  0.3141 -0.3892         0.5283     0.0003    0.1144       NaN
8      KOSPI200_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.1223  0.5230 -0.3589         0.5755     0.0078    1.4154       NaN
9   KOSPI200_EW_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.0422  0.2942 -0.4382         0.0000     0.0000       NaN       NaN
10        KOSPI200_PROXY           -         NaN          NaN     NaN        NaN        NaN 0.1123  0.4963 -0.3425         0.5189     0.0070    1.3465       NaN
```

fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in metrics.csv).

## Resolving power
106 test months x ~635 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.002; AUC gaps below ~0.006 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base sentiment=none market=KOSPI top_n_mcap=0

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.00001 -0.06861  0.52728     0.80836       106    -0.00031     0.00037 0.57800 1.00000
1     logit  prec_k   -0.00014 -0.37059  0.64415     0.61537       106    -0.00113     0.00066 0.61480 1.00000
2      lgbm     auc   -0.01281 -2.66408  0.99553     0.98823       106    -0.02535    -0.00309 0.99820 1.00000
3      lgbm  prec_k   -0.00887 -2.35168  0.98972     0.97902       106    -0.01656    -0.00113 0.98780 1.00000
4  catboost     auc   -0.00249 -0.76376  0.77664     0.78786       106    -0.00843     0.00357 0.78780 1.00000
5  catboost  prec_k    0.00113  0.30482  0.38055     0.49726       106    -0.00599     0.00887 0.38280 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.2499    0.3476 -0.0977 -0.2086 0.0307       0.9288       106
1  catboost  logit    0.3593    0.3476  0.0117 -0.0996 0.1382       0.4090       106
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
VKOSPI              0.3047
KRWUSD              0.1833
CPI_YOY             0.1739
TERM_SPREAD         0.1695
BASE_RATE           0.0707
VOL_20D             0.0364
RET_3M              0.0307
RET_1M              0.0242
ROE                 0.0234
OPM                 0.0214

[BASE_RATE high vs low] rank corr=0.667, permutation p=0.0020, months high/low=50/56, sign flips=6/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0324   0.0409          1         2   -0.4482  -0.3881      False
RET_3M       0.0178   0.0441          2         1   -0.6846  -0.7022      False
PBR          0.0174   0.0250          3         9    0.5462   0.4680      False
ROE          0.0160   0.0310          4         5    0.3830  -0.1708       True
OPM          0.0139   0.0291          5         6    0.5339   0.6256      False
RET_1M       0.0103   0.0383          6         3   -0.5703  -0.7731      False
OP_GROWTH    0.0096   0.0216          7        11    0.6060   0.6158      False
ROA          0.0063   0.0142          8        15    0.4103  -0.0756       True

[TERM_SPREAD high vs low] rank corr=0.868, permutation p=0.0020, months high/low=53/53, sign flips=3/17
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D         0.0471   0.0267          1         1   -0.5088  -0.3052      False
RET_3M          0.0381   0.0252          2         2   -0.6585  -0.7326      False
RET_1M          0.0289   0.0213          3         3   -0.7614  -0.6285      False
OPM             0.0289   0.0150          4         7    0.7035   0.4456      False
PBR             0.0273   0.0155          5         6    0.5984   0.3785      False
ROE             0.0271   0.0206          6         4    0.1203   0.0205      False
SALES_GROWTH    0.0257   0.0131          7        10    0.7170   0.3395      False
PCR             0.0173   0.0094          8        13    0.6676   0.3613      False

[CPI_YOY high vs low] rank corr=0.828, permutation p=0.0020, months high/low=53/53, sign flips=4/17
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D       0.0326   0.0412          1         1   -0.4511  -0.3808      False
RET_3M        0.0247   0.0387          2         2   -0.7130  -0.6795      False
PBR           0.0200   0.0228          3         7    0.3120   0.6952      False
ROE           0.0190   0.0288          4         4    0.2896  -0.1146       True
OPM           0.0165   0.0274          5         6    0.5654   0.6132      False
RET_1M        0.0156   0.0347          6         3   -0.6290  -0.7603      False
DEBT_RATIO    0.0142   0.0182          7        10   -0.5055  -0.0121      False
OP_GROWTH     0.0137   0.0181          8        11    0.5637   0.6392      False

Top macro x firm interactions (mean|phi_ij|*2):
                    value
VKOSPI  RET_3M     0.0226
CPI_YOY PBR        0.0178
KRWUSD  PBR        0.0128
        VOL_20D    0.0113
CPI_YOY DEBT_RATIO 0.0105
        RET_12M    0.0094
VKOSPI  PBR        0.0088
        RET_12M    0.0086

```