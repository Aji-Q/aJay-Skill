"""Dimension 2 · K线 (OHLCV + 均线 + MACD + RSI + 筹码分布 + 简单形态).

补全：原方案要求覆盖
  • Stage 阶段判断 (1底/2升/3顶/4降)
  • MA5/10/20/60/120/250 多空头排列
  • MACD/RSI
  • 量价配合
  • 关键支撑/压力位 (近 250 日高低 + 斐波)
  • 形态: VCP/突破/三角收敛 (简易标记)
  • 筹码分布 stock_cyq_em
"""
from __future__ import annotations

import json
import inspect
import sys
from datetime import datetime, timedelta
from statistics import mean

import akshare as ak  # type: ignore
from lib import data_sources as ds
from lib.market_router import parse_ticker


def _ema(values, n):
    k = 2 / (n + 1)
    out, prev = [], None
    for v in values:
        prev = v if prev is None else v * k + prev * (1 - k)
        out.append(prev)
    return out


def _ma(closes, n):
    return [sum(closes[max(0, i - n + 1):i + 1]) / min(i + 1, n) for i in range(len(closes))]


def _rsi(closes, n=14):
    if len(closes) < n + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = mean(gains[-n:])
    avg_loss = mean(losses[-n:]) or 1e-9
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


# v3.8.0 · KDJ / OBV / Williams%R (参考 ashare-mcp 指标广度 · 给 D 技术派评委加料)
def _kdj(closes, highs, lows, n=9):
    """随机指标 KDJ · 返回 (K, D, J) 末值 · 数据不足返 (None,None,None)."""
    if len(closes) < n:
        return None, None, None
    k, d = 50.0, 50.0
    for i in range(n - 1, len(closes)):
        hh = max(highs[i - n + 1:i + 1])
        ll = min(lows[i - n + 1:i + 1])
        rsv = (closes[i] - ll) / (hh - ll) * 100 if hh > ll else 50.0
        k = 2 / 3 * k + 1 / 3 * rsv
        d = 2 / 3 * d + 1 / 3 * k
    j = 3 * k - 2 * d
    return round(k, 1), round(d, 1), round(j, 1)


def _obv(closes, vols):
    """能量潮 OBV · 返回 (obv_last, obv_trend_up) · 末 20 日斜率判趋势."""
    if len(closes) < 2:
        return None, None
    obv = [0.0]
    for i in range(1, len(closes)):
        if closes[i] > closes[i - 1]:
            obv.append(obv[-1] + vols[i])
        elif closes[i] < closes[i - 1]:
            obv.append(obv[-1] - vols[i])
        else:
            obv.append(obv[-1])
    trend_up = None
    if len(obv) >= 20:
        trend_up = obv[-1] > obv[-20]
    return round(obv[-1], 0), trend_up


def _williams_r(closes, highs, lows, n=14):
    """威廉指标 %R · 返回 0..-100（越接近 0 越超买 · 越接近 -100 越超卖）."""
    if len(closes) < n:
        return None
    hh = max(highs[-n:])
    ll = min(lows[-n:])
    if hh <= ll:
        return -50.0
    return round((hh - closes[-1]) / (hh - ll) * -100, 1)


def _stage(closes, ma200) -> int:
    """Weinstein Stage Analysis: 1=底部 2=上升 3=顶部 4=下降"""
    if len(closes) < 60 or ma200 is None:
        return 0
    last = closes[-1]
    ma200_now = ma200[-1]
    ma200_60ago = ma200[-60] if len(ma200) >= 60 else ma200[0]
    above = last > ma200_now
    rising = ma200_now > ma200_60ago
    if above and rising:
        return 2
    if not above and rising:
        return 1
    if above and not rising:
        return 3
    return 4


def _vcp_score(highs: list[float], lows: list[float]) -> float:
    """Simple VCP detector: range contraction over last 30 / 60 / 90 days."""
    def rng(start, end):
        if end > len(highs):
            end = len(highs)
            start = max(0, end - (end - start))
        h, l = highs[-end:-start] if start > 0 else highs[-end:], lows[-end:-start] if start > 0 else lows[-end:]
        if not h:
            return 0
        return (max(h) - min(l)) / max(min(l), 1e-9)
    r30 = rng(0, 30)
    r60 = rng(30, 60)
    r90 = rng(60, 90)
    if r60 > 0 and r90 > 0:
        return max(0, 1 - r30 / r60) + max(0, 1 - r60 / r90)
    return 0


def compute_indicators(klines: list[dict]) -> dict:
    if not klines:
        return {}
    closes = [float(r.get("收盘") or r.get("Close") or 0) for r in klines]
    highs = [float(r.get("最高") or r.get("High") or 0) for r in klines]
    lows = [float(r.get("最低") or r.get("Low") or 0) for r in klines]
    vols = [float(r.get("成交量") or r.get("Volume") or 0) for r in klines]
    if not closes or all(c == 0 for c in closes):
        return {}

    ma5, ma10, ma20, ma60, ma120, ma200 = (_ma(closes, n) for n in (5, 10, 20, 60, 120, 200))
    ema12, ema26 = _ema(closes, 12), _ema(closes, 26)
    dif = [a - b for a, b in zip(ema12, ema26)]
    dea = _ema(dif, 9)
    macd_hist = [(d - e) * 2 for d, e in zip(dif, dea)]

    last = closes[-1]
    avg_vol_5 = mean(vols[-5:]) if len(vols) >= 5 else 0
    avg_vol_20 = mean(vols[-20:]) if len(vols) >= 20 else 0

    return {
        "last_close": last,
        "ma5": ma5[-1], "ma10": ma10[-1], "ma20": ma20[-1],
        "ma60": ma60[-1], "ma120": ma120[-1], "ma200": ma200[-1] if ma200 else None,
        "above_ma20": last > ma20[-1],
        "above_ma200": last > ma200[-1] if ma200 else None,
        "ma_bull_alignment": ma5[-1] > ma10[-1] > ma20[-1] > ma60[-1] > ma120[-1],
        "macd_dif": dif[-1], "macd_dea": dea[-1], "macd_hist": macd_hist[-1],
        "macd_golden_cross": dif[-1] > dea[-1] and dif[-2] <= dea[-2] if len(dif) > 1 else False,
        "rsi_14": _rsi(closes, 14),
        # v3.8.0 · KDJ / OBV / Williams%R (D 技术派评委用 · 本地从 kline 计算)
        "kdj_k": _kdj(closes, highs, lows, 9)[0],
        "kdj_d": _kdj(closes, highs, lows, 9)[1],
        "kdj_j": _kdj(closes, highs, lows, 9)[2],
        "obv": _obv(closes, vols)[0],
        "obv_trend_up": _obv(closes, vols)[1],
        "williams_r": _williams_r(closes, highs, lows, 14),
        "year_high": max(closes[-250:]) if len(closes) >= 250 else max(closes),
        "year_low": min(closes[-250:]) if len(closes) >= 250 else min(closes),
        "pct_from_year_high": (last - max(closes[-250:])) / max(closes[-250:]) * 100 if len(closes) >= 250 else 0,
        "stage": _stage(closes, ma200),
        "vol_5_vs_20": (avg_vol_5 / avg_vol_20) if avg_vol_20 else None,
        "vcp_score": _vcp_score(highs, lows),
    }


def fetch_chip_distribution(ti) -> dict:
    """筹码分布 — akshare stock_cyq_em."""
    if ti.market != "A":
        return {}
    try:
        df = ak.stock_cyq_em(symbol=ti.code, adjust="qfq")
        if df is None or df.empty:
            return {}
        last = df.iloc[-1].to_dict()
        return {
            "profit_ratio": last.get("获利比例"),
            "avg_cost": last.get("平均成本"),
            "concentration_70": last.get("70集中度"),
            "concentration_90": last.get("90集中度"),
            "cost_low_70": last.get("70成本-低"),
            "cost_high_70": last.get("70成本-高"),
            "history_30d": df.tail(30).to_dict("records"),
        }
    except Exception as e:
        return {"error": str(e)}


STAGE_LABEL = {0: "—", 1: "Stage 1 底部", 2: "Stage 2 上升", 3: "Stage 3 顶部", 4: "Stage 4 下跌"}


def _extract_for_viz(klines: list[dict]) -> dict:
    """Produce the shape the report viz expects: candles_60d / ma20_60d / ma60_60d / kline_stats."""
    if not klines:
        return {}

    def _v(r, *keys, default=0):
        for k in keys:
            if k in r and r[k] is not None:
                try:
                    return float(r[k])
                except (ValueError, TypeError):
                    pass
        return default

    closes = [_v(r, "收盘", "Close") for r in klines]
    opens = [_v(r, "开盘", "Open") for r in klines]
    highs = [_v(r, "最高", "High") for r in klines]
    lows = [_v(r, "最低", "Low") for r in klines]

    dates = []
    for r in klines:
        d = r.get("日期") or r.get("Date") or ""
        dates.append(str(d)[:10])

    # last 60 candles
    last_n = min(60, len(klines))
    candles_60d = []
    for i in range(len(klines) - last_n, len(klines)):
        candles_60d.append({
            "date": dates[i],
            "open": round(opens[i], 2),
            "close": round(closes[i], 2),
            "high": round(highs[i], 2),
            "low": round(lows[i], 2),
        })

    ma20_full = _ma(closes, 20)
    ma60_full = _ma(closes, 60)
    ma20_60d = [round(v, 2) if i >= 19 else None for i, v in enumerate(ma20_full)][-last_n:]
    ma60_60d = [round(v, 2) if i >= 59 else None for i, v in enumerate(ma60_full)][-last_n:]

    # stats
    stats: dict = {}
    if len(closes) >= 252:
        ytd_idx = max(0, len(closes) - 252)
        ytd_return = (closes[-1] - closes[ytd_idx]) / closes[ytd_idx] * 100
        stats["ytd_return"] = f"{ytd_return:+.1f}%"
    if len(closes) >= 20:
        # annualized volatility
        rets = [(closes[i] / closes[i - 1] - 1) for i in range(1, len(closes))]
        if rets:
            import statistics as _st
            try:
                vol = _st.stdev(rets[-252:] if len(rets) >= 252 else rets) * (252 ** 0.5) * 100
                stats["volatility"] = f"{vol:.1f}%"
            except _st.StatisticsError:
                pass
        # max drawdown last 252 days
        window = closes[-252:] if len(closes) >= 252 else closes
        peak = window[0]
        max_dd = 0.0
        for c in window:
            if c > peak:
                peak = c
            dd = (c - peak) / peak
            if dd < max_dd:
                max_dd = dd
        stats["max_drawdown"] = f"{max_dd * 100:.1f}%"

    return {
        "candles_60d": candles_60d,
        "ma20_60d": ma20_60d,
        "ma60_60d": ma60_60d,
        "close_60d": [round(c, 2) for c in closes[-last_n:]],
        "kline_stats": stats,
    }


def _supports_history_years(fetch_fn) -> bool:
    """Check whether the data-source adapter exposes the Chan history opt-in.

    Tests and downstream integrations historically monkeypatch ``fetch_kline``
    with a one-argument callable.  Signature detection keeps that compatibility
    without swallowing real provider errors.
    """
    try:
        params = inspect.signature(fetch_fn).parameters
    except (TypeError, ValueError):
        return False
    return "history_years" in params or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())


def _date_from_row(row: dict) -> datetime | None:
    value = row.get("日期") or row.get("date") or row.get("Date") or row.get("datetime") or row.get("Datetime")
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if hasattr(value, "to_pydatetime"):
        try:
            return value.to_pydatetime().replace(tzinfo=None)
        except Exception:
            return None
    text = str(value).strip()
    for candidate in (text, text[:10]):
        try:
            return datetime.fromisoformat(candidate.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            continue
    return None


def _tail_years(rows: list[dict], years: int = 2) -> list[dict]:
    """Keep the ordinary K-line view at the historical two-year window."""
    dated = [(idx, _date_from_row(row)) for idx, row in enumerate(rows or [])]
    valid_dates = [dt for _, dt in dated if dt is not None]
    if not valid_dates:
        return rows
    cutoff = max(valid_dates) - timedelta(days=365 * years)
    return [row for row, (_, dt) in zip(rows, dated) if dt is None or dt >= cutoff]


def _fetch_rows_for_analysis(ti):
    """Fetch one source window and preserve provider provenance when available."""
    fetch_fn = ds.fetch_kline
    if ti.market == "U" and _supports_history_years(fetch_fn):
        metadata_fn = getattr(ds, "fetch_kline_with_metadata", None)
        if callable(metadata_fn):
            payload = metadata_fn(ti, adjust="qfq", history_years=6)
            if isinstance(payload, dict) and isinstance(payload.get("rows"), list):
                return payload["rows"], payload.get("provenance") or {}
        return fetch_fn(ti, adjust="qfq", history_years=6), {}
    return fetch_fn(ti), {}


def _build_chan(
    ti,
    daily_rows: list[dict],
    source: str,
    *,
    adjusted: bool | None = None,
    provenance: dict | None = None,
) -> dict | None:
    """Build Chan data without making a second request or breaking K-line."""
    try:
        from chan_signals import build_chan_v1

        # Chan receives the full six-year daily source window; the normal
        # K-line cards below still use only the latest two years.
        return build_chan_v1(
            ti.full,
            daily_rows,
            market=ti.market,
            source=source,
            adjusted=adjusted,
        )
    except Exception as exc:
        # A missing/failed optional Chan dependency must not remove ordinary
        # OHLCV output. Keep a machine-readable unavailable result for the
        # report evidence panel and preserve the exception for diagnostics.
        return {
            "schema_version": "chan.v1",
            "status": "unavailable",
            "engine": "czsc",
            "engine_version": None,
            "ticker": ti.full,
            "market": ti.market,
            "source": source,
            "adjusted": adjusted,
            "price_basis": "adjusted_ohlcv" if adjusted is True else "raw_ohlcv" if adjusted is False else "unspecified",
            "computed_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "as_of": None,
            "quality": {"error": f"{type(exc).__name__}: {str(exc)[:160]}"},
            "levels": {},
            "capabilities": {
                "fractals": False,
                "strokes": False,
                "centers": False,
                "segments": False,
                "macd_divergence": False,
                "official_signals": False,
            },
        }


def main(ticker: str) -> dict:
    ti = parse_ticker(ticker)
    fetched = _fetch_rows_for_analysis(ti)
    if isinstance(fetched, tuple) and len(fetched) == 2:
        source_rows, source_provenance = fetched
    else:
        # Compatibility with integrations that still return only a list.
        source_rows, source_provenance = fetched, {}
    # Keep indicators and the existing chart payload backward-compatible while
    # allowing the Chan adapter to consume the same source's six-year window.
    klines = _tail_years(source_rows, years=2) if ti.market == "U" else source_rows
    indicators = compute_indicators(klines)
    chips = fetch_chip_distribution(ti)
    viz_shape = _extract_for_viz(klines)

    # Derive stage / ma_align / macd / rsi human labels from indicators
    stage_label = STAGE_LABEL.get(indicators.get("stage", 0), "—")
    ma_align = "多头排列" if indicators.get("ma_bull_alignment") else "非多头"
    macd_label = "金叉水上" if (indicators.get("macd_golden_cross") and indicators.get("macd_dif", 0) > 0) else (
        "死叉水上" if (indicators.get("macd_dif", 0) > 0 and indicators.get("macd_hist", 0) < 0) else
        "水下" if indicators.get("macd_dif", 0) < 0 else "中性"
    )
    rsi_val = indicators.get("rsi_14")
    rsi_label = f"{rsi_val:.0f}" if rsi_val is not None else "—"
    source_chain = {
        "A": "akshare/baostock/Eastmoney/Sina/Tencent A-share history fallback chain",
        "H": "akshare/yfinance/Yahoo HK history fallback chain",
        "U": "yfinance/akshare/Yahoo/Stooq US history fallback chain",
    }.get(ti.market, "market history provider")

    source_provenance = dict(source_provenance or {})
    actual_source = source_provenance.get("source") or "unknown"
    adjusted = source_provenance.get("adjusted")
    if adjusted not in (True, False):
        adjusted = None
    chan = _build_chan(
        ti,
        source_rows,
        actual_source,
        adjusted=adjusted,
        provenance=source_provenance,
    )
    chan_window = (chan or {}).get("input_window") if isinstance(chan, dict) else {}
    provenance = {
        # ``source`` is the actual provider hit; ``source_chain`` preserves
        # the historical human-readable fallback description.
        "source": actual_source,
        "source_id": source_provenance.get("source_id"),
        "source_chain": source_provenance.get("source_chain") or source_chain,
        "requested_adjustment": "qfq",
        "adjustment_status": source_provenance.get("adjustment_status", "unknown"),
        "adjusted": adjusted,
        "price_basis": source_provenance.get("price_basis") or (
            "adjusted_ohlcv" if adjusted is True else "raw_ohlcv" if adjusted is False else "unspecified"
        ),
        "daily_window": "2y",
        "chan_history_window": "6y" if ti.market == "U" else None,
        "weekly_last_bar_date": chan_window.get("weekly_last_bar_date") if isinstance(chan_window, dict) else None,
        "weekly_last_bar_status": chan_window.get("weekly_last_bar_status", "unavailable") if isinstance(chan_window, dict) else "unavailable",
        "weekly_last_bar_is_complete": chan_window.get("weekly_last_bar_is_complete") if isinstance(chan_window, dict) else None,
        "warnings": list((chan or {}).get("warnings", [])) if isinstance(chan, dict) else [],
        "as_of": max((_date_from_row(r) for r in source_rows if _date_from_row(r)), default=None),
    }
    if provenance["as_of"] is not None:
        provenance["as_of"] = provenance["as_of"].date().isoformat()

    # Deterministic price-action evidence shares the exact Chan bar coordinates.
    from price_action import enrich_chan_price_action
    price_action = enrich_chan_price_action(chan) if isinstance(chan, dict) else {}

    return {
        "ticker": ti.full,
        "data": {
            "kline_count": len(klines),
            "price_action": price_action,
            "indicators": indicators,
            "stage": stage_label,
            "ma_align": ma_align,
            "macd": macd_label,
            "rsi": rsi_label,
            "chip_distribution": chips,
            "kline_provenance": provenance,
            **({"chan": chan} if chan is not None else {}),
            **viz_shape,
        },
        "source": source_chain,
        "fallback": False,
    }


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1] if len(sys.argv) > 1 else "002273.SZ"), ensure_ascii=False, indent=2, default=str))
