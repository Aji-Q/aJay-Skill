"""Renderer contract tests for the complete offline JTRADER.DEMO fixture."""
from __future__ import annotations

from copy import deepcopy
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from lib.report.demo_fixture import augment_demo
from lib.report.demo_fixture import _fixture_features
from lib.report.institutional import (
    _render_catalyst_calendar,
    _render_competitive_analysis,
    _render_comps_block,
    _render_dcf_block,
    _render_ic_memo,
    _render_initiating_coverage,
    _render_institutional_section,
    _render_lbo_block,
)
from lib.report.dim_viz import _viz_financials, _viz_kline


def _raw() -> dict:
    """The intentionally sparse shape emitted by preview_editorial."""
    return {
        "ticker": "JTRADER.DEMO",
        "name": "Aster Systems",
        "market": "U",
        "is_demo": True,
        "dimensions": {
            "0_basic": {"data": {
                "code": "JTRADER.DEMO", "name": "Aster Systems", "market": "U",
                "price": 184.5, "change_pct": 1.26,
                "market_cap": "128B USD (DEMO)", "pe_ttm": 28.4, "pb": 4.2,
                "industry": "Enterprise infrastructure / 演示",
            }, "source": "aJay synthetic fixture", "fallback": False},
            "1_financials": {"data": {
                "roe": "19.2%", "net_margin": "23%", "revenue_growth": "14.8%",
                "roe_history": [14.2, 16.1, 17.3, 18.0, 19.2],
                "revenue_history": [12, 14, 16, 19, 22],
                "net_profit_history": [1.7, 2.2, 3.0, 3.9, 5.1],
                "financial_years": ["Y-4", "Y-3", "Y-2", "Y-1", "Y0"],
                "financial_health": {"current_ratio": 2.1, "debt_ratio": 28,
                                     "roic": 18.2},
            }, "source": "aJay synthetic fixture", "fallback": False},
            "2_kline": {"data": {
                "close_60d": [round(142 + i * 0.72, 2) for i in range(60)],
                "stage": "Stage 2 / DEMO", "ma_align": "多头排列",
                "macd": "金叉水上", "rsi": "58",
            }, "source": "aJay synthetic fixture", "fallback": False},
            "10_valuation": {"data": {
                "pe": 28.4, "pe_quantile": "62%", "pb_quantile": "58%",
                "industry_pe": 25,
            }, "source": "aJay synthetic fixture", "fallback": False},
            "4_peers": {"data": {"peer_table": [
                {"name": "Aster (DEMO)", "pe": "28.4", "roe": "19.2%", "is_self": True},
                {"name": "Peer A (DEMO)", "pe": "25", "roe": "16%"},
            ]}, "source": "aJay synthetic fixture", "fallback": False},
            "7_industry": {"data": {
                "growth": "12% (DEMO)", "tam": "仅作布局演示", "lifecycle": "合成成长期",
            }, "source": "aJay synthetic fixture", "fallback": False},
            "14_moat": {"data": {
                "scores": {"intangible": 7, "switching": 8, "network": 5,
                           "cost": 6, "scale": 7},
                "switching": "合成高迁移成本",
            }, "source": "aJay synthetic fixture", "fallback": False},
            "15_events": {"data": {
                "recent_news": [{"title": "合成事件，不对应真实新闻"}],
                "catalyst": "演示季度财报", "earnings_preview": "待更新",
                "warnings": "样本数据",
            }, "source": "aJay synthetic fixture", "fallback": False},
        },
    }


def test_augment_is_copy_only_and_keeps_an_explicit_gap():
    raw = _raw()
    before = deepcopy(raw)
    result = augment_demo(raw)

    assert raw == before
    assert result is not raw
    assert result["fixture"]["kind"] == "synthetic"
    assert result["fixture"]["offline"] is True
    assert {"20_valuation_models", "21_research_workflow", "22_deep_methods"} <= result["dimensions"].keys()
    # Governance was not invented just to make the page look complete.
    assert "11_governance" not in result["dimensions"]
    json.dumps(result, ensure_ascii=False, allow_nan=False)


def test_institutional_renderers_show_model_cards_not_empty_states():
    result = augment_demo(_raw())
    d20 = result["dimensions"]["20_valuation_models"]["data"]
    d21 = result["dimensions"]["21_research_workflow"]["data"]
    d22 = result["dimensions"]["22_deep_methods"]["data"]

    rendered = [
        _render_dcf_block(d20),
        _render_comps_block(d20),
        _render_lbo_block(d20),
        _render_initiating_coverage(d21),
        _render_ic_memo(d22),
        _render_catalyst_calendar(d21),
        _render_competitive_analysis(d22),
        _render_institutional_section(result),
    ]
    html = "\n".join(rendered)
    for marker in (
        "DCF VALUATION", "COMPS", "QUICK LBO", "INITIATING COVERAGE",
        "IC MEMO", "CATALYST CALENDAR", "COMPETITIVE", "敏感性",
    ):
        assert marker.lower() in html.lower()
    assert "数据缺失" not in html
    assert "尚未建立" not in html
    assert "NaN" not in html and "nan" not in html


def test_financial_and_technical_visuals_use_finite_series():
    result = augment_demo(_raw())
    financial_html = _viz_financials(result["dimensions"]["1_financials"]["data"])
    technical_html = _viz_kline(result["dimensions"]["2_kline"]["data"])

    assert "<svg" in financial_html
    assert "<svg" in technical_html
    assert "NaN" not in financial_html and "NaN" not in technical_html
    assert "nan" not in financial_html.lower() and "nan" not in technical_html.lower()
    assert "candles_60d" in result["dimensions"]["2_kline"]["data"]


def test_fixture_units_and_ic_weights_are_explicit():
    result = augment_demo(_raw())
    basic = result["dimensions"]["0_basic"]["data"]
    financials = result["dimensions"]["1_financials"]["data"]
    stats = result["dimensions"]["2_kline"]["data"]["kline_stats"]
    features = _fixture_features(result)
    d20 = result["dimensions"]["20_valuation_models"]["data"]
    d21 = result["dimensions"]["21_research_workflow"]["data"]
    d22 = result["dimensions"]["22_deep_methods"]["data"]

    # The synthetic defaults use a single coherent model unit system.
    assert features["ps"] < 10
    assert features["eps"] == pytest.approx(features["price"] / features["pe"], abs=0.02)
    assert d20["dcf"]["safety_margin_pct"] > 20
    assert "DEMO" in str(basic["market_cap"])
    assert "DEMO" in financials["unit_note"]
    assert stats["volatility"] == 24.0
    assert stats["max_drawdown"] == 8.0
    assert stats["ytd_return"] == 16.0

    scenarios = d22["ic_memo"]["sections"]["VII_returns_scenarios"]
    assert [s["weight_pct"] for s in scenarios] == [25, 50, 25]
    assert all(s["probability_pct"] is None for s in scenarios)
    ic_html = _render_ic_memo(d22)
    assert "设定权重" in ic_html
    assert "p=" not in ic_html

    calendar = d21["catalyst_calendar"]
    macro_events = [e for e in calendar["events"] if e.get("category") == "macro"]
    assert macro_events and macro_events[0]["date"] == "—"
    assert "日期未核验" in macro_events[0]["event"]
    assert all(
        "DEMO" in event.get("event", "")
        for event in calendar["events"]
        if event.get("category") in {"earnings", "corporate", "industry", "macro"}
    )
