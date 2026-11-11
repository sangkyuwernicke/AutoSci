# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
         model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost  firm      0.4847       0.4856  0.4521     0.4531     0.4548 0.1949  0.9228 -0.1520         0.3611    0.3972
1     catboost  full      0.4767       0.4843  0.4443     0.4605     0.4548 0.1861  0.8751 -0.2022         0.3889    0.4452
2         lgbm  firm      0.4838       0.4828  0.4531     0.4360     0.4548 0.1803  0.9143 -0.1574         0.3889    0.3540
3         lgbm  full      0.4704       0.4841  0.4413     0.4624     0.4548 0.2082  1.0045 -0.1789         0.5000    0.4168
4        logit  firm      0.4947       0.4966  0.4555     0.4621     0.4548 0.2321  0.9410 -0.2107         0.4444    0.2232
5        logit  full      0.4892       0.4931  0.4552     0.4673     0.4548 0.2223  0.9097 -0.1809         0.4722    0.2584
6       MARKET     -         NaN          NaN     NaN        NaN        NaN 0.2352  1.1489 -0.1424            NaN       NaN
7  EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.2813  1.3639 -0.1536         0.5833       NaN
```

## Resolving power
36 test months x ~80 stocks, positive rate 0.45: the mean monthly AUC of a model with no skill has s.e. ~0.011; AUC gaps below ~0.030 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw factor_set=base market=KOSPI top_n_mcap=100

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc   -0.00349 -0.58011  0.71722     0.80591        36    -0.01873     0.00884 0.68220 1.00000
1     logit  prec_k    0.00516  0.50744  0.30751     0.34066        36    -0.01190     0.02354 0.31460 1.00000
2      lgbm     auc    0.00130  0.19347  0.42385     0.40495        36    -0.00845     0.01208 0.40800 1.00000
3      lgbm  prec_k    0.02640  1.58113  0.06142     0.06784        36    -0.00332     0.05531 0.03940 0.36853
4  catboost     auc   -0.00126 -0.12916  0.55102     0.72516        36    -0.01799     0.01738 0.56040 1.00000
5  catboost  prec_k    0.00731  0.38099  0.35276     0.50480        36    -0.03081     0.04852 0.35880 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo  ci_hi  p_one_sided  n_months
0      lgbm  logit    1.0045    0.9097  0.0948 -0.2464 0.5983       0.2714        36
1  catboost  logit    0.8751    0.9097 -0.0346 -0.4514 0.4880       0.5136        36
```

## H3: SHAP
```
Global mean|SHAP| (top 10):
             mean_abs_shap
RET_3M              0.0701
VKOSPI              0.0688
TERM_SPREAD         0.0640
PCR                 0.0564
DEBT_RATIO          0.0426
BASE_RATE           0.0370
OP_GROWTH           0.0330
GPOA                0.0294
RET_12M             0.0293
CPI_YOY             0.0285

[BASE_RATE high vs low] rank corr=0.788, permutation p=0.0080, months high/low=21/15, sign flips=5/16
             imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M         0.0790   0.0608          1         1   -0.9586  -0.8879      False
PCR            0.0651   0.0463          2         2    0.7103   0.6977      False
DEBT_RATIO     0.0483   0.0374          3         3   -0.0285   0.2865       True
OP_GROWTH      0.0454   0.0186          4         5   -0.7538  -0.7855      False
RET_12M        0.0426   0.0141          5         7   -0.7457  -0.6497      False
QUICK_RATIO    0.0397   0.0122          6         9    0.8856   0.6867      False
OPM            0.0378   0.0106          7        12   -0.8152  -0.7717      False
GPOA           0.0349   0.0246          8         4   -0.6891  -0.8522      False

[TERM_SPREAD high vs low] rank corr=0.874, permutation p=0.0200, months high/low=18/18, sign flips=3/16
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M        0.0625   0.0803          1         1   -0.8967  -0.9594      False
PCR           0.0494   0.0652          2         2    0.7253   0.6998      False
DEBT_RATIO    0.0363   0.0512          3         3    0.2199   0.0376      False
GPOA          0.0235   0.0377          4         7   -0.8119  -0.7116      False
OP_GROWTH     0.0230   0.0455          5         4   -0.7655  -0.7410      False
OPM           0.0186   0.0344          6         8   -0.7757  -0.7851      False
RET_12M       0.0181   0.0434          7         6   -0.6765  -0.7430      False
PER           0.0180   0.0244          8        12   -0.7141  -0.6337      False

[CPI_YOY high vs low] rank corr=0.821, permutation p=0.0040, months high/low=18/18, sign flips=3/16
             imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
RET_3M         0.0821   0.0607          1         1   -0.9602  -0.8989      False
PCR            0.0656   0.0490          2         2    0.6955   0.7390      False
DEBT_RATIO     0.0526   0.0349          3         3    0.0863   0.1877      False
OP_GROWTH      0.0465   0.0221          4         4   -0.7456  -0.7599      False
QUICK_RATIO    0.0460   0.0105          5        11    0.8834   0.7281      False
RET_12M        0.0438   0.0177          6         7   -0.7501  -0.6750      False
GPOA           0.0400   0.0213          7         5   -0.7270  -0.8037      False
OPM            0.0338   0.0192          8         6   -0.7666  -0.7854      False

Top macro x firm interactions (mean|phi_ij|*2):
                        value
TERM_SPREAD RET_3M     0.0134
VKOSPI      OPM        0.0079
            PBR        0.0073
TERM_SPREAD PCR        0.0065
CPI_YOY     RET_3M     0.0062
BASE_RATE   DEBT_RATIO 0.0058
TERM_SPREAD OP_GROWTH  0.0057
BASE_RATE   RET_3M     0.0055

```