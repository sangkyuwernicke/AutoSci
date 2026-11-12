# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                   model        fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0               catboost   Firm-only      0.4868       0.5013  0.4996     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
1               catboost  Firm+Macro      0.4470       0.5031  0.4619     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
2                  dtree   Firm-only      0.4910       0.5014  0.4884     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
3                  dtree  Firm+Macro      0.4798       0.5009  0.4968     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
4                   lgbm   Firm-only      0.4965       0.5129  0.4982     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
5                   lgbm  Firm+Macro      0.4336       0.5057  0.4607     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
6                  logit   Firm-only      0.4786       0.5062  0.4883     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
7                  logit  Firm+Macro      0.4984       0.5062  0.5016     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
8                     rf   Firm-only      0.4932       0.5091  0.4888     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
9                     rf  Firm+Macro      0.4738       0.5086  0.4727     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
10                 ridge   Firm-only      0.5029       0.5152  0.5266     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
11                 ridge  Firm+Macro      0.4871       0.5152  0.5039     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
12                   xgb   Firm-only      0.4883       0.4966  0.5041     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
13                   xgb  Firm+Macro      0.4388       0.4787  0.4576     0.5027     0.5027 0.2031  1.0671 -0.1505         0.5556     0.0035    1.1055    0.0382
14                MARKET           -         NaN          NaN     NaN        NaN        NaN 0.2346  1.1450 -0.1455         0.5833     0.0058    1.1032       NaN
15           EW_UNIVERSE           -         NaN          NaN     NaN        NaN        NaN 0.2059  1.0792 -0.1500         0.5833     0.0037    1.1719       NaN
16     KOSPI200_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.2768  1.2236 -0.1724         0.6389     0.0090    1.3818       NaN
17  KOSPI200_EW_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.1617  1.0836 -0.0982         0.0000     0.0000       NaN       NaN
18        KOSPI200_PROXY           -         NaN          NaN     NaN        NaN        NaN 0.2514  1.0575 -0.1701         0.5556     0.0076    1.0420       NaN
```

fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in metrics.csv).

## Resolving power
36 test months x ~91 stocks, positive rate 0.50: the mean monthly AUC of a model with no skill has s.e. ~0.010; AUC gaps below ~0.028 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=False macro_mode=raw macro_role=feature factor_set=base sentiment=none market=KOSPI top_n_mcap=100

## H1: full (firm+macro) minus firm-only, paired by month
```
       model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0      logit     auc   -0.00002 -1.00000  0.83791     0.84134        36    -0.00005     0.00000 1.00000 1.00000
1      logit  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
2      ridge     auc    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
3      ridge  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
4      dtree     auc   -0.00053 -0.05818  0.52303     0.39853        36    -0.01752     0.01374 0.49900 1.00000
5      dtree  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
6         rf     auc   -0.00051 -0.09439  0.53733     0.55860        36    -0.00859     0.00730 0.54380 1.00000
7         rf  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
8        xgb     auc   -0.01790 -1.61294  0.94213     0.90128        36    -0.04500     0.00655 0.91880 1.00000
9        xgb  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
10      lgbm     auc   -0.00719 -0.74593  0.76966     0.81042        36    -0.02572     0.01197 0.78500 1.00000
11      lgbm  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
12  catboost     auc    0.00175  0.18495  0.42717     0.38107        36    -0.01690     0.01999 0.41100 1.00000
13  catboost  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b   diff   ci_lo  ci_hi  p_one_sided  n_months
0        rf  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.6806        36
1       xgb  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.7990        36
2      lgbm  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.6134        36
3  catboost  logit    1.0671    1.0671 0.0000 -0.0000 0.0000       0.7322        36
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
KRWUSD              0.2080
VKOSPI              0.1974
CPI_YOY             0.1430
TERM_SPREAD         0.1053
RET_3M              0.0960
RET_1M              0.0611
BASE_RATE           0.0589
GPOA                0.0442
VOL_20D             0.0377
PCR                 0.0357

[BASE_RATE high vs low] rank corr=0.400, permutation p=0.0020, months high/low=21/15, sign flips=4/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M     0.0571   0.1498          1         1   -0.9518  -0.9342      False
RET_1M     0.0456   0.0822          2         2   -0.8188  -0.7615      False
GPOA       0.0300   0.0639          3         7   -0.8668  -0.7384      False
RET_12M    0.0257   0.0445          4        12   -0.8809  -0.1092      False
PBR        0.0251   0.0432          5        13    0.8227   0.2225      False
VOL_20D    0.0189   0.0641          6         6   -0.8058  -0.0622      False
PCR        0.0139   0.0661          7         5    0.8269   0.7490      False
ROA        0.0133   0.0431          8        14   -0.8037  -0.5693      False

[TERM_SPREAD high vs low] rank corr=0.532, permutation p=0.0020, months high/low=18/18, sign flips=4/17
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M        0.1312   0.0603          1         1   -0.9207  -0.9517      False
RET_1M        0.0739   0.0478          2         2   -0.7501  -0.8335      False
GPOA          0.0600   0.0283          3         3   -0.7575  -0.8658      False
OPM           0.0591   0.0085          4        10    0.3630  -0.7755       True
VOL_20D       0.0580   0.0173          5         6   -0.1545  -0.7961      False
PCR           0.0566   0.0147          6         8    0.7319   0.8256      False
DEBT_RATIO    0.0562   0.0031          7        15    0.3828   0.1272      False
EV_EBITDA     0.0494   0.0022          8        17   -0.6553  -0.6565      False

[CPI_YOY high vs low] rank corr=0.534, permutation p=0.0020, months high/low=18/18, sign flips=4/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M     0.0620   0.1294          1         1   -0.9559  -0.9145      False
RET_1M     0.0508   0.0709          2         2   -0.8488  -0.7342      False
GPOA       0.0284   0.0599          3         3   -0.8660  -0.7562      False
RET_12M    0.0254   0.0417          4        11   -0.8827  -0.2074      False
PBR        0.0242   0.0411          5        12    0.8034   0.3096      False
VOL_20D    0.0173   0.0581          6         5   -0.7911  -0.1567      False
ROA        0.0169   0.0345          7        14   -0.7930  -0.5420      False
PCR        0.0151   0.0562          8         6    0.8277   0.7285      False

Top macro x firm interactions (mean|phi_ij|*2):
                          value
CPI_YOY     OPM          0.0306
            RET_3M       0.0272
KRWUSD      VOL_20D      0.0259
TERM_SPREAD RET_1M       0.0257
KRWUSD      OP_GROWTH    0.0169
VKOSPI      ROA          0.0169
KRWUSD      SALES_GROWTH 0.0164
VKOSPI      PBR          0.0159

```