"""Offline provenance checks for the aJay hero's historical-price chart."""
from __future__ import annotations

import pytest

from lib.report.evidence import render_hero_chart


def _raw(**kline_metadata):
    return {
        "fetched_at": "2099-12-31T23:59:59+00:00",
        "dimensions": {
            "2_kline": {
                "source": "fixture:historical_closes",
                "data": {"close_60d": [100, 101, 99]},
                **kline_metadata,
            },
        },
    }


@pytest.mark.parametrize("metadata", [
    {"fallback": True},
    {"error": "provider failed"},
    {"quality": "error"},
    {"_pipeline": {"quality": "missing"}},
    {"stale": True},
    {"_pipeline": {"stale": True}},
    {"_pipeline": {"quality": "stale"}},
    {"source": "skip"},
    {"applicable": False},
])
def test_failed_stale_or_inapplicable_series_stays_empty(metadata):
    html = render_hero_chart(_raw(**metadata))
    assert "hero-chart-empty" in html
    assert "<svg" not in html
    assert "<figure" not in html


def test_stale_series_is_labeled_as_expired_not_just_missing():
    assert "价格证据已过期" in render_hero_chart(_raw(stale=True))


@pytest.mark.parametrize("quality", ["full", "partial"])
def test_normal_available_observations_remain_visible_without_fabricated_dates(quality):
    html = render_hero_chart(_raw(_pipeline={"quality": quality}))
    assert "<svg" in html
    assert "3 OBS." in html
    assert "观测日期未记录或未对齐" in html
    assert "2099-12-31" not in html
    assert "fixture:historical_closes" in html


def _dated_raw():
    raw = _raw()
    raw["dimensions"]["2_kline"]["data"]["candles_60d"] = [
        {"date": "2026-09-03", "close": 100},
        {"date": "2026-09-04", "close": 101},
        {"date": "2026-09-08", "close": 99},
    ]
    return raw


def test_dates_come_from_aligned_candles_not_collection_timestamp():
    html = render_hero_chart(_dated_raw())
    assert "观测期 2026-09-03 — 2026-09-08" in html
    assert "2099-12-31" not in html


@pytest.mark.parametrize("problem", ["length", "price", "reverse", "invalid", "missing"])
def test_unaligned_or_invalid_candle_dates_are_not_attached_to_valid_closes(problem):
    raw = _dated_raw()
    candles = raw["dimensions"]["2_kline"]["data"]["candles_60d"]
    if problem == "length":
        candles.pop()
    elif problem == "price":
        candles[0]["close"] = 777
    elif problem == "reverse":
        candles[1]["date"] = "2026-09-02"
    elif problem == "invalid":
        candles[1]["date"] = "2026-02-31"
    else:
        candles[1].pop("date")
    html = render_hero_chart(raw)
    assert "<svg" in html
    assert "观测日期未记录或未对齐" in html
    assert "观测期 2026" not in html


@pytest.mark.parametrize("values", [[100, float("nan")], [0, 100], "100,101"])
def test_malformed_price_series_is_not_drawn(values):
    raw = _raw()
    raw["dimensions"]["2_kline"]["data"]["close_60d"] = values
    assert "<svg" not in render_hero_chart(raw)


def test_chart_source_is_escaped():
    html = render_hero_chart(_raw(source='<img src=x onerror="alert(1)">'))
    assert "<img" not in html
    assert "&lt;img" in html
