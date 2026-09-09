---
description: 完整深度分析一只股票（22 维数据 + 66 位大佬量化评委 + 22 种机构分析方法 + 杀猪盘检测 + aJay 编辑式 HTML 报告）
argument-hint: "[股票名称或代码，例如 华工科技 / 002273 / AAPL / 00700.HK]"
---

# 深度分析任务

用户输入: $ARGUMENTS

## 执行流程（两段式 · 你必须在中间介入）

### 第一段 · 数据采集 + 骨架分（脚本完成）

```bash
cd <plugin_root>
pip install -r requirements.txt 2>/dev/null
cd skills/deep-analysis/scripts
python -c "from run_real_test import stage1; stage1('$ARGUMENTS')"
```

这会跑完 Task 1 → 1.5 → 2 → 3（规则引擎骨架分），输出到 `.cache/{ticker}/` 下。

### 第一段半 · 美股补数（美股必走；A股/港股跳过）

雪球系 fetcher 对美股基本失效（ROE 史 / PE 分位 / 同业 / 资金流 / 研报整块缺失，stage2 自审门会拦）。用免费源补齐：

```bash
# cwd 仍在 skills/deep-analysis/scripts；需 AJAY_SEC_UA="姓名 邮箱"（SEC 要求），OpenD 在线则顺带补资金流
python3 us_backfill.py $ARGUMENTS --dry-run   # 先看将写入的值
python3 us_backfill.py $ARGUMENTS             # 写入 raw_data.json（SEC XBRL 财务/估值分位 + moomoo 资金流 + 同业 + czsc 缠论结构）
python -c "from run_real_test import stage1_modeling; stage1_modeling('$ARGUMENTS')"   # 补 raw 会变指纹，必须重算骨架分
```

6_research（研报共识）不在脚本里：用 FMP MCP 的 `analyst` 工具拉 price-target-consensus / grades-summary / financial-estimates，写进 `dims["6_research"]`（格式：`report_count`、`rating_distribution`、`targets`），再跑一次 `stage1_modeling`。

> ⚠️ 指纹链：raw_data.json 任何改动都会让 agent_analysis.json 失效（`analysis_input_hash` 不匹配 → stage2 丢弃 agent 分析）。顺序固定：**补 raw → stage1_modeling → agent 覆盖 → merge_panel → agent_analysis 带新 hash → stage2**。

### 第二段 · 你来分析（核心！不能跳过！）

Stage 1 跑完后，**你必须做以下事情**：

**0. 数据缺口前置（必走）**

读 `.cache/{ticker}/_data_gaps.json`（stage1 写；`_review_issues.json` 要到 stage2 才有）。`critical_missing: true` 或有 `severity: critical` 的 task 时：美股走上面的 `us_backfill.py`；A股/港股设 `AJAY_PLAYWRIGHT_FORCE=1` 后调 `lib.playwright_fallback.autofill_via_playwright(raw, ticker)`。补完都要重跑 `stage1_modeling`。

**1. 读取评委骨架分**

读 `.cache/{ticker}/panel.json`，看 66 人各自打了多少分（分组见 `lib/investor_db.py`：A 价值 6 · B 成长 9 · C 宏观 7 · D 技术 4 · E 中式价投 7 · F 游资 24 · G 量化 4 · H 科技领袖 4 · I Serenity 1）。特别关注：
- Top 5 看多和 Top 5 看空分别是谁？他们的 headline 有没有说服力？
- 有多少人 skip 了？（非 A 股时游资会 skip）
- 有没有明显不合理的分数？

**2. 逐组分析（spawn 3 个并行 sub-agent，类型 `investor-panel`）**

先写一份简报文件（公司数据摘要 + 骨架分里已知的规则引擎误伤 + 真实持仓知识）让 agent Read，不要把历史对话贴进 prompt。每个 agent 把 JSON 数组 Write 到 `.cache/{ticker}/verdicts/verdict_agentN.json`：

**Agent 1 · A 价值 + B 成长（15 人）**：buffett graham fisher munger templeton klarman lynch oneill thiel wood andreessen gurley naval gerstner chamath
**Agent 2 · C 宏观 + D 技术（11 人）**：soros dalio marks druck robertson burry chanos livermore minervini darvas gann
**Agent 3 · E 中式价投 + G 量化 + H 科技领袖 + I（16 人）**：duan zhangkun zhushaoxing xiezhiyu fengliu dengxiaofeng zhang_lei simons thorp shaw asness jensen_huang musk altman saylor serenity
**F 游资（24 人）**：非 A 股保持骨架分的 skip，不发 agent。

```
每项: {"investor_id", "signal": bullish|bearish|neutral|skip, "score": 0-100, "headline": 必须引用数字, "reasoning": 2-3 句第一人称}
以投资者本人第一人称思考；简报里标出的规则引擎误伤必须修正；真实持仓优先于规则分；禁止 spawn 其他 agent。
最后一行输出状态词 DONE / DONE_WITH_CONCERNS / BLOCKED。
```

agent 回来后不信自述，程序化核验：42 个 id 齐全、signal 合法、score 0-100、headline 含数字。

**3. 合并 agent 结果**

```bash
python3 merge_panel.py {ticker}    # 读 .cache/{ticker}/verdicts/verdict_*.json，覆盖 panel.json 并按 v2.15.5 公式重算共识/流派分/空头账本
```

**4. 写 agent_analysis.json（闭环关键！）**

对关键维度（财报/估值/护城河/行业）写 1-2 句定性评语（≥20 字，引用具体数字）。如果需要，web search 补充信息。

**⚠️ 必读：agent_analysis.json 完整 schema（缺字段 stage2 会报 schema warning/error）**

| 字段 | 要求 | 触发校验 |
|---|---|---|
| `agent_reviewed` | 必须 `true` | ⚠️ 缺 → warning |
| `analysis_input_hash` | `lib.agent_review.analysis_input_hash(raw)` 对**当前** raw_data.json 的值；补数后必须重算 | 🔴 不匹配 → stage2 整个丢弃 agent 分析 |
| `dim_commentary` | 覆盖全部 22 维，**每条 ≥20 字**（引用具体数字，禁止空泛） | ⚠️ <20 字 → warning |
| `panel_insights` | **≥30 字**，评委投票分布 + 多空分歧分析 | ⚠️ <30 字 → warning |
| `great_divide_override` | punchline(≥10 字) + bull_say_rounds(≥3 条) + bear_say_rounds(≥3 条) | 🔴 缺字段 → error |
| `narrative_override.core_conclusion` | **≥20 字**综合定论 | ⚠️ <20 字 → warning |
| `narrative_override.risks` | **≥3 条**风险 | ⚠️ <3 条 → warning |
| `narrative_override.buy_zones` | **必须含 value/growth/technical/youzi 四个 key**，每个 key 内含 `price`(数值, youzi 可为 0) + `rationale`(≥5 字解释) | 🔴 缺 key → error / ⚠️ 缺子字段 → warning |
| `qualitative_deep_dive` | 覆盖 3_macro/7_industry/8_materials/9_futures/13_policy/15_events 共 6 维。每维含：`evidence` 数组（≥2 条）、`associations` 跨域因果链（6 维合计 ≥3 条）、`conclusion`（1-2 句） | 🔴 evidence 非 list → error |
| `data_gap_acknowledged` | dict 格式 `{"dim_key": "已尝试 X 但失败的原因"}`，标记数据采集失败但 agent 已知晓的维度 | 🔴 类型非 dict → error |

把所有 agent 产出写入 `.cache/{ticker}/agent_analysis.json`：
```python
from lib.cache import write_task_output, read_task_output
from lib.agent_review import analysis_input_hash
from lib.agent_analysis_validator import validate   # 写入前先 validate，error 级不能落盘
write_task_output(ticker, "agent_analysis", {
    "agent_reviewed": True,
    "analysis_input_hash": analysis_input_hash(read_task_output(ticker, "raw_data")),
    "dim_commentary": {
        "0_basic": "公司全称+成立/上市时间+市值+行业地位，≥20字",
        "1_financials": "ROE/营收增速/净利率/毛利率/FCF等核心数据+质量判断，≥20字",
        # ... 覆盖全部 22 维，每条 ≥20 字，引用具体数字
    },
    "panel_insights": "评委投票分布(看多X/中性X/看空X)+多空分歧核心逻辑，≥30字",
    "great_divide_override": {
        "punchline": "多空对决一句话金句，≥10字",
        "bull_say_rounds": ["R1: 看多论点+引用数字", "R2: ...", "R3: ..."],
        "bear_say_rounds": ["R1: 看空论点+引用数字", "R2: ...", "R3: ..."]
    },
    "narrative_override": {
        "core_conclusion": "综合定论+评分+建仓建议，≥20字",
        "risks": ["风险1", "风险2", "风险3", ...],  # ≥3条
        "buy_zones": {
            "value":     {"price": 140, "rationale": "DCF安全边际>60%，等待极端低估"},
            "growth":    {"price": 160, "rationale": "PEG<0.1极度低估，当前即可建仓"},
            "technical": {"price": 180, "rationale": "等待Stage 2突破确认后右侧入场"},
            "youzi":     {"price": 0, "rationale": "非A股不适用游资打板策略"}
        }
    },
    "qualitative_deep_dive": {
        "3_macro": {
            "evidence": [{"source": "...", "url": "...", "finding": "...", "retrieved_at": "2026-04-27"}],
            "associations": [{"link_to": "7_industry", "chain_id": "macro->industry", "causal_chain": "...", "estimated_impact": "medium"}],
            "conclusion": "宏观结论1-2句"
        },
        # ... 7_industry, 8_materials, 9_futures, 13_policy, 15_events 同上格式
        # 重要：associations 跨所有 6 维合计 ≥3 条
    },
    "data_gap_acknowledged": {
        "10_valuation.pe_quantile": "Lixinger API 对该港股不支持历史分位查询"
    }
})
```

> 详细说明见 `skills/deep-analysis/SKILL.md` 第 464 行 schema 表，以及 `references/task2.5-qualitative-deep-dive.md` 第 5 节。

### 第三段 · 生成报告（脚本完成）

```bash
python -c "from run_real_test import stage2; stage2('$ARGUMENTS')"
```

stage2 会自动读取 panel.json + agent_analysis.json，合并生成最终报告。
agent_analysis.json 中的字段优先级高于脚本 stub。

### 第四段 · 向用户汇报

1. 综合评分 + 定调
2. 66 评委投票分布（多头账本 多/中/空/skip，空头账本 Burry/Chanos 单列）
3. DCF 内在价值 vs 当前价
4. Top 3 看多理由 + Top 3 看空理由
5. Great Divide 金句
6. 杀猪盘等级
7. 报告文件路径

## 快速模式（跳过 agent 介入）

如果用户说"快速分析"或"不用那么详细"：
```bash
cd <plugin_root>
python run.py $ARGUMENTS --no-browser
```
这会 stage1 + stage2 一把跑完，不做 agent 分析。

## 禁止

- 不跑脚本就编造数据
- 跳过 agent 分析直接出报告（除非用户明确要快速模式）
- 用"基本面良好"等模板话术
