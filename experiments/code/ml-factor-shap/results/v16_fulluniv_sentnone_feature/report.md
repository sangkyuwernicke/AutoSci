# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None
primary benchmark = KOSPI200_EW_OFFICIAL (WinRate_vs_bm, Excess_mo [mean monthly excess] and t_excess are measured against it)

## Prediction + backtest (net of costs)
```
                   model        fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Excess_mo  t_excess  Turnover
0               catboost   Firm-only      0.5346       0.5535  0.4801     0.4959     0.4638 0.1005  0.5357 -0.3022         0.5139     0.0012    0.3762    0.3746
1               catboost  Firm+Macro      0.4757       0.5496  0.4473     0.4950     0.4638 0.0862  0.4759 -0.3359         0.4583     0.0001    0.0396    0.3937
2                   lgbm   Firm-only      0.5282       0.5521  0.4796     0.4964     0.4638 0.0982  0.5275 -0.3018         0.5417     0.0010    0.3160    0.3798
3                   lgbm  Firm+Macro      0.4880       0.5365  0.4637     0.4844     0.4638 0.0771  0.4481 -0.3299         0.5000    -0.0007   -0.2188    0.4127
4                  logit   Firm-only      0.5296       0.5496  0.4819     0.4974     0.4638 0.1073  0.5703 -0.2854         0.5000     0.0016    0.5234    0.2860
5                  logit  Firm+Macro      0.5120       0.5496  0.4707     0.4976     0.4638 0.1079  0.5728 -0.2848         0.5000     0.0017    0.5391    0.2859
6                 MARKET           -         NaN          NaN     NaN        NaN        NaN 0.1149  0.6105 -0.3459         0.5139     0.0021    0.5996       NaN
7            EW_UNIVERSE           -         NaN          NaN     NaN        NaN        NaN 0.0903  0.5188 -0.2965         0.5000     0.0001    0.0482       NaN
8      KOSPI200_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.1283  0.6487 -0.3589         0.5556     0.0032    0.7726       NaN
9   KOSPI200_EW_OFFICIAL           -         NaN          NaN     NaN        NaN        NaN 0.0904  0.5300 -0.3155         0.0000     0.0000       NaN       NaN
10        KOSPI200_PROXY           -         NaN          NaN     NaN        NaN        NaN 0.1233  0.6188 -0.3377         0.4722     0.0029    0.7039       NaN
```

fset: Firm-only = firm characteristics only; Firm+Macro = firm characteristics and macro variables as direct inputs; Firm+Macro (gating) = macro variables only set the factor weights (stored as firm / full / gated in metrics.csv).

## Resolving power
72 test months x ~646 stocks, positive rate 0.46: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.008 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=feature factor_set=base sentiment=none market=KOSPI top_n_mcap=0

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.00006 -1.29720  0.90062     0.80221        72    -0.00016     0.00002 0.90800 1.00000
1     logit  prec_k    0.00028  1.27029  0.10406     0.14596        72    -0.00007     0.00069 0.11300 0.62439
2      lgbm     auc   -0.01554 -2.41936  0.99094     0.98133        72    -0.03346    -0.00246 0.99060 1.00000
3      lgbm  prec_k   -0.01194 -2.51094  0.99284     0.99207        72    -0.02222    -0.00160 0.98840 1.00000
4  catboost     auc   -0.00388 -0.93439  0.82336     0.73516        72    -0.01305     0.00496 0.80620 1.00000
5  catboost  prec_k   -0.00090 -0.19658  0.57764     0.64195        72    -0.01090     0.00917 0.57860 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo   ci_hi  p_one_sided  n_months
0      lgbm  logit    0.4481    0.5728 -0.1247 -0.2332 -0.0106       0.9832        72
1  catboost  logit    0.4759    0.5728 -0.0968 -0.2056  0.0020       0.9728        72
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
             mean_abs_shap
CPI_YOY             0.1815
TERM_SPREAD         0.1798
VKOSPI              0.1793
KRWUSD              0.1487
BASE_RATE           0.0513
VOL_20D             0.0194
RET_3M              0.0146
ROE                 0.0139
PBR                 0.0124
RET_1M              0.0116

[BASE_RATE high vs low] rank corr=0.811, permutation p=0.0045, months high/low=31/41, sign flips=2/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0158   0.0218          1         1   -0.4015  -0.4353      False
ROE          0.0081   0.0181          2         4    0.3295   0.2069      False
RET_3M       0.0068   0.0206          3         2   -0.6750  -0.7125      False
RET_1M       0.0051   0.0166          4         6   -0.4866  -0.7548      False
OPM          0.0041   0.0125          5         9    0.5121   0.6386      False
OP_GROWTH    0.0039   0.0144          6         7    0.3988   0.6119      False
PBR          0.0035   0.0193          7         3    0.4725   0.3119      False
PCR          0.0023   0.0083          8        12    0.4058   0.5157      False

[TERM_SPREAD high vs low] rank corr=0.951, permutation p=0.2619, months high/low=36/36, sign flips=2/17
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D       0.0214   0.0171          1         1   -0.4249  -0.4201      False
ROE           0.0171   0.0106          2         3    0.1834   0.3124      False
PBR           0.0151   0.0100          3         4    0.4638   0.2707      False
RET_3M        0.0149   0.0144          4         2   -0.7042  -0.6879      False
RET_1M        0.0137   0.0096          5         5   -0.7661  -0.5302      False
DEBT_RATIO    0.0125   0.0085          6         7   -0.5701  -0.3813      False
RET_12M       0.0115   0.0057          7         9   -0.2378   0.0085       True
OP_GROWTH     0.0111   0.0087          8         6    0.6085   0.4216      False

[CPI_YOY high vs low] rank corr=0.620, permutation p=0.0010, months high/low=36/36, sign flips=4/17
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D       0.0208   0.0177          1         1   -0.4268  -0.4050      False
RET_3M        0.0202   0.0091          2         5   -0.6951  -0.7083      False
DEBT_RATIO    0.0200   0.0010          3        16   -0.5058  -0.4588      False
PBR           0.0157   0.0094          4         4    0.0204   0.7622      False
OP_GROWTH     0.0150   0.0048          5         8    0.4263   0.6320      False
ROE           0.0138   0.0139          6         2    0.1587   0.3594      False
RET_1M        0.0123   0.0109          7         3   -0.6082  -0.7491      False
OPM           0.0108   0.0070          8         7    0.5319   0.6568      False

Top macro x firm interactions (mean|phi_ij|*2):
                        value
CPI_YOY     PBR        0.0172
            DEBT_RATIO 0.0105
KRWUSD      RET_12M    0.0067
TERM_SPREAD PBR        0.0066
CPI_YOY     RET_12M    0.0064
TERM_SPREAD RET_3M     0.0055
CPI_YOY     RET_3M     0.0051
VKOSPI      PBR        0.0048

```