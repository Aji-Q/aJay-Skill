"""Assemble the final HTML report from synthesis.json + dimensions.json + panel.json.

Usage: python scripts/assemble_report.py {ticker}
Output: reports/{ticker}_{YYYYMMDD}/full-report.html
"""
from __future__ import annotations

import json
import base64
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from lib.cache import read_task_output, market_status  # noqa: E402
from lib.report.security import escape_payload, escape_text  # noqa: E402
from lib.report.evidence import display_score, finite_number, render_evidence, render_hero_chart  # noqa: E402

ROOT = HERE.parent
TEMPLATE = ROOT / "assets" / "report-template.html"
AVATARS_DIR = ROOT / "assets" / "avatars"


def _safe(v, default="—"):
    return v if v not in (None, "", "nan") else default


# v2.6 · Read version from plugin manifest so report banner stays in sync
_PLUGIN_VERSION_CACHE = None
def _get_plugin_version() -> str:
    global _PLUGIN_VERSION_CACHE
    if _PLUGIN_VERSION_CACHE is not None:
        return _PLUGIN_VERSION_CACHE
    try:
        # ROOT = skills/deep-analysis · ROOT.parent.parent = repo root
        manifest = ROOT.parent.parent / ".claude-plugin" / "plugin.json"
        if manifest.exists():
            _PLUGIN_VERSION_CACHE = json.loads(manifest.read_text(encoding="utf-8")).get("version", "?")
            return _PLUGIN_VERSION_CACHE
    except Exception:
        pass
    _PLUGIN_VERSION_CACHE = "?"
    return _PLUGIN_VERSION_CACHE


def _render_pipeline_fallback_banner(ticker: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ".-_" else "_" for ch in str(ticker))[:80]
    marker = HERE / ".cache" / (safe or "unknown") / "_pipeline_fallback.json"
    if not marker.exists():
        return ""
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    error_type = escape_text(payload.get("error_type", "PipelineError"))
    message = escape_text(payload.get("error", "未知错误"))
    created_at = escape_text(payload.get("created_at", ""))
    return f'''<div class="pipeline-fallback-banner" style="margin:12px 0;padding:12px 16px;border:1px solid #f59e0b;background:#fffbeb;color:#92400e;font-size:12px">
  <strong>执行路径降级：</strong>本报告由 legacy 流程生成，pipeline 未完整执行。
  <span style="margin-left:8px">{error_type}: {message}</span>
  <span style="margin-left:8px;color:#a16207">{created_at}</span>
</div>'''



# v3.2 · 155 行 panel 相关渲染抽到 lib/report/panel_cards.py
# (GROUP_LABELS / render_jury_seat / chat_message / vote_bars / top3 / risks)
from lib.report.panel_cards import (  # noqa: E402, F401
    GROUP_LABELS,
    render_jury_seat, render_chat_message, render_vote_bars,
    render_top3_bulls, render_top3_bears, render_risks,
    _li, _render_top3_by_signal,
)



## ─── SVG VIZ HELPERS · per-dim 专属可视化 ───

# Brand colors (light theme)

# v3.2 · SVG 图元 + 颜色常量抽到 lib/report/svg_primitives.py (579 行)
# assemble_report 仍 re-export 保持兼容（内部 _viz_xxx 继续用）
from lib.report.svg_primitives import (  # noqa: E402, F401
    COLOR_BULL, COLOR_BEAR, COLOR_GOLD, COLOR_CYAN,
    COLOR_BLUE, COLOR_PINK, COLOR_INDIGO, COLOR_MUTED, COLOR_GRID,
    svg_sparkline, svg_h_bar_compare, svg_donut, svg_gauge, svg_radar,
    svg_signal_lights, svg_supply_flow, svg_timeline, svg_bars,
    svg_candlestick, svg_pe_band, svg_progress_row, svg_peer_table,
    svg_unlock_timeline, svg_dividend_combo, svg_institutional_quarters,
    svg_thermometer,
)


## ─── 19 维数据卡 配置 ───

DIM_META = {
    "1_financials": {
        "id": "01", "title": "财报扎实度", "en": "Financials", "weight": 5, "cat": "fin",
        "kpis": ["roe", "net_margin", "revenue_growth", "fcf"],
        "kpi_labels": {"roe": "ROE", "net_margin": "净利率", "revenue_growth": "营收增速", "fcf": "自由现金流"},
    },
    "2_kline": {
        "id": "02", "title": "K 线技术面", "en": "Technical", "weight": 4, "cat": "mkt",
        # 注：2_kline 走专属 candlestick viz (非 KPI 网格) · v3.8.0 的 KDJ/OBV/Williams
        # 副指标徽章在 lib/report/dim_viz._viz_kline 里渲染
        "kpis": ["stage", "ma_align", "macd", "rsi"],
        "kpi_labels": {"stage": "Stage", "ma_align": "均线", "macd": "MACD", "rsi": "RSI"},
    },
    "3_macro": {
        "id": "03", "title": "宏观环境", "en": "Macro", "weight": 3, "cat": "env",
        "kpis": ["rate_cycle", "fx_trend", "geo_risk", "commodity"],
        "kpi_labels": {"rate_cycle": "利率", "fx_trend": "汇率", "geo_risk": "地缘", "commodity": "大宗"},
    },
    "4_peers": {
        "id": "04", "title": "同行对比", "en": "Peers", "weight": 4, "cat": "ind",
        "kpis": ["rank", "gross_margin_vs", "roe_vs", "growth_vs"],
        "kpi_labels": {"rank": "行业排名", "gross_margin_vs": "毛利率vs", "roe_vs": "ROE vs", "growth_vs": "增速vs"},
    },
    "5_chain": {
        "id": "05", "title": "上下游产业链", "en": "Supply Chain", "weight": 4, "cat": "ind",
        "kpis": ["upstream", "downstream", "client_concentration", "supplier_concentration"],
        "kpi_labels": {"upstream": "上游", "downstream": "下游", "client_concentration": "大客户集中", "supplier_concentration": "供应商集中"},
    },
    "6_research": {
        "id": "06", "title": "研报观点", "en": "Sell-side", "weight": 3, "cat": "co",
        "kpis": ["coverage", "rating", "target_avg", "upside"],
        "kpi_labels": {"coverage": "覆盖券商", "rating": "买入比例", "target_avg": "目标价均值", "upside": "上涨空间"},
    },
    "7_industry": {
        "id": "07", "title": "行业景气", "en": "Industry", "weight": 4, "cat": "ind",
        "kpis": ["growth", "tam", "penetration", "lifecycle"],
        "kpi_labels": {"growth": "行业增速", "tam": "TAM", "penetration": "渗透率", "lifecycle": "生命周期"},
    },
    "8_materials": {
        "id": "08", "title": "原材料", "en": "Raw Materials", "weight": 3, "cat": "ind",
        "kpis": ["core_material", "price_trend", "cost_share", "import_dep"],
        "kpi_labels": {"core_material": "核心材料", "price_trend": "12M趋势", "cost_share": "成本占比", "import_dep": "进口依赖"},
    },
    "9_futures": {
        "id": "09", "title": "期货关联", "en": "Futures Link", "weight": 2, "cat": "ind",
        "kpis": ["linked_contract", "contract_trend"],
        "kpi_labels": {"linked_contract": "关联品种", "contract_trend": "走势"},
    },
    "10_valuation": {
        "id": "10", "title": "估值多维", "en": "Valuation", "weight": 5, "cat": "fin",
        "kpis": ["pe", "pe_quantile", "industry_pe", "dcf"],
        "kpi_labels": {"pe": "当前 PE", "pe_quantile": "PE 分位输入（窗口待核验）", "industry_pe": "行业均值", "dcf": "DCF 内在值"},
    },
    "11_governance": {
        "id": "11", "title": "管理层与治理", "en": "Governance", "weight": 4, "cat": "co",
        "kpis": ["pledge", "insider", "related_tx", "violations"],
        "kpi_labels": {"pledge": "实控人质押", "insider": "近12月增减持", "related_tx": "关联交易", "violations": "违规记录"},
    },
    "12_capital_flow": {
        "id": "12", "title": "资金面", "en": "Capital Flow", "weight": 4, "cat": "mkt",
        "kpis": ["main_20d", "margin_trend", "holders_trend", "main_5d"],
        "kpi_labels": {"main_20d": "主力资金20日", "margin_trend": "融资余额", "holders_trend": "股东户数", "main_5d": "主力5日"},
    },
    "13_policy": {
        "id": "13", "title": "政策与监管", "en": "Policy", "weight": 3, "cat": "env",
        "kpis": ["policy_dir", "subsidy", "monitoring", "anti_trust"],
        "kpi_labels": {"policy_dir": "政策方向", "subsidy": "补贴税收", "monitoring": "监管动向", "anti_trust": "反垄断"},
    },
    "14_moat": {
        "id": "14", "title": "护城河 (5 类)", "en": "Moat", "weight": 3, "cat": "fin",
        "kpis": ["intangible", "switching", "network", "scale"],
        "kpi_labels": {"intangible": "无形资产", "switching": "转换成本", "network": "网络效应", "scale": "规模优势"},
    },
    "15_events": {
        "id": "15", "title": "事件驱动", "en": "Events", "weight": 4, "cat": "co",
        "kpis": ["recent_news", "catalyst", "earnings_preview", "warnings"],
        "kpi_labels": {"recent_news": "近30天事件", "catalyst": "催化剂", "earnings_preview": "业绩预告", "warnings": "利空"},
    },
    "16_lhb": {
        "id": "16", "title": "龙虎榜", "en": "Dragon-Tiger", "weight": 4, "cat": "mkt",
        "kpis": ["lhb_30d", "youzi_matched", "inst_net", "youzi_net"],
        "kpi_labels": {"lhb_30d": "30天上榜", "youzi_matched": "识别游资", "inst_net": "机构净买", "youzi_net": "游资净买"},
    },
    "17_sentiment": {
        "id": "17", "title": "舆情与大V", "en": "Sentiment", "weight": 3, "cat": "saf",
        "kpis": ["xueqiu_heat", "guba_volume", "big_v_mentions", "positive_pct"],
        "kpi_labels": {"xueqiu_heat": "雪球热度", "guba_volume": "股吧讨论", "big_v_mentions": "大V提及", "positive_pct": "正面占比"},
    },
    "18_trap": {
        "id": "18", "title": "杀猪盘检测", "en": "Trap Scan", "weight": 5, "cat": "saf",
        "kpis": ["signals_hit", "trap_level", "high_risk_kw", "evidence_count"],
        "kpi_labels": {"signals_hit": "命中信号", "trap_level": "风险等级", "high_risk_kw": "高危词", "evidence_count": "证据数"},
    },
    "19_contests": {
        "id": "19", "title": "实盘比赛持仓", "en": "Live Contests", "weight": 4, "cat": "saf",
        "kpis": ["xq_cubes", "high_return_cubes", "tgb_mentions", "ths_simu"],
        "kpi_labels": {"xq_cubes": "雪球组合", "high_return_cubes": "高收益持有", "tgb_mentions": "淘股吧", "ths_simu": "同花顺模拟"},
    },
}

CAT_GROUPS = {
    "fin": ["1_financials", "10_valuation", "14_moat"],
    "mkt": ["2_kline", "12_capital_flow", "16_lhb"],
    "ind": ["4_peers", "5_chain", "7_industry", "8_materials", "9_futures"],
    "co":  ["11_governance", "15_events", "6_research"],
    "env": ["3_macro", "13_policy"],
    "saf": ["17_sentiment", "18_trap", "19_contests"],
}



# v3.2 · 704 行 _viz_xxx + DIM_VIZ_RENDERERS + _score_class 抽到 lib/report/dim_viz.py
# assemble_report 仍 re-export 保持兼容（render_dim_card 继续调用）
from lib.report.dim_viz import (  # noqa: E402, F401
    _score_class,
    _viz_chain, _viz_trap, _viz_valuation, _viz_financials, _viz_kline,
    _viz_macro, _viz_peers, _viz_research, _viz_industry, _viz_materials,
    _viz_futures, _viz_governance, _viz_capital_flow, _viz_policy, _viz_moat,
    _viz_events, _viz_lhb, _viz_sentiment, _viz_contests,
    DIM_VIZ_RENDERERS,
)


def _format_kpi_value(value) -> str:
    """Readable nested KPI text; values have already crossed escape_payload."""
    if value is None:
        return "—"
    if isinstance(value, list):
        return "；".join(_format_kpi_value(v) for v in value) or "—"
    if isinstance(value, dict):
        primary = [value.get(k) for k in ("date", "title", "event", "name", "expectation") if value.get(k) not in (None, "")]
        if primary:
            return " · ".join(_format_kpi_value(v) for v in primary)
        return " · ".join(f"{k}: {_format_kpi_value(v)}" for k,v in value.items()) or "—"
    return str(value)


def _extract_kpi_value(raw_dim_data: dict, key: str) -> str:
    """Best-effort extraction. Walks nested dict looking for the key, falls back to —."""
    if not isinstance(raw_dim_data, dict):
        return "—"
    # direct lookup
    if key in raw_dim_data:
        v = raw_dim_data[key]
        return _format_kpi_value(v)
    # walk one level
    for sub in raw_dim_data.values():
        if isinstance(sub, dict) and key in sub:
            v = sub[key]
            return _format_kpi_value(v)
    return "—"


def render_dim_card(dim_key: str, dim_score: dict, raw_dim: dict, market: str = None) -> str:
    """Render one dimension card (data-driven from DIM_META)."""
    dim_score = escape_payload(dim_score)
    raw_dim = escape_payload(raw_dim)
    meta = DIM_META.get(dim_key)
    if not meta:
        return ""
    from lib.data_integrity import _is_missing
    raw_data = (raw_dim or {}).get("data") or {}
    status = dim_score.get("score_status")
    unavailable = status in ("missing", "not_applicable", "stale") or _is_missing(raw_data) or raw_dim.get("source") == "skip"
    unmeasured = unavailable or status in (None, "heuristic")
    score = None if unmeasured else dim_score.get("score")
    if finite_number(score) is None:
        score = None
    label = _safe(dim_score.get("label"), "—")
    pass_items = dim_score.get("reasons_pass") or []
    fail_items = dim_score.get("reasons_fail") or []
    if unmeasured:
        label = {"not_applicable": "不适用", "stale": "证据已过期", "heuristic": "定性启发式 · 非量化评分"}.get(status, "证据不足或旧缓存 · 不显示默认分")
        pass_items, fail_items = [], []
    weight = dim_score.get("weight") or meta.get("weight", 3)
    score_cls = _score_class(score)
    score_pct = (score or 0) * 10  # 0-100 scale
    stars = "★" * weight + "☆" * (5 - weight)

    raw_data = (raw_dim or {}).get("data") or {}
    fallback = (raw_dim or {}).get("fallback", False)
    source = (raw_dim or {}).get("source", "—")
    # Preserve provenance; an SDK or web search is not an official filing.
    source_label = str(source or "来源未记录")

    # Specialized viz (overrides KPI grid if available)
    viz_html = ""
    if not unavailable and dim_key in DIM_VIZ_RENDERERS:
        try:
            # K-line candle direction is market-specific.  Dimension payloads
            # historically omitted market, so inject the top-level context
            # without mutating the raw cache or changing other renderers.
            viz_data = raw_data
            if dim_key == "2_kline" and market:
                viz_data = {**raw_data, "market": market}
            viz_html = f'<div class="dim-viz">{DIM_VIZ_RENDERERS[dim_key](viz_data)}</div>'
        except Exception:
            # Keep renderer internals out of the reader-facing report. The raw
            # evidence remains available below, so a chart failure is a visual
            # degradation rather than a loss of research inputs.
            viz_html = '<div class="dim-viz dim-viz-unavailable">数据图暂不可用，请核对下方原始记录。</div>'

    # KPI grid (only render if no specialized viz)
    kpi_html = ""
    if not viz_html:
        kpi_cells = []
        for k in meta["kpis"]:
            v = _extract_kpi_value(raw_data, k)
            if v != "—":
                label_k = meta["kpi_labels"].get(k, k)
                kpi_cells.append(f'<div class="kpi"><div class="k">{label_k}</div><div class="v">{v}</div></div>')
        if kpi_cells:
            kpi_html = f'<div class="dim-kpis">{"".join(kpi_cells)}</div>'

    # pass / fail
    pf_html = ""
    if pass_items or fail_items:
        pf_html = '<div class="dim-pass-fail">'
        if pass_items:
            pf_html += f'<div class="pass"><ul>{_li(pass_items)}</ul></div>'
        if fail_items:
            pf_html += f'<div class="fail"><ul>{_li(fail_items)}</ul></div>'
        pf_html += '</div>'

    badge_cls = "fallback" if fallback else "live"
    badge_text = source_label + (" · 备用源" if fallback else "")

    # raw data dump (collapsible)
    import json as _j
    raw_dump = _j.dumps(raw_data, ensure_ascii=False, indent=2, default=str)
    if len(raw_dump) > 1500:
        raw_dump = raw_dump[:1500] + "\n... (truncated)"
    raw_dump = escape_text(raw_dump)

    return f'''<div class="dim-card" data-dim="{meta["id"]}">
  <div class="dim-head">
    <div>
      <div class="dim-num">DIM {meta["id"]} · WEIGHT {stars}</div>
      <div class="dim-title">{meta["title"]}</div>
      <div class="dim-en">{meta["en"]}</div>
    </div>
    <div class="dim-score">
      <div class="num {score_cls}">{score if score is not None else "—"}</div>
    </div>
  </div>
  <div class="dim-bar"><div class="fill {score_cls}" style="width: {score_pct}%"></div></div>
  <div class="dim-label">{label}</div>
  {viz_html}
  {kpi_html}
  {pf_html}
  <div class="dim-source">数据来源: <span class="badge {badge_cls}">{badge_text}</span></div>
  <details>
    <summary>查看原始数据 ▼</summary>
    <pre>{raw_dump}</pre>
  </details>
</div>'''


def render_dim_category(cat: str, dimensions: dict, raw: dict) -> str:
    """Render all cards in one category."""
    raw_dims = raw.get("dimensions", {}) if raw else {}
    dim_scores = dimensions.get("dimensions", {}) if dimensions else {}
    market = (raw or {}).get("market") or (raw or {}).get("exchange")
    cards = []
    for key in CAT_GROUPS.get(cat, []):
        cards.append(render_dim_card(key, dim_scores.get(key, {}), raw_dims.get(key, {}), market=market))
    return "\n".join(cards)


## ─── Tier 4 友好层: 情景模拟 / 最像的票 / 离场触发 ───


# v3.2 · 506 行特殊卡片抽到 lib/report/special_cards.py
# (friendly_layer/fund_managers/panel_insights/school_scores/debate_rounds)
from lib.report.special_cards import (  # noqa: E402, F401
    render_friendly_layer,
    render_fund_managers, _render_fund_compact_row,
    render_panel_insights, render_school_scores, render_debate_rounds,
)




# v3.2 · 490 行机构级建模渲染抽到 lib/report/institutional.py
# assemble_report 仍 re-export 保持兼容
from lib.report.institutional import (  # noqa: E402, F401
    trap_color_emoji,
    _render_dcf_block, _render_comps_block, _render_lbo_block,
    _render_initiating_coverage, _render_ic_memo, _render_catalyst_calendar,
    _render_competitive_analysis, _render_style_chip,
    _render_data_gap_banner, _render_institutional_section,
    _render_school_lock_banner,
)


def assemble(ticker: str, layout: str = "continuous") -> Path:
    syn = read_task_output(ticker, "synthesis")
    raw = read_task_output(ticker, "raw_data")
    panel = read_task_output(ticker, "panel")
    if not (syn and raw and panel):
        raise RuntimeError(f"Missing prerequisite cache for {ticker}. Run Tasks 1-4 first.")

    if layout not in {"continuous", "council", "editorial"}:
        raise ValueError("Unknown report layout")
    council_raw = raw

    # Evidence fingerprints must use original input, before HTML escaping.
    from lib.cache import CACHE_ROOT
    from lib.data_integrity import validate
    from lib.agent_review import load_fresh_agent_analysis
    import os
    evidence_html = render_evidence(raw, panel, CACHE_ROOT / ticker,
                                    review_skipped=os.environ.get("AJAY_SKIP_REVIEW") == "1")
    hero_chart_html = render_hero_chart(raw)
    integrity = validate(raw)
    dimension_snapshot = read_task_output(ticker, "dimensions") or {}
    score_valid = not integrity.get("critical_missing", True) and dimension_snapshot.get("fundamental_score_valid", False)
    overall_display = display_score(syn.get("overall_score")) if score_valid else "—"
    fresh_analysis, _ = load_fresh_agent_analysis(CACHE_ROOT / ticker, raw)

    syn = escape_payload(syn)
    raw = escape_payload(raw)
    panel = escape_payload(panel)
    if not score_valid:
        # A hidden number alone is insufficient: strong verdicts must degrade too.
        syn["verdict_label"] = "证据不足 · 未形成综合判断"
        syn.pop("verdict_detail", None)
        syn["dashboard"] = {"core_conclusion": "关键输入缺失或过期。请先补充证据，再形成综合结论；现有规则输出仅供排查输入与假设。"}

    # v2.9 · 机械级自查 gate（代替以往"软 HARD-GATE"）
    # HTML 生成前强制跑 self_review；critical != 0 → 拒绝出报告，让 agent 修
    # 环境变量 AJAY_SKIP_REVIEW=1 可临时跳过（仅限开发调试，不该生产用）
    import os
    if os.environ.get("AJAY_SKIP_REVIEW") != "1":
        from lib.self_review import review_all, write_review, format_human
        review = review_all(ticker)
        write_review(ticker, review)
        crit = review["critical_count"]
        if crit > 0:
            print(format_human(review))
            raise RuntimeError(
                f"⛔ BLOCKED by self-review: {ticker} 有 {crit} 个 critical 问题待修。\n"
                f"→ 读 .cache/{ticker}/_review_issues.json\n"
                f"→ 对每条 critical issue 执行 suggested_fix（agent 补数据 / 重跑 stage2 / 写 agent_analysis）\n"
                f"→ 全部修完后重跑 assemble_report。\n"
                f"→ 如需强制跳过（仅调试）：export AJAY_SKIP_REVIEW=1"
            )
        elif review["warning_count"] > 0:
            # warning 允许出 HTML，但在报告 banner 里留痕
            print(format_human(review))
            print(f"⚠  {ticker}: {review['warning_count']} warning 已记录，继续生成 HTML")

    basic = (raw.get("dimensions", {}).get("0_basic") or {}).get("data") or {}
    # v3.9.4 · 币种符号按市场区分 · 港股/美股不再硬编码 ¥（此前腾讯 500 港币显示 ¥500）
    _mkt = raw.get("market") or basic.get("market") or "A"
    _currency_symbol = {"H": "HK$", "U": "$"}.get(_mkt, "¥")
    debate = syn.get("debate") or {}
    divide = syn.get("great_divide") or {}
    dashboard = syn.get("dashboard") or {}
    dp = dashboard.get("data_perspective") or {}
    intel = dashboard.get("intelligence") or {}
    # Legacy price multipliers are not a DCF / PE percentile / technical support.
    reviewed_narrative = (fresh_analysis or {}).get("narrative_override") or {}
    bp = escape_payload(((reviewed_narrative.get("dashboard") or {}).get("battle_plan") or {})) if score_valid else {}
    zones = escape_payload(reviewed_narrative.get("buy_zones") or {}) if score_valid else {}
    trap = (raw.get("dimensions", {}).get("18_trap") or {}).get("data") or {}
    trap_level = trap.get("trap_level") or "证据不足 · 未评估"
    trap_color, trap_emoji = trap_color_emoji(trap_level)
    if not trap.get("trap_level"):
        trap_color, trap_emoji = "#8393a7", "—"

    bull = debate.get("bull") or {}
    bear = debate.get("bear") or {}
    last_round = (debate.get("rounds") or [{}])[-1] if debate.get("rounds") else {}

    investors = panel.get("investors") or []

    # Sort for chat view: bullish first (hottest takes), then bearish, then neutral
    # Within each group, sort by confidence desc
    def _chat_sort_key(inv):
        sig_rank = {"bullish": 0, "bearish": 1, "neutral": 2}.get(inv.get("signal", "neutral"), 3)
        return (sig_rank, -(inv.get("confidence") or 0))
    chat_ordered = sorted(investors, key=_chat_sort_key)

    sig_dist = panel.get("signal_distribution") or {}
    bull_count = sig_dist.get("bullish", 0)
    bear_count = sig_dist.get("bearish", 0)
    neut_count = sig_dist.get("neutral", 0)

    template = TEMPLATE.read_text(encoding="utf-8")
    template = template.replace("<!-- INJECT_EDITORIAL_CSS -->", (ROOT / "assets" / "report-editorial.css").read_text(encoding="utf-8"))
    template = template.replace("<!-- INJECT_EVIDENCE_STRIP -->", evidence_html)
    template = template.replace("<!-- INJECT_HERO_CHART -->", hero_chart_html)
    for placeholder, filename in (("{{HERO_IMAGE_URI}}", "manhattan-night.png"), ("{{INTERLUDE_IMAGE_URI}}", "shanghai-night.png"), ("{{BUFFETT_IMAGE_URI}}", "buffett-portrait.png"), ("{{SIMONS_IMAGE_URI}}", "simons-portrait.png")):
        asset = ROOT / "assets" / "ajay-brand" / filename
        if not asset.is_file():
            raise RuntimeError(f"Missing J Trader report asset: {asset}")
        template = template.replace(placeholder, "data:image/png;base64," + base64.b64encode(asset.read_bytes()).decode("ascii"))

    market_state = {"label": "DEMO / 合成行情快照", "is_open": False} if raw.get("is_demo") else market_status(_mkt)
    replacements = {
        "{{NAME}}": _safe(syn.get("name") or basic.get("name")),
        "{{TICKER}}": _safe(syn.get("ticker") or basic.get("code")),
        "{{CURRENCY}}": _currency_symbol,
        "{{ONE_LINER}}": _safe(basic.get("one_liner") or basic.get("industry") or ""),
        "{{PRICE}}": str(_safe(basic.get("price"))),
        "{{CHANGE_PCT}}": f"{basic.get('change_pct', 0):+.2f}%" if basic.get("change_pct") is not None else "—",
        "{{CHANGE_DIR}}": "up" if (basic.get("change_pct") or 0) >= 0 else "down",
        "{{MCAP}}": str(_safe(basic.get("market_cap"))),
        "{{PE}}": str(_safe(basic.get("pe_ttm"))),
        "{{PB}}": str(_safe(basic.get("pb"))),
        "{{INDUSTRY}}": str(_safe(basic.get("industry"))),
        "{{OVERALL_SCORE}}": overall_display,
        "{{OVERALL_SCORE_INT}}": overall_display,
        "{{SCORE_STATUS}}": "关键证据完整性检查通过 · 未校准" if score_valid else "关键证据不足，暂不展示综合分",
        "{{REPORT_MODE}}": "DEMO / 合成样本" if raw.get("is_demo") else "RESEARCH NOTE",
        # v3.4.1 · verdict_label 后追加 detail（基本面/共识精确分）让相近 verdict 段的票仍能区分
        "{{VERDICT_LABEL}}": _safe(syn.get("verdict_label")) + (
            f" · {syn['verdict_detail']}" if syn.get("verdict_detail") else ""
        ),
        "{{TRAP_LEVEL}}": trap_level,
        "{{TRAP_COLOR}}": trap_color,
        "{{TRAP_EMOJI}}": trap_emoji,
        "{{TRAP_RECOMMENDATION}}": _safe(trap.get("recommendation"), "尚无充分证据形成风险结论"),
        "{{CORE_CONCLUSION}}": _safe(dashboard.get("core_conclusion")),
        "{{DP_TREND}}": _safe(dp.get("trend")),
        "{{DP_PRICE}}": _safe(dp.get("price")),
        "{{DP_VOLUME}}": _safe(dp.get("volume")),
        "{{DP_CHIPS}}": _safe(dp.get("chips")),
        "{{INTEL_NEWS}}": _safe(intel.get("news")),
        "{{INTEL_RISKS}}": _safe(", ".join(intel.get("risks") or [])),
        "{{INTEL_CATALYSTS}}": _safe(", ".join(intel.get("catalysts") or [])),
        "{{BP_ENTRY}}": _safe(bp.get("entry")),
        "{{BP_POSITION}}": _safe(bp.get("position")),
        "{{BP_STOP}}": _safe(bp.get("stop")),
        "{{BP_TARGET}}": _safe(bp.get("target")),
        # v2.9.1 · 不再用 buffett/graham 假头像兜底——如果 debate 真空，agent
        # 没选出多空代表，应该显示占位而不是错误的头像+空数据
        "{{BULL_ID}}": _safe(bull.get("investor_id"), "_placeholder"),
        "{{BULL_NAME}}": _safe(bull.get("name"), "（未选出）"),
        "{{BULL_SCORE}}": display_score(divide.get("bull_score")),
        "{{BULL_LAST_SAY}}": _safe(last_round.get("bull_say"), "—"),
        "{{BEAR_ID}}": _safe(bear.get("investor_id"), "_placeholder"),
        "{{BEAR_NAME}}": _safe(bear.get("name"), "（未选出）"),
        "{{BEAR_SCORE}}": display_score(divide.get("bear_score")),
        "{{BEAR_LAST_SAY}}": _safe(last_round.get("bear_say"), "—"),
        "{{PUNCHLINE}}": _safe(divide.get("punchline") or debate.get("punchline")),
        "{{ZONE_VALUE_PRICE}}": str(_safe((zones.get("value") or {}).get("price"))),
        "{{ZONE_VALUE_RATIONALE}}": _safe((zones.get("value") or {}).get("rationale"), "估值方法与输入待验证"),
        "{{ZONE_GROWTH_PRICE}}": str(_safe((zones.get("growth") or {}).get("price"))),
        "{{ZONE_GROWTH_RATIONALE}}": _safe((zones.get("growth") or {}).get("rationale"), "增长与估值假设待验证"),
        "{{ZONE_TECH_PRICE}}": str(_safe((zones.get("technical") or {}).get("price"))),
        "{{ZONE_TECH_RATIONALE}}": _safe((zones.get("technical") or {}).get("rationale"), "技术触发条件待验证"),
        "{{ZONE_YOUZI_PRICE}}": str(_safe((zones.get("youzi") or {}).get("price"))),
        "{{ZONE_YOUZI_RATIONALE}}": _safe((zones.get("youzi") or {}).get("rationale"), "市场适用性与方法待验证"),
        "{{GENERATED_AT}}": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "{{BULL_COUNT}}": str(bull_count),
        "{{BEAR_COUNT}}": str(bear_count),
        "{{NEUT_COUNT}}": str(neut_count),
        "{{CONSENSUS_PCT}}": display_score(panel.get("panel_consensus")) if panel.get("consensus_valid") else "—",
        "{{BULL_TAG}}": _safe((bull.get("group") and GROUP_LABELS.get(bull.get("group"))) or bull.get("tagline"), ""),
        "{{BEAR_TAG}}": _safe((bear.get("group") and GROUP_LABELS.get(bear.get("group"))) or bear.get("tagline"), ""),
        "{{BULL_SIGNAL_CN}}": {"bullish": "看多", "neutral": "中性", "bearish": "看空"}.get(divide.get("bull_signal", ""), "看多"),
        "{{BEAR_SIGNAL_CN}}": {"bullish": "看多", "neutral": "中性", "bearish": "看空"}.get(divide.get("bear_signal", ""), "看空"),
        "{{TOTAL_COUNT}}": str(len(investors)),
        "{{MARKET_STATUS}}": market_state.get("label", ""),
        "{{MARKET_STATUS_CLASS}}": "open" if market_state.get("is_open") else "closed",
        "{{DATA_FETCHED_AT}}": (raw.get("fetched_at") or "")[:19].replace("T", " "),
        "{{PLUGIN_VERSION}}": _get_plugin_version(),
    }
    for k, v in replacements.items():
        template = template.replace(k, escape_text(v))

    # A-share limit-up/LHB personas are not a US or HK research perspective.
    # When the market-specific panel has no F group, remove the empty filter
    # and its A-share-only decision zone instead of presenting skip records.
    has_group_f = any(i.get("group") == "F" for i in investors)
    template = template.replace(
        "<!-- INJECT_GROUP_F_TAB -->",
        '<button type="button" class="chat-tab" data-group="F" aria-pressed="false">游资</button>'
        if has_group_f else "",
    )
    tactical_zone = ""
    if has_group_f:
        tactical_zone = (
            '<div class="zone"><div class="zone-label">YOUZI 游资派</div>'
            f'<div class="zone-price">{escape_text(_currency_symbol)}'
            f'{escape_text(_safe((zones.get("youzi") or {}).get("price")))}</div>'
            f'<div class="zone-rationale">'
            f'{escape_text(_safe((zones.get("youzi") or {}).get("rationale"), "市场适用性与方法待验证"))}'
            '</div></div>'
        )
    template = template.replace("<!-- INJECT_TACTICAL_ZONE -->", tactical_zone)

    template = template.replace(
        "<!-- INJECT_JURY_SEATS -->",
        "\n".join(render_jury_seat(i) for i in investors),
    )
    template = template.replace(
        "<!-- INJECT_CHAT_MESSAGES -->",
        "\n".join(render_chat_message(i) for i in chat_ordered),
    )
    template = template.replace(
        "<!-- INJECT_VOTE_BARS -->",
        render_vote_bars(panel.get("vote_distribution") or {}),
    )
    template = template.replace(
        "<!-- INJECT_TOP3_BULLS -->",
        render_top3_bulls(investors),
    )
    # v2.9.1 · 对称补 Top 3 看空 + panel_insights 评委汇总
    template = template.replace(
        "<!-- INJECT_TOP3_BEARS -->",
        render_top3_bears(investors),
    )
    template = template.replace(
        "<!-- INJECT_PANEL_INSIGHTS -->",
        render_panel_insights(syn, panel),
    )
    # v2.15.4 · 按流派打分卡片（7 个流派 A-G 各自 consensus/avg/verdict）
    # 注入在 panel_insights 后 · 若模板尚未含 marker 则追加到 panel_insights 末
    school_html = render_school_scores(syn, panel)
    if "<!-- INJECT_SCHOOL_SCORES -->" in template:
        template = template.replace("<!-- INJECT_SCHOOL_SCORES -->", school_html or "")
    elif school_html:
        # 兼容旧模板：拼到 panel-insights 后
        template = template.replace(
            '</div>\n        <!-- Top 3 Bears',
            f'</div>\n        {school_html}\n        <!-- Top 3 Bears',
            1,
        )
        # 若旧 anchor 也没命中 · 最后兜底拼到 INJECT_DEBATE_ROUNDS 前
        if school_html not in template:
            template = template.replace(
                "<!-- INJECT_DEBATE_ROUNDS -->",
                school_html + "\n<!-- INJECT_DEBATE_ROUNDS -->",
                1,
            )
    template = template.replace(
        "<!-- INJECT_RISKS -->",
        render_risks(syn.get("risks") or []),
    )
    template = template.replace(
        "<!-- INJECT_DEBATE_ROUNDS -->",
        render_debate_rounds(debate),
    )

    # Tier 4 友好层
    template = template.replace(
        "<!-- INJECT_FRIENDLY_LAYER -->",
        render_friendly_layer(syn, raw) if fresh_analysis and (syn.get("friendly") or {}).get("assumptions") and score_valid
        else '<p class="chapter-intro">情景测算尚无明确假设；不展示默认概率或机械交易指令。</p>',
    )

    # 基金经理抄作业面板
    fund_managers = (syn.get("fund_managers") or raw.get("fund_managers") or [])
    template = template.replace(
        "<!-- INJECT_FUND_MANAGERS -->",
        render_fund_managers(fund_managers),
    )

    # 19 维深度数据卡 · 6 大类
    dimensions = escape_payload(read_task_output(ticker, "dimensions") or {})
    template = template.replace("<!-- INJECT_DIM_FINANCIAL -->", render_dim_category("fin", dimensions, raw))
    template = template.replace("<!-- INJECT_DIM_MARKET -->",    render_dim_category("mkt", dimensions, raw))
    template = template.replace("<!-- INJECT_DIM_INDUSTRY -->",  render_dim_category("ind", dimensions, raw))
    template = template.replace("<!-- INJECT_DIM_COMPANY -->",   render_dim_category("co", dimensions, raw))
    template = template.replace("<!-- INJECT_DIM_ENV -->",       render_dim_category("env", dimensions, raw))
    template = template.replace("<!-- INJECT_DIM_SAFETY -->",    render_dim_category("saf", dimensions, raw))

    # v2.0 · Institutional modeling section (dim 20/21/22)
    # v3.9.4 · 币种符号统一替换 · 港股/美股 DCF 内在价值不再硬编码 ¥
    _inst_html = _render_institutional_section(raw)
    if _currency_symbol != "¥":
        _inst_html = _inst_html.replace("¥", _currency_symbol)
    template = template.replace(
        "<!-- INJECT_INSTITUTIONAL_MODELING -->",
        _inst_html,
    )

    # v2.10 / v3.3 · Segmental Revenue Build-Up（分业务收入模型）
    # 仅当 segmental_model.json 存在时渲染（agent 跑 /segmental-model 才生成）
    try:
        from lib.report.segmental import _render_segmental_block
        seg_html = _render_segmental_block(ticker)
    except Exception as _e:
        print(f"   ⚠️ segmental block 跳过: {type(_e).__name__}: {str(_e)[:80]}")
        seg_html = ""
    template = template.replace(
        "<!-- INJECT_SEGMENTAL -->",
        seg_html,
    )

    # v2.3 · Data quality banner (only renders when synthesis.data_gaps present)
    # v3.4.4 · 传 raw 让 banner 检测 ETF/基金类型 · 优化文案避免误判可信度
    # v3.4.5 · 传 syn 让 banner 检测 low-confidence（fund_score 偏低 + 覆盖率低）
    # v3.5.0 · 在 data_gap_banner 上方追加 school_lock_banner（用户锁定流派视角）
    school_lock_html = _render_school_lock_banner(syn)
    data_gap_html = _render_data_gap_banner(syn.get("data_gaps"), raw=raw, syn=syn)
    pipeline_fallback_html = _render_pipeline_fallback_banner(ticker)
    template = template.replace(
        "<!-- INJECT_DATA_GAP_BANNER -->",
        pipeline_fallback_html + school_lock_html + data_gap_html,
    )

    # v2.7 · Style chip (动态加权说明，只在 detected_style 存在时渲染)
    template = template.replace(
        "<!-- INJECT_STYLE_CHIP -->",
        _render_style_chip(syn),
    )

    # v3.9.4 · 收尾统一币种替换 · 覆盖 panel/special/institutional 注入块里的 ¥
    # （A 股符号 == ¥ 时 replace 是 no-op · 安全）
    if _currency_symbol != "¥":
        template = template.replace("¥", _currency_symbol)

    date = datetime.now().strftime("%Y%m%d")
    out_dir = Path("reports") / f"{ticker}_{date}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "full-report.html"
    if layout in {"continuous", "council"}:
        from lib.report.council_renderer import render_council
        from lib.report.continuous_renderer import render_continuous
        analysis = {"dimensions": dimension_snapshot, "dimension_titles": {k: v["title"] for k,v in DIM_META.items()},
                    "review_skipped": os.environ.get("AJAY_SKIP_REVIEW") == "1",
                    "critical_missing": integrity.get("critical_missing", True),
                    "agent_review_current": bool(fresh_analysis),
                    "rule_coverage": [{"name": p.get("name", ""), "coverage": p.get("rule_coverage_pct"),
                                       "evaluated_weight": p.get("evaluated_weight"), "possible_weight": p.get("possible_weight")}
                                      for p in (read_task_output(ticker,"panel") or {}).get("investors", [])]}
        # Preserve the detailed legacy presentation for audit/compatibility, but not as the main UI.
        (out_dir / "research-appendix.html").write_text(template, encoding="utf-8")
        template = render_continuous(council_raw, analysis, template) if layout == "continuous" else render_council(council_raw, analysis)
    out_file.write_text(template, encoding="utf-8")
    if layout in {"continuous", "council"}:
        (out_dir / "full-report-standalone.html").write_text(template, encoding="utf-8")

    out_avatars = out_dir / "avatars"
    if not out_avatars.exists():
        shutil.copytree(AVATARS_DIR, out_avatars)

    long_active = panel.get("long_active") or sum(
        (panel.get("signal_distribution") or {}).get(key, 0)
        for key in ("bullish", "neutral", "bearish")
    )
    one_liner = (
        f"{syn.get('name')} J Trader 研究分：{overall_display}，"
        f"{syn.get('verdict_label')}。\n"
        f"{long_active} 个模拟多头流派角色里 {(panel.get('signal_distribution') or {}).get('bullish', 0)} 个看多；非真实投资者意见或胜率。\n"
        f"💬 {divide.get('punchline') or '—'}\n"
        f"{trap_emoji} {trap_level}\n"
        f"全文 → {out_file}"
    )
    (out_dir / "one-liner.txt").write_text(one_liner, encoding="utf-8")

    print(f"[ok] Report assembled: {out_file}")
    return out_file


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "002273.SZ"
    assemble(ticker)
