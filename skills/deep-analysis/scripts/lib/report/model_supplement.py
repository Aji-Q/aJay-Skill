"""Render the institutional products that the legacy report left out.

This module deliberately has no file, network, or template side effects.  It
accepts the raw data contract and returns an HTML fragment which can be placed
inside the report's modelling chapter.  The renderer is a supplement, rather
than a second implementation of :mod:`lib.report.institutional`: DCF, comps,
LBO, initiating coverage, IC memo, catalyst calendar, and competitive analysis
remain owned by the existing renderer.  The products here are the ones that
were present in the compute model but had no visible legacy UI surface.

All provider-controlled text is escaped at the final boundary.  Non-finite
numbers are shown as ``未记录`` and zero is intentionally not treated as a
missing value.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
from typing import Any

from lib.report.security import escape_text


# Only these three classes are emitted by this module.  The parent renderer
# owns their CSS; semantic elements intentionally do not carry extra classes.
SECTION_CLASS = "model-supplement"
PRODUCT_CLASS = "supplement-product"
TABLE_CLASS = "supplement-table"

_MISSING = object()


_LABELS = {
    # Common metadata / status
    "method": "计算方法",
    "source": "来源",
    "fallback": "是否备用输入",
    "assumptions": "模型假设",
    "methodology_log": "方法记录",
    "error": "错误信息",
    "years": "期间",
    # Dim 20
    "three_statement": "三表投影",
    "income_statement": "利润表",
    "cash_flow": "现金流量表",
    "balance_sheet": "资产负债表",
    "revenue": "营业收入",
    "cogs": "营业成本",
    "gross_profit": "毛利",
    "opex": "营业费用",
    "ebit": "息税前利润",
    "tax": "所得税",
    "net_income": "净利润",
    "dep_amort": "折旧摊销",
    "nwc_change": "营运资本变动",
    "ocf": "经营现金流",
    "capex": "资本开支",
    "fcf": "自由现金流",
    "equity_rollforward": "股东权益滚动",
    "growth_path": "增长路径",
    # Dim 21
    "earnings_analysis": "业绩分析",
    "latest": "最新业绩",
    "consensus": "市场一致预期",
    "beat_miss": "超预期 / 不及预期",
    "revenue_yi": "营业收入（亿元）",
    "net_profit_yi": "净利润（亿元）",
    "revenue_yoy_pct": "收入同比（%）",
    "net_profit_yoy_pct": "净利润同比（%）",
    "rev": "一致预期收入（亿元）",
    "ni": "一致预期净利润（亿元）",
    "revenue_vs_consensus_pct": "收入相对一致预期（%）",
    "revenue_tag": "收入标签",
    "net_profit_vs_consensus_pct": "净利润相对一致预期（%）",
    "net_profit_tag": "净利润标签",
    "thesis_impact": "对投资主线的影响",
    "thesis_tracker": "投资主线跟踪",
    "direction": "方向",
    "pillars": "主线支柱",
    "original_target": "原始目标",
    "current_status": "当前状态",
    "trend": "趋势",
    "verdict": "结论",
    "pillars_passed": "已通过支柱数",
    "pillars_total": "支柱总数",
    "thesis_intact_pct": "主线完整度（%）",
    "conviction": "信心",
    "recommended_action": "建议行动",
    "morning_note": "晨会简报",
    "date": "日期",
    "top_call": "首要判断",
    "recommendation": "建议",
    "bullets": "要点",
    "idea_screens": "投资想法筛选",
    "checks": "检查项",
    "criterion": "标准",
    "pass": "通过",
    "passed": "通过数",
    "total": "总数",
    "pass_rate_pct": "通过率（%）",
    "fits_screen": "符合筛选",
    "sector_overview": "行业概览",
    "industry": "行业",
    "market_size": "市场空间",
    "tam": "TAM",
    "growth": "增长",
    "lifecycle": "生命周期",
    "value_chain": "价值链",
    "upstream": "上游",
    "company": "公司",
    "downstream": "下游",
    "competitive_map": "竞争地图",
    "peer_count": "可比公司数",
    # Dim 22
    "unit_economics": "单位经济模型",
    "business_type": "业务类型",
    "metrics": "单位经济指标",
    "arpu_yi": "每用户平均收入（亿元）",
    "gross_margin_pct": "毛利率（%）",
    "churn_rate_pct": "流失率（%）",
    "ltv_yi": "客户生命周期价值（亿元）",
    "cac_yi": "获客成本（亿元）",
    "ltv_cac_ratio": "LTV / CAC",
    "payback_months": "回收期（月）",
    "opex_pct_of_rev": "运营费用率（%）",
    "net_margin_pct": "净利率（%）",
    "healthy": "健康度",
    "waterfall": "利润瀑布",
    "stage": "阶段",
    "value": "数值",
    "label": "标签",
    "value_creation_plan": "价值创造计划",
    "current_ebitda_yi": "当前 EBITDA（亿元）",
    "current_margin_pct": "当前利润率（%）",
    "levers": "改善杠杆",
    "lever": "杠杆",
    "category": "类别",
    "current_state": "当前状态",
    "target_state": "目标状态",
    "ebitda_impact_yi": "EBITDA 影响（亿元）",
    "timeline": "时间线",
    "confidence": "置信度",
    "total_uplift_yi": "总提升（亿元）",
    "target_ebitda_yi": "目标 EBITDA（亿元）",
    "target_margin_pct": "目标利润率（%）",
    "hundred_day_priorities": "百日优先事项",
    "dd_checklist": "尽调清单",
    "workstreams": "工作流",
    "items": "检查项",
    "item": "事项",
    "status": "状态",
    "total_items": "事项总数",
    "items_auto_verified": "自动核验数",
    "completion_pct": "完成度（%）",
    "manual_review_required": "需人工复核数",
    "portfolio_rebalance": "组合再平衡",
    "portfolio_total_yuan": "组合总额（元）",
    "drift_rows": "偏离明细",
    "asset_class": "资产类别",
    "target_pct": "目标权重（%）",
    "current_pct": "当前权重（%）",
    "drift_pct": "偏离（%）",
    "dollar_drift_yuan": "金额偏离（元）",
    "action": "动作",
    "needs_rebalance": "需要再平衡",
    "rebalance_trades": "再平衡交易",
    "trade": "交易",
    "quantity": "数量",
    "market_value_yuan": "市值（元）",
    "target_value_yuan": "目标市值（元）",
}

_DIMENSIONS = (
    ("20_valuation_models", "估值模型补充", "Valuation models", (
        ("three_statement", "三表投影", "3-Statement Projection"),
    )),
    ("21_research_workflow", "研究工作流补充", "Research workflow", (
        ("earnings_analysis", "业绩分析", "Earnings analysis"),
        ("thesis_tracker", "投资主线跟踪", "Thesis tracker"),
        ("morning_note", "晨会简报", "Morning note"),
        ("idea_screens", "投资想法筛选", "Idea screens"),
        ("sector_overview", "行业概览", "Sector overview"),
    )),
    ("22_deep_methods", "深度研究方法补充", "Deep methods", (
        ("unit_economics", "单位经济模型", "Unit economics"),
        ("value_creation_plan", "价值创造计划", "Value creation plan / VCP"),
        ("dd_checklist", "尽调清单", "Due-diligence checklist"),
        ("portfolio_rebalance", "组合再平衡", "Portfolio rebalance"),
    )),
)


def _mapping(value: Any) -> Mapping[str, Any]:
    """Return a mapping view without ever mutating or trusting ``value``."""
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, (list, tuple)):
        return list(value)
    # Strings are scalar values, not a sequence of characters for tables.
    return []


def _finite(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return True
    if isinstance(value, (int, float)):
        try:
            return math.isfinite(float(value))
        except (OverflowError, TypeError, ValueError):
            return False
    if isinstance(value, str):
        return value.strip().lower() not in {
            "nan", "+nan", "-nan", "inf", "+inf", "-inf",
            "infinity", "+infinity", "-infinity",
        }
    return True


def _scalar(value: Any) -> str:
    """Encode one scalar for HTML while preserving 0 and source formatting."""
    if value is _MISSING or value is None or not _finite(value):
        return "未记录"
    if isinstance(value, bool):
        return "是" if value else "否"
    return escape_text(value)


def _label(key: Any) -> str:
    key_s = str(key)
    return escape_text(_LABELS.get(key_s, key_s.replace("_", " ")))


def _compact(value: Any) -> str:
    """Encode a scalar/list/mapping as one readable cell, never as raw JSON."""
    if isinstance(value, Mapping):
        pieces: list[str] = []
        for key, item in value.items():
            if str(key).startswith("_"):
                continue
            pieces.append(f"{_label(key)}：{_compact(item)}")
        return "；".join(pieces) if pieces else "未记录"
    if isinstance(value, (list, tuple)):
        values = [_compact(item) for item in value]
        return " · ".join(values) if values else "未记录"
    return _scalar(value)


def _flatten(value: Any, prefix: str = "", depth: int = 0) -> list[tuple[str, str]]:
    """Flatten small model maps into label/value rows.

    This is intentionally bounded.  Product-specific lists (pillars, levers,
    checks, and so on) are rendered as tables below, while unknown nested
    assumptions remain readable without exposing a JSON dump.
    """
    if value is _MISSING:
        return []
    if isinstance(value, Mapping):
        rows: list[tuple[str, str]] = []
        for key, item in value.items():
            key_s = str(key)
            if key_s.startswith("_") or key_s == "methodology_log":
                continue
            current = f"{prefix} / {_label(key)}" if prefix else _label(key)
            if isinstance(item, Mapping) and depth < 2:
                nested = _flatten(item, current, depth + 1)
                rows.extend(nested or [(current, "未记录")])
            else:
                rows.append((current, _compact(item)))
        return rows
    return [(prefix or "值", _compact(value))]


def _table(rows: Sequence[tuple[Any, Any]]) -> str:
    rows = [(label, value) for label, value in rows if label is not None]
    if not rows:
        return ""
    out = [f'<table class="{TABLE_CLASS}"><tbody>']
    for label, value in rows:
        out.append(f"<tr><th scope=\"row\">{escape_text(label)}</th><td>{value}</td></tr>")
    out.append("</tbody></table>")
    return "".join(out)


def _mapping_table(value: Any, title: str | None = None) -> str:
    rows = _flatten(value)
    body = _table(rows)
    if not body:
        return ""
    return f"<details open><summary>{escape_text(title)}</summary>{body}</details>" if title else body


def _records_table(
    records: Any,
    columns: Sequence[tuple[str, str]],
    *,
    limit: int = 24,
) -> str:
    """Render a list of model records as a safe table.

    ``columns`` is an explicit allow-list.  It keeps the supplement focused
    on financial fields rather than dumping arbitrary provider payloads.
    """
    items = [item for item in _sequence(records) if isinstance(item, Mapping)]
    if not items:
        return ""
    shown = items[:limit]
    out = [f'<table class="{TABLE_CLASS}"><thead><tr>']
    out.extend(f"<th scope=\"col\">{escape_text(header)}</th>" for _, header in columns)
    out.append("</tr></thead><tbody>")
    for item in shown:
        out.append("<tr>")
        for key, _header in columns:
            out.append(f"<td>{_compact(item.get(key, _MISSING))}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    if len(items) > limit:
        out.append(f"<p>另有 {len(items) - limit} 条记录未展开。</p>")
    return "".join(out)


def _list_details(title: str, values: Any) -> str:
    items = _sequence(values)
    if not items:
        return ""
    body = "<ul>" + "".join(f"<li>{_compact(item)}</li>" for item in items) + "</ul>"
    return f"<details open><summary>{escape_text(title)}</summary>{body}</details>"


def _logs(data: Mapping[str, Any]) -> str:
    logs = _sequence(data.get("methodology_log"))
    if not logs:
        return ""
    return _list_details("方法记录", logs)


def _series_table(
    title: str,
    years: Any,
    series: Mapping[str, Any],
    *,
    limit: int = 12,
) -> str:
    """Render aligned time-series arrays without inventing values."""
    arrays = [(key, _sequence(values)) for key, values in series.items()]
    arrays = [(key, values) for key, values in arrays if values]
    if not arrays:
        return ""
    period_values = _sequence(years)
    width = max([len(values) for _, values in arrays] + [len(period_values)])
    if not period_values:
        period_values = [f"序列 {i + 1}" for i in range(width)]
    width = min(width, limit)
    out = [f"<details open><summary>{escape_text(title)}</summary>",
           f'<table class="{TABLE_CLASS}"><thead><tr><th scope="col">指标</th>']
    for period in period_values[:width]:
        out.append(f"<th scope=\"col\">{_compact(period)}</th>")
    out.append("</tr></thead><tbody>")
    for key, values in arrays:
        out.append(f"<tr><th scope=\"row\">{_label(key)}</th>")
        for index in range(width):
            out.append(f"<td>{_compact(values[index]) if index < len(values) else '未记录'}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    if max(len(values) for _, values in arrays) > limit:
        out.append(f"<p>表格最多展示前 {limit} 个期间，其余期间仍保留在数据模型中。</p>")
    out.append("</details>")
    return "".join(out)


def _meta(dim: Mapping[str, Any], payload: Any) -> tuple[str, str]:
    """Return visible status and source for one omitted product."""
    dim_data = _mapping(dim.get("data"))
    if not dim:
        return "输入缺失 · 尚未生成", "未记录"
    if str(dim.get("source", "")).lower() == "skip" or dim.get("applicable") is False:
        return "不适用", str(dim.get("source") or "skip")
    if not isinstance(payload, Mapping) or not payload:
        return "输入缺失 · 尚未生成", str(dim.get("source") or "未记录")
    useful = [key for key, value in payload.items()
              if str(key) not in {"methodology_log", "method"} and value not in (None, "", [], {})]
    if not useful:
        return "输入缺失 · 尚未生成", str(dim.get("source") or "未记录")
    if payload.get("error") and not any(key not in {"error", "method", "methodology_log"} for key in useful):
        return "模型错误 · 输入不足", str(dim.get("source") or "未记录")
    quality = str(dim.get("quality") or dim.get("status") or "").lower()
    if any(token in quality for token in ("stale", "expired", "过期")):
        status = "证据过期 · 不展示新结论"
    elif dim.get("fallback") or any(token in quality for token in ("fallback", "degraded", "备用")):
        status = "备用输入 · 模型已有"
    else:
        status = "模型已有 · 待核验假设"
    source = dim.get("source") or dim_data.get("source") or "未记录"
    return status, str(source)


def _product(
    key: str,
    title: str,
    english: str,
    dim: Mapping[str, Any],
    payload: Any,
    body: str,
    *,
    missing_note: str = "该产品未生成结果；本页面不补默认值。",
) -> str:
    status, source = _meta(dim, payload)
    out = [f'<article class="{PRODUCT_CLASS}" data-product="{escape_text(key)}">',
           f"<h3>{escape_text(title)} <small>{escape_text(english)}</small></h3>",
           f"<p>状态：<strong>{escape_text(status)}</strong> · 来源：{escape_text(source)}</p>"]
    if status.startswith("输入缺失") or status.startswith("模型错误") or status == "不适用":
        if isinstance(payload, Mapping) and payload.get("error"):
            out.append(f"<p>模型记录：{_scalar(payload.get('error'))}</p>")
        out.append(f"<p>{escape_text(missing_note)}</p>")
    elif body:
        out.append('<details><summary>查看模型、输入与方法记录</summary>' + body + '</details>')
    else:
        out.append("<p>模型已有字段，但当前字段没有可展开的内容。</p>")
    out.append("</article>")
    return "".join(out)


def _three_statement(data: Mapping[str, Any]) -> str:
    years = data.get("years")
    income = _mapping(data.get("income_statement"))
    cash = _mapping(data.get("cash_flow"))
    balance = _mapping(data.get("balance_sheet"))
    pieces = [_table([(_label("method"), _compact(data.get("method", _MISSING)))])]
    pieces.extend([
        _series_table("利润表 / Income statement", years, income),
        _series_table("现金流量表 / Cash flow", years, cash),
        _series_table("资产负债表 / Balance sheet", years, balance),
    ])
    assumptions = _mapping_table(data.get("assumptions"), "模型假设")
    growth = _list_details("增长路径", data.get("growth_path"))
    logs = _logs(data)
    return "".join(piece for piece in [*pieces, assumptions, growth, logs] if piece)


def _earnings(data: Mapping[str, Any]) -> str:
    latest = _mapping(data.get("latest"))
    consensus = _mapping(data.get("consensus"))
    beat_miss = _mapping(data.get("beat_miss"))
    rows = [
        ("最新业绩 / " + _label("revenue_yi"), _compact(latest.get("revenue_yi", _MISSING))),
        ("最新业绩 / " + _label("net_profit_yi"), _compact(latest.get("net_profit_yi", _MISSING))),
        ("最新业绩 / " + _label("revenue_yoy_pct"), _compact(latest.get("revenue_yoy_pct", _MISSING))),
        ("最新业绩 / " + _label("net_profit_yoy_pct"), _compact(latest.get("net_profit_yoy_pct", _MISSING))),
        ("一致预期 / " + _label("rev"), _compact(consensus.get("rev", _MISSING))),
        ("一致预期 / " + _label("ni"), _compact(consensus.get("ni", _MISSING))),
        (_label("revenue_vs_consensus_pct"), _compact(beat_miss.get("revenue_vs_consensus_pct", _MISSING))),
        (_label("revenue_tag"), _compact(beat_miss.get("revenue_tag", _MISSING))),
        (_label("net_profit_vs_consensus_pct"), _compact(beat_miss.get("net_profit_vs_consensus_pct", _MISSING))),
        (_label("net_profit_tag"), _compact(beat_miss.get("net_profit_tag", _MISSING))),
    ]
    pieces = [_table(rows)]
    if data.get("headline") is not None:
        pieces.append(_table([("业绩标题", _compact(data.get("headline")))]))
    if data.get("thesis_impact") is not None:
        pieces.append(_table([(_label("thesis_impact"), _compact(data.get("thesis_impact")))]))
    pieces.append(_logs(data))
    return "".join(piece for piece in pieces if piece)


def _thesis(data: Mapping[str, Any]) -> str:
    summary = [
        (_label("method"), _compact(data.get("method", _MISSING))),
        (_label("direction"), _compact(data.get("direction", _MISSING))),
        (_label("pillars_passed"), _compact(data.get("pillars_passed", _MISSING))),
        (_label("pillars_total"), _compact(data.get("pillars_total", _MISSING))),
        (_label("thesis_intact_pct"), _compact(data.get("thesis_intact_pct", _MISSING))),
        (_label("conviction"), _compact(data.get("conviction", _MISSING))),
        (_label("recommended_action"), _compact(data.get("recommended_action", _MISSING))),
    ]
    columns = [
        ("pillar", "支柱"), ("original_target", "原始目标"),
        ("current_status", "当前状态"), ("trend", "趋势"), ("verdict", "结论"),
    ]
    return _table(summary) + _records_table(data.get("pillars"), columns) + _logs(data)


def _morning(data: Mapping[str, Any]) -> str:
    rows = [
        (_label("date"), _compact(data.get("date", _MISSING))),
        (_label("top_call"), _compact(data.get("top_call", _MISSING))),
        (_label("recommendation"), _compact(data.get("recommendation", _MISSING))),
        (_label("method"), _compact(data.get("method", _MISSING))),
    ]
    return _table(rows) + _list_details("晨会要点", data.get("bullets")) + _logs(data)


def _idea_screens(data: Mapping[str, Any]) -> str:
    labels = {"value": "价值", "growth": "成长", "quality": "质量", "gulp": "GULP", "short": "短线"}
    summary_rows: list[tuple[str, str]] = []
    detail: list[str] = []
    for key, screen in data.items():
        if not isinstance(screen, Mapping):
            continue
        title = labels.get(str(key), str(key).replace("_", " "))
        summary_rows.extend([
            (f"{title} / 计算方法", _compact(screen.get("method", _MISSING))),
            (f"{title} / 通过数", _compact(screen.get("passed", _MISSING))),
            (f"{title} / 总数", _compact(screen.get("total", _MISSING))),
            (f"{title} / 通过率（%）", _compact(screen.get("pass_rate_pct", _MISSING))),
            (f"{title} / 符合筛选", _compact(screen.get("fits_screen", _MISSING))),
            (f"{title} / 结论", _compact(screen.get("verdict", _MISSING))),
        ])
        checks = _records_table(screen.get("checks"), [("criterion", "标准"), ("pass", "通过")])
        if checks:
            detail.append(f"<details open><summary>{escape_text(title)} / 检查项</summary>{checks}</details>")
        if screen.get("methodology_log"):
            detail.append(_logs(screen))
    return _table(summary_rows) + "".join(detail)


def _sector(data: Mapping[str, Any]) -> str:
    market = _mapping(data.get("market_size"))
    chain = _mapping(data.get("value_chain"))
    pieces = [_table([
        (_label("method"), _compact(data.get("method", _MISSING))),
        (_label("industry"), _compact(data.get("industry", _MISSING))),
        (_label("peer_count"), _compact(data.get("peer_count", _MISSING))),
    ])]
    pieces.append(_mapping_table(market, "市场空间"))
    pieces.append(_table([
        (_label("upstream"), _compact(chain.get("upstream", _MISSING))),
        (_label("company"), _compact(chain.get("company", _MISSING))),
        (_label("downstream"), _compact(chain.get("downstream", _MISSING))),
    ]))
    pieces.append(_records_table(data.get("competitive_map"), [
        ("name", "公司"), ("ticker", "代码"), ("market_cap_yi", "市值（亿元）"),
        ("market_share_pct", "市场份额（%）"), ("market_growth_pct", "市场增长（%）"),
        ("pe", "PE"), ("pb", "PB"), ("ps", "PS"), ("ev_ebitda", "EV/EBITDA"),
        ("ev_sales", "EV/Sales"), ("roe", "ROE"), ("net_margin", "净利率"),
        ("revenue_growth", "收入增长"),
    ]))
    pieces.append(_logs(data))
    return "".join(piece for piece in pieces if piece)


def _unit_economics(data: Mapping[str, Any]) -> str:
    metrics = _mapping(data.get("metrics"))
    pieces = [_table([
        (_label("method"), _compact(data.get("method", _MISSING))),
        (_label("business_type"), _compact(data.get("business_type", _MISSING))),
        ("营收（亿元）", _compact(data.get("revenue_yi", _MISSING))),
        (_label("gross_margin_pct"), _compact(data.get("gross_margin_pct", _MISSING))),
        (_label("opex_pct_of_rev"), _compact(data.get("opex_pct_of_rev", _MISSING))),
        (_label("net_margin_pct"), _compact(data.get("net_margin_pct", _MISSING))),
        (_label("healthy"), _compact(data.get("healthy", _MISSING))),
        (_label("verdict"), _compact(data.get("verdict", _MISSING))),
    ])]
    if metrics:
        pieces.append(_mapping_table(metrics, "单位经济指标"))
    pieces.append(_records_table(data.get("waterfall"), [
        ("stage", "阶段"), ("value", "数值"), ("label", "标签"),
    ]))
    pieces.append(_logs(data))
    return "".join(piece for piece in pieces if piece)


def _vcp(data: Mapping[str, Any]) -> str:
    pieces = [_table([
        (_label("method"), _compact(data.get("method", _MISSING))),
        (_label("current_ebitda_yi"), _compact(data.get("current_ebitda_yi", _MISSING))),
        (_label("current_margin_pct"), _compact(data.get("current_margin_pct", _MISSING))),
        (_label("total_uplift_yi"), _compact(data.get("total_uplift_yi", _MISSING))),
        (_label("target_ebitda_yi"), _compact(data.get("target_ebitda_yi", _MISSING))),
        (_label("target_margin_pct"), _compact(data.get("target_margin_pct", _MISSING))),
    ])]
    pieces.append(_records_table(data.get("levers"), [
        ("category", "类别"), ("lever", "杠杆"), ("current_state", "当前状态"),
        ("target_state", "目标状态"), ("ebitda_impact_yi", "EBITDA 影响（亿元）"),
        ("timeline", "时间线"), ("confidence", "置信度"),
    ]))
    pieces.append(_list_details("百日优先事项", data.get("hundred_day_priorities")))
    pieces.append(_logs(data))
    return "".join(piece for piece in pieces if piece)


def _dd(data: Mapping[str, Any]) -> str:
    pieces = [_table([
        (_label("method"), _compact(data.get("method", _MISSING))),
        (_label("total_items"), _compact(data.get("total_items", _MISSING))),
        (_label("items_auto_verified"), _compact(data.get("items_auto_verified", _MISSING))),
        (_label("completion_pct"), _compact(data.get("completion_pct", _MISSING))),
        (_label("manual_review_required"), _compact(data.get("manual_review_required", _MISSING))),
    ])]
    rows: list[dict[str, Any]] = []
    for workstream in _sequence(data.get("workstreams")):
        if not isinstance(workstream, Mapping):
            continue
        name = workstream.get("workstream", _MISSING)
        for item in _sequence(workstream.get("items")):
            if isinstance(item, Mapping):
                rows.append({
                    "workstream": name,
                    "item": item.get("item", _MISSING),
                    "status": item.get("status", _MISSING),
                })
    pieces.append(_records_table(rows, [
        ("workstream", "工作流"), ("item", "事项"), ("status", "状态"),
    ]))
    pieces.append(_logs(data))
    return "".join(piece for piece in pieces if piece)


def _rebalance(data: Mapping[str, Any]) -> str:
    pieces = [_table([
        (_label("method"), _compact(data.get("method", _MISSING))),
        (_label("portfolio_total_yuan"), _compact(data.get("portfolio_total_yuan", _MISSING))),
        (_label("needs_rebalance"), _compact(data.get("needs_rebalance", _MISSING))),
    ])]
    pieces.append(_records_table(data.get("drift_rows"), [
        ("asset_class", "资产类别"), ("target_pct", "目标权重（%）"),
        ("current_pct", "当前权重（%）"), ("drift_pct", "偏离（%）"),
        ("dollar_drift_yuan", "金额偏离（元）"), ("action", "动作"),
    ]))
    pieces.append(_records_table(data.get("rebalance_trades"), [
        ("asset_class", "资产类别"), ("target_pct", "目标权重（%）"),
        ("current_pct", "当前权重（%）"), ("drift_pct", "偏离（%）"),
        ("dollar_drift_yuan", "金额偏离（元）"), ("action", "动作"),
        ("quantity", "数量"), ("market_value_yuan", "市值（元）"),
        ("target_value_yuan", "目标市值（元）"),
    ]))
    pieces.append(_logs(data))
    return "".join(piece for piece in pieces if piece)


def _render_segment_status(segment_present: bool) -> str:
    if segment_present:
        status = "已接入 · 由独立分业务 renderer 展示"
        note = "分业务收入、历史构成与情景投影由独立 renderer 负责；本补充块不重复渲染数字。"
        source = "segmental_model.json / segmental_validation.json"
    else:
        status = "尚未建立 · 不显示预测结果"
        note = "未发现分业务模型文件；状态保持为尚未建立，不伪造分部收入或情景结果。"
        source = "segmental_model.json（未发现）"
    return (
        f'<article class="{PRODUCT_CLASS}" data-product="segmental">'
        f"<h3>分业务收入模型 <small>Segmental model</small></h3>"
        f"<p>状态：<strong>{escape_text(status)}</strong> · 来源：{escape_text(source)}</p>"
        f"<p>{escape_text(note)}</p></article>"
    )


def render_model_supplement(raw: Any, segment_present: bool = False) -> str:
    """Return the omitted institutional model products as safe HTML.

    Parameters
    ----------
    raw:
        A raw-data-contract mapping.  Malformed or missing dimensions render
        explicit missing states rather than raising or inventing values.
    segment_present:
        Whether the caller has an independently loaded segmental model.  The
        supplement only reports that state; it does not read the filesystem.
    """
    root = _mapping(raw)
    dimensions = _mapping(root.get("dimensions"))
    pieces = [
        f'<section class="{SECTION_CLASS}" aria-label="机构模型补充">',
        "<header><p>RESEARCH DESK / 深入研究</p>",
        "<h2>从价格，继续追问。</h2>",
        "<p>展开三表、投资主线、尽调与组合方法，核对每一步输入和假设。缺失状态保留，不补默认结果。</p></header>",
    ]

    renderers = {
        "three_statement": _three_statement,
        "earnings_analysis": _earnings,
        "thesis_tracker": _thesis,
        "morning_note": _morning,
        "idea_screens": _idea_screens,
        "sector_overview": _sector,
        "unit_economics": _unit_economics,
        "value_creation_plan": _vcp,
        "dd_checklist": _dd,
        "portfolio_rebalance": _rebalance,
    }
    for dimension_key, _dimension_title, _dimension_en, products in _DIMENSIONS:
        dim = _mapping(dimensions.get(dimension_key))
        data = _mapping(dim.get("data"))
        for product_key, title, english in products:
            payload = data.get(product_key, _MISSING)
            renderer = renderers[product_key]
            body = renderer(_mapping(payload)) if isinstance(payload, Mapping) else ""
            pieces.append(_product(product_key, title, english, dim, payload, body))

    pieces.append(_render_segment_status(bool(segment_present)))
    pieces.append("</section>")
    return "".join(pieces)


__all__ = ["render_model_supplement"]
