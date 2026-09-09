"""缠论结构摘要:日线+周线的 笔/中枢/未完成笔 + 按定义标出的买卖点候选,输出给 stock-deep-analyzer 的 2_kline 维度。

引擎用 czsc 1.0(Rust 核心,waditu/czsc);数据用 yfinance 前复权,与插件 2_kline 同源。
只做结构识别与规则标注,不做背驰的 MACD 面积比较(czsc 1.0 去掉了旧版 signals 库,
一买/二买的背驰判断这里用"同向相邻两笔力度比"做降级代理,结果一律标 候选)。

用法:
    python3 chan_signals.py META            # 打印日线+周线摘要
    from chan_signals import chan_summary   # chan_summary("META") -> dict

worked example(2026-09-09 META 日线):
    最近中枢 2025-11-19→2026-08-19 zg=674.95 zd=598.93,未完成向上笔 537→658,
    价格 641 在中枢内偏上 → 三买候选条件 = 站上 674.95 后回调不破 674.95;跌破 598.93 结构转空。
"""
import sys
from datetime import datetime

# --- 配置 ---------------------------------------------------------------
LOOKBACK = {"D": "2y", "W": "6y"}      # yfinance period;周线 6 年才够 30+ 根笔
POWER_DIVERGE_RATIO = 0.8              # 同向后一笔力度 < 前一笔 * 0.8 视为力度衰竭(背驰代理,偏保守)
NEAR_PCT = 1.5                         # 距中枢上下沿 <1.5% 记为"贴近"

def _bars(ticker: str, freq_key: str) -> list:
    import yfinance as yf
    from czsc import RawBar, Freq
    interval = {"D": "1d", "W": "1wk"}[freq_key]
    df = yf.Ticker(ticker).history(period=LOOKBACK[freq_key], interval=interval, auto_adjust=True).dropna()
    assert len(df) >= 60, f"{ticker} {freq_key} 只有 {len(df)} 根 K 线,不够识别笔段(需 ≥60);检查代码拼写或上市时间"
    return [RawBar(symbol=ticker, dt=ts.to_pydatetime().replace(tzinfo=None), freq=getattr(Freq, freq_key),
                   open=float(r.Open), close=float(r.Close), high=float(r.High), low=float(r.Low),
                   vol=float(r.Volume), amount=float(r.Volume * r.Close), id=i)
            for i, (ts, r) in enumerate(df.iterrows())]

def _level(ticker: str, freq_key: str) -> dict:
    """单级别结构 → dict。买卖点规则(缠论 108 课定义,只标候选):
      三买: 向上笔离开中枢(high>zg)后的回调笔 low 仍 > zg     三卖: 向下笔离开(low<zd)后的反弹笔 high 仍 < zd
      一买候选: 向下笔创中枢以来新低(low<dd)且力度 < 前一向下笔*0.8   一卖候选: 镜像(high>gg 且力度衰竭)
      二买候选: 一买后的向上笔,其后回调笔 low > 一买笔 low          二卖候选: 镜像
    """
    from czsc import CZSC
    c = CZSC(_bars(ticker, freq_key))
    bis, zss = c.bi_list, c.zs_list
    assert len(bis) >= 3, f"{ticker} {freq_key} 仅 {len(bis)} 笔,无法判断结构"
    last = bis[-1]
    price = float(c.bars_raw[-1].close)
    out = {
        "freq": freq_key, "bars": len(c.bars_raw), "bi_count": len(bis), "zs_count": len(zss),
        "last_bi": {"dir": "up" if "上" in str(last.direction) else "down", "sdt": str(last.sdt.date()), "edt": str(last.edt.date()),
                    "high": round(last.high, 2), "low": round(last.low, 2), "power": round(float(last.power), 2)},
        "ubi": None, "zs": None, "price": round(price, 2), "position": None, "bsp_candidates": [],
    }
    if c.ubi:
        u = c.ubi
        out["ubi"] = {"dir": "up" if "Up" in str(u["direction"]) or "上" in str(u["direction"]) else "down",
                      "high": round(float(u["high"]), 2), "low": round(float(u["low"]), 2)}
    if not zss:
        out["position"] = "无中枢(单边走势)"
        return out
    z = zss[-1]
    zg, zd, gg, dd = float(z.zg), float(z.zd), float(z.gg), float(z.dd)
    out["zs"] = {"sdt": str(z.sdt.date()), "edt": str(z.edt.date()), "zg": round(zg, 2), "zd": round(zd, 2),
                 "gg": round(gg, 2), "dd": round(dd, 2), "bi_count": len(z.bis)}
    if price > zg:
        out["position"] = "中枢上方" + ("(贴近上沿)" if (price - zg) / zg * 100 < NEAR_PCT else "")
    elif price < zd:
        out["position"] = "中枢下方" + ("(贴近下沿)" if (zd - price) / zd * 100 < NEAR_PCT else "")
    else:
        near = "贴近上沿" if (zg - price) / zg * 100 < NEAR_PCT else "贴近下沿" if (price - zd) / zd * 100 < NEAR_PCT else "中部"
        out["position"] = f"中枢内({near})"

    # 只看中枢结束后的笔:结构判断针对"离开中枢"的走势
    after = [b for b in bis if b.sdt >= z.edt] or bis[-2:]
    ups = [b for b in after if "上" in str(b.direction)]
    downs = [b for b in after if "下" in str(b.direction)]
    cands = out["bsp_candidates"]
    if ups and downs and ups[-1].high > zg and downs[-1].sdt > ups[-1].sdt and downs[-1].low > zg:
        cands.append({"type": "三买", "at": str(downs[-1].edt.date()), "level": round(float(downs[-1].low), 2),
                      "rule": f"向上笔突破 zg {zg:.2f} 后回调低点 {downs[-1].low:.2f} 未回中枢", "invalid_below": round(zg, 2)})
    if ups and downs and downs[-1].low < zd and ups[-1].sdt > downs[-1].sdt and ups[-1].high < zd:
        cands.append({"type": "三卖", "at": str(ups[-1].edt.date()), "level": round(float(ups[-1].high), 2),
                      "rule": f"向下笔跌破 zd {zd:.2f} 后反弹高点 {ups[-1].high:.2f} 未回中枢", "invalid_above": round(zd, 2)})
    all_downs = [b for b in bis if "下" in str(b.direction)]
    all_ups = [b for b in bis if "上" in str(b.direction)]
    if len(all_downs) >= 2 and all_downs[-1].low < dd and float(all_downs[-1].power) < float(all_downs[-2].power) * POWER_DIVERGE_RATIO:
        cands.append({"type": "一买候选", "at": str(all_downs[-1].edt.date()), "level": round(float(all_downs[-1].low), 2),
                      "rule": f"创新低 {all_downs[-1].low:.2f}<dd {dd:.2f} 且笔力度 {float(all_downs[-1].power):.1f} < 前笔 {float(all_downs[-2].power):.1f}×{POWER_DIVERGE_RATIO}(力度代理,非 MACD 背驰)"})
    if len(all_ups) >= 2 and all_ups[-1].high > gg and float(all_ups[-1].power) < float(all_ups[-2].power) * POWER_DIVERGE_RATIO:
        cands.append({"type": "一卖候选", "at": str(all_ups[-1].edt.date()), "level": round(float(all_ups[-1].high), 2),
                      "rule": f"创新高 {all_ups[-1].high:.2f}>gg {gg:.2f} 且笔力度衰竭(代理)"})
    return out

def chan_summary(ticker: str) -> dict:
    """日线+周线结构 + 一句话中文摘要。失败的级别记 error 字符串,不中断另一级别。"""
    res = {"computed_at": datetime.now().isoformat(timespec="minutes"), "engine": "czsc 1.0 (waditu) · yfinance 前复权", "levels": {}}
    for k in ("D", "W"):
        try:
            res["levels"][k] = _level(ticker, k)
        except Exception as e:
            res["levels"][k] = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
            print(f"  ⚠️ {ticker} {k} 级别缠论计算失败: {e}")
    d = res["levels"].get("D", {})
    if "zs" in d and d["zs"]:
        z, lb = d["zs"], d["last_bi"]
        bsp = "、".join(f"{c['type']}@{c['level']}" for c in d["bsp_candidates"]) or "无"
        res["summary"] = (f"日线最近中枢 {z['sdt']}→{z['edt']} 上沿 {z['zg']}/下沿 {z['zd']}(共 {z['bi_count']} 笔),"
                          f"价格 {d['price']} 位于{d['position']};最近完成笔{('向上' if lb['dir']=='up' else '向下')} {lb['low']}→{lb['high']},"
                          f"未完成笔{('向上' if d['ubi'] and d['ubi']['dir']=='up' else '向下') if d['ubi'] else '无'};买卖点候选:{bsp}。"
                          f"多头结构确认线 {z['zg']}(站上后回调不破=三买),空头转折线 {z['zd']}。")
    elif "position" in d:
        res["summary"] = f"日线{d['position']},最近完成笔 {d['last_bi']}"
    return res

if __name__ == "__main__":
    assert len(sys.argv) == 2, "用法: python3 chan_signals.py <TICKER>"
    import json
    r = chan_summary(sys.argv[1].upper())
    print(json.dumps(r, ensure_ascii=False, indent=1))
