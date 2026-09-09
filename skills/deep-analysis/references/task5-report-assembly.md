# Task 5 · aJay V3 continuous research report assembly

将已有分析输入装配成可连续阅读、证据可回查的 **aJay Research** 报告。主页面是金融研究快照，不是实时行情终端、交易指令或真实投资者背书；模型结果也不自动等于回测、校准概率或事实确认。

当前状态（2026-09-09）：root 已在默认 continuous 预览完成主要功能、视口、主题、`prefers-reduced-motion`、下载/分享、外部 Edge 打印和两轮视觉复核；屏幕阅读器仍待测，打印对比度、原始 JSON 省略与 PE 历史图轴语义已修复并核验；完整最终 PDF 未做逐页人工审阅。以下记录实际结果，不延伸为全部金融算法审计或全部模型校准。

## 1. 工作目录与输入

Python 入口的工作目录为仓库内 `skills/deep-analysis/scripts/`；进入此目录后不要再加一层 `scripts/`。

必需缓存：

- `raw_data.json`
- `dimensions.json`
- `panel.json`
- `synthesis.json`

可选但受当前链路读取的输入包括 `agent_analysis.json`、完整性/审阅状态和分业务模型文件。文件缺失时保留明确缺口，不为填满页面伪造文件、分数、趋势、人物意见或 segment 结果。

组装前确认：

- ticker、公司身份、市场、货币、缓存与数据时期一致；
- 来源、数据日期、采集时间、缺失、不适用、过期、备用和启发式状态保持可区分；
- 深度分析的 AI 审阅按当前输入指纹核验；旧文件时间接近不等于当前输入已审阅；
- 正式报告遵守 self-review 闸门；`AJAY_SKIP_REVIEW=1` 只用于本地调试并应在页面披露，不带入未披露的正式交付；
- 有限数字保留真实 `0`；NaN/Inf/无效序列进入缺失状态，不转换成零或中性结论。

## 2. 默认入口与产物

`assemble(ticker, layout="continuous")` 是当前默认路径。连续式入口由 `lib/report/continuous_renderer.py` 消费既有完整 HTML 和安全数据，生成主页面。

| 产物 | V3 用途 |
|---|---|
| `full-report.html` | 默认连续式六章主报告；与 standalone 一起由当前 continuous 入口生成相同的约 35MB 内联 HTML |
| `full-report-standalone.html` | 连续式单文件分享物；当前与 `full-report.html` 相同且约 35MB，外部 Edge 的下载/打印路径已实测；打印样式与断网端到端检查边界按下文记录 |
| `research-appendix.html` | 旧模板的完整研究底稿，保留 19 维、原机构块、panel、风险/区间和审计注入槽；是兼容/审计附件，不是默认主界面 |
| `one-liner.txt` | 同一输入的简短摘要，必须保留分数状态、动态角色数量和非背书说明 |
| `share-card.png` / `war-report.png` | 按需导出面；文件存在不等于视觉或数据验收通过 |

输出目录为 `reports/<ticker>_<YYYYMMDD>/`。打包器优先当天目录，否则先核对所选快照日期，避免分享旧报告。默认连续式与兼容路径均可显式调用：

```bash
cd <repo>/skills/deep-analysis/scripts
python assemble_report.py "$TICKER"                         # 默认 continuous
python -c 'from assemble_report import assemble; assemble("$TICKER", layout="council")'
python -c 'from assemble_report import assemble; assemble("$TICKER", layout="editorial")'
```

## 3. 六章连续信息架构

连续页面不是城市背景切换器。地点与章节共享输入和上下文，各自承担不同金融任务：

| 章 | 锚点 | 空间与功能 |
|---|---|---|
| 01 · Investment Brief | `section-core`、`briefing-detail` | 纽约 Wall Street 近景进入；公司身份、市场状态、摘要、证据边界、结论和报告工具 |
| 02 · Business Beneath the Price | `section-scan`、`company-evidence` | 上海中心真实窄长竖幅跨多屏纵向展开；19 个基础维度、质量/增长/治理/行业地基 |
| 03 · Price Is an Assumption | `section-modeling`、`model-workspace` | 伦敦 Canary Wharf 办公立面；DCF/WACC/敏感性、Comps、LBO、机构模型和假设工作台 |
| 04 · The Market Has Another View | `section-clash`、`section-jury`、`section-chat` | 香港 Central 横向金融空间；多空分歧、反证、8 个方法人物、评委与研究笔记检索 |
| 05 · What Would Change the Decision | `section-risks`、`section-zones` | 风险、失效条件、情景计划、条件观察区间和公开持仓边界 |
| 06 · The Research Record | `section-library`、`section-evidence` | 证据索引、来源/时期/采集时间/状态、原始输入、展开、下载、打印、分享和摄影署名 |

页面采用单一连续路径，不设置城市 A/B/C/D 标签；地点保持静态章节关系，人物和数据上下文持续一致。上海保留真实竖幅的纵向关系；纽约、伦敦、香港保持各自的近景、立面网格、横向水域构图；统一裁切或室内窗框套版均不采用。

## 4. 组装阶段与功能映射

### 4.1 证据与安全边界

1. 在 HTML 转义前从 `raw_data` 建立证据索引和有限事实，来源、日期、采集时间、状态与原始字段保持分离。
2. 使用 `lib/report/security.py`、`evidence.py` 和 `council_renderer.py` 的安全边界；动态文本走 textContent/安全 JSON，provider 文本始终作为文本处理。
3. 综合分只有在完整性和有效性通过时显示有限数值；否则同时降级强结论、条件计划与观察区间，而不只是隐藏分数。
4. 图表只使用对应维度的有效输入；少于最低序列长度、非有限或非正数时显示空状态。事实、推断、假设、公开持仓和模拟人物文本分层呈现。

### 4.2 19 个基础维度

`DIM_META` 与六类注入槽继续保留全部 19 维：

- 财务面：`1_financials`、`10_valuation`、`14_moat`；
- 行情面：`2_kline`、`12_capital_flow`、`16_lhb`；
- 行业面：`4_peers`、`5_chain`、`7_industry`、`8_materials`、`9_futures`；
- 公司面：`11_governance`、`15_events`、`6_research`；
- 环境面：`3_macro`、`13_policy`；
- 安全面：`17_sentiment`、`18_trap`、`19_contests`。

每个卡片/记录必须显示对应 `score_status`、来源、时期或采集时间、缺失/不适用/过期/备用状态，以及专属图表或明确空状态。连续式主页面通过旧模板注入结果重排这些数据；研究底册提供完整维度索引和原始记录回查。

### 4.3 机构模型与独立补充

伦敦模型工作台继续保留 `lib/report/institutional.py` 已有的 DCF、Comps、Quick LBO、Initiating Coverage、IC Memo、Catalyst Calendar、Competitive Analysis。独立 `lib/report/model_supplement.py` 已接入 continuous 主页面，把原 UI 遗漏的真实模型字段变成可读块；当前预览实际显示 11 块（10 个产品 + 1 个 segment 状态）：

- dim 20：三表投影（损益、现金流、资产负债、假设、增长路径）；
- dim 21：Earnings、Thesis、Morning、Idea Screens、Sector；
- dim 22：Unit Economics、VCP、DD Checklist、Portfolio Rebalance；
- segmental：有独立模型文件时由既有 renderer 展示；缺文件明确显示“尚未建立”，不伪造预测。

补充块已在当前主页面完成可见性检查；仅凭页面出现标题或模型有输出，仍不足以声称全部模型已校准、已回测或已覆盖所有公司类型。PE 历史图轴语义修正和全部金融算法审计单独跟踪。

### 4.4 方法人物、panel 与证据

连续页面保留 8 个方法视角：巴菲特、格雷厄姆、芒格、林奇、索罗斯、达利欧、利弗莫尔、西蒙斯。它们由 `build_council()` 在三个问题主题下生成共享输入的模拟记录，非本人发言、独立专家投票、投资建议或背书。

- 人物旁的证据按钮进入原生 dialog，显示标题、状态、来源、时期、采集时间、有限事实和原始维度记录；
- panel 席位数量、signal 分布和研究笔记条目跟随当前输入，不固定写成某个总人数；
- 研究笔记保留组别 tabs、姓名/观点/规则关键词搜索、强弱定位、展开/收起和反证条件；
- 搜索只过滤当前页面已有文本，不向远程服务发送搜索词；
- 模拟一致度、规则覆盖度和人物分数不是上涨概率，也不是样本外置信度。

## 5. 交互、导出与离线契约

- 顶部 sticky 章节导航仅指向六章；scroll spy 更新 `aria-current` 和阅读进度，不抢占滚轮。
- `details`、证据 dialog、主题切换、评委席跳转、流派筛选、研究笔记搜索、全部展开、下载输入、打印/分享均是显式操作。
- GSAP 只做轻位移/透明度章节进入；无自动轮播、自动切城、数字从零滚动或假行情。尊重 `prefers-reduced-motion`。
- 下载研究输入和分享 dialog 是本地动作；不自动上传，不把 `location.href` 发送给二维码服务。
- `#share-card` / `#war-report` 是按需导出面；保持在 DOM 中，不因屏外而用 `display:none` 破坏导出。
- 当前外部 Edge 实际下载 JSON 为 89,813 bytes，并在 Downloads 复核 ticker 与 schema；外部 Edge `Page.printToPDF` 已成功。内嵌浏览器的 `printToPDF` 不支持。
- `full-report.html` 与 `full-report-standalone.html` 当前为相同的约 35MB 内联 HTML；打印配色与原始 JSON 省略已在最终 print 媒体样式中检查：正文、标题和图表采用深色墨迹，原始 JSON 不进入打印正文。最终版未做完整 PDF 逐页人工审阅，不写死页数。断网端到端、残留占位符与非预期外部请求仍按最终文件单独核验。

## 6. 摄影、版权与素材边界

- 当前摄影清单为 `assets/ajay-council/photography.json`，包含纽约、伦敦、上海、香港的原作页、原图 URL、作者、日期类型、许可、构图、编辑提示和 hash；详见 `docs/PHOTOGRAPHY-PROVENANCE.md`。
- 纽约/伦敦/香港作品若只有发布日期，必须写“拍摄日未确认”；上海记录可核实的拍摄日期。image 工具只做轻微影像重构，不把衍生图冒称未经编辑的原片。
- 人物肖像是 AI 生成的方法论视觉，不是实拍；工具没有返回可核实模型版本时不声明特定版本。
- aJay/Aji-Q 的新增编排、实现改造和项目文案与上游权利并存；原有开源代码、GSAP、Lucide、摄影作品、许可和署名由各自权利人保留，不宣称全部原代码或第三方素材独占。
- Vantara 只作宏观布局、节奏与沉浸叙事研究参考，不复制其源码、logo、照片、字体、文案或自然主题。

## 7. 本地预览与兼容

```bash
cd <repo>/skills/deep-analysis/scripts
python preview_editorial.py       # 沿用脚本名，正式输出默认走 continuous
python preview_photography.py    # 原图与编辑衍生图并列对照
python inline_assets.py "$TICKER"
python render_share_card.py "$TICKER"   # 按需
python render_war_report.py "$TICKER"   # 按需
```

`AJAY.DEMO` / Aster Systems 是离线合成 fixture，用于 UI、缺失状态和安全边界检查，不代表真实证券。默认预览应显示 DEMO/合成样本和开发闸门状态。

## 8. root 当前验收记录

以下勾选只表示当前预览或明确工具路径已经检查；开放项继续保留：

- [x] 默认 continuous 六章、无城市换图标签或自动场景切换；上海跨多屏，其他三处构图各自成立；`council/editorial` 兼容入口保留。
- [x] 当前预览存在 19 个基础维度、对应状态/来源回查入口、8 个方法人物和 66 条原始研究笔记。
- [x] `model_supplement` 已接入；当前 11 块（10 个产品 + segment “尚未建立”状态）可读，无整包 JSON 泄漏。
- [x] 研究笔记搜索“巴菲特”显示 `1/66`，G 流派显示 `0/66`，座席重置显示 `66/66`；证据 dialog 关闭后焦点返回原入口，分享 dialog 可打开。
- [x] 1280 桌面与 390 手机无整页横向溢出；390px 浅色/深色主题切换背景与文字对比正常，`scrollWidth` 保持 390。
- [x] `prefers-reduced-motion: reduce` 下 score 稳定为 59、`chat-msg` 的 `animationName` 为 `none`，1280×720 桌面显示正常。
- [x] 外部 Edge 下载 JSON 为 89,813 bytes，并复核 ticker/schema；外部 Edge `Page.printToPDF` 成功。
- [ ] 打印配色、原始 JSON 省略、内嵌浏览器打印能力、断网端到端与残留占位符/外部请求检查仍在最终收尾；不写死页数。
- [x] Astra Low 两轮实际截图评审完成；第二轮确认三项视觉阻断已修复且无新增阻断，记录见 `docs/research/CONTINUOUS-REPORT-VISUAL-REVIEW.md`。
- [x] 当前工程回归为 `992 passed`（5 个依赖 warnings），`node --check` 与 `git diff --check` 已通过。
- [ ] 屏幕阅读器验收仍待测；PE 历史图已改为实际倍数轴，独立分位输入标注窗口/来源待核验，全部金融算法审计另行进行。
- [x] 交付汇报保持实际验证边界，不写“全部模型已校准”“全部源码/素材独占”或“已经全测”。

任务 5 的交付汇报必须列出真实文件路径、实际运行命令、通过与未测项、已知限制和数据/版权边界。
