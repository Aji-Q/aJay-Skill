"""Deterministic Chan v1 and K-line provenance contract tests."""
from __future__ import annotations

from datetime import date, datetime, timedelta
import json
import math
import sys
from types import SimpleNamespace

import pytest


SCRIPTS = __import__("pathlib").Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _daily_fixture(years: int = 7) -> list[dict]:
    """Weekday-only deterministic saw-tooth series with enough D/W swings."""
    rows: list[dict] = []
    start = date(2019, 1, 1)
    for day_index in range(years * 365):
        current = start + timedelta(days=day_index)
        if current.weekday() >= 5:
            continue
        week = day_index // 7
        phase = week % 12
        swing = phase if phase <= 6 else 12 - phase
        close = 100.0 + swing * 4.0 + week * 0.06 + (current.weekday() - 2) * 0.2
        rows.append({
            "日期": current.isoformat(),
            "开盘": close - 0.4,
            "最高": close + 1.0,
            "最低": close - 1.0,
            "收盘": close,
            "成交量": 1000.0,
        })
    return rows


def test_normalize_ohlcv_drops_invalid_and_keeps_calendar_gap_policy():
    from chan_signals import normalize_ohlcv_rows

    rows = [
        {"日期": "2025-01-02", "开盘": 10, "最高": 11, "最低": 9, "收盘": 10.5, "成交量": 1},
        # Same date: the later valid record wins, but the duplicate is counted.
        {"日期": "2025-01-02", "开盘": 12, "最高": 13, "最低": 11, "收盘": 12.5, "成交量": 2},
        {"日期": "2025-01-06", "开盘": 13, "最高": 14, "最低": 12, "收盘": 13.5, "成交量": 3},
        {"日期": "2025-01-07", "开盘": float("nan"), "最高": 14, "最低": 12, "收盘": 13.5},
        {"日期": "2025-01-08", "开盘": 13, "最高": float("inf"), "最低": 12, "收盘": 13.5},
    ]
    normalized, quality = normalize_ohlcv_rows(rows)

    assert [row["date"] for row in normalized] == ["2025-01-02", "2025-01-06"]
    assert normalized[0]["close"] == 12.5
    assert quality["invalid_rows"] == 2
    assert quality["duplicate_dates"] == 1
    assert "calendar gaps are expected" in quality["gap_policy"]
    assert all(math.isfinite(row[key]) for row in normalized for key in ("open", "high", "low", "close", "volume", "amount"))


def test_build_chan_v1_exposes_renderer_bars_and_exact_six_steps():
    from chan_signals import build_chan_v1

    payload = build_chan_v1(
        "AAPL",
        _daily_fixture(),
        market="U",
        source="fixture:yahoo",
        adjusted=True,
        computed_at="2026-01-01T00:00:00Z",
    )

    assert payload["schema_version"] == "chan.v1"
    assert payload["engine_version"] == "1.0.1"
    assert payload["input_window"]["history_years"] == 6
    assert payload["input_window"]["daily_years"] == 2
    assert payload["capabilities"]["segments"] is False
    assert payload["capabilities"]["macd_divergence"] is False

    for level_name in ("D", "W"):
        level = payload["levels"][level_name]
        assert level["bar_count"] == len(level["bars"])
        assert level["bar_count"] >= 60
        assert all(
            set(("index", "id", "dt", "open", "high", "low", "close", "volume")) <= set(bar)
            and all(math.isfinite(float(bar[key])) for key in ("open", "high", "low", "close", "volume"))
            for bar in level["bars"]
        )
        assert [step["kind"] for step in level["steps"]] == [
            "raw", "fractals_and_strokes", "unfinished_stroke", "centers", "candidates", "invalidations"
        ]
        assert all({"level", "coord_refs", "explanation", "why", "next_if", "annotation_ids"} <= set(step) for step in level["steps"])
        merged = level["steps"][1]["annotation_ids"]
        assert set(x["id"] for x in level["fractals"]).issubset(merged)
        assert set(x["id"] for x in level["bis"]).issubset(merged)
        assert all(signal["status"] == "candidate" and signal["confirmed"] is False for signal in level["signals"])
        assert all("二买" not in str(signal.get("type")) and "二卖" not in str(signal.get("type")) for signal in level["signals"])
        if level["centers"]:
            assert level["centers"][-1]["status"] == "active"
            assert all(center["status"] == "completed" for center in level["centers"][:-1])
        if level["unfinished_bi"] and level["bis"]:
            unfinished = level["unfinished_bi"]
            assert unfinished["start_index"] == level["bis"][-1]["end_index"]
            assert unfinished["start_price"] == level["bis"][-1]["end_price"]
            assert unfinished["end_index"] is not None
            assert unfinished["end_price"] is not None

    # Strict JSON is a hard boundary: NaN/Inf must not leak into a report.
    json.dumps(payload, ensure_ascii=False, allow_nan=False)


def test_build_chan_v1_partial_level_keeps_real_bars():
    from chan_signals import build_chan_v1

    rows = []
    start = date(2025, 1, 2)
    for i in range(75):
        current = start + timedelta(days=i)
        if current.weekday() >= 5:
            continue
        close = 100.0 + i * 0.2
        rows.append({"日期": current.isoformat(), "开盘": close - 0.5, "最高": close + 1, "最低": close - 1, "收盘": close, "成交量": 10})
    payload = build_chan_v1("FIXTURE", rows, market="U", source="fixture", adjusted=None, computed_at="2026-01-01T00:00:00Z")
    for level in payload["levels"].values():
        assert isinstance(level["bars"], list)
        assert level["bar_count"] == len(level["bars"])
        assert level["bar_count"] > 0
        assert level["status"] in {"partial", "unavailable"}
    assert payload["adjusted"] is None
    assert payload["price_basis"] == "unspecified"


def test_two_stroke_tail_is_not_exposed_as_center():
    from chan_signals import _center_payload, normalize_ohlcv_rows

    rows, _ = normalize_ohlcv_rows([
        {"日期": "2025-01-02", "开盘": 10, "最高": 12, "最低": 9, "收盘": 11, "成交量": 1},
        {"日期": "2025-01-03", "开盘": 11, "最高": 13, "最低": 10, "收盘": 12, "成交量": 1},
        {"日期": "2025-01-06", "开盘": 12, "最高": 14, "最低": 11, "收盘": 13, "成交量": 1},
    ])
    fake_bis = [
        SimpleNamespace(sdt=rows[0]["dt"], edt=rows[1]["dt"]),
        SimpleNamespace(sdt=rows[1]["dt"], edt=rows[2]["dt"]),
    ]
    fake_zs = SimpleNamespace(
        sdt=rows[0]["dt"], edt=rows[2]["dt"], zg=12.0, zd=10.0, gg=14.0, dd=9.0,
        zz=11.0, bis=fake_bis,
    )
    bis = [
        {"id": "D:bi:0", "sdt": rows[0]["date"], "edt": rows[1]["date"]},
        {"id": "D:bi:1", "sdt": rows[1]["date"], "edt": rows[2]["date"]},
    ]
    assert _center_payload("D", 0, fake_zs, rows, bis, fake_bis) is None


def test_fetch_kline_main_wires_one_metadata_source_into_chan(monkeypatch):
    import fetch_kline

    rows = _daily_fixture()
    calls: dict[str, object] = {}

    def fake_with_metadata(ti, *, adjust="qfq", history_years=None, **_kwargs):
        calls.update({"ticker": ti.full, "adjust": adjust, "history_years": history_years})
        return {
            "rows": rows,
            "provenance": {
                "source": "fixture.provider",
                "source_id": "fixture",
                "adjustment_requested": adjust,
                "adjustment_status": "applied",
                "adjusted": True,
                "price_basis": "adjusted_ohlcv",
                "window": "6y",
            },
        }

    monkeypatch.setattr(fetch_kline.ds, "fetch_kline_with_metadata", fake_with_metadata)
    monkeypatch.setattr(fetch_kline, "fetch_chip_distribution", lambda _ti: {})
    result = fetch_kline.main("AAPL")

    assert calls == {"ticker": "AAPL", "adjust": "qfq", "history_years": 6}
    provenance = result["data"]["kline_provenance"]
    assert provenance["source"] == "fixture.provider"
    assert provenance["source_chain"]
    assert provenance["adjusted"] is True
    assert provenance["adjustment_status"] == "applied"
    chan = result["data"]["chan"]
    assert chan["source"] == "fixture.provider"
    assert chan["adjusted"] is True
    assert chan["levels"]["D"]["bar_count"] == len(chan["levels"]["D"]["bars"])


def test_yahoo_v8_adjustment_metadata_and_ohlc_scaling(monkeypatch):
    from lib import data_sources as ds

    class Response:
        status_code = 200

        def json(self):
            return {"chart": {"result": [{
                "timestamp": [1760000000],
                "indicators": {
                    "quote": [{"open": [10], "close": [20], "high": [22], "low": [8], "volume": [100]}],
                    "adjclose": [{"adjclose": [10]}],
                },
            }]}}

    monkeypatch.setattr(ds.requests, "get", lambda *args, **kwargs: Response())
    rows = ds._yahoo_v8_chart("AAPL", range_="6y", adjusted=True)

    assert rows[0]["收盘"] == 10.0
    assert rows[0]["开盘"] == 5.0
    assert rows.provenance["source_id"] == "yahoo_v8"
    assert rows.provenance["adjustment_status"] == "applied"
    assert rows.provenance["adjusted"] is True


def test_us_akshare_window_is_dynamic(monkeypatch):
    from lib import data_sources as ds

    class FakeAK:
        def __init__(self):
            self.kwargs = None

        def stock_us_hist(self, **kwargs):
            self.kwargs = kwargs
            return __import__("pandas").DataFrame([{
                "日期": "2025-01-02", "开盘": 10, "最高": 11, "最低": 9, "收盘": 10, "成交量": 1
            }])

    fake_ak = FakeAK()
    monkeypatch.setattr(ds, "yf", None)
    monkeypatch.setattr(ds, "ak", fake_ak)
    monkeypatch.setattr(ds, "requests", None)
    ti = SimpleNamespace(code="AAPL")
    rows, provenance = ds._kline_us_chain_with_metadata(ti, range_="6y", adjust="qfq")

    assert rows and fake_ak.kwargs["adjust"] == "qfq"
    assert fake_ak.kwargs["start_date"] != "20240101"
    assert len(fake_ak.kwargs["start_date"]) == 8
    assert provenance["source_id"] == "akshare_us_hist"
    assert provenance["adjusted"] is True


def test_one_level_failure_preserves_other_level_and_actual_weekly_bars(monkeypatch):
    import chan_signals as module
    real = module._level_from_rows
    def fail_weekly(ticker, level, rows):
        if level == 'W':
            raise RuntimeError('fixture weekly calculation failure')
        return real(ticker, level, rows)
    monkeypatch.setattr(module, '_level_from_rows', fail_weekly)
    result = module.build_chan_v1('FIXTURE', _daily_fixture(), source='fixture', computed_at='2026-01-01T00:00:00Z')
    assert result['status'] == 'partial'
    assert result['levels']['D']['status'] == 'ok'
    weekly = result['levels']['W']
    assert weekly['status'] == 'unavailable'
    assert weekly['bars'] and weekly['bar_count'] == len(weekly['bars'])
    assert 'fixture weekly calculation failure' in weekly['reason']


def test_monotonic_series_without_center_retains_plain_price_history():
    from chan_signals import build_chan_v1
    start = date(2025, 1, 1)
    rows = []
    for i in range(300):
        day = start + timedelta(days=i)
        if day.weekday() < 5:
            price = 100 + i
            rows.append({'Date': day.isoformat(), 'Open': price, 'High': price + 2, 'Low': price - 1, 'Close': price + 1, 'Volume': 1000})
    result = build_chan_v1('NO_CENTER', rows, source='fixture', computed_at='2026-01-01T00:00:00Z')
    daily = result['levels']['D']
    assert daily['bar_count'] > 60
    assert not daily['centers'] and not daily['signals']
    assert daily['bars'][-1]['close'] == rows[-1]['Close']
