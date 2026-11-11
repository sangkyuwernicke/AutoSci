"""Fetch and cache market/disclosure/flow data for the pilot universe.

Pilot Spec: experiments/pilot/kospi-information-diet-vs-reasoning-scaffold.yaml

Three sources, each independently cacheable to disk so re-runs don't re-hit
external APIs:
  - OHLCV via yfinance (used by both D1 and D5)
  - DART disclosures via OpenDART's list.json endpoint (D5 only; corp domain
    verified live: opendart.fss.or.kr, NOT opendart.fse.or.kr — the latter
    does not resolve)
  - Investor net-flow (foreign/institutional/individual net buys) via pykrx,
    which requires KRX_ID/KRX_PW in the environment for this specific endpoint
    (D5 only)
"""

from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass

import pandas as pd
import requests
import yfinance as yf

DART_BASE_URL = "https://opendart.fss.or.kr/api"


@dataclass(frozen=True)
class NameSpec:
    key: str  # e.g. "samsung"
    yf_ticker: str  # e.g. "005930.KS"
    krx_code: str  # e.g. "005930"
    dart_corp_code: str | None  # None for ETFs with no DART history (e.g. KODEX 200)


def fetch_ohlcv(ticker: str, period: str, cache_dir: pathlib.Path) -> pd.DataFrame:
    """Fetch one ticker's daily OHLCV, using a local CSV cache if present."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"ohlcv_{ticker.replace('.', '_')}.csv"

    if cache_path.exists():
        return pd.read_csv(cache_path, index_col=0, parse_dates=True)

    history = yf.Ticker(ticker).history(period=period)
    if history.empty:
        raise RuntimeError(f"yfinance returned no data for ticker '{ticker}'")

    history.index = history.index.tz_localize(None)
    history.to_csv(cache_path)
    return history


def fetch_all_ohlcv(names: list[NameSpec], period: str, cache_dir: pathlib.Path) -> dict[str, pd.DataFrame]:
    return {name.yf_ticker: fetch_ohlcv(name.yf_ticker, period, cache_dir) for name in names}


# Routine, high-frequency, low-information-content filing types — excluded so the
# DART channel isn't dominated by noise. Confirmed live: these made up the large
# majority of both Samsung's (96 total) and SK Hynix's (51 total) raw filing counts.
_DART_NOISE_TITLE_SUBSTRINGS = (
    "임원ㆍ주요주주특정증권등소유상황보고서",  # routine executive/major-shareholder ownership report
    "조회공시요구",  # exchange inquiry request/response — procedural, not a company disclosure
    "풍문또는보도",  # rumor/press clarification — usually denies or is non-committal
)

# How many document.xml bodies to fetch per name — caps API calls and prompt length.
_DART_MAX_BODY_FETCHES = 8


def _is_substantive_filing(report_nm: str) -> bool:
    return not any(noise in report_nm for noise in _DART_NOISE_TITLE_SUBSTRINGS)


def _strip_dart_xml_to_text(xml_bytes: bytes, max_chars: int = 600) -> str:
    """Crude plain-text extraction from a DART document.xml filing body.

    DART's DOCUMENT schema is a proprietary table-heavy XML (TABLE/TR/TD), not
    prose — there is no single generic schema across report types (each report
    type has different table layouts), so a proper structured parser is a
    per-report-type project (flagged as a known full-study engineering risk).
    This strips all tags and collapses whitespace: good enough to surface real
    numbers/dates/terms from the filing into the LLM prompt, not a clean summary.
    """
    try:
        text = xml_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = xml_bytes.decode("euc-kr", errors="replace")
    # Some filings render as HTML with a leading <style>/<script> block (raw CSS/JS
    # text, which plain tag-stripping does NOT remove since it isn't inside angle
    # brackets) — caught live: a filing's first 600 chars came back as pure CSS.
    # Strip these blocks (tag + content) before the generic tag-strip below.
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def fetch_dart_document_body(rcept_no: str, cache_dir: pathlib.Path, api_key: str) -> str:
    """Fetch and flatten one filing's body text via OpenDART's document.xml endpoint."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"dart_body_{rcept_no}.txt"
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    response = requests.get(
        f"{DART_BASE_URL}/document.xml", params={"crtfc_key": api_key, "rcept_no": rcept_no}, timeout=30
    )
    response.raise_for_status()

    import io
    import zipfile

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        xml_bytes = zf.read(zf.namelist()[0])
    body_text = _strip_dart_xml_to_text(xml_bytes)

    cache_path.write_text(body_text, encoding="utf-8")
    return body_text


def fetch_dart_disclosures(
    corp_code: str,
    name_key: str,
    lookback_days: int,
    cache_dir: pathlib.Path,
    api_key: str,
) -> list[dict]:
    """Fetch recent DART disclosure list + body snippets for one corp_code.

    Two stages: (1) list.json for the filing list, filtered to substantive
    report types (see _DART_NOISE_TITLE_SUBSTRINGS); (2) document.xml for the
    body text of up to _DART_MAX_BODY_FETCHES of the most recent substantive
    filings. Returns a list of {rcept_dt, report_nm, rcept_no, body_snippet}
    dicts, most recent first. `body_snippet` is "" for filings beyond the fetch
    cap (list-only, title still usable). Raises RuntimeError on OpenDART list
    API failure (distinguishing that from "status 013 / no data", which is not
    an error).
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"dart_{name_key}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    end_date = pd.Timestamp.today()
    start_date = end_date - pd.Timedelta(days=lookback_days)

    response = requests.get(
        f"{DART_BASE_URL}/list.json",
        params={
            "crtfc_key": api_key,
            "corp_code": corp_code,
            "bgn_de": start_date.strftime("%Y%m%d"),
            "end_de": end_date.strftime("%Y%m%d"),
            "page_count": 100,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    status = payload.get("status")
    if status == "013":  # OpenDART's "no data found" status — not an error
        filings: list[dict] = []
    elif status != "000":
        raise RuntimeError(f"OpenDART list.json error for {name_key}: status={status} message={payload.get('message')}")
    else:
        filings = [
            {"rcept_dt": item["rcept_dt"], "report_nm": item["report_nm"], "rcept_no": item["rcept_no"]}
            for item in payload.get("list", [])
            if _is_substantive_filing(item["report_nm"])
        ]

    for filing in filings[:_DART_MAX_BODY_FETCHES]:
        try:
            filing["body_snippet"] = fetch_dart_document_body(filing["rcept_no"], cache_dir, api_key)
        except Exception as error:  # noqa: BLE001 - pilot diagnostic: a body-fetch failure degrades to title-only, not a crash
            filing["body_snippet"] = f"(body fetch failed: {type(error).__name__})"
    for filing in filings[_DART_MAX_BODY_FETCHES:]:
        filing["body_snippet"] = ""

    cache_path.write_text(json.dumps(filings, ensure_ascii=False, indent=2), encoding="utf-8")
    return filings


def fetch_investor_flow(krx_code: str, name_key: str, lookback_days: int, cache_dir: pathlib.Path) -> pd.DataFrame:
    """Fetch daily foreign/institutional/individual net-buy value via pykrx.

    Requires KRX_ID/KRX_PW in the environment (pykrx logs into the KRX data
    portal internally for this endpoint). Raises RuntimeError with a clear
    message if the call returns empty — this is the pilot's designated
    'named blocker' signal for the investor-flow channel specifically.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"flow_{name_key}.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path, index_col=0, parse_dates=True)

    from pykrx import stock  # imported lazily — this module prints a login banner on import

    end_date = pd.Timestamp.today()
    start_date = end_date - pd.Timedelta(days=lookback_days + 15)  # small buffer for non-trading days

    df = stock.get_market_trading_value_by_date(
        start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"), krx_code
    )
    if df.empty:
        raise RuntimeError(
            f"pykrx returned no investor-flow data for {name_key} ({krx_code}) — "
            "check KRX_ID/KRX_PW are set and valid (pykrx silently returns an "
            "empty frame on login/endpoint failure rather than raising)"
        )

    df.to_csv(cache_path)
    return df
