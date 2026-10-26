[English README](README.md)

# 머신러닝 기반 기업 팩터 × 거시경제 초과수익률 예측 실험 (KOSPI/KOSDAQ)

연구 계획서를 구현한 워크포워드 파이프라인입니다. 기업 팩터와 거시 지표를 결합해 차기월 초과수익 달성
여부를 분류하고, 트리 앙상블과 선형 기준 모델을 비교한 뒤, 상위 20% 포트폴리오를 백테스트하고, 거시 국면별
SHAP으로 팩터 중요도를 분석합니다.

```bash
pip install -r requirements.txt
# 0) 합성 데이터 빠른 프로필 (100종목, 2020-01-02부터, 학습 2020년~, 테스트 2023~2025, 트라이얼 15회)
python run_experiment.py --quick --out results/quick
# 1) 국면 구조를 알고 있는 합성 데이터 스모크 테스트 (API 키 불필요)
python run_experiment.py --data synthetic --trials 10 --out results/synth
# 2) 실데이터
python prepare_krx.py --krx-dir data/krx --out data/real                       # 직접 내려받은 KRX 파일 변환
python fetch_real_data.py macro --out data/real --start-year 2019              # ECOS (+ data/krx/vkospi.csv)
python fetch_real_data.py fundamentals --out data/real --market KOSPI --top-n-mcap 100 --start-year 2019   # DART
python run_experiment.py --quick --data real --raw-dir data/real --out results/q_base
# 3) 확장 팩터(모멘텀 / 재투자 / 선행 지표)와 쌍체 비교
python run_experiment.py --quick --data real --raw-dir data/real --factor-set extended --out results/q_ext
python compare_runs.py results/q_base results/q_ext --labels base extended --out results/base_vs_ext
python prepare_consensus.py vendor_export.csv --out data/real/consensus.parquet --unit 1e6   # 선택, 벤더 데이터 필요
# 4) 테스트 (오프라인)
for t in lookahead forward universe krx fetch pilot agent_eval; do python tests/test_$t.py; done
```

| 파일 | 역할 |
|---|---|
| `config.py` | 팩터 목록, ECOS 시리즈 코드 |
| `data_synth.py` | 합성 패널 (팩터 수익이 금리·장단기 금리차 국면에 따라 달라지고 가치×품질 상호작용 포함) |
| `data_real.py` | 원본 파일 → 패널. 재무제표는 **공시일** 기준으로 결합, 거시 지표는 t‑1월 말까지 공개된 값만 사용 |
| `prepare_krx.py` | 직접 내려받은 KRX 스냅샷·지수·VKOSPI csv → `prices_monthly.parquet`, `index.parquet`, `macro.parquet`의 VKOSPI |
| `fetch_real_data.py` | ECOS 거시 지표, Open DART 재무제표 수집기 (실제 API로 검증 안 됨, 재시작 가능, 호출 수 제한) |
| `universe.py` | 금융업·스팩·우선주 제외, `exclusions.csv`, 재무 커버리지 필터 |
| `prepare_consensus.py` | 벤더의 시점별 컨센서스 export 검증·정규화 → `consensus.parquet` |
| `compare_runs.py` | 두 실행(base vs extended) 쌍체 비교: 월별 AUC / Precision@K / 순 Sharpe, t검정, Wilcoxon, 블록 부트스트랩 |
| `factor_ic.py` | 팩터별 월별 순위 IC (차기월 초과수익과의 상관), 파일럿 모드 참조 |
| `pilot_suite.py` | 팩터 IC, 파일럿 설정 3종, 쌍체 비교를 한 번에 실행 |
| `data_quality.py` | 팩터별 결측·0 비율·이상치·커버리지 리포트 (`data_quality.csv`) |
| `features.py` | 타깃 생성, 월별 윈저라이징(1/99%) + 순위 정규화 또는 z-score |
| `models.py` | 로지스틱(L1/L2), 릿지, 결정트리, RF, XGB, LGBM, CatBoost + Optuna 탐색 공간 |
| `evaluation.py` | AUC, PR-AUC, Precision@20%, 백테스트, H1 쌍체 검정, H2 블록 부트스트랩 |
| `shap_analysis.py` | SHAP, 순열검정을 이용한 국면 비교, 거시×기업 상호작용 |
| `run_experiment.py` | 전체 오케스트레이션 → `results/<run>/report.md` + csv/png |
| `run_agents.py` | TradingAgents에 (종목, 월말) 표본의 등급을 요청 -> `predictions.parquet` (LLM 에이전트 절 참조) |
| `compare_agent.py` | 같은 종목-월에서 에이전트 vs ML 모델 비교, 우연 기준선 포함 |
| `agent_eval/` | TradingAgents용 시점별 데이터 공급처, 백엔드, 실행기 |

## 확장 팩터 (`--factor-set extended`)

| 그룹 | 팩터 | 출처 / 정의 |
|---|---|---|
| 모멘텀 | `RET_6M`, `MOM_12_1`, `DIST_52W_HIGH` | 월말 가격 기준. 최근 1개월을 제외한 12개월 수익률, 종가 ÷ 52주 고점 − 1 |
| 재투자 | `RD_INTENSITY`, `RD_GROWTH` | 사업보고서 연구개발비 ÷ 연 매출, 연구개발비 전년 대비 성장률. 사업보고서 공시일부터 사용. 재무제표는 있는데 R&D 항목이 없는 기업은 0 |
| | `CAPEX_INTENSITY`, `ASSET_GROWTH` | 최근 12개월 유형자산 취득 ÷ 최근 12개월 매출, 총자산 전년 대비 성장률 |
| 선행 지표 | `FWD_PER` | 시가총액 ÷ 12개월 선행 컨센서스 순이익, (12−m)/12·FY(t) + m/12·FY(t+1) |
| | `FWD_EPS_GROWTH`, `FWD_SALES_GROWTH` | 선행 추정치 대비 최근 12개월 실적 |
| | `EST_REVISION_3M` | **같은 회계연도** 추정치의 3개월 전 대비 변화 |

입력이 없는 팩터는 경고를 내고 건너뛰므로, `consensus.parquet`·설비투자·R&D가 있든 없든 파이프라인이 동작합니다.

새 입력의 룩어헤드 규칙: 컨센서스 스냅샷은 날짜가 t 이하이고 45일 이내인 것만 씁니다(`build_panel`의
`consensus_lag_days`로 보수적인 공표 지연을 더할 수 있음). 무료 출처(예: 네이버 금융)는 **현재** 컨센서스만
보여 주므로 과거에 붙이면 오늘의 추정치가 과거로 새어 들어갑니다. 따라서 시점별 이력을 가진 벤더 데이터
(FnGuide/DataGuide, Refinitiv)가 필요합니다. 실현된 미래 실적을 추정치 대신 쓰면 안 됩니다. 벤더가 추정치를
소급 수정하는 경우가 있으니 몇 개 날짜를 직접 대조해 보세요. R&D는 DART에서 표준 계정으로 잘 잡히지 않아
(`fetch_real_data.py`가 `ifrs-full_ResearchAndDevelopmentExpense`와 한글 계정명 힌트를 찾음), `RD_*`를 해석하기
전에 `data_quality.csv`의 커버리지를 확인하세요.

## 유니버스

유니버스는 직접 내려받은 월말 KRX 스냅샷(아래 참조)에서 만듭니다. 그 월말에 실제로 상장돼 있던 모든 종목이
들어가므로, 이후 상장폐지된 종목도 포함됩니다(생존 편향 필터 없음). 보통주(종목코드가 0으로 끝남)이고, 스팩이
아니며, 금융업이 아니면(종목명 키워드 기준이며 업종 파일이 있으면 보강 가능) 해당 종목-월이 투자 가능으로
분류됩니다. `build_panel` / `run_experiment`의 추가 필터는 다음과 같습니다.

- `--market KOSPI|KOSDAQ|ALL`: 유니버스와 벤치마크 지수를 함께 제한합니다.
- `--top-n-mcap N`: 매월 시가총액 상위 N개만 유지합니다(시점별로 결정).
- `--min-coverage 0.5`: 재무 기반 팩터 13개 중 50% 미만만 있는 종목-월(공시가 아직 없는 신규 상장 등)을
  횡단면 중앙값으로 채우는 대신 제외합니다.
- `--min-mcap-pct x`: 매월 시가총액 하위 x%를 제외합니다.
- 선택 파일 `data/real/exclusions.csv`(`ticker,start,end`): 관리종목·투자주의환기종목 기간입니다. KRX KIND에서
  내려받아야 하며(연결된 소스 없음), 해당 기간의 행을 제거합니다.

`tests/test_universe.py`가 필터 로직을 오프라인으로 검증합니다.

## 직접 내려받은 KRX 데이터 (KRX 자동 조회 없음)

KRX Data Marketplace는 자동화 수단을 통한 수집을 금지합니다(pykrx 경로는 IP가 차단됨). 그래서 KRX 입력은 웹
화면에서 직접 내려받아 오프라인으로 변환합니다.

```
data/krx/snapshots/*.csv   월말 전 종목 시세 (컬럼: 기준일자,종목코드,종목명,시장구분,종가,...,시가총액,상장주식수)
data/krx/index_kospi.csv   일자,종가   (index_kosdaq.csv는 선택)
python prepare_krx.py --krx-dir data/krx --out data/real      # -> prices_monthly.parquet, index.parquet
```

월말 가격만 있어서 생기는 제약: `VOL_20D`는 만들 수 없고(경고 후 제외), `DIST_52W_HIGH`는 최근 12개월 월말
종가로 계산하며, 수익률은 가격 수익률입니다. 스냅샷 종가는 수정주가가 아니므로, 상장주식수가 10% 넘게 변하는데
시가총액이 [0.75, 1.33] 범위 안에 머무르면 그 달 수익률을 시가총액 변화율로 대신합니다. 휴리스틱이라 유상증자나
합병을 잘못 판정할 수 있으니, 변환 때 출력되는 "share-count events adjusted" 개수를 확인하세요. 우선주(종목코드가
0으로 끝나지 않음), 스팩, 금융업(종목명 키워드만 사용, 업종 파일 없음)은 제외됩니다. 스냅샷에서 사라진 종목은
상장폐지 수익률이 없어 결과가 약간 낙관적으로 나옵니다. `fundamentals.parquet`과 `macro.parquet`은 여전히
`fetch_real_data.py`(DART / ECOS)로 만듭니다. `--quick`은 이제 KOSPI 전용, 시가총액 상위 100종목, 2020-01-02부터,
학습 2020년~, 테스트 2023~2025를 뜻합니다.

## 파일럿 모드: 기간과 종목 수를 늘릴 수 없을 때

테스트 36개월 × 100종목에서는 예측력이 없는 모델의 월별 AUC 평균 표준오차가 약 0.01이라, 대략 0.03 이상의
AUC 차이만 우연과 구분됩니다(`report.md`의 "Resolving power"에 출력됨). 이런 실행은 탐색적 파일럿으로 보고
p값보다 효과 크기와 신뢰구간을 읽으세요. 이를 위한 도구는 다음과 같습니다.

| 도구 | 하는 일 |
|---|---|
| `factor_ic.py` | 모든 팩터의 월별 순위 IC(차기월 초과수익과의 상관): 평균, Newey-West t, 양(+) 비율, 연도별 값. `--price-only`는 DART 없이 적격 전체 종목을 사용 |
| `--small-data` | 얕고 강하게 정규화된 탐색 공간. 기본 모델은 logit, lgbm, catboost만 사용(비교 횟수 감소) |
| `--macro-mode regime` | 거시 값을 과거 누적 중앙값 대비 1 / 0 / 0.5로 변환(룩어헤드 없음)해 트리가 월을 외우지 못하게 함. 원래 값은 SHAP 국면 구분용으로 `*_RAW`에 보관 |
| `--target-quantile 0.8` | 라벨 = 월별 초과수익 상위 20%. margin 라벨과 비교 가능(라벨이 다른 실행끼리는 쌍체 비교 불가) |
| H1 표 | 평균 차이의 블록 부트스트랩 신뢰구간과, 모든 모델×지표 검정에 대한 Holm 보정 p값 추가 |
| `pilot_suite.py` | 팩터 IC, A(원래 거시), B(국면 거시), C(B + 분위 라벨), A 대 B 쌍체 비교를 실행 |

```bash
python pilot_suite.py --raw-dir data/real --out-root results/pilot            # 실데이터 --quick 프로필
python factor_ic.py --data real --raw-dir data/real --price-only --market KOSPI --start-date 2020-01-02
```

## LLM 에이전트(TradingAgents)를 추가 "모델"로 사용하기

[TradingAgents](https://github.com/TauricResearch/TradingAgents)(Apache-2.0, LangGraph)는 트레이딩 회사처럼 구성된
LLM 에이전트 팀(시장·펀더멘털 분석가, 강세/약세 토론, 트레이더, 리스크 팀, 포트폴리오 매니저)이 한 종목의 한 날짜에 대해
`Buy / Overweight / Hold / Underweight / Sell` 등급(해석 불가 시 `REVIEW`)을 돌려줍니다. 여기서는 이것을 ML 모델과
**같은 코드로 채점되는 종목 선택 방법 하나**로 추가합니다. 데이터 수집 모듈은 그대로이고, `agent_eval/`이 그 결과를
TradingAgents가 원래 호출하는 외부 공급처 대신 넣어 줍니다.

```
data/real/*.parquet --(agent_eval.store: 공시일 / 공표일 / 월말 기준)--> "autosci" 공급처
     --> TradingAgentsGraph.propagate("005930.KS", "2025-06-30") --> 등급 --> predictions.parquet (점수 = 등급)
     --> compare_agent.py: 같은 종목-월, run_experiment.py와 같은 지표 + 우연 기준선
```

| 파일 | 역할 |
|---|---|
| `agent_eval/store.py` | `prices_monthly`, `fundamentals`, `macro`에 대한 시점별 조회 (`asof` 이후 데이터는 반환 안 함) |
| `agent_eval/vendor.py` | TradingAgents 라우터(`VENDOR_METHODS`)에 공급처 `autosci` 등록 (공개 등록 API가 없어 실행 시점에 항목을 삽입) |
| `agent_eval/backends.py` | `TradingAgentsBackend`(결정마다 새 그래프와 새 메모리), `MockBackend`(오프라인, 무작위 등급) |
| `agent_eval/jobs.py` | 종목·월 선택, 재시작 가능한 실행(`decisions.jsonl`), 등급 → `predictions.parquet` |
| `run_agents.py` | CLI: `--dry-run` 계획, `--backend mock`, `--backend tradingagents --confirm-cost` |
| `compare_agent.py` | 같은 종목-월에서 에이전트 vs ML, LLM 학습 시점 전후 구분, 순열 기반 우연 기준선 |

```bash
# 별도 가상환경, Python 3.11 이상
pip install -r requirements-agents.txt            # TradingAgents + pandas/pyarrow
pip install -r requirements.txt                   # compare_agent.py에만 필요 (scikit-learn, scipy)
export OPENAI_API_KEY=...                         # 또는 --llm-provider로 지정한 제공자의 키
COMMON="--raw-dir data/real --market KOSPI --top-n-mcap 100 --start-date 2020-01-02 --n-stocks 20 --test-start 2025 --test-end 2025"
python run_agents.py $COMMON --dry-run                                         # 결정이 몇 건인가? 비용 없음
python run_agents.py $COMMON --backend mock --out results/agents/mock          # 배선 점검, LLM 없음
python run_agents.py $COMMON --backend tradingagents --confirm-cost --max-jobs 2 --out results/agents/run1   # 2건으로 시간 측정
python run_agents.py $COMMON --backend tradingagents --confirm-cost --out results/agents/run1               # 이어서 실행
python compare_agent.py --agent results/agents/run1 --ml-run results/q_base --ml-fset firm --llm-cutoff 2025-06
```

에이전트가 보는 것: 월말 가격, 월 단위 기술 요약, 공시된 최신 재무제표(TTM 비율, 월말 시가총액 기준 PER·PBR), 그 날짜까지
공개된 거시 5개 시리즈입니다. 뉴스·SNS·내부자 거래 데이터는 이 데이터셋에 **없으므로** 기본적으로 `market`과
`fundamentals` 분석가만 실행하고, 일별 지표(RSI, MACD 등)는 계산할 수 없어 도구가 그렇게 응답합니다.

결과를 읽을 때의 주의:

- **LLM 룩어헤드.** 테스트 기간을 포함한 데이터로 학습된 모델은 그때 일어난 일을 기억할 수 있고, ML 파이프라인에는 이런
  누수가 없습니다. `compare_agent.py`에 `--llm-cutoff`(모델 학습 데이터의 끝)를 주고 "after cutoff" 구간만 신뢰하세요.
  나머지 구간은 실력이 아니라 기억일 수 있습니다. (TradingAgents README는 LLM 출력과 실시간 데이터가 달라 백테스트
  결과가 재현되지 않을 수 있다고만 경고합니다.)
- **격리.** TradingAgents는 정산된 과거 결정을 기억 로그에 쌓아 다음 실행에 반영합니다. 여기서는 결정마다 빈 메모리 파일과
  실행 후 삭제되는 캐시를 사용하므로 미래 결과가 앞선 결정에 흘러들 수 없습니다.
- **작은 표본.** 20종목 × 12개월은 약 240건이며 각각이 여러 번의 LLM 호출을 거치는 멀티에이전트 실행입니다(더 돌리기 전에
  2건의 비용을 먼저 재세요). 상위 20% 포트폴리오는 약 4종목입니다. 그래서 `compare_agent.py`는 에이전트 점수를 월별로
  섞은 순열 기준(`auc_null_p95`)과 비교합니다. 배선 점검 때 아무 정보 없는 평가자가 15종목에서 AUC 0.52를 얻었으니,
  수 백분 차이는 의미가 없습니다.
- **동률과 변동.** 등급이 5단계라 동률이 많고, 동률은 시드 고정 무작위 값으로 가릅니다. LLM 출력은 실행마다 달라지며
  (`--repeats`로 독립 실행을 평균), TradingAgents는 자체 결정을 기본 5거래일 보유(`holding_period_days`)로 채점하므로,
  여기서 쓰는 월간 라벨은 그 프레임워크가 예측하도록 만들어진 대상이 아닙니다.
- **다루지 않는 것.** Optuna, SHAP(H3), 거시 유무 비교(H1)는 없습니다. 설명할 학습된 모델이 없기 때문입니다.
- **검증 범위.** 어댑터는 실제 TradingAgents v0.7.0의 라우터와 그래프 생성에 대해 오프라인으로 검증했지만
  (`tests/test_agent_eval.py`), 실제 LLM으로는 실행해 보지 못했습니다. 첫 실제 결정에서 수정이 필요할 수 있습니다.

## 설계상 결정할 사항

- **워크포워드**는 예측 대상 월(t+1)이 속한 연도를 기준으로 합니다. 테스트 연도 Y에 대해 라벨이 Y‑2 이하인
  구간에서 튜닝하고, Y‑1로 검증한 뒤, Y‑1 이하로 다시 학습해 Y를 예측합니다. 첫 폴드는 계획서와 같이
  학습 2014~2020 / 검증 2021 / 테스트 2022이며, 어떤 학습 라벨도 첫 테스트 의사결정 시점 이후에 확정되지 않습니다.
- **타깃**은 `y = 1[R_i − R_m > margin]`입니다. `--target-quantile 0.8`을 쓰면 월별 초과수익 상위 20%를
  양성으로 둡니다(매월 1:4 고정, 시장 방향과 무관, margin과 동시 사용 불가). 계획서의 수식이 읽히지 않아
  `--target-margin` 기본값은 0(약 1:1)입니다. 계획서가 말한 1:4 비율을 원하면 분위 라벨을 쓰세요.
- **가치 비율은 역수로 순위화**합니다(E/P, B/P, CF/P, EBITDA/EV). 그래서 적자 기업이 하위로 정렬됩니다. 컬럼
  이름은 `PER` 등으로 유지되므로 `PER`의 SHAP 방향이 *양(+)* 이면 *저평가*를 뜻합니다.
- **릿지**는 이진 라벨에 대한 선형 확률 모델입니다(예측값을 점수로 사용).
- **거래비용**은 리밸런싱마다 `0.20% × Σ|Δw|`입니다(첫 달은 포트폴리오 구성 비용을 냄). Sharpe는 rf = 0,
  월 수익률 × √12입니다. 회전율은 단방향(½Σ|Δw|)입니다.
- **H1**은 모델별로 `full`(기업+거시)과 `firm`(기업만)을 월별 AUC / Precision@K로 비교합니다(쌍체 단측 t검정과
  Wilcoxon). 월별 값은 자기상관이 있으므로 p값은 참고용입니다. 한 달 안에서 거시 변수는 모든 종목이 같으므로
  *선형* 모델은 거시 변수로 종목 순위를 바꿀 수 없고(기업 팩터 계수만 약간 달라짐), 상호작용이 있는 모델만
  거시 정보를 활용할 수 있습니다.
- **H2**는 로지스틱 대비 Sharpe 차이를 쌍체 순환 블록 부트스트랩(블록 = 3개월)으로 검정합니다.
- **H3**의 국면은 거시 값이 *테스트 기간* 중앙값보다 높은지 낮은지로 나눕니다(OOS 기간의 사후 설명이며 모델
  입력이 아님. 학습 기간 중앙값으로 나누면 2022~25가 전부 "고금리"가 됨). 중앙값이 동률이면 `>=`로 대체합니다.
  보고 항목은 중요도 순위 상관, 월 단위 순열검정 p값, 팩터별 방향 반전, 거시×기업 쌍의 평균|SHAP 상호작용|
  (폴드마다 무작위 부표본으로 계산)입니다.
- CatBoost는 수치형 피처만 쓰므로 범주형 변수의 강점은 활용되지 않습니다. 원하면 `data_real.py`에 업종·시장을
  범주형으로 추가하세요.

## 문제 해결

- KRX를 자동으로 긁지 마세요(pykrx, FinanceDataReader의 KRX 엔드포인트): KRX Data Marketplace 약관이 자동화
  수집을 금지하며 IP가 차단됩니다. 화면 다운로드, 데이터 상품, 공식 KRX Open API를 사용하세요.
- `No module named 'OpenDartReader'`: 패키지 `opendartreader` 0.3 이상은 모듈 이름이 `opendartreader`입니다
  (코드가 둘 다 처리함). 먼저 `pip install -r requirements.txt`를 실행하세요.
- DART는 2019~2025 기준 종목당 약 28회 호출됩니다. `--max-calls`(기본 6000)가 일일 한도를 넘을 만한 실행을
  막아 주고, 결과는 종목별로 `data/real/dart_cache/`에 캐시되므로 재실행 시 빠진 종목만 받습니다.
- VKOSPI: KRX에서 VKOSPI 일별 종가를 `data/krx/vkospi.csv`(일자,종가)로 내려받으세요. 그 뒤
  `fetch_real_data.py macro` 또는 `prepare_krx.py`가 `macro.parquet`에 합칩니다.

## 알려진 한계

- ECOS·DART 수집기는 실제 API로 실행해 본 적이 없습니다. `config.py`의 ECOS 시리즈 코드, DART 계정 ID
  (`IS_MAP` 등), 2년 국채금리 대용(3년 국채)은 첫 실행 때 확인이 필요합니다.
- KRX 월말 스냅샷만 사용합니다: 일별 시계열이 없어 `VOL_20D`를 만들 수 없고, 수정되지 않은 종가는 주식수 변화
  휴리스틱으로 보정하며, 사라진 종목의 상장폐지 수익률은 없습니다.
- 금융업은 종목명 키워드로만 거릅니다(업종 파일 없음). 관리종목·투자주의환기종목 기간은 KRX KIND에서 받아
  `exclusions.csv`로 만들어야 합니다.
- 시점별 애널리스트 컨센서스는 무료로 구할 수 없고, 없으면 선행 팩터 4개가 제외됩니다.
- 합성 데이터 결과는 코드 경로만 검증하며 한국 시장에 대해서는 아무것도 말해 주지 않습니다.
