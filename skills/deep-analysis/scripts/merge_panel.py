"""把 role-play agent 的评委判断合并回 panel.json,并重算共识/流派分/空头账本。

用法(cwd = 本目录):
    python3 merge_panel.py META /path/to/verdicts   # 目录下所有 verdict_*.json 都会合并
    python3 merge_panel.py META                     # 默认读 .cache/META/verdicts/

verdict 文件格式:JSON 数组,每项 {investor_id, signal, score, headline, reasoning}。
只覆盖 signal/score/headline/reasoning/comment/verdict;保留骨架分的 pass/fail 证据,hollow 校验才有意义。
聚合公式逐字复刻 lib/pipeline/score_fns.py generate_panel(v2.15.5)——那里是函数内常量,无法 import,故重复。
不做:不改 raw_data.json,不算 agent_analysis 指纹。
"""
import json
import sys
from pathlib import Path

assert len(sys.argv) >= 2, "用法: python3 merge_panel.py <TICKER> [verdict_dir]"
TICKER = sys.argv[1].upper()
VDIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(f".cache/{TICKER}/verdicts")
PANEL = Path(f".cache/{TICKER}/panel.json")
assert PANEL.exists(), f"{PANEL} 不存在——先跑 stage1('{TICKER}')"
files = sorted(VDIR.glob("verdict_*.json"))
assert files, f"{VDIR} 下没有 verdict_*.json;agent 应把判断写到该目录"

panel = json.loads(PANEL.read_text(encoding="utf-8"))
overrides = {}
for f in files:
    for v in json.loads(f.read_text(encoding="utf-8")):
        assert v.get("signal") in ("bullish", "bearish", "neutral", "skip"), f"{f.name}: {v.get('investor_id')} signal 非法 {v.get('signal')!r}"
        overrides[v["investor_id"]] = v
print(f"verdicts: {len(overrides)} from {len(files)} files")

def _score_to_verdict(score, signal):
    if signal == "bullish" and score >= 80: return "强烈买入"
    if signal == "bullish": return "买入"
    if signal == "bearish" and score <= 20: return "回避"
    if signal == "bearish": return "观望"
    return "关注" if score >= 50 else "观望"

changed = 0
for inv in panel["investors"]:
    o = overrides.get(inv["investor_id"])
    if not o:
        continue
    sig = o["signal"]; score = int(max(0, min(100, o["score"])))
    inv.update({"signal": sig, "score": 0 if sig == "skip" else score, "headline": o["headline"],
                "reasoning": o["reasoning"], "comment": f"{o['reasoning']}\n{o['headline']}"})
    if sig == "skip":
        inv["verdict"] = "不适合"; inv["confidence"] = 0
    elif inv.get("mandate") == "short":
        inv["verdict"] = "做空候选" if sig == "bearish" else "无明确做空逻辑"
    else:
        inv["verdict"] = _score_to_verdict(inv["score"], sig)
    changed += 1
print(f"overridden: {changed}")

# --- aggregates · verbatim v2.15.5 ---------------------------------------
NEUTRAL_WEIGHT, SCORE_WEIGHT, VOTE_WEIGHT, POLARIZE_K = 0.6, 0.65, 0.35, 1.30
def _polarize(c, k=POLARIZE_K):
    return max(0.0, min(100.0, 50.0 + (c - 50.0) * k))

inv_out = panel["investors"]
vote_dist = {"strongly_buy": 0, "buy": 0, "watch": 0, "wait": 0, "avoid": 0, "n_a": 0, "skip": 0}
sig_dist = {"bullish": 0, "neutral": 0, "bearish": 0, "skip": 0}
v_key = {"强烈买入": "strongly_buy", "买入": "buy", "关注": "watch", "观望": "wait", "回避": "avoid", "不适合": "skip"}
for m in inv_out:
    if m.get("mandate") != "short":
        vote_dist[v_key.get(m["verdict"], "n_a")] += 1
        sig_dist[m["signal"]] += 1
bullish, neutral, bearish = sig_dist["bullish"], sig_dist["neutral"], sig_dist["bearish"]
active = bullish + neutral + bearish
scores = [m["score"] for m in inv_out if m.get("mandate") != "short" and m["signal"] != "skip"]
score_mean = sum(scores) / len(scores) if scores else 50.0
vote_weighted = (bullish + NEUTRAL_WEIGHT * neutral) / max(active, 1) * 100
consensus_raw = SCORE_WEIGHT * score_mean + VOTE_WEIGHT * vote_weighted
consensus = _polarize(consensus_raw)

short_book = [m for m in inv_out if m.get("mandate") == "short"]
short_active = [m for m in short_book if m["signal"] != "skip"]
short_scores = [m["score"] for m in short_active]
short_consensus = {
    "total": len(short_book), "active": len(short_active), "skip": len(short_book) - len(short_active),
    "short_candidates": sum(1 for m in short_active if m["signal"] == "bearish"),
    "no_short_thesis": sum(1 for m in short_active if m["signal"] in ("bullish", "neutral")),
    "avg_score": round(sum(short_scores) / len(short_scores), 1) if short_scores else 50.0,
    "top_short_candidates": [{"id": m["investor_id"], "name": m["name"], "score": m["score"], "headline": m["headline"]}
                             for m in sorted(short_active, key=lambda x: x["score"])[:5]],
}

GROUP_META = {
    "A": ("经典价值派", "巴菲特 / 格雷厄姆 / 费雪 / 芒格 一脉"), "B": ("成长派", "彼得·林奇 / 欧奈尔 / 蒂尔 / 伍德 一脉"),
    "C": ("宏观派", "索罗斯 / 达利欧 / 马克斯 一脉"), "D": ("技术派", "利弗莫尔 / Minervini / 达瓦斯 一脉"),
    "E": ("中式价投", "段永平 / 张坤 / 朱少醒 / 冯柳 一脉"), "F": ("A 股游资", "龙虎榜顶流 23 位·章盟主/孙哥/赵老哥为代表"),
    "G": ("量化派", "Simons / Thorp / Shaw 一脉"), "H": ("科技领袖派", "黄仁勋 / 马斯克 / Altman / Saylor 一脉"),
    "I": ("AI 卡位/瓶颈猎手", "Serenity · AI 供应链卡脖子/瓶颈点"),
}
def _c2v(c):
    return "重仓" if c >= 80 else "买入" if c >= 65 else "关注" if c >= 50 else "谨慎" if c >= 35 else "回避"

by_group = {}
for m in inv_out:
    by_group.setdefault(m.get("group", "?"), []).append(m)
school = {}
for g in sorted(by_group):
    allm = by_group[g]; members = [m for m in allm if m.get("mandate") != "short"]
    act = [m for m in members if m["signal"] != "skip"]; n = len(act)
    gb = sum(1 for m in act if m["signal"] == "bullish"); gn = sum(1 for m in act if m["signal"] == "neutral")
    gr = sum(1 for m in act if m["signal"] == "bearish"); gs = sum(1 for m in members if m["signal"] == "skip")
    if n:
        sm = sum(m["score"] for m in act) / n; sv = (gb + NEUTRAL_WEIGHT * gn) / n * 100
        sc = _polarize(SCORE_WEIGHT * sm + VOTE_WEIGHT * sv)
    else:
        sm = sv = sc = 0.0
    label, desc = GROUP_META.get(g, (g, ""))
    school[g] = {"group": g, "label": label, "desc": desc, "n_members": len(members), "n_active": n,
                 "short_excluded": len(allm) - len(members), "consensus": round(sc, 1), "avg_score": round(sm, 1),
                 "vote_consensus": round(sv, 1), "score_mean": round(sm, 1), "verdict": _c2v(sc) if n else "不适合",
                 "bullish": gb, "neutral": gn, "bearish": gr, "skip": gs,
                 "dominant_signal": max([("bullish", gb), ("neutral", gn), ("bearish", gr)], key=lambda x: x[1])[0] if n else "skip"}

active_long = [m for m in inv_out if m.get("mandate") != "short" and m["signal"] != "skip"]
hollow = [m["investor_id"] for m in active_long if (m.get("score") or 0) == 0 and not m.get("pass") and not m.get("fail")]
hollow_pct = round(len(hollow) / len(active_long) * 100, 0) if active_long else 0
panel.update({"panel_consensus": round(consensus, 1), "consensus_valid": hollow_pct < 20,
              "hollow_verdicts": len(hollow), "hollow_pct": hollow_pct, "hollow_ids": hollow,
              "consensus_warning": None if hollow_pct < 20 else f"共识分不可采信：{len(hollow)}/{len(active_long)} 位多头评委（{hollow_pct:.0f}%）没有任何有效规则证据。",
              "vote_distribution": vote_dist, "signal_distribution": sig_dist, "school_scores": school,
              "long_active": active, "short_consensus": short_consensus})
panel.setdefault("consensus_formula", {}).update({
    "score_mean": round(score_mean, 2), "vote_weighted": round(vote_weighted, 2), "consensus_raw": round(consensus_raw, 2),
    "consensus_final": round(consensus, 2), "bullish": bullish, "neutral_weighted": round(neutral * NEUTRAL_WEIGHT, 2),
    "bearish": bearish, "skip": sig_dist["skip"], "active": active})
PANEL.write_text(json.dumps(panel, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"consensus {panel['panel_consensus']} · 多{bullish}/中{neutral}/空{bearish}/skip{sig_dist['skip']} · active {active}")
for g, s in school.items():
    print(f"  {g} {s['label']:<10} {s['consensus']:>5} {s['verdict']} ({s['bullish']}多/{s['neutral']}中/{s['bearish']}空/{s['skip']}skip)")
ranked = sorted((m for m in inv_out if m["signal"] != "skip"), key=lambda m: -m["score"])
print("TOP5 BULL:"); [print(f"  {m['investor_id']:<12} {m['score']:>3} {m['headline'][:70]}") for m in ranked[:5]]
print("TOP5 BEAR:"); [print(f"  {m['investor_id']:<12} {m['score']:>3} {m['headline'][:70]}") for m in ranked[-5:]]
print("\n下一步: 写 agent_analysis.json(analysis_input_hash 取自当前 raw_data.json) → stage2")
