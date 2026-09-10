"""Offline J Trader visual fixture, explicitly synthetic. No market data is requested."""
from __future__ import annotations
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from lib.cache import write_task_output
from lib.pipeline.score_fns import score_dimensions, generate_panel, generate_synthesis


def build_preview():
    ticker = "JTRADER.DEMO"
    raw = {"ticker": ticker, "name": "Aster Systems", "market": "U", "is_demo": True,
           "fetched_at": datetime.now(timezone.utc).isoformat(), "dimensions": {}}
    def dim(key, data):
        raw["dimensions"][key] = {"data": data, "source": "J Trader synthetic fixture", "fallback": False}
    dim("0_basic", {"code": ticker, "name": "Aster Systems", "market": "U", "price": 184.5,
        "change_pct": 1.26, "market_cap": "128B USD (DEMO)", "pe_ttm": 28.4, "pb": 4.2,
        "industry": "Enterprise infrastructure / 演示", "one_liner": "穿透叙事，回到证据。以现金流、资本效率与风险边界，理解一家企业的长期价值。"})
    dim("1_financials", {"roe": "19.2%", "net_margin": "23%", "revenue_growth": "14.8%", "fcf": "4.8B USD",
        "roe_history": [14.2,16.1,17.3,18.0,19.2], "revenue_history": [12,14,16,19,22],
        "net_profit_history": [1.7,2.2,3,3.9,5.1], "financial_years": ["Y-4","Y-3","Y-2","Y-1","Y0"],
        "financial_health": {"current_ratio": 2.1,"debt_ratio": 28,"roic": 18.2}})
    closes = [round(142+i*.72+math.sin(i*.42)*4,2) for i in range(60)]
    dim("2_kline", {"close_60d":closes,"stage":"Stage 2 / DEMO","ma_align":"多头排列","macd":"金叉水上","rsi":"58"})
    dim("10_valuation", {"pe":28.4,"pe_quantile":"62%","pb_quantile":"58%","industry_pe":25})
    dim("3_macro", {"rate_cycle":"合成情景：利率维持","fx_trend":"合成情景：美元稳定","geo_risk":"仅作情景测试","commodity":"不适用"})
    dim("4_peers", {"rank":"演示同行组","peer_table":[{"name":"Aster (DEMO)","pe":"28.4","roe":"19.2%","is_self":True},{"name":"Peer A (DEMO)","pe":"25","roe":"16%"}]})
    dim("7_industry", {"growth":"12% (DEMO)","tam":"仅作布局演示","lifecycle":"合成成长期"})
    dim("14_moat", {"scores":{"intangible":7,"switching":8,"network":5,"cost":6,"scale":7},"switching":"合成高迁移成本"})
    dim("15_events", {"recent_news":[{"title":"合成事件，不对应真实新闻"}],"catalyst":"演示季度财报","earnings_preview":"待更新","warnings":"样本数据"})
    # Missing dimensions stay absent to exercise honest empty-state rendering.
    from lib.report.demo_fixture import augment_demo
    raw = augment_demo(raw)
    dimensions = score_dimensions(raw)
    panel = generate_panel(dimensions,raw)
    synthesis = generate_synthesis(raw,dimensions,panel)
    synthesis["dashboard"]["core_conclusion"] = "样本企业的资本效率与现金流表现支持进一步研究，但当前估值仍需要增长兑现。缺失的治理与资金证据，必须在形成真实判断前补齐。"
    synthesis["dashboard"]["battle_plan"] = {"entry":"演示情景 / 非交易指令","position":"未建模","stop":"基本面反证","target":"估值敏感性待验证"}
    synthesis["risks"] = ["此页所有证券数据均为合成样本，不对应任何真实投资标的。", "没有估计真实收益概率；尚未开展样本外验证。", "缺失维度保持未评估，不以零值或默认乐观分掩盖。"]
    synthesis["verdict_label"] = "合成样本 · 仅验证界面"
    synthesis["great_divide"]["punchline"] = "先检验假设，再讨论确定性。"
    for key,value in (("raw_data",raw),("dimensions",dimensions),("panel",panel),("synthesis",synthesis)):
        write_task_output(ticker,key,value)
    from assemble_report import assemble
    old = os.environ.get("AJAY_SKIP_REVIEW")
    os.environ["AJAY_SKIP_REVIEW"] = "1"  # Visible in generated evidence panel; fixture only.
    try:
        result = assemble(ticker)
    finally:
        if old is None: os.environ.pop("AJAY_SKIP_REVIEW",None)
        else: os.environ["AJAY_SKIP_REVIEW"]=old
    print(result.resolve())
    return result

if __name__ == "__main__":
    build_preview()
