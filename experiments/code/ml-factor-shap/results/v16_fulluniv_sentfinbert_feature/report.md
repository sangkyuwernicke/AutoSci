# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                   model        fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0               catboost   Firm-only      0.4980       0.5487  0.4740     0.4944     0.4638 0.1021  0.5419 -0.3026         0.5000     0.0013    0.4097    0.4447
1               catboost  Firm+Macro      0.4939       0.5518  0.4732     0.4980     0.4638 0.1100  0.5683 -0.3068         0.5139     0.0020    0.6682    0.4732
2                   lgbm   Firm-only      0.4836       0.5473  0.4636     0.4931     0.4638 0.1158  0.5936 -0.3017         0.5417     0.0024    0.7123    0.4761
3                   lgbm  Firm+Macro      0.4860       0.5415  0.4470     0.4872     0.4638 0.0905  0.4889 -0.3221         0.5139     0.0005    0.1595    0.4562
4                  logit   Firm-only      0.5280       0.5490  0.4806     0.4972     0.4638 0.1138  0.5973 -0.2708         0.5000     0.0021    0.6763    0.2863
5                  logit  Firm+Macro      0.5137       0.5489  0.4716     0.4970     0.4638 0.1127  0.5927 -0.2727         0.5000     0.0020    0.6482    0.2860
6                 MARKET           -         NaN          NaN     NaN        NaN        NaN 0.1149  0.6105 -0.3459         0.5139     0.0021    0.5996       NaN
7            EW_UNIVERSE           -         NaN          NaN     NaN        NaN        NaN 0.0903  0.5188 -0.2965         0.5000     0.0001    0.0482       NaN
8      KOSPI200_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.1283  0.6487 -0.3589         0.5556     0.0032    0.7726       NaN
9   KOSPI200_EW_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.0904  0.5300 -0.3155         0.0000     0.0000       NaN       NaN
10        KOSPI200_PROXY           -         NaN          NaN     NaN        NaN        NaN 0.1233  0.6188 -0.3377         0.4722     0.0029    0.7039       NaN
```

fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in metrics.csv).

## Resolving power
72 test months x ~646 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.008 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base sentiment=finbert market=KOSPI top_n_mcap=0

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.00008 -1.35512  0.91016     0.58993        72    -0.00021     0.00001 0.92860 1.00000
1     logit  prec_k   -0.00014 -0.53185  0.70176     0.69612        72    -0.00063     0.00035 0.78840 1.00000
2      lgbm     auc   -0.00581 -1.21423  0.88566     0.94697        72    -0.01568     0.00387 0.88380 1.00000
3      lgbm  prec_k   -0.00590 -1.00523  0.84090     0.87283        72    -0.01799     0.00625 0.83380 1.00000
4  catboost     auc    0.00306  0.60780  0.27263     0.25393        72    -0.00674     0.01337 0.28100 1.00000
5  catboost  prec_k    0.00354  0.62793  0.26603     0.19106        72    -0.00660     0.01514 0.27320 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    0.4889    0.5927 -0.1038 -0.2431 0.0177       0.9530        72
1  catboost  logit    0.5683    0.5927 -0.0244 -0.1596 0.1218       0.6588        72
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
               mean_abs_shap
VKOSPI                0.2345
CPI_YOY               0.2331
KRWUSD                0.1767
TERM_SPREAD           0.1672
BASE_RATE             0.0828
NEWS_COUNT_1M         0.0584
VOL_20D               0.0358
RET_3M                0.0336
RET_1M                0.0266
PBR                   0.0239

[BASE_RATE high vs low] rank corr=0.943, permutation p=0.0010, months high/low=31/41, sign flips=5/23
               imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
NEWS_COUNT_1M    0.0558   0.0607          1         1    0.6982  -0.0934       True
VOL_20D          0.0381   0.0337          2         3   -0.3853  -0.4774      False
RET_1M           0.0308   0.0235          3         5   -0.7594  -0.7736      False
RET_3M           0.0297   0.0369          4         2   -0.6910  -0.7747      False
ROE              0.0222   0.0228          5         6    0.3597   0.0973      False
OPM              0.0168   0.0194          6         8    0.6528   0.5060      False
PBR              0.0141   0.0317          7         4    0.8302   0.1892      False
PCR              0.0099   0.0155          8        11    0.7796   0.6916      False

[TERM_SPREAD high vs low] rank corr=0.976, permutation p=0.0210, months high/low=36/36, sign flips=6/23
               imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
NEWS_COUNT_1M    0.0565   0.0606          1         1   -0.0904   0.6020       True
RET_3M           0.0358   0.0318          2         3   -0.7663  -0.7185      False
VOL_20D          0.0339   0.0374          3         2   -0.4628  -0.4109      False
PBR              0.0295   0.0187          4         6    0.3326   0.5616      False
RET_1M           0.0232   0.0301          5         4   -0.7737  -0.7636      False
ROE              0.0227   0.0224          6         5   -0.0167   0.4320       True
OPM              0.0187   0.0178          7         7    0.5033   0.6241      False
RET_12M          0.0176   0.0120          8         9   -0.6024  -0.6252      False

[CPI_YOY high vs low] rank corr=0.940, permutation p=0.0005, months high/low=36/36, sign flips=5/23
               imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
NEWS_COUNT_1M    0.0759   0.0413          1         1    0.5539  -0.0850       True
VOL_20D          0.0442   0.0270          2         2   -0.4894  -0.3879      False
RET_3M           0.0408   0.0268          3         3   -0.7748  -0.7537      False
RET_1M           0.0337   0.0196          4         5   -0.7871  -0.7610      False
PBR              0.0325   0.0158          5         6    0.2646   0.6160      False
OPM              0.0249   0.0116          6         7    0.6565   0.4473      False
ROE              0.0247   0.0204          7         4    0.2246   0.1785      False
RET_12M          0.0218   0.0079          8        11   -0.6477  -0.5677      False

Top macro x firm interactions (mean|phi_ij|*2):
                           value
CPI_YOY     NEWS_COUNT_1M 0.0415
KRWUSD      NEWS_COUNT_1M 0.0276
CPI_YOY     PBR           0.0230
TERM_SPREAD PBR           0.0193
VKOSPI      NEWS_COUNT_1M 0.0139
KRWUSD      RET_12M       0.0110
            RET_1M        0.0101
TERM_SPREAD NEWS_COUNT_1M 0.0097

```