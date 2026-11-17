# Daily FinBert sentiment

Daily news-sentiment test: rank IC and a daily long-short book, by year (focus: 2025).

  python daily_sentiment_ic.py --years 2020 2021 2022 2023 2024 2025 --out results/v17_daily_sentiment

Timing (BigKinds gives the publication DATE only, no time of day):
  news dated on a weekend / holiday is rolled to the next trading day s; news dated on a trading day stays on it.
  A  enter at the close of s          optimistic: articles published after the close of s are already "known"
  B  enter at the close of s + 1      conservative and tradable; the first-day reaction is not captured
Return = close[entry + h] / close[entry] - 1.  Both are reported; read B as what could have been traded.

Long-short: each signal day, long the top q and short the bottom q of that day's stocks with news (equal weight),
held h = 1 day; cost = `cost` x sum|dw| against the previous day's book (rebuilt from scratch after a gap).
Long-only: top q minus the equal-weight mean of the same day's stocks, same cost rule on the long book only.

## Rank IC by year
   universe           timing  horizon  year  avg_N  n_days  mean_ic   t_nw  hit_rate
  all KOSPI A same-day close        1  2020 18.431     224    0.036  2.073     0.558
  all KOSPI A same-day close        1  2021 17.802     223    0.027  1.478     0.525
  all KOSPI A same-day close        1  2022 17.846     226    0.015  0.795     0.518
  all KOSPI A same-day close        1  2023 19.808     230    0.020  1.161     0.530
  all KOSPI A same-day close        1  2024 20.484     236    0.043  2.764     0.538
  all KOSPI A same-day close        1  2025 17.558     218    0.025  1.305     0.541
  all KOSPI A same-day close        5  2020 18.431     224    0.038  2.059     0.545
  all KOSPI A same-day close        5  2021 17.802     223    0.019  0.946     0.502
  all KOSPI A same-day close        5  2022 17.846     226   -0.009 -0.453     0.482
  all KOSPI A same-day close        5  2023 19.808     230   -0.013 -0.747     0.509
  all KOSPI A same-day close        5  2024 20.484     236    0.020  1.218     0.525
  all KOSPI A same-day close        5  2025 17.558     218    0.046  2.318     0.546
  all KOSPI B next-day close        1  2020 18.431     224    0.001  0.038     0.487
  all KOSPI B next-day close        1  2021 17.802     223   -0.002 -0.094     0.489
  all KOSPI B next-day close        1  2022 17.846     226   -0.013 -0.724     0.496
  all KOSPI B next-day close        1  2023 19.808     230    0.004  0.230     0.535
  all KOSPI B next-day close        1  2024 20.484     236   -0.018 -1.138     0.479
  all KOSPI B next-day close        1  2025 17.558     218    0.022  1.120     0.523
  all KOSPI B next-day close        5  2020 18.431     224    0.023  1.146     0.531
  all KOSPI B next-day close        5  2021 17.802     223    0.001  0.041     0.543
  all KOSPI B next-day close        5  2022 17.846     226   -0.015 -0.750     0.491
  all KOSPI B next-day close        5  2023 19.808     230   -0.012 -0.579     0.500
  all KOSPI B next-day close        5  2024 20.484     236   -0.008 -0.471     0.500
  all KOSPI B next-day close        5  2025 17.558     218    0.032  1.687     0.537
top200 mcap A same-day close        1  2020 12.544     175    0.038  1.582     0.554
top200 mcap A same-day close        1  2021 12.605     172    0.007  0.296     0.535
top200 mcap A same-day close        1  2022 13.175     190    0.046  1.714     0.505
top200 mcap A same-day close        1  2023 14.437     192    0.009  0.446     0.531
top200 mcap A same-day close        1  2024 14.877     217    0.035  1.882     0.553
top200 mcap A same-day close        1  2025 13.236     180    0.030  1.408     0.517
top200 mcap A same-day close        5  2020 12.544     175    0.029  1.228     0.537
top200 mcap A same-day close        5  2021 12.605     172   -0.016 -0.649     0.488
top200 mcap A same-day close        5  2022 13.175     190   -0.003 -0.132     0.511
top200 mcap A same-day close        5  2023 14.437     192   -0.020 -1.008     0.500
top200 mcap A same-day close        5  2024 14.877     217    0.013  0.626     0.516
top200 mcap A same-day close        5  2025 13.236     180    0.040  1.536     0.511
top200 mcap B next-day close        1  2020 12.544     175   -0.004 -0.170     0.480
top200 mcap B next-day close        1  2021 12.605     172    0.008  0.396     0.494
top200 mcap B next-day close        1  2022 13.175     190    0.005  0.257     0.542
top200 mcap B next-day close        1  2023 14.437     192    0.012  0.640     0.484
top200 mcap B next-day close        1  2024 14.877     217   -0.016 -0.806     0.507
top200 mcap B next-day close        1  2025 13.236     180    0.015  0.742     0.489
top200 mcap B next-day close        5  2020 12.544     175    0.011  0.450     0.514
top200 mcap B next-day close        5  2021 12.605     172   -0.012 -0.525     0.506
top200 mcap B next-day close        5  2022 13.175     190   -0.004 -0.171     0.484
top200 mcap B next-day close        5  2023 14.437     192   -0.019 -0.832     0.500
top200 mcap B next-day close        5  2024 14.877     217   -0.014 -0.613     0.498
top200 mcap B next-day close        5  2025 13.236     180    0.031  1.201     0.511

## Daily long-short / long-only by year
   universe           timing  year  n_days  avg_N  ls_gross_bp_day  ls_turnover  ls_sharpe_gross  ls_sharpe_net  breakeven_cost_bp  lo_excess_gross_bp_day  lo_sharpe_net
  all KOSPI A same-day close  2020     224 19.335           29.200        3.571            1.481         -2.134              8.176                  18.946         -1.189
  all KOSPI A same-day close  2021     223 18.426           16.794        3.569            0.950         -3.084              4.706                  16.414         -1.860
  all KOSPI A same-day close  2022     226 18.588           26.703        3.536            1.441         -2.385              7.551                  15.971         -1.732
  all KOSPI A same-day close  2023     230 20.439           74.395        3.651            3.527          0.065             20.376                  22.108         -1.278
  all KOSPI A same-day close  2024     236 20.640           44.508        3.672            2.711         -1.765             12.122                  15.823         -1.993
  all KOSPI A same-day close  2025     218 18.523           44.647        3.581            2.087         -1.262             12.468                  18.424         -1.371
  all KOSPI B next-day close  2020     224 19.344            9.494        3.571            0.559         -3.643              2.658                   2.464         -2.990
  all KOSPI B next-day close  2021     223 18.466            0.059        3.573            0.004         -5.050              0.017                   2.984         -3.354
  all KOSPI B next-day close  2022     226 18.593           -8.233        3.535           -0.589         -5.648             -2.329                   2.296         -3.718
  all KOSPI B next-day close  2023     230 20.452           37.805        3.649            2.060         -1.908             10.359                  14.857         -2.021
  all KOSPI B next-day close  2024     236 20.657            6.928        3.672            0.490         -4.711              1.887                   1.762         -3.907
  all KOSPI B next-day close  2025     218 18.523           26.953        3.581            1.454         -2.411              7.527                  17.511         -1.598
top200 mcap A same-day close  2020     175 14.926           13.847        3.226            0.605         -2.216              4.293                  11.030         -1.602
top200 mcap A same-day close  2021     172 14.919            9.189        3.114            0.580         -3.323              2.951                  17.307         -1.693
top200 mcap A same-day close  2022     190 14.953           19.689        3.262            1.243         -2.889              6.036                  10.583         -2.279
top200 mcap A same-day close  2023     192 16.479           38.367        3.400            2.086         -1.608             11.284                  18.208         -1.429
top200 mcap A same-day close  2024     217 15.770           33.908        3.524            2.209         -2.390              9.621                  11.428         -2.258
top200 mcap A same-day close  2025     180 15.339            6.611        3.283            0.411         -3.658              2.014                  -4.669         -3.610
top200 mcap B next-day close  2020     175 14.926           -4.740        3.226           -0.224         -3.278             -1.470                   0.565         -2.778
top200 mcap B next-day close  2021     172 14.919            1.267        3.114            0.087         -4.158              0.407                   6.514         -2.795
top200 mcap B next-day close  2022     190 14.953            1.919        3.262            0.157         -5.170              0.588                   2.020         -4.128
top200 mcap B next-day close  2023     192 16.479           23.382        3.400            1.422         -2.709              6.877                  17.180         -1.746
top200 mcap B next-day close  2024     217 15.770            5.503        3.524            0.373         -4.414              1.561                  -3.033         -4.057
top200 mcap B next-day close  2025     180 15.339           -8.591        3.283           -0.525         -4.549             -2.617                  -7.259         -3.995
