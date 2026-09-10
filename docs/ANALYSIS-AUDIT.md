# J Trader · 分析架构与置信度审计

- 审计日期：2026-09-09
- 基线：`d1a4439`；工作分支：`codex/ajay-report-refactor`
- 范围：采集管道、数据完整性、特征与规则评分、模拟流派共识、Agent 审阅绑定、美股补数。
- 方法：静态阅读 + 合成样本离线测试；没有抓取真实股票、连接交易网关或验证投资收益。
- 本文记录分析引擎修复与残留风险；UI 与品牌归属改动另有文档。

## 1. 结论与判断置信度

**分层方向合理，事实到结论的契约仍不够严格；当前输出是可解释的研究启发式，不是经过校准的预测概率。**

| 判断 | 结论 | 依据强度 |
|---|---|---|
| 工程分层 | collect → score → synthesize → report 的方向合理；adapter、快照缓存、可单测纯函数值得保留 | 高：直接核对入口与调用链 |
| 数据完整性 | 已有字段检查、恢复任务与 TTL；但字段存在不等于来源可靠、时点可用或市场适用 | 高：代码与离线边界测试 |
| 规则评分 | 多处缺值仍变成 0 / False / 中性默认分；评分与事实覆盖尚未彻底分离 | 高：空数据样本实测 |
| 模拟流派 | 可帮助列举不同判断框架；多个角色共享同一输入与规则/模型，并非独立证据 | 高：共享 `extract_features` 与规则链 |
| 市场预测效果 | 尚未建立可声明的胜率、收益概率、统计置信区间 | 未验证：本次没有时点回测或样本外校准 |
| 真实数据源稳定性 | 本轮没有测量在线可用率、延迟和跨源一致性 | 未验证：离线审计边界 |

### 值得保留的设计

1. `lib/pipeline/run.py:24-65`：采集和打分分离，避免重复 stage1。
2. `lib/pipeline/collect.py:222-245`：拒绝 missing/error/fallback 缓存；按维度 TTL 验证抓取时刻。
3. `lib/pipeline/validators.py:24-98`：统一空值；保留数值 0，检测非有限数与全空结构。
4. `lib/agent_review.py:56-83`：Agent 输出与当前 raw 输入 hash 绑定；deep 强制指纹，拒用过期分析。
5. `run_real_test.py:784-817`：stage2 验证 Agent 结构与 deep 审阅条件。
6. `lib/data_integrity.py:281-307`：根据最终原始数据重新生成恢复任务，避免旧缺口残留。

## 2. 本轮已修复的问题

优先级含义：P1 = 可能改变研究结论或造成显著误导；P2 = 影响可信展示/数据质量。下列行号以本工作树为准。

| 优先级 | 缺陷与复现 | 修复位置 | 验证 |
|---|---|---|---|
| P1 | 全部规则因缺值跳过时，旧 confidence 仍为 80；单条规则通过即可 92，数值被规则数量/极端度抬高 | `lib/investor_evaluator.py:229-277` | 权重 3+1：全缺=0%，只可执行权3=75%，全可执行=100%；历史持仓虚拟权重不提升覆盖 |
| P1 | 空心检测只抓 `score==0`；无规则证据的默认中性 score=50 被认定有效；零活跃角色也被认定有效 | `lib/pipeline/score_fns.py:624-659` | 默认中性空心与空集合现在 `consensus_valid=false` |
| P1 | panel 先排除 short mandate，但 synthesis 风格二次加权把其重新计入 long book | `lib/stock_style.py:244-248` | 1 个多头 bullish + 1 个空头 bearish：long 共识保留100而非误降50 |
| P1 | `_avg` / `_min` 删除真实 0 年份，ROE `[0,10,20]` 误得均值15、最低10 | `lib/stock_features.py:58-72` | 均值10、最低0；同时排除 None/NaN/占位值 |
| P1 | 美股补数只要触碰维度就把其所有缺口标 resolved，并无条件清除 critical_missing | `us_backfill.py:248-252` | 仅补 ROE 时，未补价格等缺口继续 pending/critical；raw 中完整性同步更新 |
| P1 | 在无 AJAY_DEPTH 的新进程重建审阅上下文，会把已标 deep 的流程悄悄改成 medium | `lib/agent_review.py:30-47` | 继承既有 deep；只有显式 AJAY_DEPTH 才切换档位 |
| P2 | integrity 接受 NaN/Inf/仅含空值的嵌套对象，还把字符串 "0" 当缺失 | `lib/data_integrity.py:85-97` | 递归空/非有限值为缺口；数值或字符串0均为有效观测 |

### 新字段契约

`dimensions.json`：

- `dimensions[key].score_status`：`missing / not_applicable / stale / heuristic / data_backed`。`data_backed` 仅表示该公式引用的字段存在，`heuristic` 标明固定分支。
- `fundamental_score_valid`：最低输入充分性检查（canonical integrity 无关键缺口、关键字段覆盖≥60%、财务与K线可计算），不是预测效果验证。
- `fundamental_score_status`：`heuristic` 或 `insufficient_evidence`。旧数值仍在，所有下游应先读取此状态。
- 全空样本现在 `fundamental_score_valid=false`，各维度均 `score_status=missing`；UI 应隐藏其56.3等旧数值。

`evaluate()` 及 `panel.investors[]`：

- `confidence_kind = "rule_coverage"`
- `rule_weight_evaluated`：实际可执行的定量规则权重（不含持仓加分）
- `rule_weight_possible`：配置的定量规则总权重
- `rule_coverage_pct = 100 × evaluated / possible`（分母0时为0）
- `confidence`：兼容旧接口的覆盖度数值别名；不再表示正确概率

`panel`：

- `rule_coverage_pct`：适用 long persona 覆盖率的算术平均；旧数据没有新字段时为 `null`
- `confidence_kind = "rule_coverage"`
- `consensus_kind = "simulated_persona_agreement"`
- `independent_evidence = false`

**边界：可执行规则覆盖仍不等于原始证据覆盖。** 上游特征若用默认0填空，规则仍会正常执行。该指标必须与原始数据覆盖、来源、时点一起展示，不应用“可信度100%”这样的表述。旧缓存中的 confidence 是旧启发式，应显示“旧格式／待重算”，不迁移猜测。

## 3. 残留问题：未因 UI 重构而宣称解决

### P1 · 默认评分仍能制造事实与分数

位置：`lib/pipeline/score_fns.py:102-129,205-219,231-239,296-328`；`lib/stock_features.py:14-27,131-169`。

离线输入只有 `{"ticker":"TEST","market":"U","dimensions":{}}`，本轮小修后仍得到：

- 原始关键字段覆盖：**0%**
- 基本面：**56.3/100**
- 行业：**7/10 / 行业处于成长期**
- 风险检测：**9/10 / 未发现推广痕迹**
- 可执行规则覆盖：**81.5%**（大量默认0照常进入规则）

这证明“函数正常返回/评分可计算”不代表有证据。UI 应将无证据项显示为“— / 未评估”，而不是安全、低风险、成长或负债健康。引擎下一步需要字段级 provenance 与 `observed / derived / missing / not_applicable / stale`，明确未观测数据不参加打分。本轮新增 `score_status` 与 `fundamental_score_valid` 隔离无证据数值，保留旧数值 schema 是兼容选择，并不表示接受其分析有效性。

### P1 · 综合分重复使用相同证据，且存在多套公式

位置：`lib/pipeline/score_fns.py:492-532,1091-1134`；`lib/stock_style.py:241-264`。

- 基本面与 persona 都由同一 raw_data 生成，最终 60% 基本面 + 40% 共识是启发式融合，不是独立证据确认。
- `generate_panel` 用连续分+离散票+极化系数1.3；synthesis 又通过 `apply_style_weights` 换成只计信号的加权公式。报告中的 panel 分和最终合成分可能不是同一概念。
- `per_investor_override` 改单人 signal/score 后，没有统一重新计算 panel 的 vote_distribution / school_scores / hollow 元数据（`score_fns.py:1065-1079`）。图表与角色卡片存在不一致风险。

建议：抽取唯一 `aggregate_panel()`，输出明确版本、输入 hash、权重及明细；角色覆盖后重算全部派生结果。若要表达预测概率，需要另外定义预测目标/期限、时点样本、样本外评估与校准。

### P1 · 美股“精确历史分位”的时间与口径契约不足

位置：`us_backfill.py:67-78,103-150`。

- TTM EPS/BVPS 的可用时间用报表期末 `end`，不是披露 `filed` 时点；把后来已知信息回放到此前价格，形成前视风险。
- 多次申报按迭代最后一条覆盖，没有披露版本/重述的 point-in-time 策略。
- Q4 通过同一自然年的前三个季度相减，不能直接覆盖非12月财年；四条相邻记录也没有确认季度连续性。
- BVPS 分母使用期间摊薄加权股数，和期末普通股数不是同一口径。
- 空估值序列会出现分母0、min/max 空序列；亏损/负权益并非单纯网络缺失。
- 月线时间标签与价格实际时点需对齐验证；当前 `.as_unit("s")` 只统一时间单位，不证明金融时点正确。

本轮只修复补数后的缺口复验，没有执行或宣称验证该采集/估值算法。后续应拆纯函数，基于 `period_end / filed_at / accession / currency / share_basis` 做合成单测，再验证真实申报样本。

### P1 · Agent 审阅状态是输入绑定，不是事实认证

位置：`lib/agent_review.py:56-83`、`lib/agent_analysis_validator.py:75-104`、`lib/pipeline/score.py:101-111`。

- 正确的 input hash 证明声明对应当前输入，不证明引用真实、推断合理或66个角色独立。
- 对缺少定性内容的部分校验只 warning；单纯 `agent_reviewed=true` 不应显示“全部事实已核实”。
- pipeline scoring 在 stage2 的正式 schema 校验之前，已调用 generate_synthesis 合并 Agent 数据，坏结构可能提前污染缓存/导致失败。
- dimensions/panel/synthesis 尚未共用不可变 run manifest；raw hash 与 Agent 绑定并不自动保证所有衍生文件同批。

建议：验证先于任何合并；统一 run_id/input_hash；分别记录 reviewed_inputs、cited_evidence、unverified_claims。

### P2 · 适用性、来源时效与静态人物资料

- `lib/pipeline/schema.py:16-27` 没有独立 `not_applicable` / `stale` 状态；`fetch_lhb.py:60-63` 的海外返回仅是 `_note`。市场不适用不能等同采集失败或中性5分。
- `lib/data_integrity.py:119-158` 的 coverage 是固定关键字段存在率；财务健康度只要一个子值存在就通过，不验证可信来源、报告期或字段一致性；enrichment 的说明文字也可能算“有内容”。
- `lib/pipeline/run.py:46-54` 的顶层 fetched_at 是本次组合快照创建时刻，已复用的每维数据不一定同样新；报告应区分快照生成时刻与证据观测/披露时刻。
- `lib/investor_knowledge.py:125-142` 把“曾经持有”与 `held` 静态文字混用，缺少来源 URL、有效期与更新时间；其会加权或强制 bullish（`investor_evaluator.py:241-265`）。本轮没有核验任何人物当前持仓。
- `us_backfill.py:31` 的 PEERS 固定为社交/广告平台，换行业若不手工修改会构造不适当的比较组；应按行业配置并在报告显示 peer selection reason。

## 4. 报告表达契约

建议顶部并列四类信息，互不替代：

1. **数据覆盖**：注明检查分母、缺失字段、市场适用范围；低覆盖本身就警示，不依赖分数是否好看。
2. **可执行规则覆盖**：注明仅代表代码判定所需输入可执行，含旧特征默认值影响，非胜率。
3. **Agent 输入审阅**：当前输入匹配 / 过期 / 缺失 / 旧格式；不称独立事实认证。
4. **证据时点**：报告生成、抓取、原始观测/报告期/披露日期分开；未知为“—”。

固定说明：**“流派观点为 J Trader 的方法论模拟，不代表相关人士实际意见；共享输入，不是独立投票；评分不是收益概率。”**

## 5. 验证记录

运行时：`/opt/anaconda3/bin/python`，Python 3.12.4；沿用已有依赖，没有安装全量包。

- 基线针对性回归：**61 passed**。
- 新测试最初17项对旧代码：**13 failed / 4 passed**；失败体现本文修复的实际行为。
- 新增 deep 上下文与 US 补数落盘测试后，另加入评分有效性/状态2项，共 **21** 项新测试。
- 最终扩大离线回归：**106 passed**，包含新21项及85项既有回归；用 socket connect/connect_ex 拦截出网。
- 环境警告：现有 numexpr / bottleneck 版本偏旧、protobuf 弃用提醒；没有影响该次测试通过。
- 未做：真实数据采集、OpenD 交易连接、收益回测、全市场数据质量统计。本测试数不代表项目全部测试数。

复现（从 `skills/deep-analysis/scripts`）：

```bash
/opt/anaconda3/bin/python -m pytest -q \
  tests/test_analysis_confidence_contract.py \
  tests/test_agent_review_freshness.py \
  tests/test_issue100_101_review_integrity.py \
  tests/test_pr88_missing_data_truthfulness.py \
  tests/test_short_mandate_consensus.py \
  tests/test_v3_8_1_audit_fixes.py \
  tests/test_audit_regressions.py \
  tests/test_v2_11_scoring_calibration.py \
  tests/test_v3_9_2_flow_bugfixes.py \
  tests/test_pr75_pipeline_market_metadata.py
```

## 6. 建议实施顺序

1. **先隔离虚假确定性**：报告显示证据缺口和模拟身份；已完成本轮小修；保留原始数值只用于兼容，不把它当概率。
2. **再修分析契约**：字段级事实/缺失/不适用/陈旧；消除默认分参与真实评分；统一 panel 合成；全产物输入指纹。
3. **再重构美股补数**：纯函数 + 披露时点 + 财年/股票数口径 + 同业选择 + 缺失样本测试。
4. **最后谈预测可靠性**：按明确期限和任务做 point-in-time、样本外评估，报告样本量与不确定性，而非给启发式分数贴概率标签。

## 7. 收尾补充：spawn 轻量导入修复

全量回归两次各出现一个进程启动超时：算术 fast worker、同组序列 worker 在5秒内尚未完成 bootstrap。单独复跑曾通过，随后 import-time 追踪确认既有 `lib/__init__.py → data_sources → akshare/pandas` 在纯 scheduler 导入时提前启动：一次测得 `process_runner` 总导入3.756秒，其中 `data_sources` 3.561秒。该链不包含新增 report/evidence 模块；evidence 单独新增依赖仅约1.6毫秒。

最小修复：`lib/__init__.py` 用模块级 `__getattr__` 按首次明确访问导入 `data_sources`，并缓存同一模块对象；`__all__` 保持原样，`__dir__` 继续显示该公开名称，显式属性、from-import、直接子模块导入和星号导入都保持可用。没有更改进程超时阈值或调度器。

新增 `tests/test_ajay_lazy_library_import.py` 5项独立新进程测试：纯调度器导入拦截任何 akshare/pandas/yfinance/baostock 加载；dir/all 可发现但不触发导入；旧接口身份与函数可达；星号导入；未知属性和普通子模块语义。对旧代码先复现 **3 failed / 2 passed**。修复后运行该5项、process_runner 原2项和旧API恢复回归12项，共 **19 passed**。这证明导入链已被隔离；未重跑或宣称此时全量测试已全通过。

## 新主报告追加验证（2026-09-09）

- 新增纯函数council.py：三议题×八模拟方法，严格从raw_data构建观点/反证/来源事实。保留零/负数，拒绝NaN/Inf，缺失治理不宣称清洁，60日价格变化只是历史描述。46项证据模型测试通过。
- 新UI不直接采纳旧persona随机话语或名人权威评分，全部raw维度与规则状态在底稿保留。8项新渲染/来源/注入/生产入口测试通过。
- lib包数据源改为兼容懒加载，消除多进程spawn因无关pandas导入造成的5秒超时，没有放宽测试超时。
- 最终全量回归964 passed / 5 warnings；测试通过不等于统计置信度校准。上述P1残余问题仍需独立修复/回测，未因新UI被宣告解决。

## 连续报告回归中追加的修正

- Buffett “连续五期 ROE >15%”原实现允许4期/低于15%的记录误通过；现要求最近窗口恰好5个有限观测、每期严格大于15%。同步修正研究工作流的同名筛选，不将宽松IC质量信号强改成该标准。边界测试覆盖14.2、恰15、零、短序列、缺失及完整达标。
- 合成预览统一 EPS/PE/营收/市值/DCF 单位，行情波动与回撤使用百分比点；自动事件注明 DEMO，不将占位宏观节点伪装成真实 FOMC 日程。IC 情景显示“设定权重”，不称实测概率。
- 这些修正是具体规则与演示一致性的修复，不改变上文关于默认特征、共享证据、在线数据源未实测和无预测校准的残留问题结论。
- 独立视觉复核进一步发现：原 PE 图以少量展示序列的分位着色，却与独立输入的“62%分位”并排，容易误导口径。现改为真实 PE 倍数纵轴、有效观测顺序横轴；独立分位标注“窗口/来源待核验”，不再从几条记录伪装五年分位带。
