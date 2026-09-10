"""End-to-end chan.v1 contract checks using the real backend builder."""
from __future__ import annotations

from datetime import date, timedelta
import math
import re

import pytest

from chan_signals import build_chan_v1
from lib.report.chan_desk import render_chan_desk


pytest.importorskip("czsc")


def _deterministic_ohlcv(days: int = 8 * 366):
    start = date(2018, 1, 1)
    rows = []
    for ordinal in range(days):
        current = start + timedelta(days=ordinal)
        # Keep weekends in the fixture so the backend's calendar normalization
        # and same-source weekly aggregation are exercised.
        base = 120.0 + 11.0 * math.sin(ordinal / 17.0) + 5.5 * math.sin(ordinal / 43.0)
        drift = 0.012 * ordinal
        close = base + drift
        open_price = close - 1.2 * math.sin(ordinal / 5.0)
        high = max(open_price, close) + 2.2 + 0.45 * (ordinal % 5)
        low = min(open_price, close) - 2.0 - 0.35 * (ordinal % 4)
        rows.append({
            "Date": current.isoformat(),
            "Open": round(open_price, 6),
            "High": round(high, 6),
            "Low": round(low, 6),
            "Close": round(close, 6),
            "Volume": 1_000_000 + ordinal,
        })
    return rows


def _panel(html: str, level: str) -> str:
    match = re.search(
        rf'<section class="chan-level-panel"[^>]*data-chan-level-panel="{level}".*?</section>',
        html,
        flags=re.S,
    )
    assert match, f"missing {level} panel"
    return match.group(0)


def test_real_builder_round_trips_both_levels_and_six_explanation_steps():
    chan = build_chan_v1(
        "FIXTURE",
        _deterministic_ohlcv(),
        market="U",
        source="fixture://deterministic-ohlcv",
        adjusted=True,
        computed_at="2026-09-10T12:00:00+00:00",
        history_years=6,
        daily_years=2,
    )
    output = render_chan_desk({"dimensions": {"2_kline": {"data": {"chan": chan}}}})

    assert chan["schema_version"] == "chan.v1"
    assert 'data-chan-version="chan.v1"' in output
    assert chan["levels"]["D"]["bars"]
    assert chan["levels"]["W"]["bars"]
    assert len(chan["levels"]["D"]["bars"]) > len(chan["levels"]["W"]["bars"])

    for level in ("D", "W"):
        level_data = chan["levels"][level]
        panel = _panel(output, level)
        assert panel.count("data-chan-step-card=") == 6
        assert panel.count('class="chan-step-observation"') == 6
        assert "最近完成笔" in panel
        assert str(len(level_data["bars"])) in panel
        assert all(step.get("title") and step.get("explanation") for step in level_data["steps"])
        for step in level_data["steps"]:
            assert step["title"] in panel
            assert step["explanation"] in panel
        # Real bars are retained as their actual level, not relabeled fallback
        # observations; the final source-backed date is present in the SVG.
        assert f'data-bar-index="{len(level_data["bars"]) - 1}"' in panel
        for bi in level_data["bis"]:
            assert str(bi["id"]) in panel
            assert f'{bi["start_price"]:,.2f}' in panel
            assert f'{bi["end_price"]:,.2f}' in panel
        for fractal in level_data.get("fractals", []):
            assert str(fractal["id"]) in panel
        for center in level_data.get("centers", []):
            assert str(center["id"]) in panel
            for bi_id in center.get("bi_ids", []):
                assert str(bi_id) in panel
        unfinished = level_data.get("unfinished_bi")
        if unfinished:
            assert str(unfinished["id"]) in panel
            assert unfinished.get("status") == "unfinished"
        for invalidation in level_data.get("invalidations", []):
            assert f'data-structure-id="{invalidation["id"]}"' in panel


def test_real_builder_provenance_reaches_each_level_panel():
    chan = build_chan_v1(
        "FIXTURE",
        _deterministic_ohlcv(),
        source="fixture://same-source",
        adjusted=False,
        computed_at="2026-09-10T12:00:00+00:00",
        history_years=6,
        daily_years=2,
    )
    output = render_chan_desk(chan)
    assert output.count("来源：fixture://same-source") == 2
    assert output.count("口径：原始价格") == 2
    assert output.count("截至：") >= 2


def test_real_price_action_program_coordinates_reach_workbench_and_ledger():
    from price_action import enrich_chan_price_action
    chan = build_chan_v1('FIXTURE', _deterministic_ohlcv(), market='U', source='fixture://same-price-input', adjusted=True)
    price_action = enrich_chan_price_action(chan)
    output = render_chan_desk({'dimensions': {'2_kline': {'data': {'chan': chan, 'price_action': price_action}}}})
    for level in ('D', 'W'):
        panel = _panel(output, level)
        pa = price_action['levels'][level]
        assert 'data-pa-layer="ma"' in panel
        assert 'data-pa-layer="volume"' in panel
        assert 'class="chan-plot-viewport chan-price-viewport"' in panel
        for record in pa['levels'] + pa['events']:
            assert f'data-pa-point="{record["id"]}"' in panel
            assert f'data-pa-select="{record["id"]}"' in panel
            assert f'data-price="{record["price"]}"' in panel
            assert record['evidence'] in panel
        # UI does not manufacture confirmed signals or extrapolate beyond source bars.
        assert all(record['anchor_index'] < len(chan['levels'][level]['bars']) for record in pa['events'])
        assert 'chan-expert' not in panel
