"""Focused contracts for the offline Chan v1 explainer workbench."""
from __future__ import annotations

import html
from pathlib import Path

import pytest

from lib.report.chan_desk import render_chan_desk


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"


def _bars(count: int = 8):
    return [
        {
            "index": i,
            "id": f"bar-{i}",
            "dt": f"2026-01-{i + 1:02d}",
            "open": 100 + i,
            "high": 104 + i,
            "low": 98 + i,
            "close": 102 + i,
        }
        for i in range(count)
    ]


def _chan_payload():
    return {
        "version": "chan.v1",
        "capabilities": {
            "segments": True,
            "macd_divergence": False,
            "official_signals": False,
        },
        "levels": {
            "D": {
                "status": "available",
                "bars": _bars(),
                "provenance": {"source": "fixture-source", "period": "2024—2026"},
                "fractals": [
                    {"id": "fx-top", "bar_index": 3, "dt": "2026-01-04", "mark": "top", "price": 107}
                ],
                "bis": [
                    {
                        "id": "bi-1",
                        "start_index": 0,
                        "end_index": 3,
                        "start_price": 102,
                        "end_price": 105,
                        "sdt": "2026-01-01",
                        "edt": "2026-01-04",
                        "dir": "up",
                        "high": 107,
                        "low": 98,
                        "power": 3,
                    }
                ],
                "unfinished_bi": {
                    "id": "ubi-1",
                    "status": "unfinished",
                    "repainting": True,
                    "start_index": 3,
                    "end_index": 7,
                    "start_price": 105,
                    "end_price": 109,
                    "dir": "up",
                    "high": 111,
                    "low": 103,
                },
                "centers": [
                    {"id": "zs-1", "bi_ids": ["bi-1"], "sdt": "2026-01-01", "edt": "2026-01-04", "zg": 105, "zd": 101}
                ],
                "signals": [
                    {
                        "id": "sig-3b",
                        "type": "三买候选",
                        "anchor_index": 7,
                        "level": 109,
                        "evidence": "explicit evidence",
                        "invalid_if": "跌回 105",
                        "divergence": {"method": "bi_power_proxy", "confirmed": False},
                    },
                    {"id": "sig-2s", "type": "二卖", "anchor_index": 6, "level": 108},
                ],
                "steps": [
                    {
                        "id": "step-1",
                        "level": "D",
                        "annotation_ids": ["bi-1", "zs-1", "sig-3b"],
                        "title": "读取坐标",
                        "explanation": "后端提供的讲解文本",
                        "why": "原始坐标依据",
                        "next_if": "下一坐标条件",
                        "coord_refs": ["bi-1", "zs-1"],
                    }
                ],
            },
            "W": {
                "status": "available",
                "bars": _bars(5),
                "provenance": {"source": "weekly-fixture", "period": "6y"},
                "steps": [],
            },
        },
    }


def test_render_accepts_full_raw_data_and_emits_single_scoped_workbench():
    raw = {"dimensions": {"2_kline": {"data": {"chan": _chan_payload()}}}}
    output = render_chan_desk(raw, "assets/ajay-speakers/chan-analyst-source.png")

    assert output.count('id="chan-workspace"') == 1
    assert 'class="chan-desk"' in output
    assert 'data-chan-version="chan.v1"' in output
    assert "chan-analyst-source.png" not in output
    assert "THE PRICE STRUCTURE DESK" in output
    assert "价格的结构，逐笔讲清。" in output
    assert "交互价格研究台" in output
    assert "chan-expert-portrait" not in output
    assert "全览 · 1 步" in output
    assert "<script" not in output.lower()
    assert "<style" not in output.lower()


def test_static_svg_contains_coordinates_and_semantic_line_styles():
    output = render_chan_desk(_chan_payload())

    assert '<svg class="chan-chart-svg"' in output
    assert 'data-chan-chart="D"' in output
    assert 'class="chan-candle chan-candle-up"' in output
    assert 'class="chan-bi chan-bi-complete"' in output
    assert 'class="chan-bi chan-bi-unfinished"' in output
    assert 'class="chan-center-band"' in output
    assert 'class="chan-fractal-mark"' in output
    assert 'class="chan-signal-candidate"' in output
    assert 'data-bar-index="3"' in output
    assert "105" in output and "101" in output
    assert "实线 · 已完成笔" in output
    assert "虚线 · 未完成笔 / 候选" in output


def test_only_one_three_candidate_signals_are_rendered_and_proxy_is_explicit():
    output = render_chan_desk(_chan_payload())

    assert "三买候选 · 代理" in output
    assert "sig-3b" in output
    assert "二卖" not in output
    assert "sig-2s" not in output


def test_step_text_is_input_backed_and_annotation_bridge_is_serialized():
    output = render_chan_desk(_chan_payload())

    assert "后端提供的讲解文本" in output
    assert "原始坐标依据" in output
    assert "下一坐标条件" in output
    assert 'data-annotation-ids="D-bi-bi-1 D-center-zs-1 D-signal-sig-3b"' in output
    assert "只解释输入坐标" in output


def test_missing_chan_data_falls_back_to_plain_ohlc_chart():
    raw = {
        "dimensions": {
            "2_kline": {
                "data": {"candles_60d": _bars(6)},
                "status": "missing",
            }
        }
    }
    output = render_chan_desk(raw)

    assert 'data-chan-state="fallback"' in output
    assert "普通 K 线回退图" in output
    assert "普通 K 线回退图" in output
    assert "缠论结构数据不可用，仅保留输入的 OHLC 观察。" in output


def test_missing_weekly_level_does_not_relabel_daily_fallback_as_weekly():
    chan = _chan_payload()
    chan["levels"]["D"] = {"status": "missing", "bars": []}
    chan["levels"]["W"] = {"status": "missing", "bars": []}
    raw = {"dimensions": {"2_kline": {"data": {"chan": chan, "candles_60d": _bars(6)}}}}
    output = render_chan_desk(raw)

    # Daily fallback is allowed, while the W panel must remain a genuine
    # missing/empty weekly panel rather than relabeling daily observations.
    assert output.count('data-chan-state="fallback"') == 1
    assert 'id="chan-panel-W"' in output
    assert "周线数据不足" in output
    assert 'data-chan-chart="W"' in output


def test_endpoint_price_is_not_inferred_when_backend_omits_it():
    chan = _chan_payload()
    chan["levels"]["D"]["bis"][0].pop("start_price")
    chan["levels"]["D"]["bis"][0].pop("end_price")
    output = render_chan_desk(chan)

    # The record remains inspectable, but no segment is drawn from high/low guesses.
    assert 'data-annotation-id="D-bi-bi-1"' in output
    assert 'class="chan-bi chan-bi-complete"' not in output


def test_html_escaping_and_portrait_scheme_guard():
    chan = _chan_payload()
    chan["levels"]["D"]["steps"][0]["explanation"] = '<b>do not trust</b>'
    output = render_chan_desk(chan, "javascript:alert(1)")

    assert "&lt;b&gt;do not trust&lt;/b&gt;" in output
    assert "javascript:" not in output.lower()
    assert "chan-expert-portrait-placeholder" not in output


def test_asset_runtime_is_scoped_and_motion_aware():
    js = (ASSETS / "report-chan.js").read_text(encoding="utf-8")
    css = (ASSETS / "report-chan.css").read_text(encoding="utf-8")

    assert "#chan-workspace" in js or ".chan-desk#chan-workspace" in js
    assert "data-chan-action" in js
    assert "data-chan-point" in js
    assert "prefers-reduced-motion" in js
    assert "MutationObserver" in js
    assert "window.gsap" in js
    # Replay draws only semantic Chan lines (BI/condition), never generic SVG
    # geometry such as candles or plot surfaces.
    assert "getTotalLength" in js
    assert ".chan-bi,.chan-center-band,.chan-condition-line,.chan-condition-link" in js
    assert "scrollIntoView" not in js
    assert "svg.addEventListener('pointermove'" in js
    assert "addEventListener('wheel'" not in js
    assert "chartRange" in js and "setRange" in js
    assert "chan-crosshair" in js
    assert "beforeprint" in js
    assert "querySelectorAll('path'" not in js
    assert ".chan-desk-grid" in css
    assert ".chan-desk-grid{display:block" in css
    assert "@media(prefers-reduced-motion:reduce)" in css
    assert 'html[data-motion="off"]' in css


@pytest.mark.parametrize("raw", [_chan_payload(), {"version": "chan.v1", "levels": {}}])
def test_public_renderer_never_mutates_input(raw):
    import copy

    before = copy.deepcopy(raw)
    render_chan_desk(raw)
    assert raw == before


def test_chart_workbench_has_full_width_controls_and_no_persona():
    output = render_chan_desk(_chan_payload(), "data:image/png;base64,fake")
    assert '<img' not in output
    assert 'data-chan-action="next" aria-label="下一步"' in output
    assert 'data-chan-action="prev" aria-label="上一步"' in output
    assert '点选笔 / 中枢查看解释' in output
    assert 'data-chan-range="zoom-in"' in output
    assert 'data-chan-range="recent"' in output
    assert 'data-chan-overlay="ma"' in output
    assert 'class="chan-crosshair"' in output
    assert 'data-open="' in output and 'data-close="' in output
    assert '<details class="chan-step-archive" open' not in output
    assert '<details class="chan-ledger-archive">' in output


def test_price_action_uses_supplied_coordinates_and_escapes_explanations():
    chan = _chan_payload()
    chan['levels']['D']['price_action'] = {
        'moving_averages': [{'id':'ma20','label':'MA20','points':[{'index':2,'price':103},{'index':3,'price':104}]}],
        'levels':[{'id':'res1','kind':'resistance','start_index':3,'end_index':7,'price':108,'label':'阻力','evidence':'<b>source</b>','invalid_if':{'text':'收盘高于 109'}}],
        'events':[{'id':'event1','anchor_index':5,'price':108,'label':'突破观察','evidence':'实际收盘穿越','invalid_if':{'text':'跌回 108'}}],
    }
    output = render_chan_desk(chan)
    assert 'data-pa-layer="ma"' in output
    assert 'data-pa-point="res1"' in output
    assert 'data-pa-select="event1"' in output
    assert '&lt;b&gt;source&lt;/b&gt;' in output
    assert '实际收盘穿越' in output
    assert 'data-price="108"' in output
    assert '收盘高于 109' in output


def test_machine_coordinate_records_are_only_inside_collapsed_details():
    from lib.report.chan_desk import _render_step_card
    step={'id':'s','title':'失效条件','explanation':'价格观察','observation':'再突破 344.27，观察失效。','coord_refs':[{'id':'private-structure-key','side':'above','price':344.27}]}
    output=_render_step_card(step,5)
    assert '再突破 344.27' in output
    assert '坐标范围' not in output
    before=output.split('<details class="chan-coord-details">')[0]
    assert 'private-structure-key' not in before
    assert 'private-structure-key' in output
    assert '<details class="chan-coord-details" open' not in output


def test_mobile_chart_has_a_real_layout_and_compact_tool_contract():
    output = render_chan_desk(_chan_payload())
    js = (ASSETS / "report-chan.js").read_text()
    css = (ASSETS / "report-chan.css").read_text()
    assert 'data-chan-compact-tools' in output
    assert 'function chartLayout(panel)' in js
    assert 'frame.clientWidth' in js
    assert 'height:mobile?390:550' in js
    assert "setAttribute('viewBox'" in js
    assert "chartLayout(panel).mobile?44:119" in js
    assert 'layout.volumeBottom' in js and 'layout.dateY' in js
    assert '.chan-chart-svg{min-width:0;width:100%;height:390px' in css
    assert "root._chanPrinting=true" in js
