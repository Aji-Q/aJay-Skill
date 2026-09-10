"""report.svg_primitives · SVG 图元 + 颜色常量 · v3.2 从 assemble_report.py 抽离.

19 个 svg_* 函数 · 独立无业务依赖 · 全部是纯渲染.

### 颜色语义
- COLOR_BULL · 看多绿 #059669
- COLOR_BEAR · 看空红 #dc2626
- COLOR_GOLD · 金色（高亮 / gauge）#d97706
- COLOR_CYAN · 青（主要数据色）#0891b2
- COLOR_BLUE / COLOR_PINK / COLOR_INDIGO · 辅助
- COLOR_MUTED · 灰 #94a3b8
- COLOR_GRID · 浅灰 #e2e8f0

### 函数清单
- svg_sparkline / svg_h_bar_compare / svg_donut / svg_gauge / svg_radar
- svg_signal_lights / svg_supply_flow / svg_timeline / svg_bars
- svg_candlestick / svg_pe_band / svg_progress_row / svg_peer_table
- svg_unlock_timeline / svg_dividend_combo / svg_institutional_quarters / svg_thermometer

### 向后兼容
assemble_report.py 保留 `from lib.report.svg_primitives import *` · 所有旧调用工作.
"""
from __future__ import annotations

import math


COLOR_BULL = "#059669"
COLOR_BEAR = "#dc2626"
COLOR_GOLD = "#d97706"
COLOR_CYAN = "#0891b2"
COLOR_BLUE = "#2563eb"
COLOR_PINK = "#db2777"
COLOR_INDIGO = "#4f46e5"
COLOR_MUTED = "#94a3b8"
COLOR_GRID = "#e2e8f0"

# The report has both legacy light-theme styles and the continuous report's
# semantic variables.  Keep a literal fallback so older, standalone reports
# continue to render when these variables are not defined.
TEXT_MAIN = "var(--text-main, #0f172a)"
TEXT_STRONG = "var(--text-bright, #0f172a)"
TEXT_MID = "var(--text-mid, #475569)"
TEXT_DIM = "var(--text-dim, #64748b)"
SURFACE = "var(--bg-card, #ffffff)"
SURFACE_TINT = "var(--bg-tinted, #f1f5f9)"
BORDER = "var(--border-soft, #e2e8f0)"
BORDER_STRONG = "var(--border, #cbd5e1)"


def finite_number(value, default=None):
    """Return a finite float, treating NaN/Inf and placeholders as missing."""
    if isinstance(value, bool):
        return default
    if isinstance(value, str):
        value = value.strip().replace(",", "").replace("%", "")
        if not value or value in {"—", "-", "None", "null"}:
            return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def finite_series(values) -> list[float]:
    """Filter a sequence to finite numeric observations only."""
    return [number for value in (values or []) if (number := finite_number(value)) is not None]


def _empty_viz(message: str = "数据缺失") -> str:
    """Small non-SVG state used when a chart has no valid numeric input."""
    return f'<div class="viz-empty" data-state="missing" style="color:{TEXT_DIM};font-size:11px">{message}</div>'


def _format_number(value: float) -> str:
    """Format finite chart labels without gratuitous trailing .0."""
    number = finite_number(value)
    if number is None:
        return "—"
    return str(int(number)) if number.is_integer() else f"{number:g}"


def _safe_text(value, default: str = "—") -> str:
    """Keep non-finite numeric placeholders out of SVG text nodes too."""
    if value is None:
        return default
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)) and not math.isfinite(float(value)):
        return default
    text = str(value)
    return default if text.strip().lower() in {"nan", "+nan", "-nan", "inf", "+inf", "-inf", "infinity", "+infinity", "-infinity"} else text


def _is_us_market(market) -> bool:
    """Recognize common US-market codes; missing market keeps legacy colors."""
    return str(market or "").strip().upper() in {
        "U", "US", "USA", "NYSE", "NASDAQ", "AMEX", "ARCA", "NMS", "NG",
    }


def svg_sparkline(values: list, width: int = 240, height: int = 50, color: str = COLOR_CYAN, fill: bool = True) -> str:
    """Tiny line chart. Values normalized to fit."""
    values = finite_series(values)
    if len(values) < 2:
        return f'<svg viewBox="0 0 {width} {height}" style="display:block;width:100%;height:{height}px"></svg>'
    vmin, vmax = min(values), max(values)
    span = max(vmax - vmin, 1e-9)
    pts = []
    for i, v in enumerate(values):
        x = i / (len(values) - 1) * (width - 4) + 2
        y = height - 4 - (v - vmin) / span * (height - 8)
        pts.append(f"{x:.1f},{y:.1f}")
    path = "M " + " L ".join(pts)
    fill_path = ""
    if fill:
        fill_path = f'<path d="{path} L {width-2},{height-2} L 2,{height-2} Z" fill="{color}" fill-opacity="0.12"/>'
    return f'''<svg viewBox="0 0 {width} {height}" preserveAspectRatio="none" style="display:block;width:100%;height:{height}px">
  {fill_path}
  <path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
  <circle cx="{pts[-1].split(',')[0]}" cy="{pts[-1].split(',')[1]}" r="3" fill="{color}"/>
</svg>'''


def svg_h_bar_compare(label_a: str, val_a: float, label_b: str, val_b: float, unit: str = "", width: int = 260) -> str:
    """Horizontal back-to-back bar comparing two values."""
    val_a = finite_number(val_a)
    val_b = finite_number(val_b)
    if val_a is None or val_b is None:
        return _empty_viz("对比数据缺失")
    label_a = _safe_text(label_a)
    label_b = _safe_text(label_b)
    unit = _safe_text(unit, default="")
    max_v = max(abs(val_a), abs(val_b), 1)
    pct_a = abs(val_a) / max_v * 100
    pct_b = abs(val_b) / max_v * 100
    color_a = COLOR_BULL if val_a >= val_b else COLOR_MUTED
    color_b = COLOR_BULL if val_b > val_a else COLOR_MUTED
    return f'''<div style="font-family: Fira Code, monospace; font-size: 11px;">
  <div style="display:flex; justify-content:space-between; margin-bottom:4px; color:{TEXT_MID};">
    <span>{label_a}</span><strong style="color:{TEXT_STRONG}">{_format_number(val_a)}{unit}</strong>
  </div>
  <div style="height:8px; background:{SURFACE_TINT}; border-radius:4px; overflow:hidden; margin-bottom:8px;">
    <div style="width:{pct_a}%; height:100%; background:{color_a}; border-radius:4px;"></div>
  </div>
  <div style="display:flex; justify-content:space-between; margin-bottom:4px; color:{TEXT_MID};">
    <span>{label_b}</span><strong style="color:{TEXT_STRONG}">{_format_number(val_b)}{unit}</strong>
  </div>
  <div style="height:8px; background:{SURFACE_TINT}; border-radius:4px; overflow:hidden;">
    <div style="width:{pct_b}%; height:100%; background:{color_b}; border-radius:4px;"></div>
  </div>
</div>'''


def svg_donut(segments: list[tuple], total: float = None, label: str = "", size: int = 120) -> str:
    """Donut chart. segments = [(label, value, color), ...]"""
    clean_segments = []
    for segment in segments or []:
        if len(segment) < 3:
            continue
        value = finite_number(segment[1])
        if value is None or value <= 0:
            continue
        clean_segments.append((_safe_text(segment[0]), value, segment[2]))
    if not clean_segments:
        return ""
    total = finite_number(total)
    if total is None or total <= 0:
        total = sum(s[1] for s in clean_segments)
    if total <= 0 or not math.isfinite(total):
        return ""
    cx = cy = size / 2
    r = size / 2 - 8
    inner_r = r * 0.6
    paths = []
    cur_angle = -90  # start at top
    for lbl, val, color in clean_segments:
        sweep = val / total * 360
        if sweep <= 0:
            continue
        end_angle = cur_angle + sweep
        large = 1 if sweep > 180 else 0
        x1 = cx + r * math.cos(math.radians(cur_angle))
        y1 = cy + r * math.sin(math.radians(cur_angle))
        x2 = cx + r * math.cos(math.radians(end_angle))
        y2 = cy + r * math.sin(math.radians(end_angle))
        x3 = cx + inner_r * math.cos(math.radians(end_angle))
        y3 = cy + inner_r * math.sin(math.radians(end_angle))
        x4 = cx + inner_r * math.cos(math.radians(cur_angle))
        y4 = cy + inner_r * math.sin(math.radians(cur_angle))
        d = f"M {x1},{y1} A {r},{r} 0 {large} 1 {x2},{y2} L {x3},{y3} A {inner_r},{inner_r} 0 {large} 0 {x4},{y4} Z"
        paths.append(f'<path d="{d}" fill="{color}"/>')
        cur_angle = end_angle
    legend = "".join(
        f'<div style="display:flex; align-items:center; gap:6px; font-size:10px; margin-bottom:2px;">'
        f'<span style="width:8px; height:8px; background:{c}; border-radius:2px"></span>'
        f'<span style="color:{TEXT_MID}">{l}</span>'
        f'<strong style="margin-left:auto; color:{TEXT_STRONG}">{v}</strong></div>'
        for l, v, c in clean_segments
    )
    label = _safe_text(label, default="")
    return f'''<div style="display:flex; align-items:center; gap:14px;">
  <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="flex-shrink:0">
    {"".join(paths)}
    {f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="Fira Sans" font-weight="700" font-size="14" fill="{TEXT_STRONG}">{label}</text>' if label else ""}
  </svg>
  <div style="flex:1; min-width:0">{legend}</div>
</div>'''


def svg_gauge(value: float, max_val: float = 100, label: str = "", size: int = 220, color: str = COLOR_GOLD, unit: str = "") -> str:
    """Semi-circle gauge — larger, bolder."""
    value = finite_number(value)
    max_val = finite_number(max_val)
    if value is None or max_val is None or max_val <= 0:
        return _empty_viz("仪表数据缺失")
    label = _safe_text(label, default="")
    unit = _safe_text(unit, default="")
    pct = max(0, min(1, value / max_val))
    cx = size / 2
    cy = size * 0.65
    r = size * 0.40
    val_a = 180 - pct * 180
    bg = f'<path d="M {cx-r},{cy} A {r},{r} 0 0 1 {cx+r},{cy}" fill="none" stroke="{BORDER}" stroke-width="14" stroke-linecap="round"/>'
    x2 = cx + r * math.cos(math.radians(val_a))
    y2 = cy + r * math.sin(math.radians(val_a))
    large = 1 if pct > 0.5 else 0
    val_arc = f'<path d="M {cx-r},{cy} A {r},{r} 0 {large} 1 {x2},{y2}" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round"/>'
    return f'''<svg width="{size}" height="{size*0.78}" viewBox="0 0 {size} {size*0.78}">
  {bg}
  {val_arc}
  <text x="{cx}" y="{cy-4}" text-anchor="middle" font-family="Fira Sans" font-weight="900" font-size="52" fill="{TEXT_STRONG}" letter-spacing="-2">{value:.0f}<tspan font-size="20" fill="{TEXT_DIM}" dx="2">{unit}</tspan></text>
  <text x="{cx}" y="{cy+22}" text-anchor="middle" font-family="Fira Sans" font-size="12" font-weight="600" fill="{TEXT_MID}">{label}</text>
</svg>'''


def svg_radar(labels: list, values: list, max_val: float = 10, size: int = 160) -> str:
    """5-axis radar chart."""
    max_val = finite_number(max_val)
    if max_val is None or max_val <= 0:
        return _empty_viz("雷达数据缺失")
    pairs = []
    for label, value in zip(labels or [], values or []):
        number = finite_number(value)
        if number is not None:
            pairs.append((_safe_text(label), max(0, min(max_val, number))))
    if len(pairs) < 3:
        return _empty_viz("雷达数据缺失")
    labels = [label for label, _ in pairs]
    values = [value for _, value in pairs]
    n = len(labels)
    cx = cy = size / 2
    r = size * 0.38
    # axis lines + labels
    axes = []
    for i, lbl in enumerate(labels):
        a = -math.pi / 2 + i * 2 * math.pi / n
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        axes.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="{BORDER}" stroke-width="1"/>')
        lx = cx + (r + 12) * math.cos(a)
        ly = cy + (r + 14) * math.sin(a)
        axes.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-family="Fira Code" font-size="9" fill="{TEXT_DIM}">{lbl}</text>')
    # rings
    for ring in (0.33, 0.66, 1.0):
        ring_r = r * ring
        axes.append(f'<circle cx="{cx}" cy="{cy}" r="{ring_r}" fill="none" stroke="{SURFACE_TINT}"/>')
    # value polygon
    pts = []
    for i, v in enumerate(values):
        a = -math.pi / 2 + i * 2 * math.pi / n
        rv = r * (v / max_val)
        x = cx + rv * math.cos(a)
        y = cy + rv * math.sin(a)
        pts.append(f"{x:.1f},{y:.1f}")
    poly = f'<polygon points="{" ".join(pts)}" fill="{COLOR_CYAN}" fill-opacity="0.25" stroke="{COLOR_CYAN}" stroke-width="2"/>'
    return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">{"".join(axes)}{poly}</svg>'


def svg_signal_lights(hit: int, total: int = 8) -> str:
    """N LED dots, hit ones red, ok ones green."""
    cells = []
    for i in range(total):
        on = i < hit
        color = COLOR_BEAR if on else COLOR_BULL
        opacity = 1 if on else 0.35
        cells.append(
            f'<div style="width:24px;height:24px;border-radius:50%;background:{color};opacity:{opacity};'
            f'box-shadow:0 0 8px {color}40;display:flex;align-items:center;justify-content:center;'
            f'color:#fff;font-family:Fira Code;font-size:10px;font-weight:700">{i+1}</div>'
        )
    label = "🔴 命中信号" if hit > 0 else "🟢 全部通过"
    return f'''<div>
  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px">{"".join(cells)}</div>
  <div style="font-family:Fira Code;font-size:10px;color:{TEXT_MID}">{label} · {hit}/{total}</div>
</div>'''


def svg_supply_flow(upstream: str, company: str, downstream: str) -> str:
    """Visual upstream → company → downstream flow. Truncate long text to prevent overflow."""
    # Truncate each segment to prevent CSS overflow
    def _trunc(s: str, max_len: int = 60) -> str:
        s = _safe_text(s, default="").strip()
        if len(s) > max_len:
            return s[:max_len] + "…"
        return s
    upstream = _trunc(upstream, 50)
    company = _trunc(company, 30)
    downstream = _trunc(downstream, 50)

    return f'''<div style="display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:8px;align-items:center;font-family:Fira Sans;overflow:hidden">
  <div style="padding:10px 12px;background:#cffafe;border:1px solid #0891b2;border-radius:8px;text-align:center;overflow:hidden">
    <div style="font-size:9px;color:#0891b2;letter-spacing:.1em;margin-bottom:4px">UPSTREAM</div>
    <div style="font-size:11px;font-weight:600;color:{TEXT_MAIN};line-height:1.4;word-break:break-all;overflow-wrap:break-word">{upstream}</div>
  </div>
  <div style="font-size:18px;color:#0891b2;flex-shrink:0">→</div>
  <div style="padding:10px 12px;background:#fef3c7;border:2px solid #d97706;border-radius:8px;text-align:center;overflow:hidden">
    <div style="font-size:9px;color:#d97706;letter-spacing:.1em;margin-bottom:4px">COMPANY</div>
    <div style="font-size:11px;font-weight:700;color:{TEXT_MAIN};line-height:1.4">{company}</div>
  </div>
  <div style="font-size:18px;color:#0891b2;flex-shrink:0">→</div>
  <div style="padding:10px 12px;background:#d1fae5;border:1px solid #059669;border-radius:8px;text-align:center;overflow:hidden">
    <div style="font-size:9px;color:#059669;letter-spacing:.1em;margin-bottom:4px">DOWNSTREAM</div>
    <div style="font-size:11px;font-weight:600;color:{TEXT_MAIN};line-height:1.4;word-break:break-all;overflow-wrap:break-word">{downstream}</div>
  </div>
</div>'''


def svg_timeline(events: list) -> str:
    """Vertical timeline of events."""
    if not events:
        return ""
    items = []
    for ev in events:
        ev = _safe_text(ev)
        items.append(
            f'<div style="display:flex;gap:10px;padding:8px 0">'
            f'<div style="width:10px;height:10px;border-radius:50%;background:{COLOR_GOLD};margin-top:4px;flex-shrink:0;'
            f'box-shadow:0 0 0 3px #fef3c7"></div>'
            f'<div style="font-size:11px;color:{TEXT_MAIN};line-height:1.5">{ev}</div>'
            f'</div>'
        )
    return f'<div style="border-left:2px solid {BORDER};padding-left:12px;margin-left:5px">{"".join(items)}</div>'


def svg_bars(values: list, labels: list = None, width: int = 280, height: int = 120, color: str = COLOR_CYAN, show_values: bool = True, overlay_line: list = None, line_color: str = COLOR_GOLD) -> str:
    """Vertical bar chart with optional overlay line."""
    raw_values = list(values or [])
    clean_values = []
    clean_labels = []
    for index, value in enumerate(raw_values):
        number = finite_number(value)
        if number is None:
            continue
        clean_values.append(number)
        if labels:
            clean_labels.append(_safe_text(labels[index]) if index < len(labels) else "")
    if not clean_values:
        return _empty_viz("柱状数据缺失")
    values = clean_values
    n = len(values)
    pad_l, pad_r, pad_t, pad_b = 30, 10, 14, 24
    chart_w = width - pad_l - pad_r
    chart_h = height - pad_t - pad_b
    # Overlay points are only drawn when they remain index-aligned and every
    # point is finite.  A malformed point must not turn into an SVG ``nan``.
    safe_overlay = None
    if overlay_line is not None and len(overlay_line) == len(raw_values):
        raw_overlay = [finite_number(value) for value in overlay_line]
        if all(value is not None for value in raw_overlay):
            safe_overlay = [raw_overlay[index] for index, value in enumerate(raw_values) if finite_number(value) is not None]
    all_values = values + (safe_overlay or []) + [0]
    max_v = max(all_values)
    min_v = min(all_values)
    span = max(max_v - min_v, 1e-9)
    bar_w = chart_w / n * 0.7
    gap = chart_w / n * 0.3

    bars = []
    vals_txt = []
    labels_txt = []
    for i, v in enumerate(values):
        x = pad_l + i * (chart_w / n) + gap / 2
        bar_h = (v - min_v) / span * chart_h if span else 0
        y = pad_t + chart_h - bar_h
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}" rx="2"/>')
        if show_values:
            vals_txt.append(f'<text x="{x + bar_w/2:.1f}" y="{y - 4:.1f}" text-anchor="middle" font-family="Fira Code" font-size="9" fill="{TEXT_STRONG}" font-weight="700">{_format_number(v)}</text>')
        if labels:
            labels_txt.append(f'<text x="{x + bar_w/2:.1f}" y="{pad_t + chart_h + 14}" text-anchor="middle" font-family="Fira Code" font-size="9" fill="{TEXT_DIM}">{clean_labels[i] if i < len(clean_labels) else ""}</text>')

    # y-axis zero line
    y_zero = pad_t + chart_h - (0 - min_v) / span * chart_h if span else pad_t + chart_h
    axis = f'<line x1="{pad_l}" y1="{y_zero:.1f}" x2="{pad_l+chart_w}" y2="{y_zero:.1f}" stroke="{BORDER_STRONG}" stroke-width="1"/>'

    # overlay line (e.g. growth rate)
    line_path = ""
    line_dots = ""
    if safe_overlay and len(safe_overlay) == n:
        pts = []
        for i, v in enumerate(safe_overlay):
            x = pad_l + i * (chart_w / n) + chart_w / n / 2
            y = pad_t + chart_h - (v - min_v) / span * chart_h if span else pad_t + chart_h
            pts.append((x, y))
        path_str = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        line_path = f'<path d="{path_str}" fill="none" stroke="{line_color}" stroke-width="2.5"/>'
        line_dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{line_color}"/>' for x, y in pts)

    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  {axis}
  {"".join(bars)}
  {line_path}
  {line_dots}
  {"".join(vals_txt)}
  {"".join(labels_txt)}
</svg>'''


def svg_candlestick(
    candles: list,
    width: int = 380,
    height: int = 180,
    ma_20: list = None,
    ma_60: list = None,
    market: str = None,
) -> str:
    """Hand-rolled SVG candlestick.

    ``market`` accepts common US codes (``U``, ``NYSE``, ``NASDAQ``).  US
    charts use the convention green-up/red-down; omitted/other markets retain
    the historical red-up/green-down behavior for old reports.
    """
    raw_candles = list(candles or [])
    valid = []
    for index, candle in enumerate(raw_candles):
        if not isinstance(candle, dict):
            continue
        op = finite_number(candle.get("open"))
        cl = finite_number(candle.get("close"))
        hi = finite_number(candle.get("high"))
        lo = finite_number(candle.get("low"))
        if any(value is None for value in (op, cl, hi, lo)):
            continue
        # OHLC values must form an envelope.  Dropping malformed observations
        # is preferable to drawing an inverted wick or leaking bad numbers.
        if hi < max(op, cl) or lo > min(op, cl):
            continue
        valid.append((index, {"open": op, "close": cl, "high": hi, "low": lo, "date": _safe_text(candle.get("date", ""), default="")}))
    if not valid:
        return _empty_viz("K 线数据缺失")

    n = len(raw_candles)
    pad_l, pad_r, pad_t, pad_b = 40, 10, 10, 24
    chart_w = width - pad_l - pad_r
    chart_h = height - pad_t - pad_b
    all_highs = [c["high"] for _, c in valid]
    all_lows = [c["low"] for _, c in valid]
    for moving_average in (ma_20, ma_60):
        for value in finite_series(moving_average):
            all_highs.append(value)
            all_lows.append(value)
    value_min = min(all_lows)
    value_max = max(all_highs)
    axis_pad = max((value_max - value_min) * 0.02, 1e-6)
    y_max = value_max + axis_pad
    y_min = value_min - axis_pad
    span = max(y_max - y_min, 1e-9)

    def y_of(v):
        return pad_t + chart_h - (v - y_min) / span * chart_h

    cw = chart_w / n * 0.7
    gap = chart_w / n * 0.3

    elems = []
    # grid
    for ring in (0.25, 0.5, 0.75):
        yg = pad_t + chart_h * ring
        elems.append(f'<line x1="{pad_l}" y1="{yg:.1f}" x2="{pad_l+chart_w}" y2="{yg:.1f}" stroke="{SURFACE_TINT}" stroke-width="1"/>')

    # y labels
    for frac, value in [(0, y_max), (0.5, (y_max + y_min) / 2), (1, y_min)]:
        yt = pad_t + chart_h * frac
        elems.append(f'<text x="{pad_l-5}" y="{yt+3:.1f}" text-anchor="end" font-family="Fira Code" font-size="9" fill="{TEXT_DIM}">{value:.1f}</text>')

    # candles.  Keep the original index so a missing observation produces a
    # visual gap rather than shifting dates/MA points into the wrong session.
    for i, candle in valid:
        x = pad_l + i * (chart_w / n) + gap / 2
        cx = x + cw / 2
        op, cl, hi, lo = candle["open"], candle["close"], candle["high"], candle["low"]
        is_up = cl >= op
        if _is_us_market(market):
            color = COLOR_BULL if is_up else COLOR_BEAR
        else:
            color = COLOR_BEAR if is_up else COLOR_BULL
        elems.append(f'<line x1="{cx:.1f}" y1="{y_of(hi):.1f}" x2="{cx:.1f}" y2="{y_of(lo):.1f}" stroke="{color}" stroke-width="1"/>')
        top = y_of(max(op, cl))
        bh = max(abs(y_of(cl) - y_of(op)), 1)
        elems.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{cw:.1f}" height="{bh:.1f}" fill="{color}" stroke="{color}" stroke-width="1"/>')

    # MA lines.  A non-finite point is omitted instead of becoming a ``nan``
    # coordinate in the polyline.
    def _ma_path(vals, color):
        if not vals:
            return ""
        pts = []
        for i, value in enumerate(vals):
            number = finite_number(value)
            if number is None or i >= n:
                continue
            x = pad_l + i * (chart_w / n) + cw / 2 + gap / 2
            y = y_of(number)
            pts.append(f"{x:.1f},{y:.1f}")
        if not pts:
            return ""
        return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round"/>'

    elems.append(_ma_path(ma_20, COLOR_GOLD))
    elems.append(_ma_path(ma_60, COLOR_INDIGO))

    # date labels (first, mid, last valid observations)
    date_entries = [(index, candle) for index, candle in valid if _safe_text(candle.get("date", ""), default="")]
    if date_entries:
        chosen = [date_entries[0], date_entries[len(date_entries) // 2], date_entries[-1]]
        seen = set()
        for i, candle in chosen:
            if i in seen:
                continue
            seen.add(i)
            date = _safe_text(candle.get("date", ""), default="")
            x = pad_l + i * (chart_w / n) + cw / 2
            elems.append(f'<text x="{x:.1f}" y="{pad_t+chart_h+14}" text-anchor="middle" font-family="Fira Code" font-size="8" fill="{TEXT_DIM}">{date[-5:]}</text>')

    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="width:100%">
  {"".join(elems)}
</svg>
<div style="display:flex;gap:14px;margin-top:6px;font-family:Fira Code;font-size:9px">
  <span><span style="display:inline-block;width:12px;height:2px;background:{COLOR_GOLD};vertical-align:middle"></span> MA20</span>
  <span><span style="display:inline-block;width:12px;height:2px;background:{COLOR_INDIGO};vertical-align:middle"></span> MA60</span>
</div>'''


def svg_pe_band(pe_history: list, bands: dict = None, width: int = 300, height: int = 140) -> str:
    """Render a PE history against an actual numeric PE axis.

    The old implementation inferred p25/p50/p75 from the short display
    sequence and painted those as a five-year valuation band.  That made a
    five-point history look like an independently sourced percentile series
    and could contradict the separate ``pe_quantile`` input.  ``bands`` is
    retained as a compatibility argument, but inferred percentile bands are
    intentionally not rendered; callers that have a verified percentile
    history should present it as a separate, explicitly sourced series.
    """
    if not pe_history:
        return ""

    import math

    # A PE of zero/negative, NaN, or infinity is not a usable valuation
    # observation.  Filter those values before calculating either the axis or
    # the line so malformed/missing fixture inputs never leak NaN into SVG.
    values: list[float] = []
    for value in pe_history:
        try:
            number = float(str(value).strip().replace(",", "").replace("%", ""))
        except (TypeError, ValueError):
            continue
        if math.isfinite(number) and number > 0:
            values.append(number)
    if len(values) < 2:
        return ""

    n = len(values)
    pad_l, pad_r, pad_t, pad_b = 42, 10, 14, 24
    w = max(width - pad_l - pad_r, 1)
    h = max(height - pad_t - pad_b, 1)

    value_min = min(values)
    value_max = max(values)
    value_span = value_max - value_min
    axis_pad = max(value_span * 0.08, value_max * 0.03, 0.5)
    y_min = max(0.0, value_min - axis_pad)
    y_max = value_max + axis_pad
    span = max(y_max - y_min, 1e-9)

    def y_of(value: float) -> float:
        return pad_t + h - (value - y_min) / span * h

    # Numeric y-axis ticks are actual PE multiples, not percentile labels.
    axis = []
    for fraction, value in (
        (0.0, y_max),
        (0.5, (y_max + y_min) / 2),
        (1.0, y_min),
    ):
        y = pad_t + h * fraction
        axis.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l+w}" y2="{y:.1f}" '
            f'stroke="{COLOR_GRID}" stroke-width="1" stroke-dasharray="2,3"/>'
        )
        axis.append(
            f'<text x="{pad_l-4}" y="{y+3:.1f}" text-anchor="end" '
            f'font-family="Fira Code" font-size="8" fill="{TEXT_DIM}">{value:.1f}x</text>'
        )
    axis.append(
        f'<text x="{pad_l}" y="{pad_t-4}" text-anchor="start" '
        f'font-family="Fira Code" font-size="8" fill="{TEXT_DIM}">PE (x)</text>'
    )

    pts = []
    for index, value in enumerate(values):
        x = pad_l + index / (n - 1) * w
        y = y_of(value)
        pts.append((x, y))
    line = (
        f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
        f'fill="none" stroke="{COLOR_BLUE}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{COLOR_BLUE}"/>'
        for x, y in pts
    )

    # Highlight the latest valid observation; the display sequence has already
    # removed unusable points, so this is always a finite numeric value.
    last_x, last_y = pts[-1]
    current = (
        f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="5" fill="{COLOR_BLUE}" '
        f'stroke="{SURFACE}" stroke-width="2"/>'
    )
    cur_label = (
        f'<text x="{last_x:.1f}" y="{last_y-10:.1f}" text-anchor="end" '
        f'font-family="Fira Code" font-size="10" font-weight="700" fill="{COLOR_BLUE}">'
        f'{values[-1]:.1f}x</text>'
    )
    x_labels = []
    for index in sorted({0, n // 2, n - 1}):
        x = pad_l + index / (n - 1) * w
        x_labels.append(
            f'<text x="{x:.1f}" y="{pad_t+h+15:.1f}" text-anchor="middle" '
            f'font-family="Fira Code" font-size="8" fill="{TEXT_DIM}">T{index+1}</text>'
        )

    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="width:100%" data-pe-axis="actual">
  <title>PE 历史序列（实际倍数轴）</title>
  <desc>有效 PE 观测：{", ".join(f"{value:.1f}x" for value in values)}</desc>
  {"".join(axis)}
  {line}
  {dots}
  {current}
  {cur_label}
  {"".join(x_labels)}
</svg>'''


def svg_progress_row(
    label: str,
    pct: float,
    color: str = COLOR_CYAN,
    suffix: str = "",
    display_value: float = None,
) -> str:
    """Inline labeled progress bar.

    ``pct`` controls bar width while ``display_value`` optionally preserves the
    source metric in the label.  The extra argument is backward compatible
    with historical callers that displayed ``pct`` itself.
    """
    pct = finite_number(pct)
    if pct is None:
        return _empty_viz("进度数据缺失")
    pct_clamped = max(0, min(100, pct))
    display_number = finite_number(display_value) if display_value is not None else pct
    if display_number is None:
        return _empty_viz("进度数据缺失")
    label = _safe_text(label)
    suffix = _safe_text(suffix, default="")
    display_text = f"{pct:.1f}" if display_value is None else _format_number(display_number)
    return f'''<div style="display:flex;align-items:center;gap:10px;margin:6px 0">
  <div style="width:70px;font-family:Fira Code;font-size:10px;color:{TEXT_DIM}">{label}</div>
  <div style="flex:1;height:8px;background:{SURFACE_TINT};border-radius:4px;overflow:hidden">
    <div style="width:{pct_clamped}%;height:100%;background:{color};border-radius:4px"></div>
  </div>
  <div style="min-width:50px;text-align:right;font-family:Fira Code;font-size:11px;color:{TEXT_STRONG};font-weight:700">{display_text}{suffix}</div>
</div>'''


def svg_peer_table(rows: list) -> str:
    """HTML comparison table. rows = [{name, pe, pb, roe, revenue_growth, is_self}, ...]"""
    if not rows:
        return ""
    head = '''<tr style="background:#f8fafc">
  <th style="text-align:left;padding:8px 10px;font-family:Fira Code;font-size:9px;color:#64748b;font-weight:700;border-bottom:2px solid #e2e8f0">公司</th>
  <th style="text-align:right;padding:8px 10px;font-family:Fira Code;font-size:9px;color:#64748b;font-weight:700;border-bottom:2px solid #e2e8f0">PE</th>
  <th style="text-align:right;padding:8px 10px;font-family:Fira Code;font-size:9px;color:#64748b;font-weight:700;border-bottom:2px solid #e2e8f0">PB</th>
  <th style="text-align:right;padding:8px 10px;font-family:Fira Code;font-size:9px;color:#64748b;font-weight:700;border-bottom:2px solid #e2e8f0">ROE</th>
  <th style="text-align:right;padding:8px 10px;font-family:Fira Code;font-size:9px;color:#64748b;font-weight:700;border-bottom:2px solid #e2e8f0">营收增速</th>
</tr>'''
    body = ""
    for r in rows:
        is_self = r.get("is_self", False)
        row_style = 'background:#fef3c7;font-weight:700' if is_self else 'background:#ffffff'
        body += f'''<tr style="{row_style}">
  <td style="padding:8px 10px;font-family:Fira Sans;font-size:12px;color:#0f172a;border-bottom:1px solid #f1f5f9">{'⭐ ' if is_self else ''}{r.get("name", "")}</td>
  <td style="text-align:right;padding:8px 10px;font-family:Fira Code;font-size:11px;color:#0f172a;border-bottom:1px solid #f1f5f9">{r.get("pe", "—")}</td>
  <td style="text-align:right;padding:8px 10px;font-family:Fira Code;font-size:11px;color:#0f172a;border-bottom:1px solid #f1f5f9">{r.get("pb", "—")}</td>
  <td style="text-align:right;padding:8px 10px;font-family:Fira Code;font-size:11px;color:#0f172a;border-bottom:1px solid #f1f5f9">{r.get("roe", "—")}</td>
  <td style="text-align:right;padding:8px 10px;font-family:Fira Code;font-size:11px;color:#0f172a;border-bottom:1px solid #f1f5f9">{r.get("revenue_growth", "—")}</td>
</tr>'''
    return f'<table style="width:100%;border-collapse:collapse;font-family:Fira Sans">{head}{body}</table>'


def svg_unlock_timeline(unlocks: list, width: int = 280, height: int = 100) -> str:
    """Future unlock timeline: list of {date, amount_亿}."""
    if not unlocks:
        return '<div style="text-align:center;color:#94a3b8;font-size:11px;padding:10px">未来 12 个月无解禁</div>'
    valid = []
    for unlock in unlocks:
        if not isinstance(unlock, dict):
            continue
        amount = finite_number(unlock.get("amount"))
        if amount is None or amount < 0:
            continue
        valid.append((unlock, amount))
    if not valid:
        return _empty_viz("解禁数据缺失")
    n = len(valid)
    pad_l, pad_r, pad_t, pad_b = 20, 10, 16, 24
    w = width - pad_l - pad_r
    h = height - pad_t - pad_b
    max_a = max(amount for _, amount in valid) or 1
    bar_w = w / n * 0.6
    gap = w / n * 0.4
    bars = []
    for i, (u, amt) in enumerate(valid):
        date = _safe_text(u.get("date", ""), default="")
        x = pad_l + i * (w / n) + gap / 2
        bar_h = amt / max_a * h
        y = pad_t + h - bar_h
        color = COLOR_BEAR if amt > max_a * 0.5 else COLOR_GOLD
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}" rx="2"/>')
        bars.append(f'<text x="{x + bar_w/2:.1f}" y="{y - 3:.1f}" text-anchor="middle" font-family="Fira Code" font-size="9" fill="{TEXT_STRONG}" font-weight="700">{_format_number(amt)}</text>')
        bars.append(f'<text x="{x + bar_w/2:.1f}" y="{pad_t+h+14}" text-anchor="middle" font-family="Fira Code" font-size="8" fill="{TEXT_DIM}">{date}</text>')
    axis = f'<line x1="{pad_l}" y1="{pad_t+h}" x2="{pad_l+w}" y2="{pad_t+h}" stroke="{BORDER_STRONG}"/>'
    return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="width:100%">{axis}{"".join(bars)}</svg>'


def svg_dividend_combo(years: list, amounts: list, yields: list, width: int = 300, height: int = 140) -> str:
    """Dividend history: bars for amount + line for yield."""
    if not years or not amounts:
        return ""
    valid = []
    for index, amount in enumerate(amounts):
        number = finite_number(amount)
        if number is None or number < 0:
            continue
        valid.append((index, number))
    if not valid:
        return _empty_viz("分红数据缺失")
    n = len(valid)
    pad_l, pad_r, pad_t, pad_b = 36, 40, 14, 24
    w = width - pad_l - pad_r
    h = height - pad_t - pad_b
    max_a = max(number for _, number in valid) or 1
    yield_points = []
    for index, _ in valid:
        if yields and index < len(yields):
            number = finite_number(yields[index])
            if number is not None and number >= 0:
                yield_points.append((index, number))
    max_y = max((number for _, number in yield_points), default=5) or 1
    bar_w = w / n * 0.55
    gap = w / n * 0.45

    bars = []
    valid_positions = {index: position for position, (index, _) in enumerate(valid)}
    for position, (index, amount) in enumerate(valid):
        a = amount
        x = pad_l + position * (w / n) + gap / 2
        bar_h = a / max_a * h
        y = pad_t + h - bar_h
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{COLOR_CYAN}" rx="2"/>')
        bars.append(f'<text x="{x+bar_w/2:.1f}" y="{y-3:.1f}" text-anchor="middle" font-family="Fira Code" font-size="9" fill="{TEXT_STRONG}" font-weight="700">{_format_number(a)}</text>')
        year = _safe_text(years[index], default="") if index < len(years) else ""
        bars.append(f'<text x="{x+bar_w/2:.1f}" y="{pad_t+h+14}" text-anchor="middle" font-family="Fira Code" font-size="9" fill="{TEXT_DIM}">{year}</text>')

    # yield line (right axis)
    if yield_points:
        pts = []
        for index, y in yield_points:
            position = valid_positions[index]
            x = pad_l + position * (w / n) + w / n / 2
            yy = pad_t + h - y / max_y * h
            pts.append((x, yy))
        line = f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke="{COLOR_GOLD}" stroke-width="2.5"/>'
        dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{COLOR_GOLD}"/>' for x, y in pts)
        bars.append(line)
        bars.append(dots)
        # right axis label
        bars.append(f'<text x="{pad_l+w+4}" y="{pad_t+10}" font-family="Fira Code" font-size="9" fill="{COLOR_GOLD}">{max_y:.1f}%</text>')
        bars.append(f'<text x="{pad_l+w+4}" y="{pad_t+h}" font-family="Fira Code" font-size="9" fill="{COLOR_GOLD}">0%</text>')

    return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="width:100%">{"".join(bars)}</svg>'


def svg_institutional_quarters(data: dict, width: int = 300, height: int = 120) -> str:
    """Stacked/grouped bar of institutional holdings over quarters.
    data = {'quarters': ['23Q2', '23Q3', ...], 'fund': [...], 'qfii': [...], 'shehui': [...]}"""
    quarters = data.get("quarters", [])
    if not quarters:
        return ""
    series = [
        ("公募", data.get("fund", []), COLOR_CYAN),
        ("QFII", data.get("qfii", []), COLOR_BLUE),
        ("社保", data.get("shehui", []), COLOR_GOLD),
    ]
    n = len(quarters)
    pad_l, pad_r, pad_t, pad_b = 10, 10, 16, 22
    w = width - pad_l - pad_r
    h = height - pad_t - pad_b
    all_vals = [number for _, vals, _ in series for value in vals if (number := finite_number(value)) is not None and number >= 0] + [0]
    if all_vals == [0]:
        return _empty_viz("机构持仓数据缺失")
    max_v = max(all_vals) or 1

    bar_w = w / n * 0.28
    group_gap = w / n * 0.16

    elems = []
    for i in range(n):
        bx = pad_l + i * (w / n) + group_gap / 2
        for si, (_, vals, col) in enumerate(series):
            if i >= len(vals):
                continue
            v = finite_number(vals[i])
            if v is None or v < 0:
                continue
            bar_h = v / max_v * h
            x = bx + si * bar_w
            y = pad_t + h - bar_h
            elems.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w-0.5:.1f}" height="{bar_h:.1f}" fill="{col}" rx="1"/>')
        elems.append(f'<text x="{bx + 1.5*bar_w:.1f}" y="{pad_t+h+14}" text-anchor="middle" font-family="Fira Code" font-size="9" fill="{TEXT_DIM}">{_safe_text(quarters[i], default="")}</text>')

    legend = f'''<div style="display:flex;gap:10px;margin-top:4px;font-family:Fira Code;font-size:9px">
  <span style="color:{COLOR_CYAN}">■ 公募</span>
  <span style="color:{COLOR_BLUE}">■ QFII</span>
  <span style="color:{COLOR_GOLD}">■ 社保</span>
</div>'''
    return f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="width:100%">{"".join(elems)}</svg>{legend}'


def svg_thermometer(value: int, max_val: int = 100, label: str = "") -> str:
    """Heat thermometer (vertical)."""
    value = finite_number(value)
    max_val = finite_number(max_val)
    if value is None or max_val is None or max_val <= 0:
        return _empty_viz("热度数据缺失")
    pct = min(100, max(0, value / max_val * 100))
    color = COLOR_BEAR if value > 80 else COLOR_GOLD if value > 50 else COLOR_BULL
    return f'''<div style="display:flex;align-items:center;gap:14px">
  <div style="width:24px;height:120px;background:{SURFACE_TINT};border:1px solid {BORDER_STRONG};border-radius:12px;position:relative;overflow:hidden">
    <div style="position:absolute;bottom:0;left:0;right:0;height:{pct}%;background:linear-gradient(0deg,{color},{color}cc);border-radius:0 0 12px 12px;transition:height 1s"></div>
  </div>
  <div>
    <div style="font-family:Fira Sans;font-weight:900;font-size:32px;color:{color};line-height:1">{value}</div>
    <div style="font-family:Fira Code;font-size:9px;color:{TEXT_DIM};letter-spacing:.1em">{label}</div>
  </div>
</div>'''
