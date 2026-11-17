# Weekly FinBert sentiment

Weekly news-sentiment test: 5-trading-day signal, 5-trading-day hold, by year (focus: 2025).

  python weekly_sentiment_ic.py --years 2020 2021 2022 2023 2024 2025 --out results/v17_weekly_sentiment

Signal at rebalance day r: article-weighted mean FinBert score of the news rolled onto the last `window` (5)
trading days ending at r. Hold `horizon` (5) trading days; rebalance every 5th trading day.
Timing as in daily_sentiment_ic.py:  A enter at the close of r (optimistic: r's own articles may be after the close),
B enter at the close of r + 1 (conservative / tradable).
The weekday of the rebalance is arbitrary, so all five phases (offsets of the 5-day cycle) are run and averaged;
the spread across phases is reported as a robustness check.
Long-short / long-only books and costs are the same as in daily_sentiment_ic.py, with turnover measured from one
rebalance to the next (`step` = 5) and Sharpe annualised with 252/5 periods per year.

## Rank IC by year (mean over 5 phases)
   universe                timing  year  n_weeks  avg_N  mean_ic   t_nw  hit_rate  mean_ic_min  mean_ic_max
  all KOSPI A rebalance-day close  2020   49.600 66.765    0.015  0.740     0.524       -0.003        0.033
  all KOSPI A rebalance-day close  2021   49.600 63.839    0.016  0.701     0.508        0.009        0.029
  all KOSPI A rebalance-day close  2022   49.200 63.957   -0.018 -0.827     0.491       -0.036       -0.006
  all KOSPI A rebalance-day close  2023   49.000 72.657   -0.024 -1.093     0.445       -0.028       -0.018
  all KOSPI A rebalance-day close  2024   48.800 72.356   -0.002 -0.080     0.459       -0.016        0.011
  all KOSPI A rebalance-day close  2025   48.400 64.190    0.032  1.314     0.541        0.009        0.047
  all KOSPI      B next-day close  2020   49.600 66.765    0.018  0.871     0.556        0.005        0.034
  all KOSPI      B next-day close  2021   49.600 63.839    0.003  0.138     0.500       -0.006        0.016
  all KOSPI      B next-day close  2022   49.200 63.957   -0.020 -1.019     0.476       -0.040        0.006
  all KOSPI      B next-day close  2023   49.000 72.657   -0.020 -0.876     0.441       -0.024       -0.011
  all KOSPI      B next-day close  2024   48.800 72.356    0.000  0.031     0.491       -0.022        0.017
  all KOSPI      B next-day close  2025   48.400 64.190    0.030  1.227     0.546        0.001        0.042
top200 mcap A rebalance-day close  2020   49.600 43.438    0.007  0.237     0.492       -0.011        0.023
top200 mcap A rebalance-day close  2021   49.600 41.662    0.007  0.254     0.496       -0.011        0.014
top200 mcap A rebalance-day close  2022   49.200 43.858   -0.018 -0.666     0.500       -0.042       -0.006
top200 mcap A rebalance-day close  2023   49.000 49.894   -0.027 -0.978     0.486       -0.044       -0.017
top200 mcap A rebalance-day close  2024   48.800 48.955    0.001  0.057     0.500       -0.017        0.018
top200 mcap A rebalance-day close  2025   48.400 45.925    0.018  0.574     0.467       -0.011        0.044
top200 mcap      B next-day close  2020   49.600 43.438    0.003  0.138     0.492       -0.010        0.020
top200 mcap      B next-day close  2021   49.600 41.662   -0.001 -0.017     0.460       -0.017        0.009
top200 mcap      B next-day close  2022   49.200 43.858   -0.023 -0.977     0.468       -0.042        0.005
top200 mcap      B next-day close  2023   49.000 49.894   -0.021 -0.776     0.445       -0.038        0.002
top200 mcap      B next-day close  2024   48.800 48.955   -0.001 -0.073     0.475       -0.026        0.020
top200 mcap      B next-day close  2025   48.400 45.925    0.017  0.579     0.484       -0.006        0.035

## Weekly long-short / long-only by year (mean over 5 phases)
   universe                timing  year  n_weeks  avg_N  ls_gross_bp_wk  ls_turnover  ls_sharpe_gross  ls_sharpe_net  breakeven_cost_bp  lo_excess_gross_bp_wk  lo_sharpe_net  ls_sharpe_net_min  ls_sharpe_net_max
  all KOSPI A rebalance-day close  2020   49.600 66.228          33.761        3.637            0.584         -0.612              9.312                 26.392         -0.272             -1.351             -0.182
  all KOSPI A rebalance-day close  2021   49.600 62.936          46.012        3.564            0.961         -0.558             12.904                 29.857         -0.257             -1.481              0.400
  all KOSPI A rebalance-day close  2022   49.200 63.713         -17.924        3.552           -0.345         -2.095             -5.021                 -4.757         -1.740             -2.997             -0.257
  all KOSPI A rebalance-day close  2023   49.000 72.257          -7.329        3.642           -0.134         -1.766             -1.997                 -8.303         -1.529             -2.247             -1.152
  all KOSPI A rebalance-day close  2024   48.800 71.721          11.224        3.620            0.272         -1.468              3.126                 17.465         -0.767             -2.358             -0.742
  all KOSPI A rebalance-day close  2025   48.400 63.822          99.827        3.640            1.887          0.529             27.435                 52.308          0.425             -0.048              1.273
  all KOSPI      B next-day close  2020   49.600 66.241          31.397        3.637            0.548         -0.733              8.644                 15.547         -0.612             -1.806             -0.112
  all KOSPI      B next-day close  2021   49.600 62.992           8.331        3.565            0.120         -1.463              2.341                 -0.645         -1.408             -2.787             -0.203
  all KOSPI      B next-day close  2022   49.200 63.725         -25.334        3.552           -0.561         -2.345             -7.100                -14.152         -2.310             -3.223             -1.150
  all KOSPI      B next-day close  2023   49.000 72.282         -16.216        3.642           -0.389         -2.099             -4.438                -10.020         -1.688             -2.616             -1.556
  all KOSPI      B next-day close  2024   48.800 71.754          17.211        3.620            0.446         -1.349              4.786                 34.308         -0.121             -2.176             -0.025
  all KOSPI      B next-day close  2025   48.400 63.843          88.272        3.640            1.776          0.309             24.259                 46.352          0.236             -0.285              0.970
top200 mcap A rebalance-day close  2020   49.600 43.438          29.081        3.621            0.413         -0.601              8.037                 25.144         -0.234             -0.992             -0.263
top200 mcap A rebalance-day close  2021   49.600 41.662          37.533        3.552            0.910         -0.790             10.592                 23.034         -0.503             -1.389             -0.240
top200 mcap A rebalance-day close  2022   49.200 43.858         -21.842        3.550           -0.489         -2.172             -6.175                 -9.335         -1.810             -3.063             -1.727
top200 mcap A rebalance-day close  2023   49.000 49.894           1.309        3.633           -0.005         -1.683              0.387                  4.153         -1.190             -2.516             -0.898
top200 mcap A rebalance-day close  2024   48.800 48.955          22.149        3.607            0.501         -1.019              6.171                 17.358         -0.631             -1.722             -0.190
top200 mcap A rebalance-day close  2025   48.400 45.925          49.908        3.637            0.913         -0.387             13.735                 25.936         -0.309             -1.137             -0.062
top200 mcap      B next-day close  2020   49.600 43.438          22.043        3.621            0.336         -0.792              6.082                 14.132         -0.584             -1.142             -0.483
top200 mcap      B next-day close  2021   49.600 41.662          21.691        3.552            0.483         -1.302              6.185                 12.439         -1.007             -2.260             -0.193
top200 mcap      B next-day close  2022   49.200 43.858         -26.973        3.550           -0.642         -2.356             -7.634                -10.674         -1.945             -3.199             -1.559
top200 mcap      B next-day close  2023   49.000 49.894          -8.704        3.633           -0.302         -2.154             -2.358                 -3.642         -1.653             -3.169             -0.790
top200 mcap      B next-day close  2024   48.800 48.955           9.285        3.607            0.225         -1.225              2.636                 16.276         -0.668             -2.420              0.007
top200 mcap      B next-day close  2025   48.400 45.925          52.294        3.637            0.960         -0.342             14.400                 28.122         -0.231             -0.916              0.018
