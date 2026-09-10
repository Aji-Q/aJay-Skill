"""Deterministic, evidence-bound council scripts; no provider calls or HTML.

The eight voices are simulated method lenses, not quotations, endorsements,
independent witnesses, predictions, or trading instructions. Consumers must
render strings as text and use a safe JSON-script serializer at the UI boundary.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
import math
from numbers import Real


_PROFILES = (
    ("buffett", "沃伦·巴菲特", "Warren Buffett", "现代价值投资", "质量与复利"),
    ("graham", "本杰明·格雷厄姆", "Benjamin Graham", "经典价值投资", "安全边际与资产负债"),
    ("munger", "查理·芒格", "Charlie Munger", "现代价值投资", "商业质量与反证"),
    ("lynch", "彼得·林奇", "Peter Lynch", "成长投资", "增长来源与估值"),
    ("soros", "乔治·索罗斯", "George Soros", "全球宏观", "预期变化与反身性"),
    ("dalio", "瑞·达利欧", "Ray Dalio", "系统化宏观", "周期与风险关联"),
    ("livermore", "杰西·利弗莫尔", "Jesse Livermore", "早期趋势交易", "历史价格与失效条件"),
    ("simons", "吉姆·西蒙斯", "Jim Simons", "现代量化研究", "数据质量与可检验性"),
)
_DIM_NAMES = {
    "0_basic": "基础报价", "1_financials": "财务记录", "2_kline": "历史价格",
    "3_macro": "宏观记录", "4_peers": "同行记录", "10_valuation": "估值输入",
    "11_governance": "治理记录", "12_capital_flow": "资金记录",
    "14_moat": "商业壁垒材料", "15_events": "事件记录", "18_trap": "风险检索记录",
}


def _number(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, str):
        value = value.strip().replace(",", "").removesuffix("%")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def _text(value, default="未记录"):
    return value.strip() if isinstance(value, str) and value.strip() else default


def _meaningful(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() not in {"", "—", "-", "none", "null", "nan", "n/a", "暂无", "无数据"}
    if isinstance(value, Real) and not isinstance(value, bool):
        return _number(value) is not None
    if isinstance(value, dict):
        return any(_meaningful(v) for k, v in value.items() if not str(k).startswith("_"))
    if isinstance(value, (list, tuple)):
        return any(_meaningful(v) for v in value)
    return isinstance(value, bool)


def _date_label(value):
    """Keep genuine date/year labels; never infer period-end from collection time."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if not isinstance(value, str):
        return None
    value = value.strip()
    if len(value) == 4 and value.isdigit() and 1000 <= int(value) <= 9999:
        return value
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return value


def _collection_label(value):
    if isinstance(value, Real) and not isinstance(value, bool) and _number(value) is not None:
        try:
            return datetime.fromtimestamp(value, timezone.utc).isoformat()
        except (ValueError, OverflowError, OSError):
            return "未记录"
    return _date_label(value) or "未记录"


def _fmt(value, unit="", signed=False, decimals=None):
    if value is None:
        return "未记录"
    if decimals is not None:
        value = round(value, decimals)
    shown = str(int(value)) if float(value).is_integer() else str(value)
    return ("+" if signed and value >= 0 else "") + shown + unit


def build_council(raw: dict) -> dict:
    """Build three adjudication questions and 24 distinct plain-text voices.

    Output: profiles[8], topics[3].voices[8], evidence keyed by raw dimension ID.
    supporting_facts contain value/source/date/status, including explicit gaps.
    Missing source/date metadata never invalidates a numerical observation silently
    and never becomes proof of verified provenance.
    """
    raw = raw if isinstance(raw, dict) else {}
    raw_dims = raw.get("dimensions") if isinstance(raw.get("dimensions"), dict) else {}
    profiles = [{"id": i, "name": cn, "name_zh": cn, "name_en": en,
                 "era": era, "method": method, "role": method,
                 "disclosure": "模拟方法视角 · 非本人发言或背书"}
                for i, cn, en, era, method in _PROFILES]
    profile_map = {p["id"]: p for p in profiles}
    records = {}
    data = {}
    facts = {}
    for dim_id, title in _DIM_NAMES.items():
        dim = raw_dims.get(dim_id) if isinstance(raw_dims.get(dim_id), dict) else {}
        payload = dim.get("data") if isinstance(dim.get("data"), dict) else {}
        pipeline = dim.get("_pipeline") if isinstance(dim.get("_pipeline"), dict) else {}
        quality = pipeline.get("quality") or dim.get("quality")
        if dim.get("source") == "skip" or dim.get("applicable") is False or quality == "not_applicable":
            status = "not_applicable"
        elif (dim.get("stale") is True or pipeline.get("stale") is True or quality == "stale"
              or (dim_id == "1_financials" and payload.get("financial_staleness_warning"))):
            status = "stale"
        elif dim.get("fallback") is True or pipeline.get("fallback") is True or dim.get("error") or quality in ("missing", "error"):
            status = "missing"
        else:
            status = "available" if _meaningful(payload) else "missing"
        observed = next((_date_label(payload.get(k)) for k in
                         ("financial_period", "report_date", "period_end", "as_of", "date")
                         if _date_label(payload.get(k))), None)
        records[dim_id] = {
            "id": dim_id, "title": title, "status": status,
            "source": _text(dim.get("source")), "date": observed or "未记录",
            "collected_at": _collection_label(pipeline.get("fetched_at") or dim.get("fetched_at") or raw.get("fetched_at")),
            "facts": [],
        }
        data[dim_id] = payload if status == "available" else {}

    def fact(key, dim_id, label, value, unit="", *, date_label=None, source=None, derived=False, inputs=()):
        record = records[dim_id]
        status = "derived" if derived and value is not None else "available" if value is not None else "missing"
        if record["status"] in ("stale", "not_applicable"):
            status = record["status"]
        shown = "未记录 / 未评估" if value is None else (
            _fmt(value, unit, decimals=2 if key in ("pe_relative", "window_change") else None) if isinstance(value, (float, int)) and not isinstance(value, bool)
            else "、".join(_fmt(v, unit) if v is not None else "缺失" for v in value) if isinstance(value, list)
            else str(value)
        )
        item = {
            "id": f"{dim_id}.{key}", "evidence_id": dim_id, "label": label,
            "value": value, "unit": unit, "text": f"{label}：{shown}",
            "source": _text(source, record["source"]), "date": date_label or record["date"],
            "collected_at": record["collected_at"], "status": status,
            "inputs": list(inputs),
        }
        facts[key] = item
        record["facts"].append(item)
        return value

    basic, fin, valuation = data["0_basic"], data["1_financials"], data["10_valuation"]
    health = fin.get("financial_health") if isinstance(fin.get("financial_health"), dict) else {}
    history = fin.get("roe_history") if isinstance(fin.get("roe_history"), (list, tuple)) else []
    roes = [_number(v) for v in history]
    valid_roes = [v for v in roes if v is not None]
    # financial_years can describe revenue rather than the independently fetched
    # ROE sequence. Do not label the entire history with the latest report date.
    roe_periods = fin.get("roe_periods")
    roe_dates = ([_date_label(v) for v in roe_periods]
                 if isinstance(roe_periods, (list, tuple)) and len(roe_periods) == len(history) else [])
    aligned_roe_dates = (bool(roe_dates) and all(roe_dates)
                         and all(a < b for a, b in zip(roe_dates, roe_dates[1:])))
    roe_date_range = f"{roe_dates[0]} — {roe_dates[-1]}" if aligned_roe_dates else "未记录"
    fact("roe_history", "1_financials", "已记录 ROE 序列", roes if valid_roes else None, "%",
         date_label=roe_date_range, source=fin.get("_roe_source"))
    roe_latest = _number(history[-1]) if history else _number(fin.get("roe"))
    roe_latest = fact("roe_latest", "1_financials", "序列末期 ROE" if history else "报告 ROE", roe_latest, "%",
                      date_label=(roe_dates[-1] if aligned_roe_dates else "未记录") if history else None,
                      source=fin.get("_roe_source"))
    roe_min = fact("roe_min", "1_financials", "已记录 ROE 最低值", min(valid_roes) if valid_roes else None, "%",
                   date_label=roe_date_range, source=fin.get("_roe_source"),
                   derived=True, inputs=("1_financials.roe_history",))
    net_margin = fact("net_margin", "1_financials", "报告净利率", _number(fin.get("net_margin")), "%")
    debt = fact("debt_ratio", "1_financials", "报告资产负债率", _number(health.get("debt_ratio")), "%")
    growth_raw = fin.get("revenue_growth_yoy")
    if growth_raw is None:
        growth_raw = fin.get("revenue_growth")
    growth = fact("revenue_growth", "1_financials", "输入营收同比", _number(growth_raw), "%",
                  date_label=_date_label(fin.get("revenue_growth_period")), source=fin.get("revenue_growth_source"))
    cash_ratio_raw = fin.get("ocf_to_net_income_ratio")
    if cash_ratio_raw is None:
        cash_ratio_raw = health.get("ocf_to_net_income_ratio")
    cash_ratio = fact("ocf_profit_ratio", "1_financials", "报告经营现金流 / 净利润", _number(cash_ratio_raw), "倍")
    quote = fact("price", "0_basic", "基础报价", _number(basic.get("price")))
    pe_raw = basic.get("pe_ttm")
    pe_dim = "0_basic"
    if _number(pe_raw) is None:
        pe_raw, pe_dim = valuation.get("pe"), "10_valuation"
    pe = fact("pe", pe_dim, "报告 PE", _number(pe_raw), "倍")
    industry_pe = fact("industry_pe", "10_valuation", "报告行业 PE 参照", _number(valuation.get("industry_pe")), "倍")
    quantile = _number(valuation.get("pe_quantile"))
    if quantile is not None and not 0 <= quantile <= 100:
        quantile = None
    quantile = fact("pe_quantile", "10_valuation", "输入 PE 历史分位", quantile, "%")
    premium = _number((pe / industry_pe - 1) * 100) if pe is not None and pe > 0 and industry_pe is not None and industry_pe > 0 else None
    fact("pe_relative", "10_valuation", "相对行业 PE 差异", premium, "%", derived=True,
         inputs=(facts["pe"]["id"], facts["industry_pe"]["id"]))

    kl = data["2_kline"]
    closes = kl.get("close_60d") if isinstance(kl.get("close_60d"), (list, tuple)) else []
    prices = [_number(v) for v in closes]
    valid_prices = [p for p in prices if p is not None and p > 0]
    complete_prices = len(prices) >= 2 and len(valid_prices) == len(prices)
    fact("close_60d", "2_kline", "输入历史收盘序列", prices if valid_prices else None)
    last_close = fact("close_latest", "2_kline", "缓存末端收盘值", prices[-1] if prices else None)
    fact("close_count", "2_kline", "有限且为正的历史收盘观测数", len(valid_prices) if prices else None)
    price_change = _number((prices[-1] / prices[0] - 1) * 100) if complete_prices else None
    fact("window_change", "2_kline", "缓存窗口首尾变化", price_change, "%", derived=True, inputs=("2_kline.close_60d",))
    # Date alignment is strict; no substitution with the collection timestamp.
    candles = kl.get("candles_60d")
    if isinstance(candles, list) and len(candles) == len(prices) and complete_prices:
        candle_dates = [_date_label(c.get("date")) if isinstance(c, dict) else None for c in candles]
        close_matches = all(isinstance(c, dict) and _number(c.get("close")) == p for c, p in zip(candles, prices))
        if close_matches and all(candle_dates) and all(a < b for a, b in zip(candle_dates, candle_dates[1:])):
            records["2_kline"]["date"] = f"{candle_dates[0]} — {candle_dates[-1]}"
            for item in records["2_kline"]["facts"]:
                item["date"] = records["2_kline"]["date"]

    def count_records(dim_id, key, fields, label):
        rows = []
        for field in fields:
            value = data[dim_id].get(field)
            if isinstance(value, list):
                rows.extend(row for row in value if _meaningful(row))
        # An empty provider result is not evidence that the real-world count is 0.
        return fact(key, dim_id, label, len(rows) if rows else None)

    pledge_count = count_records("11_governance", "pledges", ("pledge",), "质押记录条数")
    insider_count = count_records("11_governance", "insiders", ("insider_trades_1y",), "内部交易记录条数")
    event_count = count_records("15_events", "events", ("news", "recent_news", "recent_notices"), "已提供事件记录条数")
    flow_count = count_records("12_capital_flow", "flows", ("main_fund_flow_20d",), "资金流记录条数")
    peer_count = count_records("4_peers", "peers", ("peer_table",), "同行表记录条数（含表内自身行）")
    moat_count = count_records("14_moat", "moat_evidence", ("evidence", "sources", "snippets"), "壁垒支持材料条数")
    trap_count = count_records("18_trap", "trap_evidence", ("snippets", "signals_hit_detail"), "风险检索记录条数")
    macro_value = data["3_macro"].get("rate_cycle")
    macro_recorded = isinstance(macro_value, str) and _meaningful(macro_value)
    fact("rate_cycle", "3_macro", "利率周期输入", macro_value if macro_recorded else None)

    roe_summary = (f"已记录 {len(valid_roes)} 期 ROE，最低 {_fmt(roe_min, '%')}。"
                   if valid_roes else "ROE 历史缺失，持续性未评估。")
    roe_test = ("这些有效观测均高于 15%，但观测期数不等于连续年数。" if roe_min is not None and roe_min > 15
                else "“各期均高于 15%”未获这些记录支持。" if roe_min is not None else "先补充对应报告期，再讨论持续性。")
    margin_summary = f"报告净利率为 {_fmt(net_margin, '%')}。" if net_margin is not None else "净利率记录缺失。"
    growth_summary = f"输入营收同比为 {_fmt(growth, '%', signed=True)}。" if growth is not None else "营收同比记录缺失。"
    debt_summary = f"报告资产负债率为 {_fmt(debt, '%')}。" if debt is not None else "资产负债率记录缺失。"
    governance = ((f"质押材料 {pledge_count} 条" if pledge_count is not None else "质押材料未记录")
                  + "；" + (f"内部交易材料 {insider_count} 条" if insider_count is not None else "内部交易材料未记录")
                  + "；治理状况仍待逐项审查。"
                  if pledge_count is not None or insider_count is not None else "治理材料缺失或仅有空列表，治理状况未评估。")
    pe_summary = (f"输入 PE 为 {_fmt(pe, '倍')}。" if pe is not None else "PE 输入缺失。")
    peer_comparison = (f"PE 相对输入行业参照高约 {_fmt(premium, '%', decimals=2)}。" if premium is not None and premium >= 0
                       else f"PE 相对输入行业参照低约 {_fmt(abs(premium), '%', decimals=2)}。" if premium is not None
                       else "本公司与行业的正 PE 参照未同时具备，倍数比较未评估。")
    price_summary = (f"缓存 {len(prices)} 条收盘价，首尾变化约 {_fmt(price_change, '%', signed=True, decimals=2)}；这只是历史描述。"
                     if complete_prices and price_change is not None else "历史价格序列或变化计算存在缺口，趋势未评估。")
    cash_summary = (f"经营现金流 / 净利润的报告值为 {_fmt(cash_ratio, '倍')}。"
                    if cash_ratio is not None else "利润与经营现金流的对应比率缺失。")

    def voice(investor_id, claim, rebuttal, *keys):
        supporting = [dict(facts[key]) for key in keys]
        return {"id": investor_id, "name": profile_map[investor_id]["name"],
                "role": profile_map[investor_id]["role"], "claim": claim, "rebuttal": rebuttal,
                "evidence_ids": list(dict.fromkeys(f["evidence_id"] for f in supporting)),
                "supporting_facts": supporting,
                "disclosure": "J Trader 模拟方法视角 · 非真实发言"}

    quality_voices = [
        voice("buffett", roe_summary + roe_test,
              cash_summary + "账面回报应与现金实现相互核验。", "roe_history", "roe_min", "roe_latest", "ocf_profit_ratio"),
        voice("graham", debt_summary + "资产安全边际仍须检查负债构成与资产可回收性。",
              margin_summary + "盈利率本身不等于资产负债表的缓冲。", "debt_ratio", "net_margin"),
        voice("munger", governance + "高回报数字不替代对商业行为的核验。",
              "即使经营表现较好，关联交易与激励安排仍是独立问题。", "pledges", "insiders", "roe_latest"),
        voice("lynch", growth_summary + "持续性问题是增长来自销量、价格还是并购。",
              margin_summary + "营收扩张与利润改善应分别说明。", "revenue_growth", "net_margin"),
        voice("soros", (f"末期 ROE 为 {_fmt(roe_latest, '%')}；下一份披露是否改变质量预期？" if roe_latest is not None else "末期 ROE 未记录，预期变化缺少起点。"),
              "过去观测与未来叙事是两层证据，叙事一致不代表经营持续。", "roe_latest", "roe_history", "events"),
        voice("dalio", debt_summary + "质量还取决于融资期限与经营周期是否匹配。",
              cash_summary + "一个比率也未覆盖利率与再融资情景。", "debt_ratio", "ocf_profit_ratio", "rate_cycle"),
        voice("livermore", price_summary,
              roe_summary + "价格表现与企业质量应分开裁决，走势不证明护城河。", "close_count", "window_change", "roe_min"),
        voice("simons", f"有效 ROE 观测为 {len(valid_roes)} 个；缺失项未填成零，也未把期数写成连续年数。",
              "八个方法标签共享同一输入，不会变成八份独立的质量证据。", "roe_history", "roe_min", "close_count"),
    ]
    price_voices = [
        voice("buffett", pe_summary + "价格判断仍需要未来现金流与折现假设。",
              cash_summary + "本模块未据此生成现金流估值结论。", "pe", "ocf_profit_ratio", "price"),
        voice("graham", peer_comparison,
              "行业倍数只是相对参照，行业整体昂贵时也不构成内在价值证明。", "pe", "industry_pe", "pe_relative", "peers"),
        voice("munger", (f"输入历史 PE 分位为 {_fmt(quantile, '%')}，历史窗口与样本口径应核验。" if quantile is not None else "历史 PE 分位缺失，不把中位数当默认事实。"),
              "即使历史分位较低，业务结构变化也可能让旧区间失去可比性。", "pe_quantile", "moat_evidence"),
        voice("lynch", growth_summary + pe_summary,
              "营收同比不是每股盈利增速，以上两项不直接拼成 PEG 结论。", "revenue_growth", "pe"),
        voice("soros", (f"基础报价 {_fmt(quote)}，缓存末端收盘值 {_fmt(last_close)}；二者时点先对齐。" if quote is not None and last_close is not None else "报价与缓存末端收盘值未齐，价格预期缺少可比起点。"),
              "不同时点的价差不直接解释为预期改善或反转。", "price", "close_latest"),
        voice("dalio", ("利率周期字段已提供；折现率如何量化仍待说明。" if macro_recorded else "利率周期输入缺失，折现环境未评估。"),
              "相同 PE 在不同利率与增长期限下含义不同，相对倍数未替代情景分析。", "rate_cycle", "pe", "industry_pe"),
        voice("livermore", price_summary,
              "历史首尾变化不等于价格便宜，也不生成入场价、止损价或目标价。", "window_change", "close_count", "pe"),
        voice("simons", "本模块只计算已给出的比值与窗口变化，没有估计收益概率或开展预测回测。",
              "分位、倍数和增长各有口径；数字齐全也不证明三者属于同一时期。", "pe_relative", "pe_quantile", "revenue_growth"),
    ]
    risk_voices = [
        voice("buffett", cash_summary + "利润现金化的持续性仍需跨期核对。",
              debt_summary + "低负债也未消除经营与回款风险。", "ocf_profit_ratio", "debt_ratio"),
        voice("graham", (f"输入包含 {pledge_count} 条质押记录，金额、权利顺序与担保对象待核验。" if pledge_count is not None else "质押材料未记录，资产受限情况未评估。"),
              "检索为空不等于资产未受限；应保留信息缺口而非写零风险。", "pledges", "debt_ratio"),
        voice("munger", governance,
              "证据链缺失时，优先列出待核验行为；不把“没有记录”写成“没有问题”。", "pledges", "insiders", "trap_evidence"),
        voice("lynch", growth_summary + "下一期若偏离该观测，增长来源需要重新解释。",
              margin_summary + "单期放缓也不自动等于长期竞争力恶化。", "revenue_growth", "net_margin"),
        voice("soros", (f"输入有 {event_count} 条事件材料，哪些会改变原有假设仍待逐条判断。" if event_count is not None else "事件材料缺失，催化与反证均未评估。"),
              "事件数量不代表方向；材料存在也不等于已核验其真实性。", "events", "trap_evidence"),
        voice("dalio", (f"资金流输入有 {flow_count} 条记录，单位、覆盖主体与同期债务压力应对齐。" if flow_count is not None else "资金流材料缺失，流动性关联未评估。"),
              "资金流与盈利可能同受宏观环境驱动，不把相关性重复当作确认。", "flows", "debt_ratio", "rate_cycle"),
        voice("livermore", price_summary + "任何失效条件都应预先定义，再由后续观测检验。",
              "当前历史窗口没有提供经检验的预测规则，因此保留未评估状态。", "close_count", "window_change"),
        voice("simons", "本模块未做样本外验证或误差估计；本席只检查输入与推论是否相称。",
              "更多模拟观点不会弥补来源日期缺失，零值也应与未知值保持区分。", "roe_history", "close_count", "trap_evidence"),
    ]
    # Each primary record's status reflects the facts actually used, not query
    # strings or optimistic provider labels such as 'safe' / 'no issues'.
    for record in records.values():
        if record["status"] == "available" and not any(f["status"] in ("available", "derived") for f in record["facts"]):
            record["status"] = "missing"
    return {
        "schema_version": "ajay-council-v1", "profiles": profiles,
        "disclosure": "全部讲话为 J Trader 根据输入生成的模拟方法视角；非本人发言、背书或独立投票。肖像仅作视觉方位提示。",
        "method": "deterministic_raw_evidence_only", "is_demo": raw.get("is_demo") is True,
        "topics": [
            {"id": "quality", "title": "质量持续性", "question": "已有回报记录，足以支持持续质量吗？", "voices": quality_voices},
            {"id": "price", "title": "价格与增长", "question": "当前价格，正在要求怎样的增长兑现？", "voices": price_voices},
            {"id": "risk", "title": "风险与反证", "question": "什么证据会推翻当前假设，哪些风险仍未评估？", "voices": risk_voices},
        ],
        "evidence": records,
    }
