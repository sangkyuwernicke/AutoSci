# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
               model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0           catboost  firm      0.5371       0.5514  0.4741     0.4833     0.4503 0.0387  0.3100 -0.2210         0.4792    0.2577
1           catboost  full      0.4951       0.5482  0.4641     0.4793     0.4503 0.0496  0.3698 -0.2454         0.5000    0.3091
2               lgbm  firm      0.5316       0.5500  0.4690     0.4834     0.4503 0.0437  0.3385 -0.2328         0.4792    0.2615
3               lgbm  full      0.4800       0.5429  0.4279     0.4789     0.4503 0.0418  0.3213 -0.2635         0.5208    0.3644
4              logit  firm      0.5342       0.5474  0.4733     0.4898     0.4503 0.0700  0.4788 -0.2144         0.5000    0.2233
5              logit  full      0.5199       0.5237  0.4512     0.4745     0.4503 0.0556  0.4081 -0.2254         0.5000    0.1312
6             MARKET     -         NaN          NaN     NaN        NaN        NaN 0.0900  0.4946 -0.2190            NaN       NaN
7        EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.0220  0.2132 -0.2401         0.4583       NaN
8  KOSPI200_OFFICIAL     -         NaN          NaN     NaN        NaN        NaN 0.1135  0.5708 -0.2304         0.4583       NaN
9     KOSPI200_PROXY     -         NaN          NaN     NaN        NaN        NaN 0.0975  0.5038 -0.1984         0.5208       NaN
```

## Resolving power
48 test months x ~655 stocks, positive rate 0.45: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.009 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base market=KOSPI top_n_mcap=0

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.02369 -2.79942  0.99630     0.99724        48    -0.04043    -0.00869 0.99940 1.00000
1     logit  prec_k   -0.01531 -3.01295  0.99792     0.99505        48    -0.02573    -0.00583 0.99960 1.00000
2      lgbm     auc   -0.00703 -1.28610  0.89765     0.63327        48    -0.01635     0.00123 0.94940 1.00000
3      lgbm  prec_k   -0.00458 -0.96548  0.83038     0.66312        48    -0.01385     0.00479 0.83040 1.00000
4  catboost     auc   -0.00313 -0.57448  0.71581     0.59043        48    -0.01468     0.00765 0.70640 1.00000
5  catboost  prec_k   -0.00406 -0.71255  0.76018     0.75276        48    -0.01615     0.00781 0.73780 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.3213    0.4081 -0.0868 -0.2813 0.1410       0.7736        48
1  catboost  logit    0.3698    0.4081 -0.0382 -0.2841 0.2028       0.6182        48
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
VKOSPI              0.4024
KRWUSD              0.1588
BASE_RATE           0.1187
TERM_SPREAD         0.1033
CPI_YOY             0.0996
VOL_20D             0.0313
RET_3M              0.0268
OPM                 0.0211
RET_1M              0.0208
PER                 0.0206

[BASE_RATE high vs low] rank corr=0.664, permutation p=0.0020, months high/low=24/24, sign flips=5/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
PER        0.0230   0.0178          1         8    0.7942   0.5520      False
VOL_20D    0.0216   0.0402          2         1   -0.2489  -0.5607      False
RET_1M     0.0185   0.0231          3         5   -0.4687  -0.5293      False
RET_3M     0.0156   0.0380          4         2   -0.7263  -0.7734      False
OPM        0.0119   0.0304          5         3    0.3979   0.8726      False
PCR        0.0110   0.0267          6         4    0.7894   0.8927      False
PBR        0.0084   0.0170          7         9    0.7879   0.5522      False
RET_12M    0.0012   0.0163          8        10    0.2653  -0.3407       True

[TERM_SPREAD high vs low] rank corr=0.885, permutation p=0.0060, months high/low=24/24, sign flips=3/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0434   0.0185          1         4   -0.5025  -0.3289      False
RET_3M       0.0333   0.0203          2         2   -0.7527  -0.7172      False
OPM          0.0258   0.0165          3         5    0.8080   0.5121      False
PCR          0.0237   0.0140          4         6    0.8748   0.8003      False
PER          0.0218   0.0190          5         3    0.6715   0.7554      False
RET_1M       0.0213   0.0204          6         1   -0.5061  -0.5118      False
OP_GROWTH    0.0185   0.0029          7        12    0.8041   0.6472      False
GPOA         0.0143   0.0060          8         8   -0.6189  -0.4571      False

[CPI_YOY high vs low] rank corr=0.711, permutation p=0.0020, months high/low=24/24, sign flips=3/17
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M        0.0264   0.0272          1         2   -0.7372  -0.7251      False
RET_1M        0.0245   0.0172          2         6   -0.5745  -0.4357      False
OPM           0.0229   0.0194          3         5    0.6531   0.6916      False
PCR           0.0177   0.0200          4         4    0.8105   0.8559      False
PBR           0.0157   0.0097          5         8    0.7197   0.4542      False
PER           0.0148   0.0260          6         3    0.6198   0.7551      False
GPOA          0.0124   0.0080          7        11   -0.6680  -0.4032      False
DEBT_RATIO    0.0113   0.0046          8        14   -0.7357  -0.3266      False

Top macro x firm interactions (mean|phi_ij|*2):
                     value
VKOSPI      PBR     0.0150
KRWUSD      GPOA    0.0144
CPI_YOY     PBR     0.0120
            PCR     0.0099
VKOSPI      OPM     0.0095
KRWUSD      VOL_20D 0.0093
TERM_SPREAD PBR     0.0077
VKOSPI      PCR     0.0077

```