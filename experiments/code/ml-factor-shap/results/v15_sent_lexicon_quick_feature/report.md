# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                   model        fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0               catboost   Firm-only      0.5131       0.5070  0.5212     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
1               catboost  Firm+Macro      0.4629       0.4904  0.4785     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
2                  dtree   Firm-only      0.5011       0.5117  0.4995     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
3                  dtree  Firm+Macro      0.5129       0.5016  0.5031     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
4                   lgbm   Firm-only      0.5012       0.5048  0.5145     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
5                   lgbm  Firm+Macro      0.4448       0.5146  0.4621     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
6                  logit   Firm-only      0.4751       0.5060  0.4787     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
7                  logit  Firm+Macro      0.4949       0.5060  0.4979     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
8                     rf   Firm-only      0.5036       0.5118  0.5016     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
9                     rf  Firm+Macro      0.4707       0.5141  0.4761     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
10                 ridge   Firm-only      0.4973       0.5169  0.5252     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
11                 ridge  Firm+Macro      0.4787       0.5169  0.4994     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
12                   xgb   Firm-only      0.5097       0.4989  0.5003     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
13                   xgb  Firm+Macro      0.4422       0.4934  0.4610     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
14                MARKET           -         NaN          NaN     NaN        NaN        NaN 0.2346  1.1450 -0.1455         0.5833     0.0058    1.1032       NaN
15           EW_UNIVERSE           -         NaN          NaN     NaN        NaN        NaN 0.2059  1.0792 -0.1500         0.5833     0.0037    1.1719       NaN
16     KOSPI200_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.2768  1.2236 -0.1724         0.6389     0.0090    1.3818       NaN
17  KOSPI200_EW_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.1617  1.0836 -0.0982         0.0000     0.0000       NaN       NaN
18        KOSPI200_PROXY           -         NaN          NaN     NaN        NaN        NaN 0.2514  1.0575 -0.1701         0.5556     0.0076    1.0420       NaN
```

fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in metrics.csv).

## Resolving power
36 test months x ~91 stocks, positive rate 0.50: the mean monthly AUC of a model with no skill has s.e. ~0.010; AUC gaps below ~0.028 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=False macro_mode=raw macro_role=feature factor_set=base sentiment=lexicon market=KOSPI top_n_mcap=100

## H1: full (firm+macro) minus firm-only, paired by month
```
       model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0      logit     auc    0.00001  0.41810  0.33922     0.32736        36    -0.00004     0.00008 0.45380 1.00000
1      logit  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
2      ridge     auc    0.00003  0.20729  0.41849     0.19400        36    -0.00018     0.00026 0.39100 1.00000
3      ridge  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
4      dtree     auc   -0.01013 -0.88587  0.80913     0.64238        36    -0.03063     0.00902 0.84480 1.00000
5      dtree  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
6         rf     auc    0.00232  0.54952  0.29307     0.23013        36    -0.00504     0.00999 0.27740 1.00000
7         rf  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
8        xgb     auc   -0.00549 -0.43597  0.66723     0.59505        36    -0.03263     0.02007 0.64320 1.00000
9        xgb  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
10      lgbm     auc    0.00979  1.07974  0.14382     0.15001        36    -0.00428     0.02504 0.09060 1.00000
11      lgbm  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
12  catboost     auc   -0.01665 -0.94505  0.82444     0.73033        36    -0.05096     0.01704 0.82080 1.00000
13  catboost  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b   diff   ci_lo  ci_hi  p_one_sided  n_months
0        rf  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.6966        36
1       xgb  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.6276        36
2      lgbm  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.7988        36
3  catboost  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.8108        36
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
              mean_abs_shap
KRWUSD               0.2876
VKOSPI               0.1790
CPI_YOY              0.1402
BASE_RATE            0.0902
TERM_SPREAD          0.0862
RET_3M               0.0648
SENT_MEAN_3M         0.0606
RET_1M               0.0588
GPOA                 0.0406
VOL_20D              0.0350

[BASE_RATE high vs low] rank corr=0.610, permutation p=0.0020, months high/low=21/15, sign flips=11/23
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M          0.0565   0.0758          1         1   -0.9571  -0.9394      False
SENT_MEAN_3M    0.0509   0.0743          2         2   -0.8132  -0.7646      False
RET_1M          0.0498   0.0710          3         3   -0.8984  -0.9057      False
PBR             0.0337   0.0174          4        16    0.8808  -0.1338       True
GPOA            0.0286   0.0575          5         4   -0.8628  -0.8767      False
VOL_20D         0.0212   0.0544          6         5   -0.7952  -0.7515      False
RET_12M         0.0184   0.0239          7        12   -0.8345  -0.4903      False
OPM             0.0177   0.0224          8        13   -0.7643   0.5718       True

[TERM_SPREAD high vs low] rank corr=0.694, permutation p=0.0020, months high/low=18/18, sign flips=9/23
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
SENT_MEAN_3M    0.0722   0.0491          1         3   -0.7702  -0.8084      False
RET_3M          0.0696   0.0596          2         1   -0.9281  -0.9559      False
RET_1M          0.0656   0.0517          3         2   -0.8898  -0.9025      False
GPOA            0.0553   0.0260          4         5   -0.8805  -0.8561      False
VOL_20D         0.0506   0.0194          5         6   -0.7647  -0.7929      False
PER             0.0399   0.0115          6        11    0.5831   0.1446      False
EV_EBITDA       0.0330   0.0023          7        20   -0.6287   0.4675       True
DEBT_RATIO      0.0289   0.0037          8        18    0.2364   0.1994      False

[CPI_YOY high vs low] rank corr=0.692, permutation p=0.0020, months high/low=18/18, sign flips=9/23
              imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M          0.0620   0.0672          1         2   -0.9570  -0.9212      False
RET_1M          0.0542   0.0631          2         3   -0.9043  -0.8799      False
SENT_MEAN_3M    0.0478   0.0735          3         1   -0.8160  -0.7702      False
PBR             0.0331   0.0208          4        13    0.8843   0.1207      False
GPOA            0.0252   0.0562          5         4   -0.8529  -0.8863      False
VOL_20D         0.0191   0.0510          6         5   -0.7907  -0.7665      False
RET_12M         0.0178   0.0236          7        10   -0.8231  -0.5412      False
ROA             0.0167   0.0153          8        16   -0.7885  -0.6447      False

Top macro x firm interactions (mean|phi_ij|*2):
                     value
TERM_SPREAD RET_1M  0.0240
CPI_YOY     OPM     0.0203
VKOSPI      ROA     0.0177
BASE_RATE   RET_1M  0.0134
KRWUSD      VOL_20D 0.0124
TERM_SPREAD VOL_20D 0.0117
VKOSPI      PBR     0.0112
            PER     0.0099

```