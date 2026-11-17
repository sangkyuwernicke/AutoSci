# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:46cd31e7 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   bd dolt push
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->


## 프로젝트 개요

**ML 팩터 × 거시 변수 초과수익 실험 (KOSPI/KOSDAQ)** — AutoSci(ΩmegaWiki) 저장소의 `experiments/ml-factor-shap` 브랜치 작업 디렉터리.
기업 팩터 + 거시 변수로 **다음 달 초과수익(시장 대비) 분류**를 학습하고, 트리 앙상블 vs 선형 베이스라인을 비교한 뒤
상위 종목 백테스트와 거시 레짐별 SHAP 분석까지 수행하는 **walk-forward 파이프라인**이다.

- 상위 저장소 루트(`/Users/sangkyu/Work/AutoSci`)의 `CLAUDE.md`는 ΩmegaWiki 런타임 계약이다(wiki/raw/runtime 규칙). 이 디렉터리의 실험 코드는 그와 별개이며, `tools/` 아래 파일들은 위키 도구 복사본 + 한국어 뉴스 수집/감성 분석기다.
- 문서: `README.md`(영문), `README.ko.md`(국문). 설계 결정·알려진 한계는 README의 "Design decisions to review", "Known gaps" 참고.
- 응답·문서는 한국어로 작성한다(사용자 선호).

## 빌드 & 테스트

```bash
# 환경: .venv/bin/python 우선 → conda → python3 (.env 의 API 키는 tools/_env.py 가 자동 로드)
pip install -r requirements.txt

# 합성 데이터 스모크 (API 키 불필요)
python run_experiment.py --quick --out results/quick
python run_experiment.py --data synthetic --trials 10 --out results/synth
python run_experiment.py --data synthetic --macro-role gating --trials 15 --out results/synth_gated

# 실데이터
python prepare_krx.py --krx-dir data/krx --out data/real                 # 수동 다운로드 KRX 파일 → parquet
python prepare_marcap.py --marcap-dir data/marcap/data --out data/real   # (대안) marcap 일별 시총 데이터 → 일별 가격
python fetch_real_data.py macro --out data/real --start-year 2019        # ECOS 거시 (+ data/krx/vkospi.csv)
python fetch_real_data.py fundamentals --out data/real --market KOSPI --top-n-mcap 100 --start-year 2019   # DART 재무
python run_experiment.py --quick --data real --raw-dir data/real --out results/q_base
python run_experiment.py --data real --raw-dir data/real --macro-role gating --out results/<run>_gating

# 비교·파일럿
python compare_runs.py results/q_base results/q_ext --labels base extended --out results/base_vs_ext
python pilot_suite.py --raw-dir data/real --out-root results/pilot
python factor_ic.py --data real --raw-dir data/real --price-only --market KOSPI --start-date 2020-01-02

# 테스트 (오프라인, pytest 없이 스크립트로 실행)
for t in lookahead forward universe krx fetch pilot macro_gated target_impute topk tune_metric sentiment daily_sentiment weekly_sentiment summary_table; do python tests/test_$t.py; done
```

- 린터/포매터/CI 설정은 없다. 코드 변경 후에는 위 `tests/` 스크립트를 실행해 확인한다.
- `--quick` = KOSPI, 시총 상위 100, 2021-01-01부터, 학습 2021+ / 테스트 2023~2025, Optuna 15 trials.
  명시적으로 준 플래그가 `--quick` 기본값을 덮어쓴다.

## 아키텍처

데이터 흐름: **원천 파일 → 패널 → 전처리 → 모델 튜닝/예측 → 평가·백테스트 → SHAP/게이팅 분석 → `results/<run>/`**

| 파일 | 역할 |
|---|---|
| `config.py` | 팩터 목록(`BASE_FACTORS` 17개, `EXTENDED_FACTORS`), 거시 변수(`MACRO`), 역수 랭크 대상(`INVERT_BEFORE_RANK`), 레짐 변수, 모델 목록, ECOS 통계 코드 |
| `run_experiment.py` | 오케스트레이션·CLI 진입점. `parse()` → `load()` → 폴드별 튜닝/예측 → 평가 → `report.md` 생성 |
| `data_synth.py` | 합성 패널(금리/장단기 스프레드 레짐에 따라 팩터 보상이 달라지는 알려진 구조) — 코드 경로 검증용 |
| `data_real.py` | `build_panel()`: 원천 파일 → 패널. 재무는 **공시일** 기준 결합, 거시는 t‑1 말일로 지연 (look-ahead 방지) |
| `universe.py` | 금융/스팩/우선주 제외, `exclusions.csv`, 재무제표 커버리지 필터 |
| `features.py` | 타깃 생성(`add_target`), 월별 winsorize(1/99) + rank-gauss/z-score, 결측 대체(`impute_ffill`), 거시 레짐화(`macro_to_regime`) |
| `models.py` | Logit(L1/L2), Ridge, DTree, RF, XGB, LGBM, CatBoost + Optuna 탐색 공간(`suggest`, `tune`), `RegimeGatedScorer`(거시 게이팅 MoE) |
| `evaluation.py` | AUC, PR-AUC, Precision@K, 백테스트(거래비용 반영), H1 쌍체 검정, H2 블록 부트스트랩 |
| `shap_analysis.py` | SHAP, 레짐 비교(순열검정), 거시×기업 상호작용 |
| `factor_ic.py` / `pilot_suite.py` / `compare_runs.py` / `data_quality.py` | 단일 팩터 rank IC, 파일럿 일괄 실행, 두 실행 쌍체 비교, 팩터 품질 리포트 |
| `prepare_krx.py` / `prepare_marcap.py` / `prepare_consensus.py` | 수동 KRX 스냅샷·marcap·벤더 컨센서스 → parquet 변환 |
| `build_news_sentiment_panel.py` / `compare_sentiment_methods.py` | BigKinds 엑셀 → 코스피 종목별 일별 뉴스 감성(KR-FinBert-SC, `--method model` 기본) / 사전 vs FinBert 비교 연구(실험 본체 아님, 감성 지수는 FinBert만 사용) |
| `daily_sentiment_ic.py` / `weekly_sentiment_ic.py` | 일·주 단위 감성 순위 IC와 롱숏·롱온리 포트폴리오(연도별, 비용 0.2%×Σ\|dw\|). 주말 기사는 다음 거래일로 이월, 진입 A(같은 날 종가, 낙관) vs B(다음 거래일 종가, 실행 가능)를 함께 보고. 주 단위는 5일 신호·5일 보유·리밸런싱 요일 5가지 평균. `compare_sentiment_methods.py`의 일별 IC는 시점이 약해 상한값 |
| `make_summary_table.py` | Firm × Macro × Sentiment 대표 표(Panel A 모델별 AUC·순 Sharpe + 통합 효과 CI, Panel B 감성 IC). 모델은 데이터에서 읽음(`--quick` 7모델·`--small-data` 모두), 전 종목 200개 보유는 `--top-q 200`, Panel B는 `--ic DIR=LABEL`. 논문용 요약은 `results/v18_paper_summary/summary_ko.md` |
| `analyze_auc_sources.py` | 모델 AUC의 출처 분해: 점수에서 변동성·규모·반전·모멘텀·가치·수익성을 월별 횡단면으로 제거한 잔차 AUC와 팩터 단독 AUC·상관(`results/v18_auc_sources/`) |
| `prepare_sentiment.py` / `sentiment.py` | 일별 FinBert 감성 → `data/real/sentiment_finbert.parquet` / 월말 팩터(`SENTIMENT_FACTORS`). `run_experiment.py --sentiment finbert`, 뉴스 없음 = 결측(ffill·max-missing 제외), 뉴스는 2025-12까지라 `--test-end 2025` |
| `fetch_real_data.py` | ECOS(거시), Open DART(재무) 수집기 (재개 가능, 호출 횟수 제한 `--max-calls`) |
| `tools/fetch_news_bigkinds.py`, `fetch_news_naver.py`, `analyze_news_sentiment.py` | 한국어 뉴스 수집(BigKinds, 네이버 검색 API) 및 감성 분석(사전 기반 / KR-FinBert-SC). 출력 스키마(JSONL/CSV)는 공통 |
| `data/` | `krx/`(스냅샷·지수·VKOSPI), `marcap/`(외부 repo 클론), `real/`(parquet, DART 캐시), `news/` |
| `results/` | 실행별 산출물. `v2…v14_*` 는 반복 실험 버전(`_feature` = 거시를 입력 피처로, `_gating` = 게이팅), `pilot/`, `agents/`(TradingAgents 결과) |

### 두 가지 거시 사용 방식 (`--macro-role`)

- `feature`(기본): 거시 변수를 기업 팩터와 동일 수준의 입력으로 사용. Firm-only vs Firm+Macro 비교(H1).
- `gating`: 거시 변수는 `RegimeGatedScorer`의 게이팅 네트워크에만 입력되어 레짐 가중치 α_k(m_t)를 만들고, 최종 점수는 Σ α_k·p_k(z_i). 직접 예측변수로는 쓰이지 않는다. 추가 산출물 `gating_factor_weights.csv`, 레짐 중심 플롯.

### 가설

- **H1**: 거시 포함(또는 게이팅) 모델이 기업 팩터 단독 모델보다 월별 AUC/Precision@K가 높은가 (쌍체 t, Wilcoxon, 부트스트랩 CI, Holm 보정).
- **H2**: 모델의 Sharpe가 로지스틱 대비 우월한가 (3개월 블록 순환 부트스트랩).
- **H3**: 거시 레짐(테스트 기간 중앙값 상/하) 별로 SHAP 중요도·방향이 달라지는가.

## 컨벤션 & 주의사항

**Look-ahead 방지 (최우선 불변식)**
- Walk-forward는 *레이블 월(t+1)의 연도* 기준: 테스트 연도 Y에 대해 ≤Y‑2 튜닝, Y‑1 검증, ≤Y‑1 재학습, Y 예측.
- 재무는 공시일 이후에만, 거시는 t‑1 말일로 지연, 컨센서스는 날짜 ≤ t 이고 45일 이내 스냅샷만 사용. 실현된 미래 실적을 추정치 대용으로 쓰지 않는다.
- 팩터/피처 로직을 바꾸면 반드시 `tests/test_lookahead.py`, `tests/test_forward.py`를 실행한다.

**모델링 규약**
- 가치 비율(PER, PBR, PCR, EV_EBITDA, FWD_PER)은 **역수로 랭크**한다. 컬럼명은 그대로이므로 `PER`의 SHAP 양(+) 방향 = *저평가*.
- 타깃: `--target direction`(기본) 또는 `excess`, `--target-quantile 0.8`(상위 20% 라벨, 1:4 고정) 은 margin 라벨과 배타적. 라벨이 다른 실행끼리는 쌍체 비교 불가.
- 비용: 리밸런싱마다 `0.20% × Σ|dw|`; Sharpe는 rf=0, 월수익×√12; 회전율은 편도(0.5×Σ|dw|).
- Ridge는 이진 레이블에 대한 선형확률모형. CatBoost는 수치형 피처만 사용.
- 소표본(파일럿)은 분해능이 낮다 — `report.md`의 "Resolving power"를 읽고 p값이 아닌 효과 크기·구간을 해석한다. `--small-data`는 얕고 강하게 정규화된 탐색 공간 + 모델 3종(logit, lgbm, catboost).

**뉴스 감성 (`--sentiment finbert`)**
- 감성 지수는 **KR-FinBert-SC 하나만** 쓴다(사전 방식은 실험에서 제외, 비교 연구용 코드만 남김). 뉴스 없음은 0이 아니라 **결측**이고 `impute_ffill`·`--max-missing`을 거치지 않는다. 뉴스가 2025-12-31까지라 `--test-end 2025`로 제한한다(범위를 넘으면 경고).
- 일·주 단위 평가는 BigKinds에 시각이 없어 진입 시점을 A(낙관)와 B(보수) 두 가지로 함께 보고하고 **B를 실행 가능한 값으로 읽는다**. 월 단위 모델은 월말 하루 전(`--sentiment-lag-days 1`)까지의 뉴스만 쓴다.
- LLM으로 감성을 다시 매기면 학습 데이터가 2015~2025를 포함해 look-ahead가 생길 수 있다. 종목명을 가린 대조 실행으로 점검하고, BigKinds 기사의 외부 API 전송이 약관상 허용되는지 먼저 확인한다.
- `NEWS_COUNT_1M`처럼 시가총액과 상관된 팩터는 `--residualize-on ... mcap`으로 규모를 통제하기 전에는 해석하지 않는다.

**평가 설정 (원래 설계 vs quick)**
- 원래 설계는 코스피 전 종목(`--top-n-mcap 0`, 월 약 650종목) 중 `--top-k 200`개 보유, 1차 벤치마크는 공식 KOSPI200 동일가중 지수(`KOSPI200_EW_OFFICIAL`). `--quick`은 월 약 91종목이라 기본 `--top-k 200`이 전 종목 보유가 되어 `report.md`·`metrics.csv`의 CAGR/Sharpe/MDD/Precision@K가 모델 간 동일하다(경고 출력). 이 경우 AUC와 `compare_runs.py`(상위 20% 재선정)로 비교하거나 `--top-k 20`을 쓴다. 결과 요약은 README의 "Evidence so far".

**데이터 규칙**
- **KRX 자동 수집(pykrx, FinanceDataReader의 KRX 엔드포인트 등) 금지** — 약관 위반 및 IP 차단. 수동 다운로드 파일만 사용한다.
- 월말 스냅샷 전용 경로는 `VOL_20D` 없음, 종가 미조정(주식수 변동 휴리스틱으로 보정), 상폐 수익률 없음 → 결과가 약간 상향 편향.
- ECOS/DART 수집기는 실제 API로 검증된 적 없음 — 첫 실행 시 ECOS 코드(`config.py`), DART 계정 ID(`IS_MAP`), 2년물 프록시(3년 KTB) 확인.
- 합성 데이터 결과는 코드 경로 검증용일 뿐 한국 시장에 대한 증거가 아니다.

**비밀·산출물**
- `.env`(API 키: ECOS, DART, NAVER 등)는 절대 커밋/출력하지 않는다. `.gitignore`는 `__pycache__/`, `docs_cache/`만 제외한다.
- `results/`는 git에 추적된다(csv/png/report.md/parquet). 새 실험은 `results/<버전>_<설명>_<feature|gating>` 형식의 별도 디렉터리에 저장하고 기존 결과를 덮어쓰지 않는다.

**코드 스타일**
- Python, 모듈은 최상위 평면 구조. 커밋 메시지는 `<type>: <description>` (feat, fix, refactor, docs, test, chore …).
- 새 CLI 옵션은 `run_experiment.py`의 `parse()`에 추가하고 README(영/국문)에 반영한다.
- `AGENTS.md`는 이 파일과 독립된 별도 파일이다. 실질적인 내용을 바꾸면 양쪽에 반영한다.
