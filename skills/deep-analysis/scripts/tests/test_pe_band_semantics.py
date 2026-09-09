"""PE history chart semantics and finite-input boundaries."""
from __future__ import annotations

import math
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_pe_history_uses_actual_multiple_axis_not_inferred_percentile_band():
    from lib.report.svg_primitives import svg_pe_band

    html = svg_pe_band([22.0, 24.0, 26.0, 27.0, 28.4], width=320, height=160)

    assert 'data-pe-axis="actual"' in html
    assert "PE (x)" in html
    assert "28.4x" in html
    assert "25%" not in html
    assert "50%" not in html
    assert "75%" not in html
    assert "<rect" not in html


def test_pe_history_filters_zero_missing_and_non_finite_values():
    from lib.report.svg_primitives import svg_pe_band

    html = svg_pe_band([0, None, -1, float("nan"), float("inf"), 20.0, 21.0])

    assert '<svg' in html
    assert "20.0x" in html and "21.0x" in html
    assert "nan" not in html.lower()
    assert "inf" not in html.lower()
    assert "-1.0x" not in html


def test_pe_history_returns_empty_when_fewer_than_two_valid_observations():
    from lib.report.svg_primitives import svg_pe_band

    assert svg_pe_band([]) == ""
    assert svg_pe_band([0, None, math.nan, math.inf]) == ""
    assert svg_pe_band([None, 20.0]) == ""


def test_valuation_caption_separates_history_from_independent_percentile_input():
    from lib.report.dim_viz import _viz_valuation

    html = _viz_valuation({
        "pe": 28.4,
        "pe_quantile": "62%",
        "industry_pe": 25,
        "dcf": "¥223.13 (DEMO)",
        "pe_history": [22.0, 24.0, 26.0, 27.0, 28.4],
    })

    assert "PE 分位输入（窗口/来源待核验）" in html
    assert "PE 历史序列 · 纵轴=实际 PE" in html
    assert "红区=偏贵" not in html
    assert "设定权重" not in html
