"""J Trader report evidence surface. Coverage is not calibrated predictive confidence."""
from __future__ import annotations

import math
from pathlib import Path

from lib.agent_review import load_fresh_agent_analysis
from lib.data_integrity import CRITICAL_CHECKS, validate
from lib.report.security import escape_text


def finite_number(value):
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (ValueError, TypeError):
        return None


def display_score(value):
    number = finite_number(value)
    return str(round(number)) if number is not None else "—"


def render_evidence(raw: dict, panel: dict, cache_dir: Path, *, review_skipped=False) -> str:
    # Recompute from original input rather than trusting cached display metadata.
    integrity = validate(raw)
    coverage = integrity.get("coverage_pct", 0)
    active = [i for i in panel.get("investors", []) if i.get("signal") != "skip"]
    rules = [finite_number(i.get("rule_coverage_pct")) for i in active]
    rules = [value for value in rules if value is not None]
    # Do not silently average a subset: old cache records have unknown semantics.
    rule_label = f"{sum(rules) / len(rules):.0f}%" if rules and len(rules) == len(active) else "未记录"
    analysis, freshness = load_fresh_agent_analysis(cache_dir, raw)
    agent_label = "输入指纹匹配" if analysis and freshness == "fingerprint matched" else "未完成当前输入审阅"
    if analysis and freshness != "fingerprint matched":
        agent_label = "旧式时间校验 · 无指纹"
    fetched = str(raw.get("fetched_at") or "未记录").replace("T", " ")
    if "." in fetched:
        import re
        fetched = re.sub(r"\.\d+", "", fetched)
    missing_dims = len(integrity.get("missing_enrichment") or [])
    warning = "开发预览 · 质量闸门已跳过" if review_skipped else "数据覆盖不代表数据正确；采集时间不等于行情或财报时点。"
    demo = '<p class="demo-notice">DEMO / 合成样本，仅验证报告布局，不代表任何真实证券。</p>' if raw.get("is_demo") else ""
    return f'''<section class="evidence-strip" id="section-evidence" aria-label="证据与置信度边界">
      {demo}<div class="evidence-grid">
        <div><span>CHECKED FIELDS</span><strong>{coverage:.0f}%</strong><p>{len(CRITICAL_CHECKS)} 项字段抽检 · {missing_dims} 个补充维度缺失</p></div>
        <div><span>EXECUTABLE RULES</span><strong>{rule_label}</strong><p>规则可执行比例 · 包含默认特征</p></div>
        <div><span>AGENT REVIEW</span><strong class="evidence-status">{escape_text(agent_label)}</strong><p>AI 审阅状态 · 非人工签核</p></div>
        <div><span>COLLECTED AT</span><strong class="evidence-status">{escape_text(fetched)}</strong><p>单次采集快照 · 非实时监控</p></div>
      </div><p class="evidence-caveat">{escape_text(warning)} 模拟流派共享输入，并非独立专家投票；评分与共识均非上涨概率。尚无样本外置信度校准。</p>
    </section>'''


def render_hero_chart(raw: dict) -> str:
    """Render available historical closes with verified alignment, never fake dates."""
    kline = ((raw.get("dimensions") or {}).get("2_kline") or {})
    data = kline.get("data") or {}
    pipeline = kline.get("_pipeline") or {}
    quality = pipeline.get("quality") or kline.get("quality")
    stale = kline.get("stale") is True or pipeline.get("stale") is True or quality == "stale"
    failed = kline.get("fallback") is True or bool(kline.get("error")) or quality in ("missing", "error")
    not_applicable = quality == "not_applicable" or kline.get("source") == "skip" or kline.get("applicable") is False
    if stale or failed or not_applicable:
        reason = "价格证据已过期" if stale else "价格维度不适用" if not_applicable else "价格采集未通过质量检查"
        return f'<div class="hero-chart-empty"><span>PRICE OBSERVATIONS</span><p>{reason}</p><small>保留留白；失败、回退或已标记过期的序列不作为有效行情展示。</small></div>'
    values = data.get("close_60d") or []
    if not isinstance(values, (list, tuple)):
        values = []
    values = [finite_number(v) for v in values]
    if len(values) < 2 or any(v is None or v <= 0 for v in values):
        return '<div class="hero-chart-empty"><span>PRICE OBSERVATIONS</span><p>价格序列待补充</p><small>缺失数据保持留白，不绘制模拟走势。</small></div>'
    # fetch_kline emits candles_60d alongside close_60d. Only borrow their dates
    # when both sequences align, so a report-generation time never becomes an
    # observation date and unrelated cached candles never label this series.
    from datetime import date
    date_label = "观测日期未记录或未对齐"
    candles = data.get("candles_60d")
    if isinstance(candles, (list, tuple)) and len(candles) == len(values):
        dates = []
        for candle, close in zip(candles, values):
            if not isinstance(candle, dict):
                break
            candle_close = finite_number(candle.get("close"))
            if candle_close is None or not math.isclose(candle_close, close, rel_tol=1e-9, abs_tol=1e-9):
                break
            try:
                observed = date.fromisoformat(str(candle.get("date") or "")[:10])
            except ValueError:
                break
            if dates and observed <= dates[-1]:
                break
            dates.append(observed)
        if len(dates) == len(values):
            date_label = f"观测期 {dates[0].isoformat()} — {dates[-1].isoformat()}"
    low, high = min(values), max(values)
    span = high - low or max(high * 0.02, 1)
    points = [(24 + i * 592 / (len(values) - 1), 308 - (v - low) / span * 220) for i, v in enumerate(values)]
    path = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    x, y = points[-1]
    source = escape_text(kline.get("source") or "来源未记录")
    return f'''<figure class="hero-chart"><figcaption>PRICE OBSERVATIONS <span>{len(values)} OBS.</span></figcaption>
      <svg viewBox="0 0 640 360" role="img" aria-label="缓存收盘价序列，非预测走势">
        <path class="chart-grid" d="M24 88H616 M24 198H616 M24 308H616"/>
        <path class="chart-area" d="{path} L616,340 L24,340 Z"/>
        <path class="chart-line" d="{path}"/><circle class="chart-point" cx="{x:.2f}" cy="{y:.2f}" r="5"/>
        <text x="24" y="72">HIGH {high:g}</text><text x="24" y="333">LOW {low:g}</text>
      </svg><div class="chart-caption"><span>{escape_text(date_label)}</span><span>历史观测 / 非预测</span></div>
      <div class="chart-caption"><span>{source}</span></div></figure>'''
