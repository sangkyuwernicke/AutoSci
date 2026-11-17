# Experiment report
data=real trials=15 cost=0.002 top_q=0.2 margin=0.0 quantile=0.8

## Prediction + backtest (net of costs)
```
         model  fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0     catboost  firm      0.5171       0.5451  0.2229     0.2295     0.2051 0.2771  0.9760 -0.2608         0.5000    0.1856
1     catboost  full      0.5084       0.5219  0.2079     0.2176     0.2051 0.2681  0.9402 -0.2765         0.5278    0.2722
2         lgbm  firm      0.5132       0.5200  0.2114     0.2439     0.2051 0.3567  1.1296 -0.2791         0.5833    0.2484
3         lgbm  full      0.5175       0.5204  0.2117     0.2160     0.2051 0.2023  0.7602 -0.2889         0.5000    0.2863
4        logit  firm      0.5371       0.5511  0.2171     0.2689     0.2051 0.4139  1.3235 -0.2555         0.6111    0.1895
5        logit  full      0.5370       0.5512  0.2168     0.2689     0.2051 0.4139  1.3235 -0.2555         0.6111    0.1895
6       MARKET     -         NaN          NaN     NaN        NaN        NaN 0.2352  1.1489 -0.1424            NaN       NaN
7  EW_UNIVERSE     -         NaN          NaN     NaN        NaN        NaN 0.2813  1.3639 -0.1536         0.5833       NaN
```

## Resolving power
36 test months x ~80 stocks, positive rate 0.21: the mean monthly AUC of a model with no skill has s.e. ~0.013; AUC gaps below ~0.038 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=regime factor_set=base market=KOSPI top_n_mcap=100

## H1: full (firm+macro) minus firm-only, paired by month
```
      model  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0     logit     auc    0.00005  1.42911  0.08092     0.08986        36     0.00000     0.00012 0.11700 0.40459
1     logit  prec_k    0.00000      NaN      NaN         NaN        36     0.00000     0.00000 1.00000     NaN
2      lgbm     auc    0.00038  0.05256  0.47919     0.42918        36    -0.01620     0.01610 0.47140 1.00000
3      lgbm  prec_k   -0.02793 -3.18640  0.99849     0.99779        36    -0.04675    -0.00975 0.99840 1.00000
4  catboost     auc   -0.02325 -2.67012  0.99429     0.98584        36    -0.03902    -0.00873 0.99960 1.00000
5  catboost  prec_k   -0.01191 -0.84385  0.79776     0.88403        36    -0.04186     0.01592 0.79260 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo   ci_hi  p_one_sided  n_months
0      lgbm  logit    0.7602    1.3235 -0.5633 -0.9322 -0.2510       0.9996        36
1  catboost  logit    0.9402    1.3235 -0.3834 -0.7664 -0.0608       0.9886        36
```

## H3: SHAP
```
Global mean|SHAP| (top 10):
             mean_abs_shap
DEBT_RATIO          0.0921
RET_3M              0.0848
ICR                 0.0806
PCR                 0.0780
OPM                 0.0687
QUICK_RATIO         0.0584
PBR                 0.0542
PER                 0.0512
RET_12M             0.0484
OP_GROWTH           0.0483

[BASE_RATE high vs low] rank corr=0.650, permutation p=0.0080, months high/low=21/15, sign flips=3/16
             imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
DEBT_RATIO     0.1017   0.0878          1         1    0.7597   0.9142      False
ICR            0.1002   0.0616          2         6   -0.8710  -0.8361      False
PCR            0.0964   0.0642          3         4    0.4489   0.0815      False
RET_3M         0.0956   0.0768          4         2   -0.8319  -0.9453      False
QUICK_RATIO    0.0780   0.0414          5         9    0.8116   0.8257      False
PER            0.0695   0.0313          6        10   -0.5778  -0.7582      False
RET_1M         0.0663   0.0240          7        13   -0.6757  -0.3932      False
OPM            0.0651   0.0713          8         3   -0.4791  -0.8426      False

[TERM_SPREAD high vs low] rank corr=0.647, permutation p=0.0040, months high/low=18/18, sign flips=3/16
            imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
DEBT_RATIO    0.0775   0.1143          1         1    0.8715   0.7512      False
OPM           0.0728   0.0626          2         9   -0.8583  -0.3695      False
RET_3M        0.0710   0.1046          3         4   -0.9345  -0.8355      False
ICR           0.0605   0.1077          4         3   -0.8483  -0.8721      False
RET_12M       0.0560   0.0404          5        13    0.6021  -0.3419       True
PCR           0.0546   0.1113          6         2    0.0842   0.4431      False
PBR           0.0467   0.0652          7         8   -0.8289  -0.8373      False
OP_GROWTH     0.0435   0.0564          8        11   -0.1848  -0.5636      False

[CPI_YOY high vs low] rank corr=0.521, permutation p=0.0020, months high/low=18/18, sign flips=3/16
             imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
DEBT_RATIO     0.1234   0.0684          1         2    0.7521   0.8714      False
PCR            0.1211   0.0448          2         6    0.4391   0.0808      False
ICR            0.1132   0.0550          3         4   -0.8763  -0.8566      False
RET_3M         0.1106   0.0650          4         3   -0.8397  -0.9384      False
QUICK_RATIO    0.0969   0.0286          5        10    0.8066   0.8319      False
RET_1M         0.0778   0.0196          6        13   -0.6950  -0.4476      False
PER            0.0749   0.0323          7         9   -0.5856  -0.7279      False
PBR            0.0689   0.0430          8         7   -0.8391  -0.8303      False

Top macro x firm interactions (mean|phi_ij|*2):
                  value
VKOSPI      ROA  0.0055
            PBR  0.0017
BASE_RATE   GPOA 0.0016
CPI_YOY     PER  0.0015
VKOSPI      OPM  0.0012
            ICR  0.0010
CPI_YOY     ROA  0.0009
TERM_SPREAD ICR  0.0008

```