"""美股维度补数器:给 stock-deep-analyzer 插件的 .cache/<TICKER>/ 补上美股缺口。

只做五件事,全部免费数据源:
  1. SEC XBRL  → ROE 5年史(精确) / 现金+短投 / 逐季 TTM EPS+BVPS → 精确 PE/PB 5年分位
  2. moomoo    → 美股日度资金流向(超大/大单) → 12_capital_flow(需 OpenD 在线,断了只警告不中断)
  3. yfinance  → 同业对标表 → 4_peers
  4. FMP(可选) → 目标价共识/评级/预估 → 6_research(设 FMP_APIKEY 才跑;不设则留给 agent 经 FMP MCP 填)
  5. czsc 缠论 → 日线+周线 笔/中枢/买卖点候选 → 2_kline.chan(同目录 chan_signals.py;pip install czsc)
不做:定性维度(护城河/舆情/事件)——那是 agent 的活;不重跑打分。

用法(cwd = 本目录;先跑完插件 stage1,再跑本脚本,然后按打印的链条重跑建模):
    python3 us_backfill.py META --dry-run     # 只打印将写入的值,不落盘
    python3 us_backfill.py META               # 写入 raw_data.json + 标记 _data_gaps resolved

补完后的重跑链(补 raw 会变指纹,顺序不能乱):
    stage1_modeling(T) → [agent 覆盖 panel] → agent_analysis 带新 hash → stage2(T)
"""
import json
import sys
import time
import urllib.request
from datetime import date, timedelta
from pathlib import Path

# --- 配置 ---------------------------------------------------------------
PLUGIN_CACHE = Path(__file__).resolve().parent / ".cache"  # 与插件 scripts 同目录,随插件走
import os
SEC_UA = os.environ.get("AJAY_SEC_UA", "")  # SEC 要求带联系方式的 UA,匿名 UA 会被 403;在 .env 或 shell 里设 AJAY_SEC_UA="name email"
assert SEC_UA.strip(), "缺 AJAY_SEC_UA 环境变量:SEC EDGAR 要求 User-Agent 带姓名+邮箱,例如 export AJAY_SEC_UA=\"Zhang San zs@example.com\""
OPEND_HOST, OPEND_PORT = "127.0.0.1", 11111  # moomoo OpenD 网关
PEERS = ["GOOGL", "SNAP", "PINS", "RDDT"]    # 社交/广告平台对标;换行业记得换这组
QUANTILE_YEARS = 5                            # PE/PB 分位回看窗口

assert len(sys.argv) >= 2, "用法: python3 us_backfill.py <TICKER> [--dry-run]  (TICKER 如 META,不带 US. 前缀)"
TICKER = sys.argv[1].upper()
DRY = "--dry-run" in sys.argv
CACHE = PLUGIN_CACHE / TICKER
assert CACHE.exists(), f"{CACHE} 不存在——先跑插件 stage1('{TICKER}') 再补数"

raw_path = CACHE / "raw_data.json"
raw = json.loads(raw_path.read_text(encoding="utf-8"))
dims = raw["dimensions"]

def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": SEC_UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def wrap(data: dict, source: str) -> dict:
    return {"ticker": TICKER, "data": data, "source": source, "fallback": False, "error": None}

# --- 1. SEC XBRL: ROE 史 + 现金 + 逐季 EPS/BVPS -------------------------
print(f"[1/5] SEC XBRL · {TICKER}")
tickers_map = _get_json("https://www.sec.gov/files/company_tickers.json")
cik = next((v["cik_str"] for v in tickers_map.values() if v["ticker"] == TICKER), None)
assert cik, f"SEC ticker 表里没有 {TICKER}——ADR/外国公司可能不申报 XBRL,本脚本只支持美国申报公司"
facts = _get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")["facts"]
gaap = facts["us-gaap"]

def units_usd(concept: str) -> list:
    node = gaap.get(concept) or {}
    for unit in ("USD", "USD/shares"):
        if unit in node.get("units", {}):
            return node["units"][unit]
    return []

def annual_series(concept: str, duration: bool) -> dict:
    """10-K 年度值 {fy_end_year: value}。duration=True 取跨年区间,False 取时点(instant)。"""
    out = {}
    for e in units_usd(concept):
        if e.get("form") != "10-K" or "frame" in e and "Q" in e.get("frame", ""):
            continue
        end = e.get("end", "")
        if duration:
            start = e.get("start", "")
            if not start or (date.fromisoformat(end) - date.fromisoformat(start)).days < 300:
                continue
        out[end[:4]] = e["val"]  # 同年多次申报取最后一条(修订值)
    return out

ni_y = annual_series("NetIncomeLoss", duration=True)
eq_y = annual_series("StockholdersEquity", duration=False)
fin = dims["1_financials"]["data"]
years = fin.get("financial_years") or sorted(ni_y)[-5:]
roe_hist = [round(ni_y[y] / eq_y[y] * 100, 1) for y in years if y in ni_y and y in eq_y]
print(f"  ROE {years}: {roe_hist}")

def latest_val(*concepts) -> float:
    """多概念取最新报告期值;不同公司短投挂不同概念(META 用 MarketableSecuritiesCurrent)。"""
    best = (None, 0.0)
    for c in concepts:
        entries = sorted(units_usd(c), key=lambda e: e["end"])
        if entries and (best[0] is None or entries[-1]["end"] > best[0]):
            best = (entries[-1]["end"], entries[-1]["val"])
    return best[1]

cash_total = latest_val("CashAndCashEquivalentsAtCarryingValue") + latest_val("ShortTermInvestments", "MarketableSecuritiesCurrent")
print(f"  现金+短投(最新报告期): ${cash_total/1e9:.1f}B")

# 逐季摊薄 EPS → TTM 序列。10-Q 给 Q 值,10-K 给全年,Q4 = FY − (Q1+Q2+Q3)。
eps_q = {}   # {end_date: q_eps}
eps_fy = {}  # {fy_end: fy_eps}
for e in units_usd("EarningsPerShareDiluted"):
    start, end = e.get("start"), e.get("end")
    if not start or not end:
        continue
    days = (date.fromisoformat(end) - date.fromisoformat(start)).days
    if 80 <= days <= 100:
        eps_q[end] = e["val"]
    elif days >= 300 and e.get("form") == "10-K":
        eps_fy[end] = e["val"]
for fy_end, fy_val in eps_fy.items():  # 补 Q4
    y = fy_end[:4]
    qs = [v for d, v in eps_q.items() if d[:4] == y and d != fy_end]
    if len(qs) == 3 and fy_end not in eps_q:
        eps_q[fy_end] = round(fy_val - sum(qs), 2)
q_ends = sorted(eps_q)
ttm = {q_ends[i]: sum(eps_q[d] for d in q_ends[i-3:i+1]) for i in range(3, len(q_ends))}

# 季末 BVPS = 权益(instant) / 当季摊薄加权股数
shares_q = {e["end"]: e["val"] for e in (gaap.get("WeightedAverageNumberOfDilutedSharesOutstanding", {}).get("units", {}).get("shares", []))
            if e.get("start") and 80 <= (date.fromisoformat(e["end"]) - date.fromisoformat(e["start"])).days <= 100}
eq_q = {e["end"]: e["val"] for e in units_usd("StockholdersEquity")}
bvps = {d: eq_q[d] / shares_q[d] for d in q_ends if d in eq_q and d in shares_q}

# --- 精确 PE/PB 分位: 月收盘 ÷ 最近已披露季度的 TTM EPS / BVPS(阶梯,无插值) ---
import yfinance as yf
hist = yf.Ticker(TICKER).history(period=f"{QUANTILE_YEARS}y", interval="1mo", auto_adjust=False)["Close"].dropna()
# subtle: pandas 3.0 的 DatetimeIndex 单位可能是秒而 to_datetime 默认微秒——统一 as_unit("s") 否则比较全错(2026-09-09 踩过)
m_ts = hist.index.tz_localize(None).as_unit("s").asi8
import bisect
ttm_ts = [int(time.mktime(date.fromisoformat(d).timetuple())) for d in sorted(ttm)]
ttm_vals = [ttm[d] for d in sorted(ttm)]
bv_ts = [int(time.mktime(date.fromisoformat(d).timetuple())) for d in sorted(bvps)]
bv_vals = [bvps[d] for d in sorted(bvps)]

def step_at(ts, xs, vs):  # 取 ≤ts 的最近一个已披露值;窗口早于首个披露则返回 None
    i = bisect.bisect_right(xs, ts) - 1
    return vs[i] if i >= 0 else None

pe_series, pb_series = [], []
for ts, px in zip(m_ts, hist.values):
    e, b = step_at(ts, ttm_ts, ttm_vals), step_at(ts, bv_ts, bv_vals)
    if e and e > 0: pe_series.append(px / e)
    if b and b > 0: pb_series.append(px / b)
cur_pe = float(dims["0_basic"]["data"]["pe_ttm"])
cur_pb = float(dims["0_basic"]["data"]["pb"])
pe_q_pct = round(sum(1 for x in pe_series if x < cur_pe) / len(pe_series) * 100)
pb_q_pct = round(sum(1 for x in pb_series if x < cur_pb) / len(pb_series) * 100)
print(f"  PE 分位 P{pe_q_pct} (区间 {min(pe_series):.1f}-{max(pe_series):.1f}, n={len(pe_series)}月) · PB 分位 P{pb_q_pct} (区间 {min(pb_series):.1f}-{max(pb_series):.1f})")

# --- 2. moomoo 资金流向 → 12_capital_flow --------------------------------
print(f"[2/5] moomoo 资金流向 · US.{TICKER}")
flow_rows = []
try:
    from moomoo import OpenQuoteContext, RET_OK, PeriodType
    q = OpenQuoteContext(host=OPEND_HOST, port=OPEND_PORT)
    try:
        start = (date.today() - timedelta(days=40)).isoformat()
        ret, df = q.get_capital_flow(f"US.{TICKER}", period_type=PeriodType.DAY, start=start, end=date.today().isoformat())
        assert ret == RET_OK, f"get_capital_flow: {df}"
        df = df.tail(20)
        for _, r in df[::-1].iterrows():  # 新→旧,打分器取前 5 行当"5日"
            main = float(r.get("super_in_flow") or 0) + float(r.get("big_in_flow") or 0)
            flow_rows.append({"日期": str(r.get("capital_flow_item_time"))[:10],
                              "主力净流入-净额": main, "净流入": float(r.get("in_flow") or 0)})
        print(f"  {len(flow_rows)} 天 · 5日主力净流入 {sum(x['主力净流入-净额'] for x in flow_rows[:5])/1e8:+.1f}亿$")
    finally:
        q.close()
except Exception as e:
    print(f"  ⚠️⚠️ moomoo 拉取失败({type(e).__name__}: {str(e)[:80]})——12_capital_flow 保持原样。修复:启动 OpenD 并登录后重跑本脚本")

# --- 3. 同业对标 → 4_peers ------------------------------------------------
print(f"[3/5] yfinance 同业 · {PEERS}")
peer_rows = [{"name": raw.get("dimensions", {}).get("0_basic", {}).get("data", {}).get("name", TICKER),
              "code": TICKER, "pe": round(cur_pe, 1),
              "market_cap_b": round(dims["0_basic"]["data"]["market_cap"] / 1e9), "is_self": True}]
for code in PEERS:
    try:
        info = yf.Ticker(code).info
        peer_rows.append({"name": info.get("shortName", code), "code": code,
                          "pe": round(info["trailingPE"], 1) if info.get("trailingPE") else None,
                          "market_cap_b": round(info["marketCap"] / 1e9) if info.get("marketCap") else None,
                          "is_self": False})
    except Exception as e:
        print(f"  ⚠️ {code} 拉取失败: {e}")
print("  " + " · ".join(f"{p['code']} PE {p['pe']}" for p in peer_rows))

# --- 4. FMP 研报共识 → 6_research(可选,无 key 则跳过留给 agent) ----------
print("[4/5] FMP 共识(可选)")
import os
research_data = None
fmp_key = os.environ.get("FMP_APIKEY")
if fmp_key:
    base = "https://financialmodelingprep.com/stable"
    try:
        ptc = _get_json(f"{base}/price-target-consensus?symbol={TICKER}&apikey={fmp_key}")[0]
        gs = _get_json(f"{base}/grades-consensus?symbol={TICKER}&apikey={fmp_key}")[0]
        buy_n = gs.get("strongBuy", 0) + gs.get("buy", 0)
        total_n = buy_n + gs.get("hold", 0) + gs.get("sell", 0) + gs.get("strongSell", 0)
        research_data = {"report_count": total_n, "rating_distribution": {"买入": buy_n, "持有": gs.get("hold", 0), "卖出": gs.get("sell", 0) + gs.get("strongSell", 0)},
                         "targets": [{"broker": "街面共识", "rating": gs.get("consensus", "-"), "pt": ptc.get("targetConsensus")},
                                     {"broker": "中位", "rating": "-", "pt": ptc.get("targetMedian")}],
                         "target_high_low": [ptc.get("targetHigh"), ptc.get("targetLow")]}
        print(f"  共识 PT {ptc.get('targetConsensus')} (高 {ptc.get('targetHigh')}/低 {ptc.get('targetLow')}) · {total_n} 位分析师 买入 {buy_n}")
    except Exception as e:
        print(f"  ⚠️ FMP 拉取失败: {e} —— 6_research 留给 agent 经 FMP MCP 填")
else:
    print("  未设 FMP_APIKEY —— 6_research 留给 agent 经 FMP MCP 填(当前接入实测免费可用)")

# --- 5. 缠论结构 → 2_kline.chan(czsc 引擎,见 chan_signals.py) ---------------
print(f"[5/5] 缠论结构 · {TICKER}(日线+周线)")
chan = None
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from chan_signals import chan_summary
    chan = chan_summary(TICKER)
    print("  " + chan.get("summary", "无日线中枢摘要"))
    w = chan["levels"].get("W", {})
    if w.get("zs"):
        print(f"  周线中枢 {w['zs']['sdt']}→{w['zs']['edt']} zg {w['zs']['zg']} / zd {w['zs']['zd']} · 价格{w['position']}")
except Exception as e:
    print(f"  ⚠️⚠️ 缠论计算失败({type(e).__name__}: {str(e)[:80]})——2_kline 不加 chan 字段。修复:pip install czsc 或检查 chan_signals.py 同目录")

# --- 落盘 -----------------------------------------------------------------
if DRY:
    print("\n--dry-run · 未写入任何文件")
    sys.exit(0)

fin["roe_history"] = roe_hist
fin["roe_history_basis"] = f"SEC XBRL CIK{cik} 10-K NI/期末权益, {date.today()}"
fin.setdefault("financial_health", {})["cash"] = round(cash_total / 1e8, 2)  # 亿$,对齐插件口径
val = dims["10_valuation"]["data"] if "data" in dims["10_valuation"] else dims["10_valuation"]
val["pe_quantile"], val["pb_quantile"] = f"{pe_q_pct}%", f"{pb_q_pct}%"
val["_quantile_basis"] = f"SEC 逐季 TTM EPS/BVPS 阶梯 × yfinance {QUANTILE_YEARS}y 月收盘, {date.today()}"
dims["4_peers"] = wrap({"peer_table": peer_rows, "global_peer_comparison": {"peer_count": len(peer_rows) - 1, "scope": "US comparables"}},
                       f"us_backfill:yfinance {date.today()}")
if flow_rows:
    dims["12_capital_flow"] = wrap({"main_fund_flow_20d": flow_rows, "unlock_schedule": [],
                                    "_note": "moomoo OpenD 美股资金流向(超大+大单=主力),非 A 股北向口径"},
                                   f"us_backfill:moomoo {date.today()}")
if research_data:
    dims["6_research"] = wrap(research_data, f"us_backfill:FMP {date.today()}")
if chan:
    kl = dims["2_kline"]["data"] if "data" in dims["2_kline"] else dims["2_kline"]
    kl["chan"] = chan  # 结构+买卖点候选+中文摘要;技术派评委简报与 dim_commentary 直接引用

from lib.data_integrity import refresh_recovery_artifact
# A touched dimension is not necessarily complete. Revalidate each field instead
# of clearing all critical gaps (including unrelated missing price/industry).
refresh_recovery_artifact(raw, TICKER, CACHE / "_data_gaps.json")
raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n已写入 {raw_path}\n下一步(指纹已变,顺序不能乱):\n  python3 -c \"from run_real_test import stage1_modeling; stage1_modeling('{TICKER}')\"\n  → agent 覆盖 panel → agent_analysis.json 带新 hash → stage2('{TICKER}')")
