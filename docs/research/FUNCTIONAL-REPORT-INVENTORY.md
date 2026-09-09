# 功能报告清单审计

**日期：** 2026-09-09
**范围：** `assets/report-template.html`（原 V1 完整报告）、`assets/report-council.html`、`assets/report-council.js`、`scripts/assemble_report.py` 及 `scripts/lib/report/*`。
**目的：** 给连续、多层的金融研究汇报页提供可直接实现的功能、输入、renderer 与交互契约。本文是功能审计，不是视觉 moodboard；不修改源代码。

## 0. 结论先行：Council 当前是“导览层”，不是完整报告

`assemble_report.py` 先把原版模板的全部内容组装好（证据、图表、19 张维度卡、机构模型、分歧、评委、研究笔记、风险、区间和导出），但在 `layout="council"` 时：

1. 将这份完整结果另存为 `research-appendix.html`；
2. 再把主 `full-report.html` 与 `full-report-standalone.html` 替换成 `render_council(...)` 的 31 行 shell。

因此目前主入口只保留：4 个场景、3 个问题、8 个方法视角、当前观点、3 条 supporting facts、底稿 dialog、场景 lightbox 和原始输入下载。`raw` 虽然内嵌在 `#council-data`，但“存在 JSON”不等于“功能已交付”。原版功能不是被重新布局，而是主入口不可见。

**实现决策：** 保留 Council 的沉浸式 briefing / 人物讲述作为首层或章节导航；后面连续接回原版报告章节。城市只能改变视觉上下文，不得替代数据章节、模型章节或证据路径。不得以一个场景切换器取代金融研究的信息架构。

### 计数口径必须固定

- 页面上的 **22 个分析维度** = `1_financials`–`19_contests` 的 19 张数据卡 + `20_valuation_models`、`21_research_workflow`、`22_deep_methods` 三个机构级数据包。
- `0_basic` 是身份、报价和市场元数据，不应计入 19 张评分卡，但存在于 `raw_data.json#/dimensions`。
- 因而原始 JSON 的维度 key 实际是 `0_basic` + `1..22`（共 23 个 key）；文档里不要再用“19 个 raw key”或把 `0_basic` 算入 22 个分析维度。

## 1. 原版到 Council 的功能差距

| 功能表面 | 原版 `report-template.html` | 当前 Council | 主入口必须恢复 |
|---|---|---|---|
| 身份/行情封面 | 公司、代码、行业、one-liner、价格、涨跌、市场状态、采集时间、版本 | 只有 ticker/name/sample label/snapshot date | 保留身份和报价，不把 demo 或快照误写成实时行情 |
| 证据边界 | `section-evidence` + coverage、rules、agent review、collected at、数据缺口 | 只有底稿里按记录查看 | 证据条应在报告前段可见；底稿是逐条核验的第二层 |
| 历史价格图 | `render_hero_chart(raw)`，严格使用 `2_kline.data.close_60d`，可对齐 `candles_60d` | 无图表 | 恢复历史观察图；缺失/过期/回退时显示留白状态 |
| 核心结论 | 综合分、结论、趋势/价位/量能/筹码、新闻/风险/催化、条件计划 | 只有当前 topic 的 claim | 恢复一击结论和可审计的输入摘要 |
| 19 张深度数据卡 | 六类 `<details>`、每维 score/status、特化 SVG、pass/fail、source、原始 JSON | 无 | 19 张卡和六类分组必须可读、可折叠、可回到原始值 |
| 机构模型 | DCF、Comps、LBO、首次覆盖、IC memo、催化剂、竞争分析；旧版还保留它们的计算日志 | models tab 只泛化展示 20/21/22 原始 JSON | 用实际模型 renderer 展示数字、假设、敏感性和缺口；不能用 JSON dump 代替 |
| 三表 | 输入和计算存在于 dim 20，但旧版机构入口没有专门 renderer | 无 | 补三表投影表/链接关系/假设/日志；不能因现有入口没渲染就丢弃 |
| 分业务模型 | `INJECT_SEGMENTAL`，可选但完整：对账、donut、历史+情景、3×3 数字表、driver 卡 | 无 | 存在模型时进入连续正文；不存在时显示“未建立”，不要静默消失 |
| 分歧/反证 | bull/bear、3 回合、punchline、panel insights、school scores | 无 | 让每个论点能回到具体维度/记录；保留分歧而非只显示一个 verdict |
| 评委/方法讨论 | 统计、席位、流派筛选、全部展开/收起、点席位跳转聊天 | 无 | 保留数据驱动的 panel，而非只保留 8 张人物图 |
| 公开持仓/友好层 | 一万块情景、相似股、离场触发、基金经理列表 | 无 | 作为研究附录/决策层恢复；必须标注数据性质和缺口 |
| 风险/条件区间 | `section-risks`、`section-zones`、风险条目和四类 rationale | 无 | 恢复；证据不足时一起降级，不能只隐藏分数 |
| 导出/分享 | native dialog、local QR 占位、print、`#share-card`、`#war-report` | 无 | 保留 ID 和导出契约；离线，不向远程 QR 服务发送 URL |
| 主题/目录/可访问性 | theme localStorage、TOC scroll spy/collapse、`prefers-reduced-motion`、dialog 焦点 | Council 自己有 reduced motion、dialog 焦点 | 合并而不是二选一；保留键盘、折叠和返回焦点 |

### 当前 Council 已有的交互，应该嵌回连续报告

`report-council.js:16–60, 109–120` 的以下行为可保留，但不能成为唯一 IA：

- 城市按钮切换背景并更新 `#room-location`；切换公告明确“研究议题和方法视角保持不变”。
- 3 个 agenda topic 与 8 个 perspective choice 更新当前 voice，portrait / claim / rebuttal / facts 同步替换。
- `检验证据` 和 `查看反证与缺口` 打开 dossier；`研究底稿` 打开全量 evidence。
- dossier 的 `evidence / models / about` tabs、原始 JSON 下载、场景来源/许可 lightbox、返回焦点。
- `prefers-reduced-motion` 关闭 GSAP 转场；portrait 和场景切换使用 token，避免快速点击后的旧动画覆盖新状态。

## 2. 连续报告的章节/注入 mapping

下表是恢复顺序和现有 renderer 的稳定契约。实现时可以换 CSS、容器或章节节奏，但不要删除 anchor、marker、输入来源或交互目标。

| 章节/稳定 ID | 原版 marker 或元素 | 输入 | 现有 renderer / 输出 | 必须保留的契约 |
|---|---|---|---|---|
| 0 身份 + 证据 | `section-evidence`、`INJECT_EVIDENCE_STRIP`、`INJECT_DATA_GAP_BANNER`、`INJECT_STYLE_CHIP` | `raw`、`panel`、`synthesis.data_gaps`、`synthesis.detected_style`、当前 agent review | `render_evidence`、`_render_data_gap_banner`、`_render_style_chip` | `coverage` 不是正确率；采集时间与行情/财报日期分开；缺口和低可信度显式显示 |
| 1 核心 | `section-core`、`INJECT_HERO_CHART`、`{{CORE_CONCLUSION}}` 等 | `synthesis.dashboard`、`synthesis.overall_score`、`dimensions.fundamental_score_valid`、`0_basic`、`2_kline` | `render_hero_chart` + assemble replacements | score 只有完整性通过才显示；`—` 不补 0；趋势图仅历史观察，非预测 |
| 2 深度扫描 | `section-scan`、六个 `INJECT_DIM_*` | `dimensions.json#/dimensions/<id>` + `raw.dimensions/<id>` | `render_dim_category` → `render_dim_card` → `DIM_VIZ_RENDERERS` | 六类 `<details class="research-category">`；每卡可看原始数据、来源、fallback、pass/fail、status |
| 3 机构模型 | `section-modeling`、`INJECT_INSTITUTIONAL_MODELING` | `raw.dimensions.20/21/22.data` | `_render_institutional_section`（现仅拼 7 个 block） | 20/21/22 的所有产物需可定位；缺失显示明确状态，不用空白掩盖 |
| 3a 分业务 | `INJECT_SEGMENTAL` | `.cache/<ticker>/segmental_model.json`、`segmental_validation.json`、`synthesis.json` | `_render_segmental_block(ticker)` | 可选不等于删除；存在时保留对账、三情景、历史序列和 DCF cross-check |
| 4 分歧 | `section-clash`、`INJECT_DEBATE_ROUNDS`、`INJECT_PANEL_INSIGHTS`、`INJECT_SCHOOL_SCORES` | `synthesis.debate`、`great_divide`、`panel` | `render_debate_rounds`、`render_panel_insights`、`render_school_scores` | bull/bear 的每个说法需能回溯到输入；共同输入不能伪装成独立投票 |
| 5 评委 | `section-jury`、`INJECT_JURY_SEATS` | `panel.investors`、`signal_distribution`、`panel_consensus` | `render_jury_seat` | `data-target="msg-<safe investor_id>"` 是聊天跳转契约；skip 的 score 显示 `—` |
| 6 研究笔记 | `section-chat`、`INJECT_CHAT_MESSAGES` | `panel.investors`，排序后按 signal/confidence | `render_chat_message` + template JS | 组别 A–I、`data-group`、`aria-pressed`、展开/收起、bull/bear 定位和键盘可用 |
| 6a 公开持仓/友好层 | `INJECT_FRIENDLY_LAYER`、`INJECT_FUND_MANAGERS` | `synthesis.friendly`、`synthesis.fund_managers` 或 `raw.fund_managers` | `render_friendly_layer`、`render_fund_managers` | 只有当前审阅与假设充分才展示情景；lite 基金行不能伪造 5Y 收益/排名 |
| 7 风险 | `section-risks`、`INJECT_RISKS` | `synthesis.risks`，最好附维度/证据 ID | `render_risks` | 风险具体到数字/事件；无输入时留缺口，不写“无风险” |
| 8 区间 | `section-zones`、四个 `ZONE_*` | 当前 agent narrative 的 `buy_zones` | assemble replacements | 每个价位都需 rationale + 输入；分数无效时一起降级，不能保留机械交易指令 |
| 工具/分享 | `#open-share`、`#share-overlay`、`#report-qr-canvas`、`#print-report`、`#share-card`、`#war-report` | 同一份已审阅的 replacements + panel/divide/trap | native dialog、print、`render_share_card.py`、`render_war_report.py` | 两个屏外 surface 的 ID/尺寸不可改；local-only，不上传、不调用远程 QR |

`assemble_report.py:463–668` 已定义上述注入顺序；`assemble_report.py:673–687` 的 Council 分支是造成主入口丢功能的替换点。连续 renderer 应复用已经组装完成的正文和同一份数据快照，而不是重新实现第二套数据逻辑。

## 3. 19 张深度卡：输入字段、renderer 和分组

公共卡 contract：

- 分数来自 `dimensions.json#/dimensions/<id>.score`，状态来自 `score_status`；`data_backed` 才是量化输入触发的分数，`heuristic`、缺失、过期、不适用不得伪装成测量值。
- 原始维度至少保留 `{data, source, fallback}`，并保留 `_pipeline`、`stale`、`error`、`applicable` 等质量元数据。
- `render_dim_card` 在状态可用时调用专用 renderer，否则输出 KPI grid；所有卡都有来源 badge、pass/fail 和可折叠 raw JSON。
- 19 卡的页面分组由 `DIM_META.cat` / `CAT_GROUPS` 固定为：财务 `[1,10,14]`、行情 `[2,12,16]`、行业 `[4,5,7,8,9]`、公司 `[11,15,6]`、环境 `[3,13]`、安全 `[17,18,19]`。

| ID / 页面字段 | `DIM_META` KPI（卡头输入） | 专用 renderer | 图表/展开所用字段（除 KPI 外） |
|---|---|---|---|
| 01 `1_financials` 财报扎实度 | `roe`, `net_margin`, `revenue_growth`, `fcf` | `_viz_financials` | `revenue_history`, `roe_history`, `net_profit_history`, `financial_years`；可选 `dividend_years/amounts/yields`、`financial_health.current_ratio/debt_ratio/fcf_margin/roic` |
| 02 `2_kline` K 线技术面 | `stage`, `ma_align`, `macd`, `rsi` | `_viz_kline`；核心图另走 `render_hero_chart` | `candles_60d`, `ma20_60d`, `ma60_60d`, `close_60d`；`indicators.kdj_j/williams_r/obv_trend_up`；`kline_stats.beta/volatility/max_drawdown/ytd_return` |
| 03 `3_macro` 宏观环境 | `rate_cycle`, `fx_trend`, `geo_risk`, `commodity` | `_viz_macro` | 四项文本状态；缺失保持“未记录/不适用”，不填中性宏观结论 |
| 04 `4_peers` 同行对比 | `rank`, `gross_margin_vs`, `roe_vs`, `growth_vs` | `_viz_peers` | `peer_table`、`peer_comparison`、`global_peer_comparison`；空的 self/peer 值要跳过，不绘制 0 对比条 |
| 05 `5_chain` 上下游产业链 | `upstream`, `downstream`, `client_concentration`, `supplier_concentration` | `_viz_chain` | `main_business_breakdown`；输出供应链流向和主营构成 donut |
| 06 `6_research` 研报观点 | `coverage`, `rating`, `target_avg`, `upside` | `_viz_research` | `rating` 分布解析、`price`；目标价/涨跌空间缺失时留 `—`，不能展示 `None` |
| 07 `7_industry` 行业景气 | `growth`, `tam`, `penetration`, `lifecycle` | `_viz_industry` | 增速 gauge + TAM/渗透率/生命周期 |
| 08 `8_materials` 原材料 | `core_material`, `price_trend`, `cost_share`, `import_dep` | `_viz_materials` | `price_history_12m` sparkline |
| 09 `9_futures` 期货关联 | `linked_contract`, `contract_trend` | `_viz_futures` | 关联品种与走势状态；不把关联关系当价格预测 |
| 10 `10_valuation` 估值多维 | `pe`, `pe_quantile`, `industry_pe`, `dcf` | `_viz_valuation` | `pe_history`、`dcf_sensitivity.{waccs,growths,values,current_price}`；另有 dim 20 完整 DCF，二者要标清“卡内摘要/机构模型” |
| 11 `11_governance` 管理层与治理 | `pledge`, `insider`, `related_tx`, `violations` | `_viz_governance` | `insider_trades_1y`、`violation_hits`、`qualitative_search`；空检索不等于“未发现问题” |
| 12 `12_capital_flow` 资金面 | `main_20d`, `margin_trend`, `holders_trend`, `main_5d` | `_viz_capital_flow` | `main_fund_flow_20d`、`block_trades_recent`、`holder_count_history`、`institutional_history`、`unlock_schedule` |
| 13 `13_policy` 政策与监管 | `policy_dir`, `subsidy`, `monitoring`, `anti_trust` | `_viz_policy` | 四项政策/监管文本和缺失状态 |
| 14 `14_moat` 护城河 | `intangible`, `switching`, `network`, `scale` | `_viz_moat` | `efficient_scale`、四/五轴文本；`scores` 还供竞争分析读取，不能只保留最终总分 |
| 15 `15_events` 事件驱动 | `recent_news`, `catalyst`, `earnings_preview`, `warnings` | `_viz_events` | 优先 `event_timeline`，否则回退四项字段；日期/来源需跟采集时间分开 |
| 16 `16_lhb` 龙虎榜 | `lhb_30d`, `youzi_matched`, `inst_net`, `youzi_net` | `_viz_lhb` | `lhb_count_30d`、`inst_vs_youzi.institutional_net/youzi_net`、`sector_lhb_top50`；自身无记录时可显示板块替代，但要标明替代 |
| 17 `17_sentiment` 舆情与大 V | `xueqiu_heat`, `guba_volume`, `big_v_mentions`, `positive_pct` | `_viz_sentiment` | `thermometer_value`、`sentiment_label` 可作为补充；热度不是概率 |
| 18 `18_trap` 风险检测 | `signals_hit`, `trap_level`, `high_risk_kw`, `evidence_count` | `_viz_trap` | `recommendation`、`trap_evidence`、命中详情；状态缺失时必须保留“未评估” |
| 19 `19_contests` 实盘比赛持仓 | `xq_cubes`, `high_return_cubes`, `tgb_mentions`, `ths_simu` | `_viz_contests` | `xq_cubes_list`、`tgb_list`、`ths_list`；链接需安全白名单和明确外链语义 |

这些 renderer 已在 `scripts/lib/report/dim_viz.py:52–788` 注册为 `DIM_VIZ_RENDERERS`。不要仅恢复卡片标题/KPI；专用 SVG、原始数据、来源和缺失态才是原功能的一部分。

## 4. 机构级三维度：所有产物的输入和可见性

### 4.1 dim 20 · `20_valuation_models`

来源是 `compute_dim_20(features, raw)`，结构为 `data.dcf`、`data.comps`、`data.three_statement`、`data.lbo`、`data.summary`。当前 `_render_institutional_section` 只拼 DCF/Comps/LBO 三个 renderer；三表有计算结果但没有展示函数。

| 产物 | 输入字段（最小完整集） | 现有 renderer / 当前问题 | 恢复要求 |
|---|---|---|---|
| DCF | `intrinsic_per_share`、`current_price`、`safety_margin_pct`、`verdict`；`wacc_breakdown.wacc/cost_of_equity/after_tax_kd`；`tv_pct_of_ev`；`sensitivity_table.wacc_axis/g_axis/values_per_share`；`methodology_log`；保留 `base_fcf_yi/projected_fcf_yi/pv_explicit_yi/terminal_value_yi/tv_pv_yi/enterprise_value_yi/net_debt_yi/equity_value_yi/assumptions` | `_render_dcf_block`；有 DCF 缺失/不可收敛状态和 5×5 热力图 | 显示假设、终值依赖、净债桥提示和中心格；默认假设与审阅后的 adjusted DCF 若同时存在必须并列，不覆盖原结果 |
| Comps | `peer_stats`（PE/PB/PS/EV EBITDA/ROE/net margin 等统计）、`target_percentile`、`implied_price`、`valuation_verdict`、`current_price`、`peers/peer_count`、`methodology_log` | `_render_comps_block`；显示六项统计和目标分位，缺少同行会明确无样本 | 保留同行池、剔除自身的口径、样本数、分位和隐含价；不要把相对估值写成内在价值 |
| 三表 | `years`；`income_statement.revenue/cogs/gross_profit/opex/ebit/tax/net_income`；`cash_flow.net_income/dep_amort/nwc_change/ocf/capex/fcf`；`balance_sheet.equity_rollforward`；`assumptions`、`growth_path`、`methodology_log` | `project_three_stmt` 已返回上述结构，但 `_render_institutional_section` 没有 block | 增加三表专用 renderer 或等价 UI：同一列对齐年度、显示假设和方法日志；不可只把三表塞入“原始记录”折叠框 |
| Quick LBO | `entry_ebitda_yi/entry_multiple/entry_ev_yi/entry_debt_yi/entry_equity_yi/leverage_turns`；`ebitda_path/debt_schedule`；`exit_ebitda_yi/exit_multiple/exit_ev_yi/exit_equity_yi`；`moic/irr_pct/pass_pe_test/verdict/methodology_log` | `_render_lbo_block`；展示入场/杠杆/IRR/MOIC、EBITDA 与偿债 sparkline，未展示全部退出字段 | 保留 5 年路径、债务偿还、阈值和假设；LBO 是交叉验证，不是保证收益或实盘交易指令 |
| 交叉摘要 | `dcf_intrinsic/dcf_safety_margin_pct/dcf_verdict/lbo_irr_pct/lbo_verdict/comps_verdict` | `summary` 本身不单独出现在页面 | 在 dim 20 章节头或三角验证条展示，并链接到 DCF/Comps/LBO 原位 |

实现依赖：`lib/fin_models.py` 的 `compute_dcf`、`build_comps_table`、`project_three_stmt`、`quick_lbo`；计算函数每个都返回 `methodology_log`，应作为“查看推导”的输入而不是丢弃。当前 DCF/Comps block 内部有 `¥`，assemble 会按市场做收尾替换；新 renderer 应直接使用统一的 currency contract，避免 HK/US 再次显示人民币。

### 4.2 dim 21 · `21_research_workflow`

来源是 `compute_dim_21`，包含七个研究产品。现有页面只显示 `initiating_coverage` 的部分字段和 `catalyst_calendar`；其余数据虽写入 raw，却不可见。

| 研究产品 | 输入字段 | 现有状态 | 可执行恢复 mapping |
|---|---|---|---|
| Initiating Coverage | `headline.rating/target_price/current_price/upside_pct/report_date`；`executive_summary`；`investment_thesis[]` 的 `pillar/evidence/weight`；`key_risks[]` 的 `risk/severity/detail`；另外保留 `company`、`valuation_bridge`、`financial_snapshot`、`coverage_universe_pos`、`methodology_log` | `_render_initiating_coverage` 只渲染 headline、summary、thesis、risk | 恢复估值桥、财务快照和覆盖定位；与 dim 20 的目标价来源建立链接 |
| Earnings Analysis | `headline`；`latest.revenue_yi/net_profit_yi/revenue_yoy_pct/net_profit_yoy_pct`；`consensus.rev/ni`；`beat_miss.revenue_vs_consensus_pct/revenue_tag/net_profit_vs_consensus_pct/net_profit_tag`；`thesis_impact`、`methodology_log` | 无 renderer | 用“实际 vs 共识”表/小图和 thesis impact；若共识是默认代理要显示口径 |
| Catalyst Calendar | `events[].date/event/category/impact/expectation`；`high_impact_count`、past/forward count、`next_30d`、`methodology_log` | `_render_catalyst_calendar` 显示最多 12 条 date/event/expectation/impact | 保留 past/forward/risk/earnings 分类和过滤/展开；日期必须是真实事件日期或明确预计日期 |
| Thesis Tracker | `pillars[].pillar/original_target/current_status/trend/verdict`；`pillars_passed/total`、`thesis_intact_pct`、`conviction`、`recommended_action`、`methodology_log` | 无 renderer | 恢复逐条 thesis scorecard；不能把完好率变成上涨概率 |
| Morning Note | `date`、`top_call`、`recommendation`、`bullets[]`、`methodology_log` | 无 renderer | 作为短晨报入口/可折叠摘要；与完整报告采集时点并列显示 |
| Idea Screens | `value/growth/quality/gulp` 各自 `checks[].criterion/pass`、`passed/total`、`pass_rate_pct`、`fits_screen`、`verdict`、`methodology_log` | 无 renderer | 以筛选条件列表展示命中/未命中；不把 `fits_screen` 直接变成买入建议 |
| Sector Overview | `industry`；`market_size.tam/growth/lifecycle`；`value_chain.upstream/company/downstream`；`competitive_map`、`peer_count`、`methodology_log` | 无 renderer | 恢复行业/链条/竞争地图；同 4/5/7 维重复时注明“工作流汇总”而非丢弃来源 |
| dim 21 summary | `rec_rating/target_price/upside_pct/thesis_intact_pct/next_high_impact_event/earnings_headline/screens_passed` | 未单独渲染 | 作为章节导航摘要，并链接到七个产品 |

### 4.3 dim 22 · `22_deep_methods`

来源是 `compute_dim_22`，包含 IC、单位经济、价值创造、尽调、竞争和组合再平衡六类方法。现有页面只显示 IC memo 与 competitive analysis。

| 方法 | 输入字段 | 现有 renderer / 恢复要求 |
|---|---|---|
| IC Memo | `sections.I_exec_summary.headline/recommendation/top_3_risks`；`II_company_overview`；`III_industry_market`；`IV_financial_analysis`；`V_valuation`；`VI_risks_mitigants[]` 的 `risk/severity/detail/mitigant`；`VII_returns_scenarios[]` 的 `scenario/price_target/return_pct/probability_pct/assumptions`；`VIII_recommendation`；`methodology_log` | `_render_ic_memo` 目前只显示 headline、三情景、前 5 风险。恢复八章节的导航/折叠，尤其公司/行业/财务/估值和 recommendation，不要以三张情景卡冒充完整 memo。 |
| Unit Economics | recurring：`business_type`、`metrics.arpu_yi/gross_margin_pct/churn_rate_pct/ltv_yi/cac_yi/ltv_cac_ratio/payback_months`、`healthy`、`verdict`；non-recurring：`revenue_yi/gross_margin_pct/opex_pct_of_rev/net_margin_pct/waterfall[]` | 无 renderer。按业务类型显示 ARR/LTV/CAC 或毛利→费用→净利 waterfall；不要给非 recurring 公司硬套 SaaS 指标。 |
| Value Creation Plan | `current_ebitda_yi/current_margin_pct`；`levers[]` 的 `category/lever/current_state/target_state/ebitda_impact_yi/timeline/confidence`；`total_uplift_yi/target_ebitda_yi/target_margin_pct`；`hundred_day_priorities[]`；`methodology_log` | 无 renderer。恢复 EBITDA bridge、杠杆时间线和置信度；不是对当前股价的目标价。 |
| DD Checklist | `workstreams[]` 的 `workstream/items[].item/status`；`total_items/items_auto_verified/completion_pct/manual_review_required`；`methodology_log` | 无 renderer。恢复按工作流的清单和人工复核数量；`⚪ 需人工核查` 不能被当作已完成。 |
| Competitive | `porter_five_forces` 五项各 `score/rationale`；`industry_attractiveness_pct`；`bcg_position.category/market_share_pct/market_growth_pct/strategic_action`；`methodology_log` | `_render_competitive_analysis` 显示 radar、BCG 和吸引力，但没有显示每项 rationale；恢复 rationale 与评分口径。 |
| Portfolio Rebalance | `portfolio_total_yuan`；`drift_rows[]` 的 `asset_class/target_pct/current_pct/drift_pct/dollar_drift_yuan/action`；`needs_rebalance`、`rebalance_trades`、`methodology_log` | 无 renderer。恢复配置漂移表；明确这是示例单仓/大类再平衡，不要隐藏样本持仓假设。 |
| dim 22 summary | `ic_recommendation/bcg_position/industry_attractiveness/dd_completion_pct/value_creation_uplift_yi/unit_economics_verdict` | 未单独渲染 | 作为章节导航摘要，不能替代明细。 |

## 5. 分业务模型（segmental）必须作为独立功能恢复

它不是 `20/21/22` 的普通字段，而是可选的 `.cache/<ticker>/segmental_model.json` 产物，由 `segmental_validation.json` 和 `synthesis.json` 辅助。`assemble_report.py:633–644` 只有文件存在时才调用 `_render_segmental_block(ticker)`；当前 Council 替换正文后该 block 不会出现在主入口。

### 输入 contract

- model 级：`name`、`core_thesis`（或 `thesis`）、`total_revenue_latest_yi`、`total_revenue_history_yi[]`、`currency`、`source_notes[]`。
- 每条 segment：`name`、`latest_revenue_yi`、`latest_share_pct`、`drivers[]`、`thesis_tag`、`bull_growth_3y_cagr`、`base_growth_3y_cagr`、`bear_growth_3y_cagr`、`agent_note`；可选 `gross_margin_pct`、`profit_share_pct`、`revenue_history_yi[]`、`history_periods[]`。
- validation：`passed`、`summary.reconciliation_gap_pct`、`summary.base_3y_total_growth_pct`、`warnings[]`。
- DCF cross-check 从 `synthesis.raw_data.dimensions.20_valuation_models.data.dcf.assumptions`（或兼容字段）读取 stage 1 增速。

### 输出 contract

`_render_segmental_block` 输出顺序为：对账/growth/DCF badges → core thesis → 当前营收 donut → 历史 + 三情景线图 → 每 segment × Bull/Base/Bear × Y+1/Y+2/Y+3 数字表 → segment driver/毛利/利润贡献/历史 sparkline 卡 → warnings/source。模型缺失时至少给一个“分业务模型尚未建立”状态块，以免用户把无内容误读成已完成。

## 6. 证据、状态、来源与数据安全契约

### 6.1 单一数据流

建议连续 renderer 接收一个共享的 `reportModel`（概念上，不是新增文件），其中保持：

```text
raw_data       = raw（原始输入、来源、日期、pipeline 状态）
dimensions     = dimensions.json（分数、权重、status、pass/fail、raw_pointer）
panel          = panel.json（角色输出、信号、coverage、投票分布）
synthesis      = synthesis.json（结论、分歧、风险、区间、dashboard）
agent_review   = 当前输入指纹对应的审阅状态
segmental      = 可选 segmental_model + validation
```

Council 不应继续自己只从 11 个维度重算一套事实。`council.py:24–29` 的 `_DIM_NAMES` 目前只覆盖 `0_basic、1、2、3、4、10、11、12、14、15、18`；`build_council` 只有质量/价格/风险三题。它可生成“方法视角”，但不能作为 22 维数据的 canonical renderer。所有“证据”链接应指向同一维度/模型记录。

### 6.2 状态矩阵

| 层 | 状态/字段 | UI 规则 |
|---|---|---|
| raw 质量 | `source`、`fallback`、`_pipeline.quality`、`_pipeline.fallback`、`stale`、`error`、`applicable` | 原样呈现来源和质量；web search/SDK/备用源不得洗成“官方” |
| evidence record | `available`、`derived`、`missing`、`stale`、`not_applicable` | 日期、来源、采集时间分行；缺失显示缺口，不用 0 |
| score | `score_status=data_backed`、`heuristic`、`missing` 等 | 只有 data-backed 且有限数字才显示分；heuristic 显示“定性启发式” |
| 综合分 | `dimensions.fundamental_score_valid` + `validate(raw)` | critical 缺失时隐藏综合分，并同步降级 verdict、battle plan、buy zones |
| panel | `signal`、`score`、`confidence`、`rule_coverage_pct`、`mandate` | 角色 score 与旧 confidence 分开；skip 不显示 0；coverage 不是置信概率 |
| 模型 | `methodology_log`、`assumptions`、`summary` | 模型数字必须可展开推导和假设；默认值要带默认口径 |

`render_evidence` 会从 `validate(raw)` 重算覆盖率、检查 active investors 的完整 rule coverage、读取 agent review freshness 和 raw fetched time。不要在 Council 中只显示一个“available” badge 就替代这四项边界。

### 6.3 Council dossier 的现有缺口

- evidence tab 默认合并 `data.council.evidence` 与 `raw.dimensions`；Council 自建 evidence 只有 11 个 ID，其他 ID 使用 `rawRecord`，无 facts，只能看到泛化 payload。
- models tab 使用 `/^2[012]_/.test(id)`，范围正确，但只是 `recordNode` 原始记录，不调用 DCF/Comps/LBO/IC renderer；因此“模型 tab 有内容”不能算模型功能已恢复。
- `view-evidence` 与 `test-counterpoint` 都传当前 voice 的同一组 `evidence_ids`；需要保留“当前论点证据”与“反证/缺口”两个 action context，而不是两个按钮最终完全相同。
- `rawRecord` 的标题依赖 `data.analysis.dimension_titles`；连续 renderer 应无论从哪个入口打开都提供 22 个标题、来源、日期和 raw pointer。

## 7. 交互契约清单

### 7.1 导航与逐层阅读

保留这些可深链 ID：`section-evidence`、`section-core`、`section-scan`、`section-modeling`、`section-clash`、`section-jury`、`section-chat`、`section-risks`、`section-zones`。原版顶部导航和 sticky TOC 依赖这些 ID；evidence strip 必须实际存在 `id="section-evidence"`，不要只有一个链接。

建议行为：

1. Council briefing 的“当前观点/换一种视角”只改变 voice 讲述；点击“检验证据”滚到或打开对应证据记录。
2. 章节摘要必须有“展开全部/打开明细”路径；不能把所有数字只藏在 dossier。
3. dimension card 的 raw details、机构 block 的 methodology/sensitivity、segmental 的 scenario table、chat message 的 full conclusion 都是第二层阅读，不是装饰性折叠。
4. 页面跳转应保留 URL hash；返回 dossier/lightbox 时恢复触发按钮焦点。

### 7.2 Panel / chat

- `render_jury_seat` 输出 `.seat`、`data-group`、`data-target="msg-<safe_asset_id(investor_id)>"`。
- `render_chat_message` 输出 `id="msg-<safe_asset_id(investor_id)>"`、`data-group`、`details.msg-details`。
- 点击席位：清除 group filter → 显示目标消息 → 展开 details → 滚动并短暂高亮；Enter/Space 键盘操作同样有效。
- A–I filter 要更新 `aria-pressed`，不以颜色作为唯一信号。
- `expand-all` / `collapse-all`、`scroll-bull` / `scroll-bear` 保留；没有 active 角色时显示状态而不是定位空节点。

### 7.3 Council / scene

- 城市切换只修改 `state.city`、背景和 provenance；不要修改 `topic`、raw input、score 或证据。
- topic 切换更新问题、voice、supporting facts、rebuttal 和 portrait；topic 数量不能硬编码为“03”，应从数据/章节配置读取或保持明确的 3 题契约。
- 场景 lightbox 必须显示 `credit`、原始作品链接、`license`/`license_url`；人物继续标注 AI 生成、非本人发言/背书。
- `download-inputs` 使用本地 Blob 下载 raw；若增加 dimensions/panel/synthesis 下载，文件名和快照应一致，且不得上传。

### 7.4 导出 / 分享 / 离线

- 保留 native `<dialog id="share-overlay">`、`#open-share`、`#print-report`、`#report-qr-canvas`、`#report-qr-url`。
- 二维码当前是本地状态占位，不能把 `location.href` 发送到 QR API；离线打开仍可读。
- PNG 入口继续绑定 `#share-card`（1080×1920）和 `#war-report`（1920×1080），不能改成 `display:none` 导致截图空白。
- `full-report-standalone.html` 必须在断网时打开，正文、图片、GSAP、图标和样式可用；任何外链只作为用户主动点击的来源/许可证链接。
- `research-appendix.html` 可保留作为审计兼容件，但不能让它成为用户必须寻找的功能入口。

## 8. 给实现者的最短执行顺序

1. **不要再用 `render_council(...)` 覆盖完整正文。** 将 Council 的 briefing/scene/portrait 接到完整章节之前或作为其第一章；继续使用同一份 `raw/panel/synthesis/dimensions`。
2. 先恢复 `section-evidence` → `section-core` → `section-scan`，确认 19 个 renderer 全部出现在正文；这一步先于加人物和场景。
3. 恢复 dim 20 的 DCF/Comps/LBO，并补三表；恢复 dim 21 的七个 workflow 产品；恢复 dim 22 的六个 deep methods 产品。现有七个 block 可直接复用，未渲染的产品必须有明确的 renderer/状态块。
4. 接入 segmental 独立产物；同时把“未建立”变成可见状态。将 DCF cross-check 与 segmental base 情景并排但不合并成一个数字。
5. 接回 clash → jury → chat → holdings/friendly → risks/zones，并维持 `seat → chat`、group filter 和反证证据链。
6. 最后恢复 share dialog、两个屏外导出 surface、print、standalone；再做 desktop/窄屏/断网验收。

## 9. 验收矩阵（功能而非审美）

### 数据完整 fixture

- 19 张卡：六组可折叠；每张显示有限 score、特化图/表、source、pass/fail、raw details。
- dim 20：DCF 5×5 敏感性、Comps 分位/隐含价、三表年度列、LBO IRR/MOIC/两条路径。
- dim 21：首次覆盖、业绩 vs 共识、催化剂日期分类、thesis tracker、morning note、四个 idea screen、sector overview。
- dim 22：IC 八章节、unit economics、VCP bridge、DD 清单、Porter rationale/BCG、rebalance 漂移表。
- segmental：对账 badge、donut、历史+三情景、数字预测表、每 segment driver 与 DCF cross-check。
- debate/panel/chat：多空回合、panel insights、school scores、席位跳转、A–I filter、全部展开/收起。
- 导出：dialog、print、`share-card`、`war-report` 结构均仍可找到并绑定当前数据。

### 缺失/过期 fixture

- `score_status` 为 missing/stale/not_applicable/heuristic 时不显示默认分，图表进入明确 empty state。
- DCF FCF/营收缺失时显示 DCF 不可用；Comps 同行不足时显示样本不足；三表无基期时显示错误状态；segmental 文件不存在时显示未建立。
- evidence 明确区分来源、观测日期、采集时间、fallback 和 agent review freshness。
- critical 输入缺失时综合 verdict、battle plan、buy zones 同步降级，不出现“值得重仓”之类残余强结论。

### 交互/打包

- Council 城市/主题/人物切换不改变数据快照；dossier tabs、source/license links、输入下载和返回焦点可用。
- TOC hash、主题记忆、类别折叠、chat filters、席位键盘跳转可用；`prefers-reduced-motion` 下无必要转场。
- `full-report-standalone.html` 断网打开无脚本错误、无缺图、无正文横向溢出；PNG 导出读取正确 surface。

## 10. 审计依据

- `skills/deep-analysis/assets/report-template.html:2762–3170, 3180–3405`：原版章节、marker、share surfaces、TOC/theme/chat/jury JS。
- `skills/deep-analysis/assets/report-council.html:1–31`、`report-council.js:1–121`：当前 Council shell、3 题/8 视角/4 场景/dossier 交互。
- `skills/deep-analysis/scripts/assemble_report.py:463–668, 673–687`：注入顺序、segmental、Council 替换主入口与 appendix 行为。
- `skills/deep-analysis/scripts/lib/report/evidence.py:21–111`：coverage、agent freshness、历史价格图和质量边界。
- `skills/deep-analysis/scripts/lib/report/dim_viz.py:52–788`、`assemble_report.py:99–193`：19 张卡的字段、分组和专用 renderer。
- `skills/deep-analysis/scripts/lib/report/institutional.py:78–467, 689–707`：现有 DCF/Comps/LBO/Initiating/IC/Catalyst/Competitive block 与 dim 20/21/22 总入口。
- `skills/deep-analysis/scripts/lib/report/segmental.py:47–557`：分业务模型输入、图表、情景表、校验和 DCF cross-check。
- `skills/deep-analysis/scripts/lib/report/council.py:14–345`：8 个方法标签、3 个 topic、当前 11 个 evidence ID 的边界。
- `skills/deep-analysis/assets/data-contracts.md:1–225`、`references/task1-data-collection.md:1–220`、`references/task1.5-institutional-modeling.md`：raw/dimensions/panel/synthesis 和机构模型数据结构。
