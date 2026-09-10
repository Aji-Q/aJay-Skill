"""Complete the offline ``JTRADER.DEMO`` report fixture.

This module is deliberately a data-only fixture adapter.  It never resolves a
ticker, reads a provider, or makes a network request.  ``augment_demo`` takes
the small snapshot produced by :mod:`preview_editorial`, returns a deep-copied
snapshot, and fills the institutional model dimensions using the project's
existing pure computation functions.

The values in this file are synthetic UI inputs.  They are not observations
for a listed security and must remain visibly labelled as a fixture in the
report provenance.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
import math
from typing import Any, Mapping


FIXTURE_ID = "JTRADER.DEMO"
FIXTURE_SOURCE = "fixture:JTRADER.DEMO synthetic/offline"
FIXTURE_DATE = date(2026, 9, 9)


def _dimension(data: dict[str, Any], model: str) -> dict[str, Any]:
    """Build a raw dimension envelope with explicit fixture provenance."""
    return {
        "data": data,
        "source": f"{FIXTURE_SOURCE} · {model}",
        "fallback": False,
        "synthetic": True,
        "fixture_id": FIXTURE_ID,
    }


def _to_number(value: Any, default: float = 0.0) -> float:
    """Parse a finite number without allowing NaN/Infinity into the fixture."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _add_synthetic_financial_inputs(raw: dict[str, Any]) -> None:
    """Add deterministic inputs used by the financial and visual renderers."""
    dimensions = raw.setdefault("dimensions", {})

    basic_entry = dimensions.setdefault(
        "0_basic", _dimension({}, "base identity")
    )
    basic = basic_entry.setdefault("data", {})
    # Keep the demo's price / market cap / share count in one unit system.  The
    # original compact preview used ``128B USD`` beside a model value in
    # ``亿元``; the fixture now labels the same synthetic value explicitly.
    if basic.get("market_cap") == "128B USD (DEMO)":
        basic["market_cap"] = "1,280 亿（DEMO）"
    basic.setdefault("market_cap_yi", 1280.0)
    basic.setdefault("shares_outstanding_yi", 6.938)
    basic.setdefault("eps", 6.496)
    basic.setdefault("bvps", 43.96)
    basic.setdefault("unit_note", "金额以 DEMO 亿元计；价格与每股指标为同一演示单位")
    basic_entry.setdefault("synthetic", True)
    basic_entry.setdefault("fixture_id", FIXTURE_ID)

    financial_entry = dimensions.setdefault(
        "1_financials", _dimension({}, "base financial history")
    )
    financials = financial_entry.setdefault("data", {})
    # The compact preview's 12→22 revenue series made a 1,280-yi market cap
    # look like PS 58x, and its 5.1-yi profit implied EPS 0.735 rather than the
    # displayed price / PE pair.  Normalize only those known preview defaults;
    # caller-supplied fixture histories remain untouched.
    if financials.get("revenue_history") == [12, 14, 16, 19, 22]:
        financials["revenue_history"] = [100.0, 120.0, 145.0, 170.0, 195.0]
    if financials.get("net_profit_history") == [1.7, 2.2, 3.0, 3.9, 5.1]:
        financials["net_profit_history"] = [18.0, 23.0, 30.0, 38.0, 45.1]
    if financials.get("fcf") == "4.8B USD":
        financials["fcf"] = "45.1 亿（DEMO）"

    # These are intentionally coherent synthetic series.  They make the
    # existing chart renderer useful without implying a real filing.
    financials.setdefault("operating_cash_flow_yi", 45.1)
    financials.setdefault("gross_margin", 42.0)
    financials.setdefault("dividend_years", ["Y-4", "Y-3", "Y-2", "Y-1", "Y0"])
    financials.setdefault("dividend_amounts", [0.22, 0.25, 0.29, 0.33, 0.38])
    financials.setdefault("dividend_yields", [0.7, 0.8, 0.9, 1.0, 1.1])
    financials.setdefault("unit_note", "金额字段以 DEMO 亿元计；不是财报观测")
    health = financials.setdefault("financial_health", {})
    health.setdefault("fcf_margin", 23.1)
    health.setdefault("total_debt", 140.0)
    health.setdefault("cash", 110.0)
    health.setdefault("equity", 305.0)
    financial_entry.setdefault("synthetic", True)
    financial_entry.setdefault("fixture_id", FIXTURE_ID)


def _add_synthetic_technical_inputs(raw: dict[str, Any]) -> None:
    """Give the K-line card OHLC, moving averages, and finite indicators."""
    dimensions = raw.setdefault("dimensions", {})
    entry = dimensions.setdefault("2_kline", _dimension({}, "technical history"))
    data = entry.setdefault("data", {})
    closes = [
        _to_number(value)
        for value in (data.get("close_60d") or [])
    ]
    closes = [value for value in closes if value > 0]
    if not closes:
        closes = [100.0 + index * 0.35 for index in range(60)]
        data["close_60d"] = closes

    # The preview already has closes.  Add aligned candles rather than
    # replacing them, so the historical-price chart can render its richer
    # candlestick path and retain the original fixture narrative.
    if not data.get("candles_60d"):
        candles = []
        for index, close in enumerate(closes):
            previous = closes[index - 1] if index else close - 0.45
            open_price = round(previous + (0.18 if index % 2 else -0.12), 4)
            high = round(max(open_price, close) + 0.85 + (index % 3) * 0.08, 4)
            low = round(min(open_price, close) - 0.75 - (index % 2) * 0.06, 4)
            candles.append({
                "date": (FIXTURE_DATE - timedelta(days=len(closes) - index - 1)).isoformat(),
                "open": open_price,
                "high": high,
                "low": low,
                "close": round(close, 4),
                "volume": 1000 + index * 17,
            })
        data["candles_60d"] = candles

    if not data.get("ma20_60d"):
        ma20 = []
        for index in range(len(closes)):
            window = closes[max(0, index - 19): index + 1]
            ma20.append(round(sum(window) / len(window), 4))
        data["ma20_60d"] = ma20
    if not data.get("ma60_60d"):
        ma60 = []
        for index in range(len(closes)):
            window = closes[max(0, index - 59): index + 1]
            ma60.append(round(sum(window) / len(window), 4))
        data["ma60_60d"] = ma60

    data.setdefault(
        "indicators",
        {
            "kdj_k": 68.0,
            "kdj_d": 62.0,
            "kdj_j": 80.0,
            "obv_trend_up": True,
            "williams_r": -36.0,
        },
    )
    stats = data.setdefault("kline_stats", {})
    stats.setdefault("beta", 1.08)
    # The feature/rule layer consumes percentage points, not fractions.  Also
    # normalize the legacy fractional demo values when a caller supplies them.
    for key, default in (
        ("volatility", 24.0),
        ("max_drawdown", 8.0),
        ("ytd_return", 16.0),
    ):
        value = stats.get(key, default)
        number = _to_number(value, default)
        stats[key] = round(number * 100, 2) if 0 < abs(number) <= 1 else number
    stats.setdefault("unit_note", "波动、回撤、YTD 均为百分比点（DEMO）")
    entry.setdefault("synthetic", True)
    entry.setdefault("fixture_id", FIXTURE_ID)


def _add_synthetic_peer_inputs(raw: dict[str, Any]) -> None:
    """Provide enough clearly fake peers for the Comps renderer to be useful."""
    dimensions = raw.setdefault("dimensions", {})
    entry = dimensions.setdefault("4_peers", _dimension({}, "synthetic peer set"))
    data = entry.setdefault("data", {})
    peers = data.setdefault("peer_table", [])
    for peer in peers:
        if isinstance(peer, dict) and peer.get("is_self"):
            # ``compute_dim_20`` normalises peers before ``build_comps_table``;
            # carry the self marker through the canonical ticker so the target
            # row is not counted as a comparable company.
            peer.setdefault("ticker", raw.get("ticker", FIXTURE_ID))
    synthetic_peers = [
        {
            "name": "Peer A (DEMO)",
            "ticker": "SYNTH.PEER.A",
            "pe": 25.0,
            "pb": 3.5,
            "ps": 4.1,
            "ev_ebitda": 15.0,
            "ev_sales": 4.5,
            "roe": 16.0,
            "net_margin": 19.0,
            "revenue_growth": 10.0,
            "market_cap_yi": 820.0,
        },
        {
            "name": "Peer B (DEMO)",
            "ticker": "SYNTH.PEER.B",
            "pe": 29.0,
            "pb": 4.0,
            "ps": 4.8,
            "ev_ebitda": 17.0,
            "ev_sales": 5.3,
            "roe": 18.0,
            "net_margin": 21.0,
            "revenue_growth": 14.0,
            "market_cap_yi": 1040.0,
        },
        {
            "name": "Peer C (DEMO)",
            "ticker": "SYNTH.PEER.C",
            "pe": 33.0,
            "pb": 4.6,
            "ps": 5.5,
            "ev_ebitda": 19.0,
            "ev_sales": 6.1,
            "roe": 14.0,
            "net_margin": 17.0,
            "revenue_growth": 18.0,
            "market_cap_yi": 1460.0,
        },
    ]
    for peer in synthetic_peers:
        matching = next(
            (
                old for old in peers
                if isinstance(old, dict)
                and (
                    old.get("ticker") == peer["ticker"]
                    or old.get("name") == peer["name"]
                )
            ),
            None,
        )
        if matching is None:
            peers.append(peer)
        else:
            # preview_editorial starts with a compact Peer A row.  Fill only
            # missing keys, preserving any explicitly supplied fixture value.
            for key, value in peer.items():
                matching.setdefault(key, value)
    # The legacy visualizer can also display direct comparison rows.
    data.setdefault(
        "peer_comparison",
        [
            {"name": "PE", "self": 28.4, "peer": 29.0},
            {"name": "PB", "self": 4.2, "peer": 4.0},
            {"name": "ROE", "self": 19.2, "peer": 16.0},
        ],
    )
    entry.setdefault("synthetic", True)
    entry.setdefault("fixture_id", FIXTURE_ID)


def _add_synthetic_industry_and_event_inputs(raw: dict[str, Any]) -> None:
    """Add only the deterministic fields consumed by competitive/catalyst views."""
    dimensions = raw.setdefault("dimensions", {})

    industry_entry = dimensions.setdefault(
        "7_industry", _dimension({}, "synthetic industry context")
    )
    industry = industry_entry.setdefault("data", {})
    industry.setdefault("penetration", "21% (DEMO)")
    industry.setdefault("cninfo_metrics", {"total_mcap_yi": 18000.0})
    industry_entry.setdefault("synthetic", True)
    industry_entry.setdefault("fixture_id", FIXTURE_ID)

    events_entry = dimensions.setdefault(
        "15_events", _dimension({}, "synthetic event calendar")
    )
    events = events_entry.setdefault("data", {})
    catalyst = events.get("catalyst")
    if not isinstance(catalyst, list):
        # Preserve the original preview text as one synthetic forward event.
        original = str(catalyst).strip() if catalyst not in (None, "") else ""
        catalyst = []
        if original:
            catalyst.append({
                "date": "2026-09-30",
                "event": original,
                "impact": "medium",
                "expectation": "合成演示节点；不代表真实日历",
            })
        events["catalyst"] = catalyst
    events["catalyst"].extend([
        item for item in [
            {
                "date": "2026-10-15",
                "event": "产品路线图评审（DEMO）",
                "impact": "medium",
                "expectation": "观察收入质量与资本效率假设",
            },
            {
                "date": "2026-11-05",
                "event": "行业需求窗口（DEMO）",
                "impact": "low",
                "expectation": "仅作滚动研究流程占位",
            },
        ]
        if not any(
            isinstance(old, dict) and old.get("event") == item["event"]
            for old in events["catalyst"]
        )
    ])
    warnings = events.get("warnings")
    if not isinstance(warnings, list):
        # Keep the preview's scalar warning shape (the catalyst builder only
        # turns list entries into calendar events).  The explicit fixture
        # notice below carries the no-real-probability disclosure without
        # turning it into a fake high-impact event.
        events.setdefault(
            "synthetic_notice",
            "合成样本没有实测新闻、胜率或收益概率；需补真实证据后再判断。",
        )
    events_entry.setdefault("synthetic", True)
    events_entry.setdefault("fixture_id", FIXTURE_ID)


def _normalise_dates_for_fixture(dim21_data: dict[str, Any]) -> None:
    """Remove wall-clock dependence from the research products.

    ``build_catalyst_calendar`` is also used in live reports and therefore
    calls ``datetime.now``.  A fixture should render identically in every run,
    so its generated dates are replaced with a short, deterministic schedule.
    """
    initiating = dim21_data.get("initiating_coverage") or {}
    headline = initiating.get("headline") or {}
    if isinstance(headline, dict):
        headline["report_date"] = FIXTURE_DATE.isoformat()

    morning = dim21_data.get("morning_note") or {}
    if isinstance(morning, dict):
        morning["date"] = FIXTURE_DATE.isoformat()

    calendar = dim21_data.get("catalyst_calendar") or {}
    if not isinstance(calendar, dict):
        return
    calendar["generated_at"] = FIXTURE_DATE.isoformat()
    events = calendar.get("events") or []
    future_index = 0
    for event in events:
        if not isinstance(event, dict):
            continue
        category = event.get("category")
        if category == "past":
            event["date"] = (FIXTURE_DATE - timedelta(days=7)).isoformat()
        elif category == "forward":
            event["date"] = (
                FIXTURE_DATE + timedelta(days=21 + future_index * 17)
            ).isoformat()
            future_index += 1
        elif category == "earnings":
            event["date"] = (FIXTURE_DATE + timedelta(days=28)).isoformat()
        elif category == "corporate":
            event["date"] = (FIXTURE_DATE + timedelta(days=30)).isoformat()
        elif category == "industry":
            event["date"] = (FIXTURE_DATE + timedelta(days=60)).isoformat()
        elif category == "macro":
            # Do not turn the pure builder's rough FOMC cadence into an
            # apparently verified calendar commitment in a demo report.
            event["date"] = "—"
            event["event"] = "宏观会议窗口（DEMO · 日期未核验）"
            event["expectation"] = "仅作情景占位；不对应具体 FOMC 日程"
        elif category == "risk":
            event["date"] = FIXTURE_DATE.isoformat()

        if category in {"earnings", "corporate", "industry"}:
            label = str(event.get("event") or "自动研究节点")
            if "DEMO" not in label:
                event["event"] = f"{label}（DEMO · 自动情景）"
            expectation = str(event.get("expectation") or "").strip()
            if expectation and "DEMO" not in expectation:
                event["expectation"] = f"{expectation}（DEMO）"

    # The source builder documents the generic macro slot as FOMC.  Keep the
    # fixture's method log truthful without presenting that slot as a dated
    # external event.
    if isinstance(dim21_data.get("catalyst_calendar"), dict):
        log = dim21_data["catalyst_calendar"].get("methodology_log") or []
        dim21_data["catalyst_calendar"]["methodology_log"] = [
            str(item).replace("FOMC", "宏观窗口（DEMO）") for item in log
        ]
        dim21_data["catalyst_calendar"]["notice"] = (
            "DEMO 日历仅验证渲染流程；自动节点与日期均不代表真实公告或会议安排。"
        )


def _fixture_features(raw: dict[str, Any]) -> dict[str, Any]:
    """Extract model features through the same pure adapter as live reports."""
    from lib.stock_features import extract_features, sanitize_features

    features = sanitize_features(extract_features(raw, raw.get("dimensions", {})))
    basic = (raw.get("dimensions", {}).get("0_basic") or {}).get("data") or {}
    financials = (raw.get("dimensions", {}).get("1_financials") or {}).get("data") or {}
    health = financials.get("financial_health") or {}

    # ``extract_features`` intentionally leaves evidence missing when a live
    # provider did not report it.  The fixture supplies the same values as
    # explicit, named model inputs so DCF/Comps/LBO can exercise full paths.
    market_cap = _to_number(basic.get("market_cap_yi"), 1280.0)
    price = _to_number(basic.get("price"), 184.5)
    shares = _to_number(basic.get("shares_outstanding_yi"), market_cap / price)
    equity = _to_number(health.get("equity"), 305.0)
    revenue = _to_number(features.get("revenue_latest_yi"), 195.0)
    net_income = _to_number(features.get("net_profit_latest_yi"), 45.1)
    fcf = _to_number(features.get("fcf_latest_yi"), 45.1)
    roe_history = financials.get("roe_history") or [14.2, 16.1, 17.3, 18.0, 19.2]
    latest_roe = _to_number(roe_history[-1] if roe_history else 19.2, 19.2)
    revenue_growth = _to_number(
        features.get("revenue_growth_3y_cagr"),
        _to_number(financials.get("revenue_growth"), 14.8),
    )

    features.update({
        "ticker": raw.get("ticker", FIXTURE_ID),
        "name": raw.get("name") or basic.get("name") or "Aster Systems",
        "price": price,
        "market_cap_yi": market_cap,
        "shares_outstanding_yi": shares,
        "revenue_latest_yi": revenue,
        "net_profit_latest_yi": net_income,
        "fcf_latest_yi": fcf,
        "fcf_known": True,
        "fcf_positive": fcf > 0,
        "ebitda_yi": _to_number(features.get("ebitda_yi"), net_income / 0.6),
        "total_debt_yi": _to_number(health.get("total_debt"), 140.0),
        "cash_yi": _to_number(health.get("cash"), 110.0),
        "equity_yi": equity,
        "gross_margin": _to_number(financials.get("gross_margin"), 42.0),
        "eps": round(net_income / shares, 3) if shares > 0 else 0.0,
        "bvps": round(equity / shares, 3) if shares > 0 else 0.0,
        "roe_last": latest_roe,
        # Older research builders still read this compatibility alias.
        "rev_growth_3y": revenue_growth,
        "revenue_growth_3y_cagr": revenue_growth,
        "industry_growth": _to_number(features.get("industry_growth"), 12.0),
        "market_share": _to_number(features.get("market_share"), 7.11),
    })
    return features


def _mark_model_output(output: dict[str, Any], model: str) -> dict[str, Any]:
    """Attach fixture provenance without changing renderer-facing model keys."""
    output = deepcopy(output)
    output["source"] = f"{FIXTURE_SOURCE} · {model}"
    output["synthetic"] = True
    output["fixture_id"] = FIXTURE_ID
    output["notice"] = (
        "合成 UI fixture：模型数字用于验证渲染与交互，不代表真实证券、实测收益、"
        "收益概率或胜率。"
    )
    return output


def augment_demo(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Return a complete, deterministic copy of an ``is_demo`` raw snapshot.

    Non-demo snapshots are copied and returned untouched.  For demo snapshots
    this function enriches the existing technical/financial cards, adds the
    20/21/22 institutional dimensions, and deliberately leaves unavailable
    dimensions (for example ``11_governance``) absent so empty-state behaviour
    remains testable.
    """
    if not isinstance(raw, Mapping):
        raise TypeError("augment_demo expects a mapping snapshot")
    result = deepcopy(dict(raw))
    if not result.get("is_demo"):
        return result

    result.setdefault("ticker", FIXTURE_ID)
    result.setdefault("name", "Aster Systems")
    result.setdefault("market", "U")
    result["fixture"] = {
        "id": FIXTURE_ID,
        "kind": "synthetic",
        "offline": True,
        "notice": (
            "All values are synthetic UI fixture inputs; no real security or "
            "measured return probability is represented."
        ),
    }
    if not isinstance(result.get("dimensions"), dict):
        result["dimensions"] = {}
    # Preview output uses these envelopes, but normalising malformed entries
    # keeps the fixture adapter a useful pure test helper as well.
    for key, model in (
        ("0_basic", "base identity"),
        ("1_financials", "base financial history"),
        ("2_kline", "technical history"),
        ("4_peers", "synthetic peer set"),
        ("7_industry", "synthetic industry context"),
        ("10_valuation", "synthetic valuation card"),
        ("15_events", "synthetic event calendar"),
    ):
        entry = result["dimensions"].get(key)
        if not isinstance(entry, dict):
            result["dimensions"][key] = _dimension({}, model)
        elif not isinstance(entry.get("data"), dict):
            entry["data"] = {}

    _add_synthetic_financial_inputs(result)
    _add_synthetic_technical_inputs(result)
    _add_synthetic_peer_inputs(result)
    _add_synthetic_industry_and_event_inputs(result)

    # Reuse the canonical pure model builders; no fetcher is imported or run.
    from compute_deep_methods import compute_dim_20, compute_dim_21, compute_dim_22

    features = _fixture_features(result)
    dim20 = compute_dim_20(features, result)
    dim20_data = _mark_model_output(dim20["data"], "compute_dim_20 / DCF-Comps-LBO")
    result["dimensions"]["20_valuation_models"] = _dimension(
        dim20_data, "compute_dim_20 / DCF-Comps-LBO"
    )

    dim21 = compute_dim_21(features, result, dim20_data)
    dim21_data = deepcopy(dim21["data"])
    _normalise_dates_for_fixture(dim21_data)
    dim21_data = _mark_model_output(dim21_data, "compute_dim_21 / research-workflow")
    result["dimensions"]["21_research_workflow"] = _dimension(
        dim21_data, "compute_dim_21 / research-workflow"
    )

    dim22 = compute_dim_22(features, result, dim20_data, dim21_data)
    dim22_data = _mark_model_output(dim22["data"], "compute_dim_22 / IC-competitive")
    # Keep the renderer's historical field for schema compatibility, while
    # exposing the fixture values as analyst-set scenario weights (not measured
    # probabilities or a win rate).
    memo = dim22_data.get("ic_memo") or {}
    sections = memo.get("sections") or {}
    for scenario in sections.get("VII_returns_scenarios") or []:
        if isinstance(scenario, dict):
            base = str(scenario.get("assumptions") or "合成情景")
            weight = scenario.get("probability_pct")
            if weight is not None:
                scenario["weight_pct"] = weight
                scenario["probability_pct"] = None
            scenario["assumptions"] = (
                f"合成演示假设 · {base} · 权重不代表实测概率或胜率"
            )
    result["dimensions"]["22_deep_methods"] = _dimension(
        dim22_data, "compute_dim_22 / IC-competitive"
    )

    # Surface the DCF output in the original valuation card too.  This keeps
    # the existing 10_valuation visualizer useful while the institutional
    # section renders the full WACC/sensitivity block from dim 20.
    dcf = dim20_data.get("dcf") or {}
    sensitivity = dcf.get("sensitivity_table") or {}
    valuation_entry = result["dimensions"].setdefault(
        "10_valuation", _dimension({}, "synthetic valuation card")
    )
    valuation = valuation_entry.setdefault("data", {})
    intrinsic = dcf.get("intrinsic_per_share")
    valuation.setdefault(
        "dcf",
        f"¥{intrinsic:.2f} (DEMO)" if isinstance(intrinsic, (int, float)) else "—",
    )
    valuation.setdefault("pe_history", [22.0, 24.0, 26.0, 27.0, 28.4])
    valuation.setdefault(
        "dcf_sensitivity",
        {
            "waccs": [
                _to_number(label.rstrip("%"))
                for label in sensitivity.get("wacc_axis", [])
            ],
            "growths": [
                _to_number(label.rstrip("%"))
                for label in sensitivity.get("g_axis", [])
            ],
            "values": sensitivity.get("values_per_share", []),
            "current_price": _to_number(dcf.get("current_price"), 184.5),
        },
    )
    valuation_entry.setdefault("synthetic", True)
    valuation_entry.setdefault("fixture_id", FIXTURE_ID)

    return result


__all__ = ["augment_demo", "FIXTURE_ID", "FIXTURE_SOURCE"]
