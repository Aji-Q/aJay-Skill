"""P0 chart semantics: missing values, normalization, and market colors."""

from __future__ import annotations

import math
from lib.report.dim_viz import _viz_financials, _viz_kline, _viz_valuation
from assemble_report import render_dim_card, render_dim_category
from lib.report.svg_primitives import (
    svg_bars,
    svg_candlestick,
    svg_dividend_combo,
    svg_donut,
    svg_gauge,
    svg_h_bar_compare,
    svg_institutional_quarters,
    svg_progress_row,
    svg_radar,
    svg_sparkline,
    svg_thermometer,
    svg_unlock_timeline,
)


def test_missing_pe_quantile_is_explicit_and_never_neutral_50():
    html = _viz_valuation({"pe": 24.0, "industry_pe": 28.0})

    assert 'data-quantile-status="missing"' in html
    assert "PE 分位输入" in html
    assert ">—<" in html
    assert 'data-quantile-value="50"' not in html


def test_financial_health_progress_uses_normalized_bar_but_source_value_label():
    html = _viz_financials(
        {
            "financial_health": {
                "current_ratio": 2.1,
                "debt_ratio": 28,
                "fcf_margin": 60,
                "roic": 12,
            }
        }
    )

    # Current ratio is 2.1 / 3.0 = 70%; debt ratio is inverted because lower
    # leverage is healthier (100 - 28 = 72%).
    assert 'width:70.0%;height:100%' in html
    assert 'width:72.0%;height:100%' in html
    assert ">2.1<" in html
    assert ">28%<" in html


def test_us_candlestick_uses_green_up_red_down_and_legacy_default_is_preserved():
    candles = [
        {"open": 10, "close": 12, "high": 13, "low": 9, "date": "2026-01-01"},
        {"open": 12, "close": 10, "high": 13, "low": 9, "date": "2026-01-02"},
    ]

    us_html = svg_candlestick(candles, market="U")
    legacy_html = svg_candlestick(candles)
    assert us_html.count('fill="#059669"') >= 1
    assert us_html.count('fill="#dc2626"') >= 1
    # Existing non-US reports retain the historical red-up/green-down mapping.
    assert legacy_html.count('fill="#dc2626"') >= 1
    assert legacy_html.count('fill="#059669"') >= 1


def test_kline_passes_explicit_us_market_to_candlestick():
    candles = [
        {"open": 10 + i, "close": 11 + i, "high": 12 + i, "low": 9 + i, "date": f"2026-01-{i+1:02d}"}
        for i in range(10)
    ]
    html = _viz_kline({"candles_60d": candles, "market": "US"})
    assert 'fill="#059669"' in html
    assert 'fill="#dc2626"' not in html


def _ten_up_candles():
    return [
        {"open": 10 + i, "close": 11 + i, "high": 12 + i, "low": 9 + i, "date": f"2026-01-{i+1:02d}"}
        for i in range(10)
    ]


def test_render_dim_card_injects_top_level_market_into_kline_payload():
    html = render_dim_card(
        "2_kline",
        {"score_status": "measured", "score": 7, "label": "观察", "weight": 4},
        {"data": {"candles_60d": _ten_up_candles()}},
        market="U",
    )
    assert 'fill="#059669"' in html
    assert 'fill="#dc2626"' not in html


def test_render_dim_category_propagates_top_level_market_to_kline_card():
    raw = {"market": "U", "dimensions": {"2_kline": {"data": {"candles_60d": _ten_up_candles()}}}}
    dimensions = {"dimensions": {"2_kline": {"score_status": "measured", "score": 7, "label": "观察", "weight": 4}}}
    html = render_dim_category("mkt", dimensions, raw)
    assert 'fill="#059669"' in html
    assert 'fill="#dc2626"' not in html


def test_comps_renderer_marks_missing_percentile_instead_of_showing_50():
    from lib.report.institutional import _render_comps_block

    html = _render_comps_block(
        {"comps": {"peer_stats": {"roe": {"min": 5, "median": 10, "max": 20}}}}
    )
    assert 'data-percentile-status="missing"' in html
    assert "目标分位" in html and "—" in html
    assert "50%" not in html


def test_invalid_numeric_values_never_leak_nan_or_inf_into_chart_markup():
    invalid = [math.nan, math.inf, -math.inf]
    candles = [
        {"open": math.nan, "close": 11, "high": 12, "low": 9, "date": "bad"},
        {"open": 10, "close": 12, "high": 13, "low": 9, "date": "2026-01-01"},
    ]
    outputs = [
        svg_sparkline([1, math.nan, 3, math.inf]),
        svg_bars([1, math.nan, 3], overlay_line=[2, math.inf, 4]),
        svg_candlestick(candles, ma_20=invalid, ma_60=[10, math.nan]),
        svg_donut([("valid", 1, "#059669"), ("bad", math.nan, "#dc2626")]),
        svg_gauge(math.nan),
        svg_h_bar_compare( "A", math.nan, "B", 1),
        svg_radar(["A", "B", "C", "D"], [1, math.nan, 3, math.inf]),
        svg_progress_row("X", math.inf),
        svg_unlock_timeline([{"date": "2026", "amount": math.nan}]),
        svg_dividend_combo([2025, 2026], [1, math.nan], [math.inf, 2]),
        svg_institutional_quarters({"quarters": ["25Q1"], "fund": [math.nan]}),
        svg_thermometer(math.inf),
    ]

    for output in outputs:
        assert "nan" not in output.lower()
        assert "inf" not in output.lower()


def test_kline_and_financial_renderers_drop_invalid_series_points():
    kline = _viz_kline(
        {"close_60d": [1, math.nan, 3, math.inf], "market": "U"}
    )
    financials = _viz_financials(
        {
            "revenue_history": [100, math.nan, 120],
            "financial_years": ["Y1", "Y2", "Y3"],
            "roe_history": [math.inf, 10, 12],
            "net_profit_history": [5, math.nan, 8],
            "financial_health": {"current_ratio": math.nan, "roic": 12},
        }
    )
    assert "nan" not in kline.lower()
    assert "inf" not in kline.lower()
    assert "nan" not in financials.lower()
    assert "inf" not in financials.lower()
