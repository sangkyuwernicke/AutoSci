# Experiment report
data=real trials=15 cost=0.002 top_q=200.0 (>=1: number of stocks) target=direction margin=0.0 quantile=None

## Prediction + backtest (net of costs)
```
               model   fset  auc_pooled  auc_monthly  pr_auc  prec_at_k  base_rate   CAGR  Sharpe     MDD  WinRate_vs_bm  Turnover
0           catboost   firm      0.5371       0.5514  0.4741     0.4833     0.4503 0.0387  0.3100 -0.2210         0.4792    0.2577
1               lgbm   firm      0.5316       0.5500  0.4690     0.4834     0.4503 0.0437  0.3385 -0.2328         0.4792    0.2615
2              logit   firm      0.5342       0.5474  0.4733     0.4898     0.4503 0.0700  0.4788 -0.2144         0.5000    0.2233
3        macro_gated  gated      0.5093       0.5409  0.4604     0.4803     0.4503 0.0708  0.4633 -0.2163         0.4792    0.2871
4             MARKET      -         NaN          NaN     NaN        NaN        NaN 0.0900  0.4946 -0.2190            NaN       NaN
5        EW_UNIVERSE      -         NaN          NaN     NaN        NaN        NaN 0.0220  0.2132 -0.2401         0.4583       NaN
6  KOSPI200_OFFICIAL      -         NaN          NaN     NaN        NaN        NaN 0.1135  0.5708 -0.2304         0.4583       NaN
7     KOSPI200_PROXY      -         NaN          NaN     NaN        NaN        NaN 0.0975  0.5038 -0.1984         0.5208       NaN
```

## Resolving power
48 test months x ~655 stocks, positive rate 0.45: the mean monthly AUC of a model with no skill has s.e. ~0.003; AUC gaps below ~0.009 (80% power) cannot be told from noise. Treat results as exploratory; read effect sizes and intervals, not p-values.

settings: small_data=True macro_mode=raw macro_role=gating factor_set=base market=KOSPI top_n_mcap=0

## H1: macro_gated vs firm-only models (paired by month)
```
  macro_gated_vs  metric  mean_diff   t_stat  p_ttest  p_wilcoxon  n_months  boot_ci_lo  boot_ci_hi  p_boot  p_holm
0          logit     auc   -0.00651 -1.97121  0.97270     0.96500        48    -0.01436     0.00082 0.95740 1.00000
1          logit  prec_k   -0.00948 -1.95548  0.97176     0.96022        48    -0.02063     0.00042 0.97100 1.00000
2           lgbm     auc   -0.00910 -1.71150  0.95321     0.87658        48    -0.02071     0.00250 0.93440 1.00000
3           lgbm  prec_k   -0.00313 -0.47998  0.68326     0.72161        48    -0.01729     0.01146 0.66680 1.00000
4       catboost     auc   -0.01049 -2.12917  0.98075     0.95611        48    -0.02129     0.00051 0.96600 1.00000
5       catboost  prec_k   -0.00302 -0.45513  0.67444     0.60121        48    -0.01719     0.01157 0.65980 1.00000
```

## H2: Sharpe(model) - Sharpe(logit), block bootstrap
```
      model     vs  sharpe_a  sharpe_b    diff   ci_lo   ci_hi  p_one_sided  n_months
0      lgbm  logit    0.3385    0.4788 -0.1403 -0.2744  0.0057       0.9702        48
1  catboost  logit    0.3100    0.4788 -0.1687 -0.3232 -0.0480       0.9960        48
```

## H3: SHAP / Gating analysis
```
Global mean|SHAP| (top 10):
              mean_abs_shap
VOL_20D              0.0537
PCR                  0.0431
RET_3M               0.0382
OPM                  0.0374
GPOA                 0.0352
PER                  0.0330
RET_12M              0.0310
RET_1M               0.0283
PBR                  0.0254
SALES_GROWTH         0.0230

[BASE_RATE high vs low] rank corr=0.637, permutation p=0.0020, months high/low=24/24, sign flips=3/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D    0.0541   0.0535          1         1   -0.6823  -0.6360      False
RET_3M     0.0387   0.0381          2         7   -0.4177  -0.5263      False
RET_1M     0.0356   0.0212          3        12   -0.7270  -0.3523      False
PCR        0.0353   0.0518          4         2    0.9471   0.8430      False
PBR        0.0314   0.0197          5        13    0.9650   0.4489      False
GPOA       0.0304   0.0408          6         5   -0.8134  -0.7333      False
OPM        0.0272   0.0483          7         3    0.5718   0.6906      False
PER        0.0259   0.0406          8         6    0.7094   0.4591      False

[TERM_SPREAD high vs low] rank corr=0.949, permutation p=0.0359, months high/low=24/24, sign flips=0/17
           imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
VOL_20D      0.0519   0.0558          1         1   -0.6122  -0.6908      False
PCR          0.0408   0.0463          2         2    0.8592   0.9033      False
OPM          0.0382   0.0372          3         5    0.7112   0.5916      False
RET_3M       0.0335   0.0434          4         3   -0.5484  -0.4199      False
PER          0.0330   0.0336          5         8    0.5703   0.5713      False
GPOA         0.0311   0.0401          6         4   -0.7239  -0.8257      False
RET_12M      0.0286   0.0344          7         7   -0.3876  -0.8319      False
OP_GROWTH    0.0223   0.0223          8        11    0.6869   0.7737      False

[CPI_YOY high vs low] rank corr=0.875, permutation p=0.0020, months high/low=24/24, sign flips=3/17
         imp_high  imp_low  rank_high  rank_low  dir_high  dir_low  sign_flip
PCR        0.0598   0.0272          1         3    0.8671   0.9012      False
VOL_20D    0.0557   0.0519          2         1   -0.7273  -0.5568      False
GPOA       0.0511   0.0201          3         6   -0.8499  -0.6937      False
RET_12M    0.0507   0.0123          4        11   -0.8224  -0.4000      False
OPM        0.0497   0.0257          5         4    0.6030   0.7489      False
RET_3M     0.0492   0.0277          6         2   -0.4088  -0.5736      False
PER        0.0438   0.0228          7         5    0.4364   0.7491      False
RET_1M     0.0373   0.0195          8         7   -0.5525  -0.5842      False

[Macro-Gated Mode] Factor weight time series -> gating_factor_weights.csv
Regime centroids (last test fold):
          BASE_RATE  TERM_SPREAD  CPI_YOY    KRWUSD  VKOSPI
regime_0     3.1774       0.0900   3.8698 1328.8161 17.8919
regime_1     0.7411       0.5678   1.6027 1167.6429 23.7375

Factor weights at first/last test month:
              PER    PBR    PCR  EV_EBITDA     ROE     ROA    OPM    GPOA  SALES_GROWTH  OP_GROWTH  DEBT_RATIO  QUICK_RATIO     ICR  RET_1M  RET_3M  RET_12M  VOL_20D
2021-12-31 0.0428 0.0889 0.0843    -0.0367 -0.0141 -0.0149 0.0902 -0.0580        0.0633    -0.0005     -0.0194      -0.0005 -0.0063 -0.0222 -0.0320  -0.0518  -0.0117
2025-11-30 0.0165 0.0315 0.0289    -0.0018  0.0107  0.0370 0.0538 -0.0114        0.0027     0.0353      0.0186       0.0174  0.0078 -0.0232 -0.0504   0.0329   0.0201

```