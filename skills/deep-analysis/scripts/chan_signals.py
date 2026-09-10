"""CZSC Chan structure adapter used by the standard K-line fetcher.

The adapter deliberately exposes a small, honest chan.v1 contract:
confirmed fractals, completed/unfinished strokes, stroke-level centres and
four candidate annotations (1/3 buy and sell). It does not manufacture
segments, 2nd buy/sell points or MACD-area divergence. chan_summary is kept
as a compatibility entry point for the historical US backfill script; the
normal path should call build_chan_v1 with its own daily rows so daily and
weekly structures share one input window.
"""
from __future__ import annotations

from bisect import bisect_left
from datetime import date, datetime, timedelta, timezone
import math
import sys
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "chan.v1"
LOOKBACK = {"D": "2y", "W": "6y"}
HISTORY_YEARS = 6
DAILY_YEARS = 2
MIN_BARS = 60
POWER_DIVERGE_RATIO = 0.8
NEAR_PCT = 1.5


def _number(value: Any) -> float | None:
    """Return a finite float, treating empty/placeholder values as missing."""
    if value is None or isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _pick(row: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, "", "—", "-"):
            return row[key]
    return None


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime.combine(value, datetime.min.time())
    elif hasattr(value, "to_pydatetime"):
        try:
            dt = value.to_pydatetime()
        except Exception:
            dt = None
    else:
        text = str(value).strip()
        if not text:
            return None
        dt = None
        for candidate in (text, text[:10]):
            try:
                dt = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
                break
            except ValueError:
                continue
    if dt is None:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.replace(microsecond=0)


def _iso(value: Any) -> str | None:
    dt = _parse_dt(value)
    return dt.date().isoformat() if dt else None


def _direction(value: Any) -> str:
    text = str(value or "")
    return "up" if any(token in text for token in ("Up", "UP", "向上", "上")) else "down"


def _mark(value: Any) -> str:
    text = str(value or "")
    return "top" if any(token in text for token in ("顶", "G", "g", "top")) else "bottom"


def normalize_ohlcv_rows(rows: Iterable[Mapping[str, Any]] | None) -> tuple[list[dict], dict]:
    """Normalize Chinese/English OHLCV rows and record input quality.

    Calendar gaps (weekends and exchange holidays) are not treated as data
    errors. Only malformed/invalid rows and duplicate dates are counted and
    removed. The returned rows contain no non-finite numbers.
    """
    input_rows = list(rows or [])
    dedup: dict[date, dict] = {}
    invalid_rows = 0
    duplicate_dates = 0
    invalid_examples: list[dict] = []
    for raw_index, raw in enumerate(input_rows):
        if not isinstance(raw, Mapping):
            invalid_rows += 1
            if len(invalid_examples) < 3:
                invalid_examples.append({"index": raw_index, "reason": "row_not_mapping"})
            continue
        dt = _parse_dt(_pick(raw, "日期", "date", "Date", "datetime", "Datetime", "dt"))
        values = {
            "open": _number(_pick(raw, "开盘", "open", "Open")),
            "close": _number(_pick(raw, "收盘", "close", "Close")),
            "high": _number(_pick(raw, "最高", "high", "High")),
            "low": _number(_pick(raw, "最低", "low", "Low")),
            "volume": _number(_pick(raw, "成交量", "volume", "Volume", "vol")),
            "amount": _number(_pick(raw, "成交额", "amount", "Amount")),
        }
        reason = None
        if dt is None:
            reason = "invalid_date"
        elif any(values[k] is None for k in ("open", "close", "high", "low")):
            reason = "invalid_ohlc"
        elif min(values[k] for k in ("open", "close", "high", "low")) <= 0:
            reason = "non_positive_ohlc"
        elif values["high"] < max(values["open"], values["close"]):
            reason = "high_below_open_or_close"
        elif values["low"] > min(values["open"], values["close"]):
            reason = "low_above_open_or_close"
        if reason:
            invalid_rows += 1
            if len(invalid_examples) < 3:
                invalid_examples.append({"index": raw_index, "reason": reason})
            continue
        volume = values["volume"] if values["volume"] is not None and values["volume"] >= 0 else 0.0
        amount = values["amount"] if values["amount"] is not None and values["amount"] >= 0 else volume * values["close"]
        row = {
            "dt": dt,
            "date": dt.date().isoformat(),
            "open": values["open"],
            "close": values["close"],
            "high": values["high"],
            "low": values["low"],
            "volume": volume,
            "amount": amount,
        }
        if dt.date() in dedup:
            duplicate_dates += 1
        dedup[dt.date()] = row
    out = [dedup[k] for k in sorted(dedup)]
    quality = {
        "input_rows": len(input_rows),
        "valid_rows": len(out),
        "invalid_rows": invalid_rows,
        "duplicate_dates": duplicate_dates,
        "dropped_rows": invalid_rows + duplicate_dates,
        "date_start": out[0]["date"] if out else None,
        "date_end": out[-1]["date"] if out else None,
        "gap_policy": "calendar gaps are expected; only malformed/duplicate rows are dropped",
    }
    if invalid_examples:
        quality["invalid_examples"] = invalid_examples
    return out, quality


def aggregate_weekly(rows: Iterable[Mapping[str, Any]] | None) -> list[dict]:
    """Aggregate canonical daily rows into Monday-Friday trading weeks.

    The week date is the last valid trading date in the group. This avoids a
    Sunday timestamp and keeps anchors aligned with the source daily series.
    """
    groups: dict[date, list[Mapping[str, Any]]] = {}
    for row in rows or []:
        dt = _parse_dt(row.get("dt") or row.get("date"))
        if dt is None:
            continue
        start = dt.date() - timedelta(days=dt.weekday())
        groups.setdefault(start, []).append(row)
    out: list[dict] = []
    for week_start in sorted(groups):
        items = sorted(
            groups[week_start],
            key=lambda r: _parse_dt(r.get("dt") or r.get("date")) or datetime.min,
        )
        first, last = items[0], items[-1]
        out.append({
            "dt": _parse_dt(last.get("dt") or last.get("date")),
            "date": _iso(last.get("dt") or last.get("date")),
            "open": float(first["open"]),
            "close": float(last["close"]),
            "high": max(float(r["high"]) for r in items),
            "low": min(float(r["low"]) for r in items),
            "volume": sum(float(r.get("volume") or 0) for r in items),
            "amount": sum(float(r.get("amount") or 0) for r in items),
            "source_start": _iso(first.get("dt") or first.get("date")),
            "source_end": _iso(last.get("dt") or last.get("date")),
        })
    return out


def _trim_years(rows: list[dict], years: int) -> list[dict]:
    if not rows:
        return []
    cutoff = rows[-1]["dt"] - timedelta(days=365 * years)
    return [row for row in rows if row["dt"] >= cutoff]


def _raw_bars(ticker: str, freq_key: str, rows: list[dict]) -> list[Any]:
    from czsc import Freq, RawBar

    freq = getattr(Freq, freq_key)
    return [
        RawBar(
            symbol=ticker,
            dt=row["dt"],
            freq=freq,
            open=float(row["open"]),
            close=float(row["close"]),
            high=float(row["high"]),
            low=float(row["low"]),
            vol=float(row.get("volume") or 0),
            amount=float(row.get("amount") or 0),
            id=i,
        )
        for i, row in enumerate(rows)
    ]


def _anchor_index(value: Any, rows: list[dict]) -> int | None:
    if not rows:
        return None
    dt = _parse_dt(value)
    if dt is None:
        return None
    dates = [row["dt"].date() for row in rows]
    pos = bisect_left(dates, dt.date())
    if pos >= len(dates):
        return len(dates) - 1
    return pos


def _bar_payload(rows: list[dict]) -> list[dict]:
    """Expose finite, renderer-ready OHLCV bars for every Chan level."""
    out: list[dict] = []
    for index, row in enumerate(rows or []):
        values = {
            "open": _number(row.get("open")),
            "high": _number(row.get("high")),
            "low": _number(row.get("low")),
            "close": _number(row.get("close")),
            "volume": _number(row.get("volume")),
        }
        if any(values[key] is None for key in ("open", "high", "low", "close")):
            continue
        out.append({
            "index": index,
            "id": f"bar:{index}",
            "dt": _iso(row.get("dt") or row.get("date")),
            "open": round(values["open"], 8),
            "high": round(values["high"], 8),
            "low": round(values["low"], 8),
            "close": round(values["close"], 8),
            "volume": round(values["volume"] if values["volume"] is not None else 0.0, 8),
        })
    return out


def _czsc_version() -> str | None:
    try:
        import czsc
        return str(getattr(czsc, "__version__", None) or "unknown")
    except Exception:
        return None


def _obj_number(obj: Any, attr: str) -> float | None:
    return _number(getattr(obj, attr, None))


def _fx_payload(freq_key: str, index: int, fx: Any, rows: list[dict], confirmed: bool = True) -> dict | None:
    price = _obj_number(fx, "fx")
    dt = _parse_dt(getattr(fx, "dt", None))
    bar_index = _anchor_index(dt, rows)
    if price is None or dt is None or bar_index is None:
        return None
    uid = f"{freq_key}:fx:{index}"
    return {
        "id": uid,
        "index": index,
        "bar_index": bar_index,
        "dt": dt.date().isoformat(),
        "mark": _mark(getattr(fx, "mark", None)),
        "raw_mark": str(getattr(fx, "mark", "")),
        "price": round(price, 8),
        "confirmed": bool(confirmed),
    }


def _bi_payload(freq_key: str, index: int, bi: Any, rows: list[dict]) -> dict | None:
    sdt = _parse_dt(getattr(bi, "sdt", None))
    edt = _parse_dt(getattr(bi, "edt", None))
    start_index = _anchor_index(sdt, rows)
    end_index = _anchor_index(edt, rows)
    high = _obj_number(bi, "high")
    low = _obj_number(bi, "low")
    if sdt is None or edt is None or start_index is None or end_index is None or high is None or low is None:
        return None
    direction = _direction(getattr(bi, "direction", None))
    fx_a = getattr(bi, "fx_a", None)
    fx_b = getattr(bi, "fx_b", None)
    start_price = _obj_number(fx_a, "fx")
    end_price = _obj_number(fx_b, "fx")
    if start_price is None:
        start_price = high if direction == "down" else low
    if end_price is None:
        end_price = low if direction == "down" else high
    uid = f"{freq_key}:bi:{index}"
    payload = {
        "id": uid,
        "index": index,
        "start_index": start_index,
        "end_index": end_index,
        "sdt": sdt.date().isoformat(),
        "edt": edt.date().isoformat(),
        "dir": direction,
        "direction": direction,
        "start_price": round(start_price, 8),
        "end_price": round(end_price, 8),
        "high": round(high, 8),
        "low": round(low, 8),
    }
    for name in ("power", "power_price", "length", "rsq", "slope"):
        value = _obj_number(bi, name)
        if value is not None:
            payload[name] = round(value, 8)
    payload["annotation"] = {
        "title": "完成上行笔" if direction == "up" else "完成下行笔",
        "behavior": "上行摆动" if direction == "up" else "下行摆动",
        "text": f"{payload['sdt']} {payload['start_price']:.2f} → {payload['edt']} {payload['end_price']:.2f}",
    }
    return payload


def _center_payload(
    freq_key: str,
    index: int,
    zs: Any,
    rows: list[dict],
    bis: list[dict],
    bi_objects: list[Any],
    *,
    active: bool = False,
) -> dict | None:
    sdt = _parse_dt(getattr(zs, "sdt", None))
    edt = _parse_dt(getattr(zs, "edt", None))
    start_index = _anchor_index(sdt, rows)
    end_index = _anchor_index(edt, rows)
    values = {name: _obj_number(zs, name) for name in ("zg", "zd", "gg", "dd", "zz")}
    if sdt is None or edt is None or start_index is None or end_index is None or any(values[n] is None for n in ("zg", "zd", "gg", "dd")):
        return None
    z_bis = list(getattr(zs, "bis", []) or [])
    # A CZSC ``ZS`` can be emitted while only two strokes overlap at the
    # tail.  That is not a completed Chan centre: do not expose it as active
    # or use it as the boundary for a buy/sell candidate.
    if len(z_bis) < 3:
        return None
    tuple_ids = {(payload["sdt"], payload["edt"]): payload["id"] for payload in bis}
    ids: list[str] = []
    for bi in z_bis:
        bid = tuple_ids.get((_iso(getattr(bi, "sdt", None)), _iso(getattr(bi, "edt", None))))
        if bid is not None:
            ids.append(bid)
    if len(ids) < 3 or values["zg"] <= values["zd"]:
        return None
    uid = f"{freq_key}:zs:{index}"
    payload = {
        "id": uid,
        "index": index,
        "start_index": start_index,
        "end_index": end_index,
        "sdt": sdt.date().isoformat(),
        "edt": edt.date().isoformat(),
        "zg": round(values["zg"], 8),
        "zd": round(values["zd"], 8),
        "gg": round(values["gg"], 8),
        "dd": round(values["dd"], 8),
        "bi_ids": ids,
        "bi_count": len(z_bis) or len(ids),
        "status": "active" if active else "completed",
    }
    if values["zz"] is not None:
        payload["zz"] = round(values["zz"], 8)
    is_valid = getattr(zs, "is_valid", None)
    if isinstance(is_valid, bool):
        payload["is_valid"] = is_valid
    payload["annotation"] = {
        "title": "当前笔级中枢" if active else "历史笔级中枢",
        "behavior": "区间重叠",
        "text": f"{payload['sdt']}→{payload['edt']} · {payload['zd']:.2f}–{payload['zg']:.2f}",
    }
    return payload


def _unfinished_payload(freq_key: str, c: Any, rows: list[dict], completed_bis: list[dict] | None = None) -> dict | None:
    u = getattr(c, "ubi", None)
    if not u:
        return None
    direction = _direction(u.get("direction") if isinstance(u, Mapping) else getattr(u, "direction", None))

    def uv(name: str) -> Any:
        return u.get(name) if isinstance(u, Mapping) else getattr(u, name, None)

    high = _number(uv("high"))
    low = _number(uv("low"))
    if high is None or low is None:
        return None
    high_bar = uv("high_bar")
    low_bar = uv("low_bar")
    high_index = _anchor_index(getattr(high_bar, "dt", None), rows)
    low_index = _anchor_index(getattr(low_bar, "dt", None), rows)
    high_dt = _parse_dt(getattr(high_bar, "dt", None))
    low_dt = _parse_dt(getattr(low_bar, "dt", None))
    # The unfinished stroke starts at the last completed BI's fx_b endpoint
    # and ends at the actual current-direction extreme.  Using bars_ubi[0]
    # and bars_ubi[-1] would shift both price and date anchors after include
    # removal, which makes a front-end overlay visibly drift.
    previous = (completed_bis or [])[-1] if completed_bis else None
    start_price = previous.get("end_price") if previous else None
    start_index = previous.get("end_index") if previous else None
    start_dt = _parse_dt(previous.get("edt")) if previous else None

    # A few czsc releases expose the UBI extreme but not its ``*_bar``
    # object.  Reconstruct only the coordinate from the source rows after the
    # previous completed endpoint; never use the first UBI bar or the last
    # candle merely because it is convenient.
    search_from = max(int(start_index or 0), 0)
    candidates = list(enumerate(rows[search_from:], start=search_from))
    if direction == "up" and (high_index is None or high_dt is None) and candidates:
        high_index, high_row = max(candidates, key=lambda pair: float(pair[1]["high"]))
        high_dt = _parse_dt(high_row.get("dt") or high_row.get("date"))
    if direction == "down" and (low_index is None or low_dt is None) and candidates:
        low_index, low_row = min(candidates, key=lambda pair: float(pair[1]["low"]))
        low_dt = _parse_dt(low_row.get("dt") or low_row.get("date"))
    if direction == "up":
        end_price, end_index, end_dt = high, high_index, high_dt
    else:
        end_price, end_index, end_dt = low, low_index, low_dt
    if start_price is None:
        start_price = low if direction == "up" else high
    if end_price is None:
        return None
    return {
        "id": f"{freq_key}:ubi",
        "status": "unfinished",
        "repainting": True,
        "dir": direction,
        "direction": direction,
        "start_index": start_index,
        "end_index": end_index,
        "start_price": round(float(start_price), 8),
        "end_price": round(float(end_price), 8),
        "high_index": high_index,
        "low_index": low_index,
        "high": round(high, 8),
        "low": round(low, 8),
        "sdt": _iso(start_dt),
        "edt": _iso(end_dt),
        "annotation": {"title": "未完成笔", "behavior": "当前摆动仍可能重绘", "text": "仅作观察，不进入确认信号"},
    }


def _candidate(
    freq_key: str,
    index: int,
    kind: str,
    label: str,
    bi: dict,
    level: float,
    rule: str,
    evidence: dict,
    invalid_if: dict | None = None,
    divergence: dict | None = None,
) -> dict:
    payload = {
        "id": f"{freq_key}:signal:{index}",
        "kind": kind,
        "type": label,
        "status": "candidate",
        "confirmed": False,
        "at": bi["edt"],
        "anchor_index": bi["end_index"],
        "level": round(float(level), 8),
        "rule": rule,
        "evidence": evidence,
        "invalid_if": invalid_if,
    }
    if invalid_if and "below" in invalid_if:
        payload["invalid_below"] = invalid_if["below"]
    if invalid_if and "above" in invalid_if:
        payload["invalid_above"] = invalid_if["above"]
    if divergence:
        payload["divergence"] = divergence
    payload["annotation"] = {
        "title": label if "候选" in label else f"{label}候选",
        "behavior": "结构候选，等待后续 K 线确认",
        "text": rule,
    }
    return payload


def _level_error(freq_key: str, rows: list[dict] | int, reason: str) -> dict:
    bars = _bar_payload(rows) if isinstance(rows, list) else []
    return {
        "freq": freq_key,
        "status": "unavailable",
        "reason": reason,
        "bars": bars,
        "bar_count": len(bars),
        "bi_count": 0,
        "zs_count": 0,
        "fractals": [],
        "fx_list": [],
        "bis": [],
        "centers": [],
        "zs_list": [],
        "unfinished_bi": None,
        "ubi": None,
        "signals": [],
        "bsp_candidates": [],
        "error": reason,
    }


def _level_from_rows(ticker: str, freq_key: str, rows: list[dict]) -> dict:
    if len(rows) < MIN_BARS:
        return _level_error(freq_key, rows, f"{ticker} {freq_key} 仅 {len(rows)} 根有效 K 线，至少需要 {MIN_BARS} 根")
    from czsc import CZSC

    raw_bars = _raw_bars(ticker, freq_key, rows)
    c = CZSC(raw_bars)
    bi_objects = list(getattr(c, "bi_list", []) or [])
    zs_objects = list(getattr(c, "zs_list", []) or [])
    fractals = []
    for i, fx in enumerate(list(getattr(c, "fx_list", []) or [])):
        item = _fx_payload(freq_key, i, fx, rows, confirmed=True)
        if item:
            fractals.append(item)
    unfinished_fractals = []
    for i, fx in enumerate(list(getattr(c, "ubi_fxs", []) or [])):
        item = _fx_payload(freq_key, i, fx, rows, confirmed=False)
        if item:
            unfinished_fractals.append(item)

    bis = []
    for i, bi in enumerate(bi_objects):
        item = _bi_payload(freq_key, i, bi, rows)
        if item:
            bis.append(item)
    centers = []
    for i, zs in enumerate(zs_objects):
        item = _center_payload(freq_key, i, zs, rows, bis, bi_objects)
        if item:
            centers.append(item)
    # Some raw ZS objects can be filtered (e.g. two-stroke tail).  Mark the
    # last *accepted* centre active, not the last raw object index.
    if centers:
        for center in centers:
            center["status"] = "completed"
            if isinstance(center.get("annotation"), dict):
                center["annotation"]["title"] = "历史笔级中枢"
        centers[-1]["status"] = "active"
        if isinstance(centers[-1].get("annotation"), dict):
            centers[-1]["annotation"]["title"] = "当前笔级中枢"

    price = float(rows[-1]["close"])
    last = bis[-1] if bis else None
    out: dict[str, Any] = {
        "freq": freq_key,
        "status": "ok" if len(bis) >= 3 else "partial",
        "bars": _bar_payload(rows),
        "bar_count": len(rows),
        "bar_start": rows[0]["date"],
        "bar_end": rows[-1]["date"],
        "price": round(price, 8),
        "bi_count": len(bis),
        "zs_count": len(centers),
        "fractals": fractals,
        "fx_list": fractals,
        "unfinished_fractals": unfinished_fractals,
        "bis": bis,
        "centers": centers,
        "zs_list": centers,
        "signals": [],
        "bsp_candidates": [],
        "position": "无中枢(单边走势)",
        "unfinished_bi": _unfinished_payload(freq_key, c, rows, bis),
        "ubi": _unfinished_payload(freq_key, c, rows, bis),
        "capabilities": {
            "fractals": hasattr(c, "fx_list"),
            "strokes": hasattr(c, "bi_list"),
            "centers": hasattr(c, "zs_list"),
            # This release intentionally exposes no line-segment contract,
            # even if a future czsc build adds a similarly named attribute.
            "segments": False,
            "macd_divergence": False,
            "official_signals": False,
        },
    }
    out["last_bi"] = dict(last) if last else None

    if centers:
        z = centers[-1]
        zg, zd, gg, dd = z["zg"], z["zd"], z["gg"], z["dd"]
        out["zs"] = dict(z)
        if price > zg:
            out["position"] = "中枢上方" + ("(贴近上沿)" if (price - zg) / zg * 100 < NEAR_PCT else "")
        elif price < zd:
            out["position"] = "中枢下方" + ("(贴近下沿)" if (zd - price) / zd * 100 < NEAR_PCT else "")
        else:
            near = "贴近上沿" if (zg - price) / zg * 100 < NEAR_PCT else "贴近下沿" if (price - zd) / zd * 100 < NEAR_PCT else "中部"
            out["position"] = f"中枢内({near})"

        def bi_dt(item: dict) -> date:
            return date.fromisoformat(item["sdt"])

        after = [item for item in bis if bi_dt(item) >= date.fromisoformat(z["edt"])] or bis[-2:]
        ups = [item for item in after if item["dir"] == "up"]
        downs = [item for item in after if item["dir"] == "down"]
        cands = out["bsp_candidates"]
        if ups and downs and ups[-1]["high"] > zg and downs[-1]["sdt"] > ups[-1]["sdt"] and downs[-1]["low"] > zg:
            up, down = ups[-1], downs[-1]
            cands.append(_candidate(
                freq_key, len(cands), "third_buy_candidate", "三买", down, down["low"],
                f"向上笔突破 zg {zg:.2f} 后回调低点 {down['low']:.2f} 未回中枢",
                {"center_id": z["id"], "stroke_ids": [up["id"], down["id"]]},
                {"below": round(zg, 8)},
            ))
        if ups and downs and downs[-1]["low"] < zd and ups[-1]["sdt"] > downs[-1]["sdt"] and ups[-1]["high"] < zd:
            down, up = downs[-1], ups[-1]
            cands.append(_candidate(
                freq_key, len(cands), "third_sell_candidate", "三卖", up, up["high"],
                f"向下笔跌破 zd {zd:.2f} 后反弹高点 {up['high']:.2f} 未回中枢",
                {"center_id": z["id"], "stroke_ids": [down["id"], up["id"]]},
                {"above": round(zd, 8)},
            ))

        all_downs = [item for item in bis if item["dir"] == "down"]
        all_ups = [item for item in bis if item["dir"] == "up"]
        if len(bis) >= 3 and len(all_downs) >= 2 and all_downs[-1]["low"] < dd:
            current, previous = all_downs[-1], all_downs[-2]
            cp, pp = current.get("power"), previous.get("power")
            if cp is not None and pp is not None and cp < pp * POWER_DIVERGE_RATIO:
                cands.append(_candidate(
                    freq_key, len(cands), "first_buy_candidate", "一买候选", current, current["low"],
                    f"创新低 {current['low']:.2f}<dd {dd:.2f} 且笔力度 {cp:.4f} < 前笔 {pp:.4f}×{POWER_DIVERGE_RATIO}",
                    {"center_id": z["id"], "stroke_ids": [previous["id"], current["id"]]},
                    # This is an observational invalidation boundary, not a
                    # trading stop-loss recommendation.
                    {"below": current["low"]},
                    divergence={"method": "bi_power_proxy", "ratio": POWER_DIVERGE_RATIO, "confirmed": False, "macd_area": False},
                ))
        if len(bis) >= 3 and len(all_ups) >= 2 and all_ups[-1]["high"] > gg:
            current, previous = all_ups[-1], all_ups[-2]
            cp, pp = current.get("power"), previous.get("power")
            if cp is not None and pp is not None and cp < pp * POWER_DIVERGE_RATIO:
                cands.append(_candidate(
                    freq_key, len(cands), "first_sell_candidate", "一卖候选", current, current["high"],
                    f"创新高 {current['high']:.2f}>gg {gg:.2f} 且笔力度 {cp:.4f} < 前笔 {pp:.4f}×{POWER_DIVERGE_RATIO}",
                    {"center_id": z["id"], "stroke_ids": [previous["id"], current["id"]]},
                    # This is an observational invalidation boundary, not a
                    # trading stop-loss recommendation.
                    {"above": current["high"]},
                    divergence={"method": "bi_power_proxy", "ratio": POWER_DIVERGE_RATIO, "confirmed": False, "macd_area": False},
                ))
        out["signals"] = cands

    invalidations = []
    for signal in out["signals"]:
        invalid_if = signal.get("invalid_if")
        if not isinstance(invalid_if, Mapping):
            continue
        for side, key in (("below", "below"), ("above", "above")):
            price_level = _number(invalid_if.get(key))
            if price_level is None:
                continue
            invalidations.append({
                "id": f"{signal['id']}:invalid:{side}",
                "candidate_id": signal["id"],
                "side": side,
                "price": round(price_level, 8),
                "anchor_index": signal.get("anchor_index"),
                "annotation": {
                    "title": "候选失效线",
                    "behavior": "价格越过该线，候选不再成立",
                    "text": f"{side} {price_level:.2f}",
                },
            })
    out["invalidations"] = invalidations

    ubi = out["unfinished_bi"]
    bar_payload = out["bars"]
    candidate_payload = out["signals"]
    invalidation_payload = out["invalidations"]
    steps = [
        {
            "id": f"{freq_key}:step:raw", "level": freq_key, "kind": "raw", "title": "原始 K 线",
            "annotation_ids": [x["id"] for x in bar_payload],
            "coord_refs": {"bar_indices": [x["index"] for x in bar_payload], "dates": [x["dt"] for x in bar_payload]},
            "explanation": "先读取同一命中来源的 OHLCV 原始 K 线，日线与周线均保留真实时间锚点。",
            "why": "所有结构结论都必须落在可复核的价格和日期上。",
            "next_if": "沿用这些 K 线坐标，进入分型与完成笔识别。",
        },
        {
            "id": f"{freq_key}:step:fractals_and_strokes", "level": freq_key, "kind": "fractals_and_strokes", "title": "分型与完成笔",
            "annotation_ids": [x["id"] for x in fractals] + [x["id"] for x in bis],
            "coord_refs": {
                "fractal_points": [{"bar_index": x["bar_index"], "price": x["price"]} for x in fractals],
                "stroke_ranges": [{"start": x["start_index"], "end": x["end_index"], "start_price": x["start_price"], "end_price": x["end_price"]} for x in bis],
            },
            "explanation": "先标出引擎确认的顶/底分型，再按端点连接完成笔，并保留起止价格。",
            "why": "分型是端点证据，笔的方向、端点和力度是中枢及候选点的依据。",
            "next_if": "新确认分型出现后，新增或更新完成笔序列。",
        },
        {
            "id": f"{freq_key}:step:unfinished", "level": freq_key, "kind": "unfinished_stroke", "title": "未完成笔",
            "annotation_ids": [ubi["id"]] if ubi else [],
            "coord_refs": {"bar_ranges": [{"start": ubi["start_index"], "end": ubi["end_index"]}] if ubi and ubi.get("start_index") is not None and ubi.get("end_index") is not None else []},
            "explanation": "虚线标出当前未完成摆动，起点承接上一完成笔终点。",
            "why": "未完成笔可能重绘，不能作为确认买卖点。",
            "next_if": "只有形成确认分型并完成笔后，才转入完成笔步骤。",
        },
        {
            "id": f"{freq_key}:step:centers", "level": freq_key, "kind": "centers", "title": "笔级中枢",
            "annotation_ids": [x["id"] for x in centers],
            "coord_refs": {"bar_ranges": [{"start": x["start_index"], "end": x["end_index"]} for x in centers], "price_ranges": [{"low": x["zd"], "high": x["zg"]} for x in centers]},
            "explanation": "把重叠完成笔的价格区间标为笔级中枢，并保留全历史中枢。",
            "why": "中枢上下沿是三买/三卖候选的结构边界。",
            "next_if": "价格离开中枢并出现回抽结构后，才检查三买/三卖候选。",
        },
        {
            "id": f"{freq_key}:step:candidates", "level": freq_key, "kind": "candidates", "title": "候选点",
            "annotation_ids": [x["id"] for x in candidate_payload],
            "coord_refs": {"bar_indices": [x["anchor_index"] for x in candidate_payload], "prices": [x["level"] for x in candidate_payload]},
            "explanation": "仅标出一买/一卖力度代理与三买/三卖结构候选。",
            "why": "当前契约没有二买、线段或 MACD 面积背驰证据。",
            "next_if": "沿 invalid_if 观察后续 K 线；候选状态不会自动升级为确认信号。",
        },
        {
            "id": f"{freq_key}:step:invalidations", "level": freq_key, "kind": "invalidations", "title": "失效条件",
            "annotation_ids": [x["id"] for x in invalidation_payload],
            "coord_refs": [{"id": x["id"], "candidate_id": x["candidate_id"], "side": x["side"], "bar_index": x["anchor_index"], "price": x["price"]} for x in invalidation_payload],
            "explanation": "把每个候选的 invalid_if 转为价格失效线，越过该线即停止把候选当作有效结构。",
            "why": "候选不是确认信号，明确失效条件可以避免把代理判断写成结论。",
            "next_if": "新 K 线未越过失效线则继续观察；越过后标记该候选失效。",
        },
    ]
    out["steps"] = steps
    return out


def _fetch_yfinance_daily_rows(ticker: str) -> list[dict]:
    import yfinance as yf

    df = yf.Ticker(ticker).history(period=f"{HISTORY_YEARS}y", interval="1d", auto_adjust=True).dropna()
    if df is None or len(df) == 0:
        return []
    out = []
    for ts, row in df.iterrows():
        out.append({
            "Date": ts,
            "Open": row.get("Open"),
            "Close": row.get("Close"),
            "High": row.get("High"),
            "Low": row.get("Low"),
            "Volume": row.get("Volume"),
            "Amount": (_number(row.get("Volume")) or 0) * (_number(row.get("Close")) or 0),
        })
    return out


def _bars(ticker: str, freq_key: str) -> list[Any]:
    """Legacy helper returning CZSC RawBars from one six-year daily source."""
    normalized, _ = normalize_ohlcv_rows(_fetch_yfinance_daily_rows(ticker))
    normalized = _trim_years(normalized, DAILY_YEARS) if freq_key == "D" else normalized
    if freq_key == "W":
        normalized = aggregate_weekly(normalized)
    return _raw_bars(ticker, freq_key, normalized)


def build_chan_v1(
    ticker: str,
    daily_rows: Iterable[Mapping[str, Any]] | None,
    *,
    market: str = "U",
    source: str = "unknown",
    adjusted: bool | None = True,
    computed_at: str | None = None,
    history_years: int = HISTORY_YEARS,
    daily_years: int = DAILY_YEARS,
) -> dict:
    """Build chan.v1 from canonical daily OHLCV rows.

    The function is deterministic for a fixed input and engine version apart
    from computed_at. It catches dependency/level errors into the contract so
    ordinary K-line rendering can continue.
    """
    normalized, quality = normalize_ohlcv_rows(daily_rows)
    history = _trim_years(normalized, history_years)
    daily = _trim_years(history, daily_years)
    weekly = aggregate_weekly(history)
    version = _czsc_version()
    now = computed_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    weekly_last_dt = _parse_dt(weekly[-1].get("dt")) if weekly else None
    # A date-only OHLCV feed cannot prove that the current Friday bar has
    # closed.  Weekdays before Friday are explicitly marked in progress; even
    # Friday remains unverified rather than being presented as a close.
    weekly_bar_status = (
        "in_progress" if weekly_last_dt and weekly_last_dt.weekday() < 4 else "unverified"
        if weekly_last_dt else "unavailable"
    )
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "unavailable",
        "engine": "czsc",
        "engine_version": version,
        "ticker": ticker,
        "market": market,
        "source": source,
        "adjusted": adjusted,
        "price_basis": "adjusted_ohlcv" if adjusted is True else "raw_ohlcv" if adjusted is False else "unspecified",
        "provenance": {
            "source": source,
            "adjusted": adjusted,
            "price_basis": "adjusted_ohlcv" if adjusted is True else "raw_ohlcv" if adjusted is False else "unspecified",
            "weekly_last_bar_status": weekly_bar_status,
            "weekly_last_bar_is_complete": False,
        },
        "computed_at": now,
        "as_of": quality.get("date_end"),
        "warnings": ["周线最后一根仅代表截至当前 as_of 的已采集交易日，未确认周收盘；不据此确认周线信号。"] if weekly else [],
        "input_window": {
            "history_years": history_years,
            "daily_years": daily_years,
            "weekly_years": history_years,
            "history_start": history[0]["date"] if history else None,
            "history_end": history[-1]["date"] if history else None,
            "daily_start": daily[0]["date"] if daily else None,
            "daily_end": daily[-1]["date"] if daily else None,
            "weekly_rule": "same-source daily OHLCV grouped by Monday-Friday trading week",
            "amount_policy": "provider amount or volume*adjusted_close proxy",
            "weekly_last_bar_date": weekly[-1]["date"] if weekly else None,
            "weekly_last_bar_status": weekly_bar_status,
            "weekly_last_bar_is_complete": False,
        },
        "quality": quality,
        "capabilities": {
            "fractals": False,
            "strokes": False,
            "centers": False,
            "segments": False,
            "macd_divergence": False,
            "official_signals": False,
        },
        "levels": {},
    }
    if not history:
        result["quality"]["error"] = "no_valid_daily_rows"
        return result
    for freq_key, rows in (("D", daily), ("W", weekly)):
        try:
            level = _level_from_rows(ticker, freq_key, rows)
        except Exception as exc:
            level = _level_error(freq_key, rows, f"{type(exc).__name__}: {str(exc)[:160]}")
        result["levels"][freq_key] = level
        level["provenance"] = {
            "source": source,
            "adjusted": adjusted,
            "price_basis": result["price_basis"],
            "as_of": level.get("bar_end"),
            "weekly_last_bar_status": weekly_bar_status if freq_key == "W" else "not_applicable",
            "weekly_last_bar_is_complete": False if freq_key == "W" else None,
        }
        caps = level.get("capabilities") or {}
        for key in ("fractals", "strokes", "centers"):
            result["capabilities"][key] = bool(result["capabilities"][key] or caps.get(key))
    statuses = [level.get("status") for level in result["levels"].values()]
    if all(s == "ok" for s in statuses):
        result["status"] = "ok"
    elif any(s == "ok" for s in statuses):
        result["status"] = "partial"

    d = result["levels"].get("D", {})
    if d.get("status") == "ok" and d.get("zs"):
        z, lb = d["zs"], d["last_bi"]
        bsp = "、".join(f"{c['type']}@{c['level']}" for c in d.get("bsp_candidates", [])) or "无"
        ubi_dir = "向上" if d.get("ubi") and d["ubi"].get("dir") == "up" else "向下" if d.get("ubi") else "无"
        result["summary"] = (
            f"日线最近中枢 {z['sdt']}→{z['edt']} 上沿 {z['zg']}/下沿 {z['zd']}(共 {z['bi_count']} 笔),"
            f"价格 {d['price']} 位于{d['position']};最近完成笔{('向上' if lb['dir']=='up' else '向下')} {lb['low']}→{lb['high']},"
            f"未完成笔{ubi_dir};买卖点候选:{bsp}。"
            f"多头结构确认线 {z['zg']}(站上后回调不破=三买),空头转折线 {z['zd']}。"
        )
    elif d.get("status") == "ok":
        result["summary"] = f"日线{d.get('position', '结构未形成中枢')},最近完成笔 {d.get('last_bi')}"
    return result


def _level(ticker: str, freq_key: str) -> dict:
    """Compatibility wrapper for callers that used the old private helper."""
    normalized, _ = normalize_ohlcv_rows(_fetch_yfinance_daily_rows(ticker))
    rows = _trim_years(normalized, DAILY_YEARS) if freq_key == "D" else aggregate_weekly(normalized)
    return _level_from_rows(ticker, freq_key, rows)


def chan_summary(ticker: str) -> dict:
    """Compatibility API used by us_backfill.py and the CLI."""
    try:
        from lib.market_router import parse_ticker
        market = parse_ticker(ticker).market
    except Exception:
        market = "U"
    try:
        rows = _fetch_yfinance_daily_rows(ticker)
        return build_chan_v1(
            ticker,
            rows,
            market=market,
            source="yfinance:Ticker.history(auto_adjust=True)",
            adjusted=True,
        )
    except Exception as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "unavailable",
            "engine": "czsc",
            "engine_version": _czsc_version(),
            "ticker": ticker,
            "market": market,
            "source": "yfinance:Ticker.history(auto_adjust=True)",
            "adjusted": True,
            "computed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "levels": {},
            "quality": {"error": f"{type(exc).__name__}: {str(exc)[:160]}"},
            "capabilities": {"fractals": False, "strokes": False, "centers": False, "segments": False, "macd_divergence": False, "official_signals": False},
        }


if __name__ == "__main__":
    import json

    assert len(sys.argv) == 2, "用法: python3 chan_signals.py <TICKER>"
    print(json.dumps(chan_summary(sys.argv[1].upper()), ensure_ascii=False, indent=1, allow_nan=False))
