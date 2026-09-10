"""J Trader 缠论离线讲解工作台渲染器。

本模块只渲染 ``chan.v1`` 已给出的坐标与讲解，不在前端推导缠论结论。

公开接口::

    render_chan_desk(raw, portrait_uri='') -> str

输入优先从整份 raw_data 读取::

    raw['dimensions']['2_kline']['data']['chan']

同时兼容 ``raw['chan']``、``raw['chan_v1']``、``raw['kline']['data']['chan']``
以及直接传入的 chan.v1 对象。推荐的 chan.v1 结构为::

    {
      "version": "chan.v1",
      "capabilities": {
        "segments": <bool>,
        "macd_divergence": <bool>,
        "official_signals": <bool>
      },
      "levels": {
        "D": {
          "status": "available",
          "bars": [{"index": 0, "dt": "...", "open": 1,
                    "high": 2, "low": 0.5, "close": 1.5}],
          "provenance": {"source": "...", "period": "..."},
          "fractals": [{"id": "f1", "bar_index": 4,
                        "dt": "...", "mark": "top", "price": 2}],
          "bis": [{"id": "bi1", "start_index": 1, "end_index": 8,
                   "start_price": 1, "end_price": 2, "sdt": "...",
                   "edt": "...", "dir": "up", "high": 2,
                   "low": 0.8, "power": 1.2}],
          "unfinished_bi": {"status": "unfinished", "repainting": true,
                             "start_index": 8, "end_index": 12,
                             "start_price": 2, "end_price": 2.4,
                             "dir": "up", "high": 2.4, "low": 1.8},
          "centers": [{"id": "zs1", "bi_ids": ["bi1"],
                       "sdt": "...", "edt": "...", "zg": 2,
                       "zd": 1.2, "gg": 2.5, "dd": 0.9}],
          "signals": [{"id": "s1", "type": "三买候选",
                       "anchor_index": 12, "level": 2.3,
                       "evidence": "...", "invalid_if": "...",
                       "divergence": {"method": "bi_power_proxy",
                                      "confirmed": false}}],
          "steps": [{"id": "step-1", "level": "D",
                      "annotation_ids": ["bi1", "zs1"],
                      "title": "...", "explanation": "...",
                      "why": "...", "next_if": "...",
                      "coord_refs": ["..."]}]
        },
        "W": {"...": "同上"}
      },
      "steps": []
    }

``bis`` 的起终点价格必须由后端提供（推荐 ``start_price`` / ``end_price``，
也接受 ``start.price`` / ``end.price`` 等别名）；渲染器不会用 high/low 猜端点。
后端可将 ``levels.*.bars`` 作为实际 OHLC 列表或仅作为已验证的根数；只有拿到
OHLC 列表时才绘制蜡烛，根数仍会在概览与状态中保留。
``signals`` 只显示 1/3 买卖点候选，二买/二卖或未识别类型会被过滤。解释文本
只显示输入的 ``explanation``、``why``、``next_if`` 与坐标引用，缺失时显示“未提供”，
不编造投资判断。

输出只依赖本文件与标准库/报告 HTML 转义工具；CSS 与 JS 分别在 assets/report-chan.css
和 assets/report-chan.js，不依赖 CDN 或新增运行库。
"""
from __future__ import annotations

import html
import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

try:  # normal report import path: scripts/ is on sys.path
    from lib.report.security import escape_text
    from lib.report.chan_table import render_chan_table
except ImportError:  # pragma: no cover - package-style import fallback
    from .security import escape_text
    from .chan_table import render_chan_table


__all__ = ["render_chan_desk"]

_MISSING = "未记录"
_LEVELS = ("D", "W")
_LEVEL_ALIASES = {
    "D": "D", "DAY": "D", "DAILY": "D", "日": "D", "日线": "D",
    "W": "W", "WEEK": "W", "WEEKLY": "W", "周": "W", "周线": "W",
}
_SAFE_ID = re.compile(r"[^A-Za-z0-9_-]+")


def _esc(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value)
    return escape_text(text) if text else default


def _finite(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _integer(value: Any) -> int | None:
    number = _finite(value)
    if number is None or not number.is_integer():
        return None
    return int(number)


def _fmt_number(value: Any, default: str = "—") -> str:
    number = _finite(value)
    if number is None:
        if value not in (None, ""):
            return _esc(value, default)
        return default
    if abs(number) >= 1000:
        text = f"{number:,.2f}"
    elif abs(number) >= 100:
        text = f"{number:.2f}"
    elif abs(number) >= 1:
        text = f"{number:.3f}"
    else:
        text = f"{number:.5f}"
    text = text.rstrip("0").rstrip(".")
    return text or "0"


def _safe_dom_id(value: Any, fallback: str) -> str:
    cleaned = _SAFE_ID.sub("-", str(value or "")).strip("-")[:80]
    return cleaned or fallback


def _dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return []


def _first(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return value
    return None


def _level_name(value: Any, default: str = "D") -> str:
    raw = str(value or default).strip().upper()
    return _LEVEL_ALIASES.get(raw, _LEVEL_ALIASES.get(str(value or "").strip(), default))


def _unwrap_chan(candidate: Any) -> dict[str, Any]:
    """Find a chan.v1 mapping without mutating the caller's raw payload."""
    current = _dict(candidate)
    for _ in range(4):
        if not current:
            return {}
        if isinstance(current.get("chan"), Mapping):
            current = _dict(current["chan"])
            continue
        if isinstance(current.get("chan_v1"), Mapping):
            current = _dict(current["chan_v1"])
            continue
        if isinstance(current.get("data"), Mapping) and not (
            current.get("levels") or current.get("D") or current.get("W")
        ):
            current = _dict(current["data"])
            continue
        break
    return current


def _extract_payload(raw: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (chan payload, kline payload) for all supported wrapper shapes."""
    root = _dict(raw)
    dimensions = _dict(root.get("dimensions"))
    dim_kline = _dict(dimensions.get("2_kline"))
    kline = _dict(root.get("kline"))
    if not kline:
        kline = _dict(root.get("2_kline"))
    if dim_kline:
        kline = dim_kline
    kline_data = _dict(kline.get("data"))

    candidates = [
        kline_data.get("chan"),
        kline_data.get("chan_v1"),
        kline.get("chan"),
        kline.get("chan_v1"),
        root.get("chan"),
        root.get("chan_v1"),
        root.get("chan.v1"),
        root,
    ]
    chan: dict[str, Any] = {}
    for candidate in candidates:
        unpacked = _unwrap_chan(candidate)
        if (
            unpacked.get("levels")
            or unpacked.get("D")
            or unpacked.get("W")
            or _first(unpacked, "version", "schema_version", "schemaVersion") == "chan.v1"
        ):
            chan = unpacked
            break
    return chan, kline_data or kline


def _level_payload(chan: Mapping[str, Any], level: str) -> dict[str, Any]:
    levels = _dict(chan.get("levels"))
    if levels:
        aliases = (level, "daily" if level == "D" else "weekly", "day" if level == "D" else "week")
        for alias in aliases:
            if isinstance(levels.get(alias), Mapping):
                return _dict(levels[alias])
    aliases = (level, "daily" if level == "D" else "weekly", "day" if level == "D" else "week")
    for alias in aliases:
        if isinstance(chan.get(alias), Mapping):
            return _dict(chan[alias])
    return {}


def _level_status(level: Mapping[str, Any]) -> str:
    status = _first(level, "status", "quality", "state")
    if status not in (None, ""):
        return str(status).strip().lower()
    if level.get("error"):
        return "error"
    if any(_list(level.get(key)) for key in ("bars", "fractals", "bis", "centers", "signals")) or level.get("unfinished_bi"):
        return "available"
    return "missing"


def _normalize_bar(value: Any, ordinal: int) -> dict[str, Any] | None:
    item = _dict(value)
    if not item:
        return None
    index = _first(item, "bar_index", "index", "i")
    index_int = _integer(index)
    if index_int is None:
        index_int = ordinal
    values = {key: _finite(item.get(key)) for key in ("open", "high", "low", "close")}
    if any(number is None for number in values.values()):
        return None
    if values["high"] < max(values["open"], values["close"]) or values["low"] > min(values["open"], values["close"]):
        return None
    raw_id = _first(item, "id", "bar_id")
    return {
        "index": index_int,
        "id": str(raw_id) if raw_id not in (None, "") else f"bar-{index_int}",
        "dt": _first(item, "dt", "date", "datetime", "time") or "",
        "volume": _finite(item.get("volume", item.get("vol"))),
        **values,
    }


def _normalize_bars(values: Any) -> list[dict[str, Any]]:
    bars: list[dict[str, Any]] = []
    for ordinal, value in enumerate(_list(values)):
        bar = _normalize_bar(value, ordinal)
        if bar is not None:
            bars.append(bar)
    return bars


def _fallback_bars(kline: Mapping[str, Any], level: str = "D") -> list[dict[str, Any]]:
    data = _dict(kline.get("data")) if isinstance(kline.get("data"), Mapping) else _dict(kline)
    if level == "W":
        # A weekly fallback is valid only when the backend supplied a weekly
        # series.  Do not relabel daily candles as weekly observations.
        keys = ("candles_weekly", "weekly_candles", "kline_weekly", "weekly", "week", "w_bars")
    else:
        keys = ("candles_60d", "candles", "bars", "kline_daily", "daily")
    for key in keys:
        bars = _normalize_bars(data.get(key))
        if bars:
            return bars
    closes = [_finite(value) for value in _list(data.get("close_60d"))]
    if len(closes) >= 2 and all(value is not None for value in closes):
        # Close-only input is intentionally not expanded into synthetic OHLC.
        return []
    return []


def _index(value: Any, *keys: str) -> int | None:
    item = _dict(value)
    raw = _first(item, *keys)
    return _integer(raw)


def _direction(value: Any) -> str:
    text = str(value or "").strip().lower()
    if any(token in text for token in ("up", "上", "bull", "rise", "多")):
        return "up"
    if any(token in text for token in ("down", "下", "bear", "fall", "空")):
        return "down"
    return "unknown"


def _endpoint_price(item: Mapping[str, Any], side: str) -> float | None:
    """Read explicit BI endpoint prices; never infer them from high/low."""
    if side == "start":
        keys = ("start_price", "sprice", "start_value", "from_price", "begin_price")
        nested_keys = ("start", "from", "begin")
    else:
        keys = ("end_price", "eprice", "end_value", "to_price", "finish_price")
        nested_keys = ("end", "to", "finish")
    direct = _finite(_first(item, *keys))
    if direct is not None:
        return direct
    for key in nested_keys:
        nested = item.get(key)
        if isinstance(nested, Mapping):
            value = _finite(_first(nested, "price", "value", "close"))
            if value is not None:
                return value
        else:
            value = _finite(nested)
            if value is not None:
                return value
    return None


def _signal_supported(signal: Mapping[str, Any]) -> bool:
    raw = str(_first(signal, "type", "kind", "label", "name") or "").strip().lower()
    if not raw:
        return False
    if re.search(r"(?:二|2)\s*(?:买|卖)|(?:buy|sell)[_-]?2", raw):
        return False
    return bool(re.search(r"(?:一|三|1|3)\s*(?:买|卖)|(?:buy|sell)[_-]?[13]", raw))


def _signal_label(signal: Mapping[str, Any]) -> str:
    label = _first(signal, "type", "kind", "label", "name")
    text = str(label or "买卖点候选")
    return text if "候选" in text else f"{text}候选"


def _proxy_label(signal: Mapping[str, Any]) -> str:
    divergence = _dict(signal.get("divergence"))
    confirmed = divergence.get("confirmed")
    method = divergence.get("method")
    if confirmed is False or method == "bi_power_proxy":
        return "代理"
    return ""


def _invalid_condition(signal: Mapping[str, Any]) -> tuple[str, float] | None:
    """Return the backend's explicit directional invalidation threshold."""
    condition = _dict(signal.get("invalid_if"))
    below = _finite(_first(condition, "below", "lt", "under"))
    if below is None:
        below = _finite(_first(signal, "invalid_below"))
    if below is not None:
        return "below", below
    above = _finite(_first(condition, "above", "gt", "over"))
    if above is None:
        above = _finite(_first(signal, "invalid_above"))
    if above is not None:
        return "above", above
    return None


def _provenance(level: Mapping[str, Any], chan: Mapping[str, Any]) -> dict[str, Any]:
    source = _dict(level.get("provenance"))
    if not source:
        source = _dict(chan.get("provenance"))
    return source


def _annotation_key(level: str, kind: str, raw_id: Any, ordinal: int) -> str:
    return _safe_dom_id(f"{level}-{kind}-{raw_id or ordinal}", f"{level}-{kind}-{ordinal}")


def _annotation_detail(kind: str, item: Mapping[str, Any], label: str) -> str:
    if kind == "bi":
        start = _first(item, "start_index", "sindex")
        end = _first(item, "end_index", "eindex")
        return f"{label} · {start if start is not None else _MISSING} → {end if end is not None else _MISSING}"
    if kind == "center":
        return f"{label} · zg {_fmt_number(item.get('zg'))} / zd {_fmt_number(item.get('zd'))}"
    if kind == "signal":
        return f"{label} · {item.get('anchor_index', item.get('bar_index', _MISSING))} · {_fmt_number(item.get('level'))}"
    if kind == "fractal":
        return f"{label} · {item.get('bar_index', item.get('index', _MISSING))} · {_fmt_number(item.get('price'))}"
    return label


def _step_observation(kind: str, payload: Mapping[str, Any]) -> str:
    """Short source-coordinate observations, not a generated trading conclusion."""
    bars = _normalize_bars(payload.get("bars"))
    if not bars:
        return "本周期缺少可核对的 OHLC 记录。"
    last = bars[-1]
    bis = [_dict(v) for v in _list(payload.get("bis"))]
    centers = [_dict(v) for v in _list(payload.get("centers"))]
    unfinished = _dict(payload.get("unfinished_bi"))
    signals = [_dict(v) for v in _list(payload.get("signals")) if _signal_supported(_dict(v))]
    def date_for(index):
        return next((str(b.get("dt"))[:10] for b in bars if b["index"] == _integer(index)), "日期未记录")
    if kind == "raw":
        return f'{len(bars)} 根 K 线，{str(bars[0]["dt"])[:10]} → {str(last["dt"])[:10]}；末根开 {_fmt_number(last["open"])} / 高 {_fmt_number(last["high"])} / 低 {_fmt_number(last["low"])} / 收 {_fmt_number(last["close"])}。'
    if kind == "fractals_and_strokes":
        tail = bis[-1] if bis else {}
        detail = f'最近完成笔：{date_for(tail.get("start_index"))} {_fmt_number(_endpoint_price(tail,"start"))} → {date_for(tail.get("end_index"))} {_fmt_number(_endpoint_price(tail,"end"))}。' if tail else '当前没有完成笔。'
        return f'{len(_list(payload.get("fractals")))} 个分型、{len(bis)} 段完成笔。' + detail
    if kind == "unfinished_stroke":
        if not unfinished: return '当前载荷没有未完成笔坐标。'
        return f'未完成笔：{date_for(unfinished.get("start_index"))} {_fmt_number(_endpoint_price(unfinished,"start"))} → {date_for(unfinished.get("end_index"))} {_fmt_number(_endpoint_price(unfinished,"end"))}；虚线终点仍可随新 K 线变化。'
    if kind == "centers":
        if not centers: return '当前完成笔中没有满足条件的笔级中枢；本步骤不补画示意中枢。'
        center = centers[-1]
        lo, hi, close = _finite(center.get("zd")), _finite(center.get("zg")), last["close"]
        relation = '上方' if hi is not None and close > hi else '下方' if lo is not None and close < lo else '内部'
        return f'{len(centers)} 个笔级中枢。最近区间 {_fmt_number(lo)}–{_fmt_number(hi)}，{str(center.get("sdt") or date_for(center.get("start_index")))[:10]} → {str(center.get("edt") or date_for(center.get("end_index")))[:10]}；末根收盘 {_fmt_number(close)} 位于该历史区间{relation}。'
    if kind == "candidates":
        if not signals: return '当前结构未产生首版支持的一买 / 一卖力度代理或三买 / 三卖候选。没有候选不等于看多或看空。'
        points = signals[-2:]
        return '；'.join(f'{_signal_label(v)} · {date_for(_first(v,"anchor_index","bar_index"))} · {_fmt_number(v.get("level"))}' for v in points) + '。这些是待条件确认的候选，不是已确认交易信号。'
    if kind == "invalidations":
        conditions = [(v,_invalid_condition(v)) for v in signals]
        conditions = [(v,c) for v,c in conditions if c]
        if not conditions: return '本周期没有带数值失效边界的候选，因此不绘制额外条件线。'
        return '；'.join(f'{_signal_label(v)}：{"跌破" if c[0]=="below" else "突破"} {_fmt_number(c[1])} 时，该候选观察失效' for v,c in conditions[-2:]) + '。'
    return ""


def _build_level_model(level: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    level = _level_name(level)
    level = level if level in _LEVELS else "D"
    bars = _normalize_bars(payload.get("bars"))
    annotations: list[dict[str, Any]] = []
    by_alias: dict[str, str] = {}
    bis: list[dict[str, Any]] = []

    def register(kind: str, item: Mapping[str, Any], ordinal: int, label: str, *, index: int | None = None, status: str = "complete") -> str:
        raw_id = _first(item, "id", f"{kind}_id") or f"{kind}-{ordinal + 1}"
        key = _annotation_key(level, kind, raw_id, ordinal)
        detail = _annotation_detail(kind, item, label)
        annotation = {
            "key": key,
            "raw_id": str(raw_id),
            "kind": kind,
            "label": label,
            "detail": detail,
            "index": index,
            "status": status,
            "item": item,
        }
        annotations.append(annotation)
        aliases = {str(raw_id), key, f"{kind}-{raw_id}", f"{level}-{raw_id}"}
        for alias in aliases:
            by_alias[alias] = key
        return key

    for ordinal, value in enumerate(_list(payload.get("bis"))):
        item = _dict(value)
        if not item:
            continue
        start_index = _index(item, "start_index", "sindex", "from_index")
        end_index = _index(item, "end_index", "eindex", "to_index")
        label = "已完成笔 · " + ("向上" if _direction(item.get("dir", item.get("direction"))) == "up" else "向下" if _direction(item.get("dir", item.get("direction"))) == "down" else "方向未记录")
        key = register("bi", item, ordinal, label, index=end_index, status="complete")
        bis.append({**item, "_key": key, "_start_index": start_index, "_end_index": end_index})

    unfinished = _dict(payload.get("unfinished_bi"))
    if unfinished:
        start_index = _index(unfinished, "start_index", "sindex", "from_index")
        end_index = _index(unfinished, "end_index", "eindex", "to_index")
        direction = _direction(unfinished.get("dir", unfinished.get("direction")))
        label = "未完成笔 · " + ("向上" if direction == "up" else "向下" if direction == "down" else "方向未记录")
        key = register("unfinished-bi", unfinished, 0, label, index=end_index, status="unfinished")
        unfinished = {**unfinished, "_key": key, "_start_index": start_index, "_end_index": end_index}
    else:
        unfinished = None

    for ordinal, value in enumerate(_list(payload.get("centers", payload.get("zs", [])))):
        item = _dict(value)
        if not item:
            continue
        label = f"中枢 {_first(item, 'id', 'name') or ordinal + 1}"
        key = register("center", item, ordinal, label, index=_index(item, "end_index", "eindex"))
        item = {**item, "_key": key}
        for center_id in _list(item.get("bi_ids")):
            by_alias[f"center:{center_id}"] = key
        # Accept explicit center endpoints as well as center bi_ids.
        if _index(item, "start_index", "sindex") is None:
            matching = [bi for bi in bis if str(_first(bi, "id", "bi_id") or "") in {str(x) for x in _list(item.get("bi_ids"))}]
            if matching:
                item["_start_index"] = matching[0].get("_start_index")
                item["_end_index"] = matching[-1].get("_end_index")
        else:
            item["_start_index"] = _index(item, "start_index", "sindex")
            item["_end_index"] = _index(item, "end_index", "eindex")
        for existing in annotations:
            if existing["key"] == key:
                existing["item"] = item
                break

    for ordinal, value in enumerate(_list(payload.get("fractals", payload.get("fx", [])))):
        item = _dict(value)
        if not item:
            continue
        mark = str(_first(item, "mark", "type", "kind", "direction") or "分型")
        label = "顶分型" if any(token in mark.lower() for token in ("top", "顶")) else "底分型" if any(token in mark.lower() for token in ("bottom", "底")) else f"分型 · {mark}"
        index = _index(item, "bar_index", "index", "i")
        register("fractal", item, ordinal, label, index=index)

    signals: list[dict[str, Any]] = []
    for ordinal, value in enumerate(_list(payload.get("signals", payload.get("bsp_candidates", [])))):
        item = _dict(value)
        if not item or not _signal_supported(item):
            continue
        label = _signal_label(item)
        proxy = _proxy_label(item)
        if proxy:
            label += " · 代理"
        index = _index(item, "anchor_index", "bar_index", "index", "at_index")
        key = register("signal", item, ordinal, label, index=index, status="candidate")
        signals.append({**item, "_key": key, "_index": index, "_label": label})

    # Backend invalidation records are condition-line references, not a new
    # point type.  Resolve their IDs to the owning candidate so the final
    # explanation step can reveal the directional condition line without
    # duplicating rows in the structure ledger.
    for invalidation in _list(payload.get("invalidations")):
        item = _dict(invalidation)
        candidate_id = _first(item, "candidate_id", "signal_id", "point_id")
        mapped = by_alias.get(str(candidate_id)) if candidate_id not in (None, "") else None
        invalidation_id = _first(item, "id", "invalidation_id")
        if mapped and invalidation_id not in (None, ""):
            by_alias[str(invalidation_id)] = mapped

    # Preserve backend IDs and also allow step references using annotation keys.
    for annotation in annotations:
        item = annotation["item"]
        for alias in (annotation["raw_id"], annotation["key"]):
            by_alias.setdefault(alias, annotation["key"])
        if annotation["kind"] == "bi":
            raw_id = _first(item, "id", "bi_id")
            if raw_id not in (None, ""):
                by_alias.setdefault(f"bi:{raw_id}", annotation["key"])

    steps_raw = _list(payload.get("steps"))
    steps: list[dict[str, Any]] = []
    for ordinal, value in enumerate(steps_raw):
        step = _dict(value)
        if not step:
            continue
        raw_ids = _list(step.get("annotation_ids") or step.get("annotations") or step.get("point_ids"))
        resolved: list[str] = []
        for raw_id in raw_ids:
            candidate = _dict(raw_id)
            token = _first(candidate, "id", "annotation_id", "point_id") if candidate else raw_id
            mapped = by_alias.get(str(token))
            if mapped and mapped not in resolved:
                resolved.append(mapped)
        steps.append({
            "id": str(_first(step, "id", "step_id") or f"{level}-step-{ordinal + 1}"),
            "kind": str(_first(step, "kind", "type") or ""),
            "title": str(_first(step, "title", "name") or f"第 {ordinal + 1} 步"),
            "explanation": str(_first(step, "explanation", "text", "comment") or "未提供该步骤的原始讲解文本。"),
            "why": str(_first(step, "why", "reason") or ""),
            "next_if": str(_first(step, "next_if", "next", "condition") or ""),
            "coord_refs": step.get("coord_refs") or step.get("coordinates") or step.get("coords") or [],
            "annotation_keys": resolved,
            "focus_keys": resolved[-2:] if str(_first(step, "kind", "type") or "") == "fractals_and_strokes" else resolved[-1:],
            "observation": _step_observation(str(_first(step, "kind", "type") or ""), payload),
            "raw": step,
        })

    indices = [bar["index"] for bar in bars]
    for annotation in annotations:
        item = annotation["item"]
        for key in ("start_index", "end_index", "anchor_index", "bar_index", "index"):
            idx = _integer(item.get(key))
            if idx is not None:
                indices.append(idx)
    if unfinished:
        indices.extend(index for index in (unfinished.get("_start_index"), unfinished.get("_end_index")) if index is not None)
    min_index, max_index = (min(indices), max(indices)) if indices else (0, 1)
    if min_index == max_index:
        max_index = min_index + 1

    return {
        "level": level,
        "payload": dict(payload),
        "status": _level_status(payload),
        "bars": bars,
        "bar_count": len(bars) if bars else (_integer(payload.get("bars")) or 0),
        "bis": bis,
        "unfinished_bi": unfinished,
        "signals": signals,
        "annotations": annotations,
        "steps": steps,
        "by_alias": by_alias,
        "min_index": min_index,
        "max_index": max_index,
        "provenance": _provenance(payload, {}),
    }


def _price_domain(model: Mapping[str, Any]) -> tuple[float, float]:
    values: list[float] = []
    for bar in model.get("bars", []):
        values.extend(value for value in (bar.get("high"), bar.get("low")) if value is not None)
    for bi in model.get("bis", []):
        values.extend(value for value in (bi.get("high"), bi.get("low"), _endpoint_price(bi, "start"), _endpoint_price(bi, "end")) if _finite(value) is not None)
    unfinished = model.get("unfinished_bi") or {}
    values.extend(value for value in (unfinished.get("high"), unfinished.get("low"), _endpoint_price(unfinished, "start"), _endpoint_price(unfinished, "end")) if _finite(value) is not None)
    for annotation in model.get("annotations", []):
        item = annotation.get("item") or {}
        values.extend(value for value in (item.get("price"), item.get("level"), item.get("zg"), item.get("zd"), item.get("gg"), item.get("dd")) if _finite(value) is not None)
    values = [value for value in values if _finite(value) is not None]
    if not values:
        return 0.0, 1.0
    low, high = min(values), max(values)
    span = high - low
    pad = max(span * 0.06, abs(high) * 0.01, 1e-6)
    return low - pad, high + pad


def _svg_scale(model: Mapping[str, Any]):
    left, right, top, bottom = 84.0, 930.0, 28.0, 410.0
    low, high = _price_domain(model)
    min_index, max_index = model["min_index"], model["max_index"]
    span_index = max(max_index - min_index, 1)

    def x(index: Any) -> float | None:
        number = _integer(index)
        if number is None:
            return None
        return left + (number - min_index) / span_index * (right - left)

    def y(value: Any) -> float | None:
        number = _finite(value)
        if number is None:
            return None
        return bottom - (number - low) / max(high - low, 1e-9) * (bottom - top)

    return x, y, (left, right, top, bottom, low, high)


def _svg_text(value: Any, default: str = "—") -> str:
    return _esc(value, default) if value not in (None, "") else default


def _svg_label_position(point_x: float, right: float, offset: float = 6.0) -> tuple[float, str]:
    """Keep edge labels inside the viewBox instead of clipping them."""
    if point_x > right - 96:
        return right - offset, "end"
    return min(point_x + offset, right - offset), "start"


def _svg_price_action(model: Mapping[str, Any], x, y, left: float, right: float) -> str:
    """Render only price_action.v1 coordinates supplied by the analysis program."""
    pa = _dict((model.get("payload") or {}).get("price_action"))
    output: list[str] = []
    for ordinal, series in enumerate(_list(pa.get("moving_averages"))):
        item = _dict(series)
        runs: list[list[str]] = [[]]
        for point in _list(item.get("points")):
            point = _dict(point)
            xx, yy = x(point.get("index")), y(point.get("price"))
            if xx is None or yy is None:
                if runs[-1]: runs.append([])
                continue
            runs[-1].append(f"{xx:.2f},{yy:.2f}")
        for points in runs:
            if len(points) > 1:
                output.append(f'<polyline class="chan-ma chan-ma-{ordinal % 2}" data-pa-layer="ma" points="{" ".join(points)}" aria-label="{_esc(item.get("label"))}"/>')
    source_levels = [_dict(v) for v in _list(pa.get("levels"))]
    valid_levels = [v for v in source_levels if v.get("status") not in {"invalidated", "retest_failed"}]
    default_ids = {str(v.get("id")) for v in valid_levels[-6:]}
    for item in source_levels:
        item = _dict(item)
        x1, x2, yy = x(item.get("start_index")), x(item.get("end_index")), y(item.get("price"))
        if None in (x1, x2, yy): continue
        label = str(item.get("label") or ("阻力" if item.get("kind") == "resistance" else "支撑"))
        key = str(item.get("id") or "")
        evidence = str(item.get("evidence") or item.get("reason") or "")
        invalid = item.get("invalid_if")
        invalid = str(invalid.get("text") or invalid) if isinstance(invalid, Mapping) else str(invalid or "未记录")
        label_x, anchor = _svg_label_position(x2, right)
        output.append(f'<g class="chan-pa-point" data-pa-layer="levels" data-pa-secondary="{'false' if key in default_ids else 'true'}" data-pa-point="{_esc(key)}" data-start-index="{item.get("start_index")}" data-end-index="{item.get("end_index")}" data-label="{_esc(label)}" data-price="{_esc(item.get("price"))}" data-evidence="{_esc(evidence)}" data-invalid="{_esc(invalid)}" role="button" tabindex="0" aria-label="{_esc(label)} {_fmt_number(item.get("price"))}"><line class="chan-pa-level" x1="{x1:.2f}" y1="{yy:.2f}" x2="{x2:.2f}" y2="{yy:.2f}"/><text class="chan-pa-label" x="{label_x:.2f}" y="{yy-7:.2f}" text-anchor="{anchor}">{_esc(label)} {_fmt_number(item.get("price"))}</text></g>')
    for item in _list(pa.get("events")):
        item = _dict(item)
        index = _first(item, "anchor_index", "index")
        xx, yy = x(index), y(item.get("price"))
        if None in (xx, yy): continue
        label = str(item.get("label") or item.get("kind") or "价格行为")
        key = str(item.get("id") or "")
        invalid = item.get("invalid_if")
        invalid = str(invalid.get("text") or invalid) if isinstance(invalid, Mapping) else str(invalid or "未记录")
        label_x, anchor = _svg_label_position(xx, right)
        evidence = str(item.get("evidence") or item.get("reason") or "")
        output.append(f'<g class="chan-pa-point" data-pa-layer="events" data-pa-point="{_esc(key)}" data-anchor-index="{index}" data-label="{_esc(label)}" data-price="{_esc(item.get("price"))}" data-date="{_esc(item.get("dt"))}" data-evidence="{_esc(evidence)}" data-invalid="{_esc(invalid)}" tabindex="0" role="button" aria-label="{_esc(label)}"><circle class="chan-pa-event" cx="{xx:.2f}" cy="{yy:.2f}" r="4"/><text class="chan-pa-label" x="{label_x:.2f}" y="{yy-10:.2f}" text-anchor="{anchor}">{_esc(label)}</text></g>')
    bars = model.get("bars") or []
    volumes = [b.get("volume") for b in bars if _finite(b.get("volume")) is not None and b["volume"] >= 0]
    max_volume = max(volumes) if volumes else 0
    if max_volume:
        width = max(0.75, min(7.0, (right-left)/max(len(bars), 1)*0.65))
        output.append('<g data-pa-layer="volume" class="chan-volume">')
        for bar in bars:
            volume = _finite(bar.get("volume"))
            xx = x(bar["index"])
            if volume is None or volume < 0 or xx is None: continue
            height = volume/max_volume*62
            klass = "up" if bar["close"] >= bar["open"] else "down"
            output.append(f'<rect class="chan-volume-{klass}" x="{xx-width/2:.2f}" y="{512-height:.2f}" width="{width:.2f}" height="{height:.2f}"/>')
        output.append('</g>')
    return "".join(output)


def _svg_chart(model: Mapping[str, Any], *, fallback: bool = False) -> str:
    level = model["level"]
    x, y, box = _svg_scale(model)
    left, right, top, bottom, low, high = box
    title_id = f"chan-chart-title-{level}"
    desc_id = f"chan-chart-desc-{level}"
    svg: list[str] = [
        f'<svg class="chan-chart-svg" viewBox="0 0 960 550" role="img" aria-labelledby="{title_id} {desc_id}" data-chan-chart="{level}" data-min-index="{model["min_index"]}" data-max-index="{model["max_index"]}" data-price-low="{low}" data-price-high="{high}" tabindex="0" aria-description="拖拽平移，双指缩放，方向键平移，加减键缩放">',
        f'<title id="{title_id}">{"普通 K 线回退图" if fallback else f"{level} 级别缠论坐标图"}</title>',
        f'<desc id="{desc_id}">{"缠论结构数据不可用，仅保留输入的 OHLC 观察。" if fallback else "实线为已完成笔，虚线为未完成笔；中枢与买卖点候选均来自 chan.v1 坐标。"}</desc>',
        '<rect class="chan-plot-surface" x="0" y="0" width="960" height="550"/>',
    ]
    bars = model.get("bars", [])
    numeric_values = []
    for bar in bars:
        numeric_values.extend(value for value in (bar.get("high"), bar.get("low")) if _finite(value) is not None)
    for annotation in model.get("annotations", []):
        item = annotation.get("item") or {}
        numeric_values.extend(value for value in (item.get("price"), item.get("level"), item.get("zg"), item.get("zd"), item.get("gg"), item.get("dd"), _endpoint_price(item, "start"), _endpoint_price(item, "end")) if _finite(value) is not None)
    has_price_domain = bool(numeric_values)
    # Do not draw a synthetic 0..1 price axis for a missing weekly payload.
    if has_price_domain:
        # Horizontal grid and numeric labels are static, so the chart remains useful without JS.
        for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
            yy = top + fraction * (bottom - top)
            value = high - fraction * (high - low)
            svg.append(f'<line class="chan-grid-line" x1="{left:.1f}" y1="{yy:.1f}" x2="{right:.1f}" y2="{yy:.1f}"/>')
            svg.append(f'<text class="chan-axis-label" x="{left - 10:.1f}" y="{yy + 3:.1f}" text-anchor="end">{_fmt_number(value)}</text>')
        svg.append(f'<line class="chan-axis-line" x1="{left:.1f}" y1="{bottom:.1f}" x2="{right:.1f}" y2="{bottom:.1f}"/>')

    svg.append(f'<defs><clipPath id="chan-clip-{level}"><rect x="{left}" y="{top - 12}" width="{right-left}" height="{bottom-top+24}"/></clipPath><clipPath id="chan-volume-clip-{level}"><rect x="{left}" y="448" width="{right-left}" height="66"/></clipPath></defs><g clip-path="url(#chan-clip-{level})"><g class="chan-plot-viewport chan-price-viewport">')
    if not bars:
        bar_count = model.get("bar_count") or 0
        empty_label = (
            f"OHLC 明细未随结构载荷传入 · {bar_count} 根"
            if bar_count
            else "周线数据不足" if level == "W" else "价格坐标未记录"
        )
        svg.append(f'<text class="chan-empty-label" x="{(left + right) / 2:.1f}" y="{(top + bottom) / 2:.1f}" text-anchor="middle">{empty_label}</text>')
    else:
        n = max(len(bars), 1)
        body_width = max(1.0, min(9.0, (right - left) / n * 0.62))
        for ordinal, bar in enumerate(bars):
            xx = x(bar["index"])
            yo, yc, yh, yl = (y(bar[key]) for key in ("open", "close", "high", "low"))
            if xx is None or None in (yo, yc, yh, yl):
                continue
            up = bar["close"] >= bar["open"]
            klass = "chan-candle chan-candle-up" if up else "chan-candle chan-candle-down"
            bar_dom_id = _safe_dom_id(f"{level}-bar-{bar['id']}", f"{level}-bar-{ordinal}")
            top_body = min(yo, yc)
            body_height = max(abs(yc - yo), 1.0)
            svg.append(
                f'<g class="{klass}" data-chan-bar="{_esc(bar["id"])}" data-bar-index="{bar["index"]}" data-date="{_esc(bar.get("dt"))}" data-open="{bar["open"]}" data-high="{bar["high"]}" data-low="{bar["low"]}" data-close="{bar["close"]}" data-volume="{bar.get("volume") if bar.get("volume") is not None else ''}" aria-label="{_svg_text(bar.get("dt"), "K 线")}">'
                f'<line x1="{xx:.1f}" y1="{yh:.1f}" x2="{xx:.1f}" y2="{yl:.1f}"/> '
                f'<rect id="{bar_dom_id}" x="{xx - body_width / 2:.1f}" y="{top_body:.1f}" width="{body_width:.1f}" height="{body_height:.1f}" rx="1"/>''</g>'
            )

    if not fallback:
        # Completed BIs have explicit endpoint prices. Missing endpoints stay in the table,
        # but do not receive an invented line.
        for bi in model.get("bis", []):
            x1, x2 = x(bi.get("_start_index")), x(bi.get("_end_index"))
            y1, y2 = y(_endpoint_price(bi, "start")), y(_endpoint_price(bi, "end"))
            if None in (x1, x2, y1, y2):
                continue
            key = bi["_key"]
            label = "已完成笔"
            label_x, label_anchor = _svg_label_position(x2, right)
            svg.append(
                f'<g id="chan-ann-{key}" class="chan-annotation" data-chan-annotation="{key}" data-kind="bi" data-start-index="{bi.get("_start_index")}" data-end-index="{bi.get("_end_index")}" tabindex="0" role="button" aria-label="{_esc(label)}">'
                f'<line class="chan-bi chan-bi-complete" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/> '
                f'<circle class="chan-annotation-halo" cx="{x2:.1f}" cy="{y2:.1f}" r="5"/> '
                f'<text class="chan-annotation-label chan-label-optional" x="{label_x:.1f}" y="{y2 - 7:.1f}" text-anchor="{label_anchor}">{_esc(label)}</text></g>'
            )
        unfinished = model.get("unfinished_bi")
        if unfinished:
            x1, x2 = x(unfinished.get("_start_index")), x(unfinished.get("_end_index"))
            y1, y2 = y(_endpoint_price(unfinished, "start")), y(_endpoint_price(unfinished, "end"))
            if None not in (x1, x2, y1, y2):
                key = unfinished["_key"]
                label_x, label_anchor = _svg_label_position(x2, right)
                svg.append(
                    f'<g id="chan-ann-{key}" class="chan-annotation" data-chan-annotation="{key}" data-kind="unfinished-bi" data-start-index="{unfinished.get("_start_index")}" data-end-index="{unfinished.get("_end_index")}" tabindex="0" role="button" aria-label="未完成笔">'
                    f'<line class="chan-bi chan-bi-unfinished" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/> '
                    f'<circle class="chan-annotation-halo" cx="{x2:.1f}" cy="{y2:.1f}" r="5"/> '
                    f'<text class="chan-annotation-label chan-label-optional" x="{label_x:.1f}" y="{y2 - 7:.1f}" text-anchor="{label_anchor}">未完成笔</text></g>'
                )

        # Centers are bands, not inferred signals.
        bi_lookup = {str(_first(bi, "id", "bi_id")): bi for bi in model.get("bis", [])}
        center_annotations = [a for a in model.get("annotations", []) if a["kind"] == "center"]
        last_center_key = center_annotations[-1]["key"] if center_annotations else None
        for annotation in center_annotations:
            item = annotation["item"]
            start_idx = _index(item, "start_index", "sindex")
            end_idx = _index(item, "end_index", "eindex")
            if start_idx is None or end_idx is None:
                ids = [str(value) for value in _list(item.get("bi_ids"))]
                matches = [bi_lookup[identifier] for identifier in ids if identifier in bi_lookup]
                if matches:
                    start_idx = matches[0].get("_start_index")
                    end_idx = matches[-1].get("_end_index")
            x1, x2 = x(start_idx), x(end_idx)
            yt, yb = y(item.get("zg")), y(item.get("zd"))
            if None in (x1, x2, yt, yb):
                continue
            key = annotation["key"]
            left_x, width, top_y, height = min(x1, x2), abs(x2 - x1), min(yt, yb), abs(yb - yt)
            label_class = "chan-annotation-label chan-label-default" if key == last_center_key else "chan-annotation-label chan-label-optional"
            label_x, label_anchor = (right - 8, "end") if left_x > right - 210 else (left_x + 6, "start")
            svg.append(
                f'<g id="chan-ann-{key}" class="chan-annotation" data-chan-annotation="{key}" data-kind="center" data-start-index="{start_idx}" data-end-index="{end_idx}" tabindex="0" role="button" aria-label="{_esc(annotation["label"])}">'
                f'<rect class="chan-center-band" x="{left_x:.1f}" y="{top_y:.1f}" width="{max(width, 2):.1f}" height="{max(height, 2):.1f}" rx="4"/> '
                f'<text class="{label_class}" x="{label_x:.1f}" y="{top_y + 14:.1f}" text-anchor="{label_anchor}">中枢 {_fmt_number(item.get("zd"))}–{_fmt_number(item.get("zg"))}</text></g>'
            )

        for annotation in (a for a in model.get("annotations", []) if a["kind"] == "fractal"):
            item = annotation["item"]
            xx, yy = x(_index(item, "bar_index", "index", "i")), y(item.get("price"))
            if None in (xx, yy):
                continue
            key = annotation["key"]
            top_mark = "顶" in annotation["label"]
            mark_y = yy - 7 if top_mark else yy + 7
            label_x, label_anchor = _svg_label_position(xx, right, 5.0)
            svg.append(
                f'<g id="chan-ann-{key}" class="chan-annotation" data-chan-annotation="{key}" data-kind="fractal" data-anchor-index="{_index(item, "bar_index", "index", "i")}" tabindex="0" role="button" aria-label="{_esc(annotation["label"])}">'
                f'<circle class="chan-fractal-mark" cx="{xx:.1f}" cy="{yy:.1f}" r="3.5"/> '
                f'<text class="chan-annotation-label chan-label-optional" x="{label_x:.1f}" y="{mark_y:.1f}" text-anchor="{label_anchor}">{_esc(annotation["label"])}</text></g>'
            )

        invalidation_ids: dict[tuple[str, str], str] = {}
        for invalidation in _list((model.get("payload") or {}).get("invalidations")):
            invalidation_item = _dict(invalidation)
            candidate_id = _first(invalidation_item, "candidate_id", "signal_id", "point_id")
            side = _first(invalidation_item, "side", "direction")
            invalidation_id = _first(invalidation_item, "id", "invalidation_id")
            if candidate_id not in (None, "") and side not in (None, "") and invalidation_id not in (None, ""):
                invalidation_ids[(str(candidate_id), str(side))] = str(invalidation_id)

        for signal in model.get("signals", []):
            item = signal
            xx, yy = x(signal.get("_index")), y(item.get("level"))
            if None in (xx, yy):
                continue
            key = signal["_key"]
            label = signal["_label"]
            label_x, label_anchor = _svg_label_position(xx, right, 10.0)
            condition = _invalid_condition(item)
            condition_html = ""
            if condition:
                direction, invalid_price = condition
                condition_y = y(invalid_price)
                if condition_y is not None:
                    arrow_y = condition_y - 6 if direction == "below" else condition_y + 6
                    arrow_points = (
                        f"{xx - 4:.1f},{arrow_y:.1f} {xx + 4:.1f},{arrow_y:.1f} {xx:.1f},{condition_y:.1f}"
                        if direction == "below"
                        else f"{xx - 4:.1f},{arrow_y:.1f} {xx + 4:.1f},{arrow_y:.1f} {xx:.1f},{condition_y:.1f}"
                    )
                    direction_label = "失效 ↓" if direction == "below" else "失效 ↑"
                    raw_signal_id = _first(item, "id", "signal_id")
                    condition_id = invalidation_ids.get((str(raw_signal_id), direction))
                    condition_attr = f' data-structure-id="{_esc(condition_id)}"' if condition_id else ""
                    condition_html = (
                        f'<line class="chan-condition-link" data-direction="{direction}"{condition_attr} x1="{xx:.1f}" y1="{yy:.1f}" x2="{xx:.1f}" y2="{condition_y:.1f}"/> '
                        f'<polygon class="chan-condition-arrow" data-direction="{direction}"{condition_attr} points="{arrow_points}"/> '
                        f'<line class="chan-condition-line" data-direction="{direction}"{condition_attr} x1="{xx:.1f}" y1="{condition_y:.1f}" x2="{right:.1f}" y2="{condition_y:.1f}"/> '
                        f'<text class="chan-condition-label" data-direction="{direction}"{condition_attr} x="{right - 6:.1f}" y="{condition_y + 18:.1f}" data-anchor-y="{condition_y:.2f}" data-label-offset="18" text-anchor="end">{direction_label} {_fmt_number(invalid_price)}</text>'
                    )
            svg.append(
                f'<g id="chan-ann-{key}" class="chan-annotation" data-chan-annotation="{key}" data-kind="signal" data-anchor-index="{signal.get("_index")}" data-level="{_fmt_number(item.get("level"), "")}" tabindex="0" role="button" aria-label="{_esc(label)}">'
                f'{condition_html}<circle class="chan-signal-candidate" cx="{xx:.1f}" cy="{yy:.1f}" r="7"/> '
                f'<text class="chan-annotation-label chan-label-default" x="{label_x:.1f}" y="{yy - 12:.1f}" data-anchor-y="{yy:.2f}" data-label-offset="-12" text-anchor="{label_anchor}">{_esc(label)} · {_fmt_number(item.get("level"))}</text></g>'
            )

    pa_svg = _svg_price_action(model, x, y, left, right)
    volume_start = pa_svg.find('<g data-pa-layer="volume"')
    price_svg, volume_svg = (pa_svg[:volume_start], pa_svg[volume_start:]) if volume_start >= 0 else (pa_svg, "")
    svg.append(price_svg)
    svg.append('</g></g>')
    if volume_svg:
        svg.append(f'<g clip-path="url(#chan-volume-clip-{level})"><g class="chan-plot-viewport chan-volume-viewport">{volume_svg}</g></g>')
    svg.append('<g class="chan-crosshair" hidden aria-hidden="true"><line class="chan-crosshair-v" x1="84" y1="28" x2="84" y2="512"/><line class="chan-crosshair-h" x1="84" y1="28" x2="930" y2="28"/><rect x="2" y="16" width="80" height="21"/><text x="80" y="30" text-anchor="end"></text></g>')
    # Date labels are deliberately sparse but still source-backed.
    if bars:
        labels = [bars[0], bars[len(bars) // 2], bars[-1]]
        seen: set[str] = set()
        for bar in labels:
            dt = str(bar.get("dt") or "")
            if not dt or dt in seen:
                continue
            seen.add(dt)
            xx = x(bar["index"])
            if xx is not None:
                anchor = "end" if bar is bars[-1] else "start" if bar is bars[0] else "middle"
                svg.append(f'<text class="chan-date-label" x="{xx:.1f}" y="535" text-anchor="{anchor}">{_esc(dt[:16])}</text>')
    else:
        payload = model.get("payload") or {}
        dates = [payload.get("bar_start"), payload.get("bar_end")]
        if dates[0] and dates[1]:
            svg.append(f'<text class="chan-date-label" x="{left:.1f}" y="535" text-anchor="start">{_esc(str(dates[0])[:16])}</text>')
            svg.append(f'<text class="chan-date-label" x="{right:.1f}" y="535" text-anchor="end">{_esc(str(dates[1])[:16])}</text>')
    svg.append("</svg>")
    return "".join(svg)


def _status_label(status: str) -> str:
    labels = {
        "available": "可用", "ok": "可用", "ready": "可用", "complete": "可用",
        "error": "计算失败", "failed": "计算失败", "missing": "不可用",
        "unavailable": "不可用", "stale": "已过期", "partial": "部分可用",
    }
    return labels.get(status, status or "未记录")


def _period_value(model: Mapping[str, Any]) -> Any:
    payload = model.get("payload") or {}
    context = _dict(model.get("source_context"))
    provenance = _provenance(payload, context)
    level = model.get("level", "D")
    input_window = _dict(context.get("input_window"))
    period = _first(provenance, "period", "date_range", "window") or _first(payload, "period", "date_range")
    if period in (None, ""):
        period = _first(payload, "bar_start") and f"{payload.get('bar_start')} → {payload.get('bar_end')}"
    if period in (None, ""):
        start_key, end_key = ("daily_start", "daily_end") if level == "D" else ("history_start", "history_end")
        if input_window.get(start_key) and input_window.get(end_key):
            period = f"{input_window[start_key]} → {input_window[end_key]}"
    return period


def _render_provenance(model: Mapping[str, Any]) -> str:
    payload = model.get("payload") or {}
    context = _dict(model.get("source_context"))
    provenance = _provenance(payload, context)
    period = _period_value(model)
    source = _first(provenance, "source", "provider", "name") or _first(payload, "source", "provider") or _first(context, "source", "provider")
    collected = _first(provenance, "collected_at", "fetched_at", "observed_at") or _first(context, "computed_at")
    bits = [f"来源：{_esc(source, _MISSING)}", f"时期：{_esc(period, _MISSING)}"]
    if "adjusted" in context:
        basis = "前复权" if context.get("adjusted") is True else "原始价格" if context.get("adjusted") is False else "价格口径未指定"
        bits.append(f"口径：{basis}")
    if _first(context, "as_of"):
        bits.append(f"截至：{_esc(context.get('as_of'))}")
    if collected not in (None, ""):
        bits.append(f"采集：{_esc(collected)}")
    return '<div class="chan-provenance">' + " · ".join(bits) + "</div>"


def _render_capabilities(chan: Mapping[str, Any]) -> str:
    caps = _dict(chan.get("capabilities"))
    labels = []
    labels.append("完成笔坐标已提供" if caps.get("strokes") is True else "完成笔坐标未提供")
    labels.append("中枢坐标已提供" if caps.get("centers") is True else "中枢坐标未提供")
    labels.append("MACD 背驰已提供" if caps.get("macd_divergence") is True else "背驰代理未确认")
    labels.append("正式信号已提供" if caps.get("official_signals") is True else "仅候选点")
    return '<div class="chan-capabilities" aria-label="能力边界">' + " · ".join(_esc(label) for label in labels) + "</div>"


def _render_data_notes(model: Mapping[str, Any]) -> str:
    """Expose backend reasons/warnings without turning them into conclusions."""
    payload = model.get("payload") or {}
    context = _dict(model.get("source_context"))
    notes: list[str] = []
    reason = _first(payload, "reason", "error", "message")
    if reason:
        notes.append(f'<p class="chan-data-reason"><strong>数据状态</strong>{_esc(reason)}</p>')
    warnings: list[Any] = []
    for value in _list(payload.get("warnings")):
        if value not in warnings:
            warnings.append(value)
    # A top-level warning in chan.v1 is currently used for the weekly
    # in-progress tail; keep it with W rather than repeating it on D.
    if model.get("level") == "W":
        for value in _list(context.get("warnings")):
            if value not in warnings:
                warnings.append(value)
    if warnings:
        notes.append('<ul class="chan-data-warnings">' + "".join(f"<li>{_esc(value)}</li>" for value in warnings) + "</ul>")
    if not notes:
        return ""
    return '<div class="chan-data-notes" aria-label="数据提示">' + "".join(notes) + "</div>"


def _render_step_card(step: Mapping[str, Any], ordinal: int, *, current: bool = False) -> str:
    annotation_ids = " ".join(str(value) for value in (step.get("annotation_keys") or []) if value)
    observation = f'<p class="chan-step-observation"><strong>当前结构</strong>{_esc(step.get("observation"))}</p>' if step.get("observation") else ""
    focus_ids = " ".join(step.get("focus_keys") or [])
    why = f'<p><strong>依据</strong>{_esc(step.get("why"))}</p>' if step.get("why") else ""
    next_if = f'<p><strong>下一步条件</strong>{_esc(step.get("next_if"))}</p>' if step.get("next_if") else ""
    coord_refs = step.get("coord_refs") or []
    coord_html = ""
    if coord_refs:
        detail = json.dumps(coord_refs, ensure_ascii=False, default=str, separators=(", ", ": "))
        coord_html = f'<details class="chan-coord-details"><summary>查看完整坐标引用</summary><code>{_esc(detail)}</code></details>'
    cls = "chan-step-card chan-step-current" if current else "chan-step-card"
    return f'''<article class="{cls}" data-chan-step-card="{ordinal}" data-step-id="{_esc(step.get("id"))}" data-step-kind="{_esc(step.get("kind"))}" data-annotation-ids="{_esc(annotation_ids)}" data-focus-ids="{_esc(focus_ids)}">
  <div class="chan-step-kicker">STEP {ordinal + 1}</div>
  <h4>{_esc(step.get("title"), f"第 {ordinal + 1} 步")}</h4>
  {observation}
  <p>{_esc(step.get("explanation"), "未提供该步骤的原始讲解文本。")}</p>
  {why}{next_if}{coord_html}
</article>'''


def _render_overview_note(model: Mapping[str, Any], *, source: bool = False) -> str:
    bars = model.get("bars") or []
    latest = bars[-1] if bars else {}
    centers = [a["item"] for a in model.get("annotations", []) if a["kind"] == "center"]
    center = centers[-1] if centers else {}
    unfinished = model.get("unfinished_bi") or {}
    direction = _direction(unfinished.get("dir", unfinished.get("direction")))
    direction_label = "向上延伸" if direction == "up" else "向下延伸" if direction == "down" else "尚无未完成笔"
    center_text = f'{_fmt_number(center.get("zd"))}–{_fmt_number(center.get("zg"))}' if center else "尚未形成"
    source_class = " chan-overview-source" if source else ""
    hidden_attr = " hidden" if source else ""
    return f'''<article class="chan-step-card chan-overview-note{source_class}" data-chan-overview{hidden_attr}>
  <div class="chan-step-kicker">STRUCTURE SNAPSHOT · {model.get("level", "D")}</div>
  <h4>从走势，到成立条件。</h4>
  <div class="chan-snapshot-metrics"><span>最新收盘<strong>{_fmt_number(latest.get("close"))}</strong></span><span>最近中枢<strong>{center_text}</strong></span><span>未完成结构<strong>{direction_label}</strong></span></div>
  <p>选择图上的笔、中枢或候选点，查看它的价格、日期和失效条件；按“下一步”逐层读图。</p>
</article>'''


def _render_price_action_records(model: Mapping[str, Any]) -> str:
    pa = _dict((model.get("payload") or {}).get("price_action"))
    records = _list(pa.get("levels")) + _list(pa.get("events"))
    if not records:
        return ""
    rows = []
    for value in records:
        item = _dict(value)
        invalid = item.get("invalid_if")
        invalid = str(invalid.get("text") or invalid) if isinstance(invalid, Mapping) else str(invalid or "未记录")
        rows.append(f'<tr><td><button type="button" class="chan-point-button" data-pa-select="{_esc(item.get("id"))}">{_esc(item.get("label"))}</button></td><td>{_esc(item.get("dt") or item.get("confirmed_at"))}</td><td>{_fmt_number(item.get("price"))}</td><td class="chan-basis-cell">{_esc(item.get("evidence") or item.get("reason"))}</td><td class="chan-invalid-cell">{_esc(invalid)}</td></tr>')
    return '<div class="chan-point-table-wrap"><table class="chan-point-table"><caption>价格行为观察 · 摆动支撑阻力与突破 / 回踩 · 与严格缠论信号分开</caption><thead><tr><th>结构</th><th>日期</th><th>价格</th><th>成立依据</th><th>失效条件</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'


def _render_point_table(model: Mapping[str, Any]) -> str:
    return render_chan_table(model) + _render_price_action_records(model)


def _render_level_panel(model: Mapping[str, Any], *, active: bool, fallback: bool = False) -> str:
    level = model["level"]
    steps = model.get("steps", [])
    step_cards = "".join(_render_step_card(step, index, current=index == 0) for index, step in enumerate(steps))
    if not step_cards:
        step_cards = '<article class="chan-step-card chan-step-empty"><div class="chan-step-kicker">OFFLINE NOTES</div><p>本级别暂无离线讲解步骤；图形仅展示输入坐标。</p></article>'
    status = _status_label(model.get("status", "missing"))
    status_attr = "" if active else " hidden"
    state = "fallback" if fallback else "available" if (model.get("bars") or model.get("bar_count")) else "empty"
    heading = "普通 K 线回退图" if fallback else "日线结构" if level == "D" else "周线数据不足" if not (model.get("bars") or model.get("bar_count")) else "周线结构"
    return f'''<section class="chan-level-panel" id="chan-panel-{level}" data-chan-level-panel="{level}" role="tabpanel" aria-labelledby="chan-level-tab-{level}" data-chan-state="{state}"{status_attr}>
  <div class="chan-chart-heading"><h3>{heading}</h3><div class="chan-ohlc-readout" data-chan-ohlc aria-live="off">点选笔 / 中枢查看解释 · 轻触读取 OHLC</div><span class="chan-status-badge">{_esc(status)}</span></div>
  <div class="chan-chart-frame">{_svg_chart(model, fallback=fallback)}</div>
  <div class="chan-chart-legend"><span class="legend-solid">实线 · 已完成笔</span><span class="legend-dashed">虚线 · 未完成笔 / 候选</span><span class="legend-band">带状 · 中枢</span><span data-chan-visible-range></span></div>
  <div class="chan-live-explanation" data-chan-current-step aria-live="polite">{_render_overview_note(model)}</div>
  <div class="chan-evidence-tray">
    <details class="chan-step-archive"><summary>逐层讲解 · {len(steps)} 步</summary>{_render_overview_note(model, source=True)}<div data-chan-step-list>{step_cards}</div></details>
    <details class="chan-ledger-archive"><summary>结构与价位明细</summary>{_render_point_table(model)}</details>
    <details class="chan-source-archive"><summary>来源与方法</summary>{_render_provenance(model)}{_render_data_notes(model)}<p>只解释输入坐标；笔级中枢与价格行为叠加分开标识。候选不是已确认买卖点，力度代理不等于严格 MACD 背驰。</p></details>
  </div>
</section>'''


def _render_fallback_model(level: str, bars: list[dict[str, Any]], source: Mapping[str, Any]) -> dict[str, Any]:
    payload = {"status": "missing", "bars": bars, "provenance": _dict(source.get("provenance"))}
    return _build_level_model(level, payload)


def _safe_portrait(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    lower = raw.lower()
    if lower.startswith("javascript:") or lower.startswith("vbscript:"):
        return ""
    if lower.startswith("data:") and not lower.startswith("data:image/"):
        return ""
    if re.match(r"^[a-z][a-z0-9+.-]*:", lower) and not lower.startswith(("http://", "https://", "data:image/")):
        return ""
    return _esc(raw)


def render_chan_desk(raw: Any, portrait_uri: str = "") -> str:
    """Render the standalone Chan v1 workbench as a scoped HTML section."""
    chan, kline = _extract_payload(raw)
    raw_levels = {level: _level_payload(chan, level) for level in _LEVELS} if chan else {level: {} for level in _LEVELS}
    models: dict[str, dict[str, Any]] = {}
    for level in _LEVELS:
        payload = dict(raw_levels[level])
        pa = _dict(kline.get("price_action"))
        if not payload.get("price_action") and _dict(pa.get("levels")).get(level):
            payload["price_action"] = _dict(pa["levels"].get(level))
        models[level] = _build_level_model(level, payload) if payload else _build_level_model(level, {})
        models[level]["source_context"] = chan or kline
        if not payload or (not models[level]["bars"] and models[level]["status"] in {"missing", "error", "unavailable"}):
            fallback = _fallback_bars(kline, level)
            if fallback:
                models[level] = _render_fallback_model(level, fallback, kline)
                models[level]["source_context"] = chan or kline

    has_chan = bool(chan)
    ticker = str(_first(chan, "ticker", "symbol") or _first(_dict(raw), "ticker", "symbol") or "")
    tab_html = []
    for index, level in enumerate(_LEVELS):
        tab_html.append(
            f'<button type="button" class="chan-level-tab" id="chan-level-tab-{level}" role="tab" aria-selected="{"true" if index == 0 else "false"}" aria-controls="chan-panel-{level}" data-chan-level="{level}">{"日线 D" if level == "D" else "周线 W"}</button>'
        )

    panel_html = []
    for index, level in enumerate(_LEVELS):
        model = models[level]
        fallback = not has_chan or model.get("status") in {"missing", "error", "unavailable"} and bool(model.get("bars"))
        panel_html.append(_render_level_panel(model, active=index == 0, fallback=fallback))

    capabilities = _render_capabilities(chan) if chan else '<div class="chan-capabilities">chan.v1 不可用 · 保留普通 K 线</div>'
    version = _first(chan, "version", "schema_version", "schemaVersion", "schema", "contract") or "chan.v1"
    overall = "有结构坐标" if has_chan else "结构数据不可用 · 普通 K 线回退"
    return f'''<section class="chan-desk" id="chan-workspace" data-chan-version="{_esc(version, "chan.v1")}" data-chan-state="{"available" if has_chan else "fallback"}" data-annotations="all" aria-label="缠论离线讲解工作台">
  <header class="chan-desk-header">
    <div><span class="chan-eyebrow">THE PRICE STRUCTURE DESK</span><h2>价格的结构，逐笔讲清。</h2><p class="chan-dek">从原始 K 线到中枢与候选点，沿着图上的证据，检查每一个成立与失效条件。</p></div>
    <div class="chan-header-meta"><strong>{_esc(ticker)}</strong><span>PRICE ACTION × CHAN</span><span>交互价格研究台</span></div>
  </header>
  <div class="chan-toolbar" role="toolbar" aria-label="缠论讲解控制">
    <div class="chan-level-tabs" role="tablist" aria-label="级别切换">{"".join(tab_html)}</div>
  <div class="chan-step-controls"><button type="button" class="chan-tool-button" data-chan-action="prev" aria-label="上一步">上一步</button><span class="chan-step-live" data-chan-live aria-live="polite">全览 · {len(models['D'].get('steps', []))} 步</span><button type="button" class="chan-tool-button" data-chan-action="next" aria-label="下一步">下一步</button></div>
    <details class="chan-presentation-options" data-chan-compact-tools open><summary>讲解显示</summary><div class="chan-view-controls"><button type="button" class="chan-tool-button" data-chan-action="all" aria-pressed="true">全部标注</button><button type="button" class="chan-tool-button" data-chan-action="hide" aria-pressed="false">隐藏标注</button><button type="button" class="chan-tool-button" data-chan-action="replay">重新讲解</button></div></details>
  </div>
  <div class="chan-chart-tools" role="toolbar" aria-label="图表视图与叠加层">
    <div class="chan-range-controls"><button type="button" class="chan-tool-button" data-chan-range="recent">近期</button><button type="button" class="chan-tool-button" data-chan-range="full">全历史</button><button type="button" class="chan-tool-button" data-chan-range="zoom-in" aria-label="放大时间轴">＋</button><button type="button" class="chan-tool-button" data-chan-range="zoom-out" aria-label="缩小时间轴">−</button><button type="button" class="chan-tool-button" data-chan-range="left" aria-label="向较早日期平移">←</button><button type="button" class="chan-tool-button" data-chan-range="right" aria-label="向最近日期平移">→</button></div>
    <details class="chan-overlay-details" data-chan-compact-tools open><summary>图层</summary><div class="chan-overlay-controls"><button type="button" class="chan-tool-button" data-chan-overlay="ma" aria-pressed="true">MA 20 / 60</button><button type="button" class="chan-tool-button" data-chan-overlay="levels" aria-pressed="true" title="默认显示最近六条尚未失效的关键位">关键位</button><button type="button" class="chan-tool-button" data-chan-overlay="level-history" aria-pressed="false">历史位</button><button type="button" class="chan-tool-button" data-chan-overlay="events" aria-pressed="true">突破 / 回踩</button><button type="button" class="chan-tool-button" data-chan-overlay="volume" aria-pressed="true">成交量</button><button type="button" class="chan-tool-button" data-chan-overlay="fractals" aria-pressed="false">分型</button></div></details>
  </div>
  <div class="chan-desk-grid"><div class="chan-chart-column">{"".join(panel_html)}</div></div>
  <noscript><p class="chan-noscript-note">当前浏览器未启用脚本：默认显示日线与周线静态结构图；下方步骤、点位表与周线记录仍可直接阅读。</p></noscript>
</section>'''
