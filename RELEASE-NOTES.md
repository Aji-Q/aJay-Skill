# J Trader 变更记录

上游 stock-deep-analyzer 的历史见 [docs/UPSTREAM-RELEASE-NOTES.md](docs/UPSTREAM-RELEASE-NOTES.md)。

## v1.2.0 · 2026-09-10

### 产品品牌与 README

- 产品名称由 aJay Research 更新为 **J Trader**；**aJay（Aji-Q）是维护者**，继续保留创作者与项目修改署名。
- 中文 README 按“给你的自选股，配个研究员”重新组织：先建立真实研究场景，再展示经营质量、估值、反方观点、可保存研报与分层工作流，减少架构术语先行。
- 英文 README 同步产品定位、名称、版本和使用边界；主报告截图重新由当前 J Trader fixture 生成。
- 为保护现有用户，仓库 `aJay-Skill`、插件 ID `ajay`、命令 `/ajay:`、环境变量 `AJAY_*` 与既有内部资源路径暂不改名。

### 运行时与归属

- CLI、会话 hook、主报告、投委会、组合 / 对比页、输入导出与免责声明统一展示 J Trader，并保留 `Maintained by aJay`。
- 合成 UI 样本由 `AJAY.DEMO` 更新为 `JTRADER.DEMO`；仍明确标注为离线合成 fixture，不代表证券或分析业绩。
- 插件与技能版本同步到 `1.2.0`；`NOTICE`、品牌规范、归属文档和回归断言同步更新。
- 品牌迁移不改变上游 MIT 版权、第三方依赖许可、摄影来源记录或历史归档。
- v1.2.0 发布闸门完成 **1006 passed**；桌面与 390px 移动端实测品牌、无整页横向溢出，浏览器控制台无错误。

## v1.1.0 · 2026-09-09

### 分析可信边界

- 审计采集 → 评分 → 综合 → 报告链；区分数据字段抽检、可执行规则覆盖与模拟流派一致度，均不表示预测胜率。
- 修复缺失规则仍高置信度、空心中性意见、空头重复计入多头共识、真实零 ROE 被删除、补数错误清除缺口与 deep 审阅上下文降级。
- 新增评分有效性与状态元数据；无依据综合分及强结论同步降级；隐藏定性固定分、默认价格倍数/无假设概率，失败/陈旧行情留白。
- 尚存默认特征参与引擎、综合公式重复计证与美股披露时点风险；详见 [分析审计](docs/ANALYSIS-AUDIT.md)，不以 UI 完成代替统计校准。

### 主报告视觉与交互

- Luna Max 完成复用 skill、原报告功能与真实摄影研究；默认界面改为连续六章研究网站，Vantara 仅作初期节奏参照，撤掉城市换图标签。
- 八位 AI 模拟方法视角按研究任务分布，连接原始证据、判断及反证；完整规则引擎草稿另保留并标明其默认特征与未核验措辞边界。
- 弃用同构纯生成城市图与游客街拍；四个真实金融主题原作经image工具轻微重构，署名/日期类型/许可/提示词/hash均可追溯。
- 纽约近景承担简报，上海长幅跨多屏展开，伦敦立面引入模型工作区，香港全幅提供市场与流派检索入口；手机上海增加三层研究注记。
- 19 维研究、DCF/Comps/LBO/敏感性、机构研究及遗漏模型补充回到主报告；支持模型目录、66 流派笔记搜索与筛选、原生证据窗口、输入下载与打印。
- 独立 HTML/CSS/JS 与本地 GSAP，默认正式报告与 standalone 均为同一内联版本；旧布局保留为显式兼容入口，不再作为默认主页面。
- GPT-6 Astra Low 两轮查看真实桌面/手机截图；首屏判断、手机研究连续性、模型/市场入口三项视觉问题均经修正。浏览器与回归结果详见 [UI 验收](docs/UI-REFACTOR.md)。精确图像模型版本未返回，不宣称 image-2.5。

### 产品归属

- 当前产品统一为 **aJay Research**，以美股研究为主线；保留 A 股 / 港股兼容功能。
- 重建中文 / 英文 README，统一插件作者、技能版本、安装与支持链接至 `Aji-Q/aJay-Skill`。
- 修复 Cursor 作者、Codex/OpenCode/Gemini 安装地址、Hermes 更新提示及组合 / 对比报告中的上游产品署名。
- 明确安装远端身份边界，更新检查继续显式启用；不将上游 release 作为 aJay 升级目标。
- 保留 MIT 上游版权，新增 aJay 修改版权、`NOTICE` 与 `docs/OWNERSHIP.md`；旧 README 留档，旧社群入口不再作为当前产品入口。
- 新增身份、版权保留、版本一致性、安装与更新目标的回归测试。

## v1.0.1 · 2026-09-09

- 安装脚本 `setup.sh` / `install-hermes.sh` / `INSTALL-HERMES.md` 不再默认克隆上游 UZI-Skill:源码目录内直跑,否则需 `AJAY_REPO_URL`。
- 修复上游 `hooks/session-start` 在 macOS 上因 GNU-only sed 输出非法 JSON、banner 被静默丢弃的 bug(改用 python 编码)。
- 安装快照不再带测试夹具缓存。

## v1.0.0 · 2026-09-09

派生自 stock-deep-analyzer 3.9.4(wbh604/UZI-Skill,MIT)。

- 改名:插件 `ajay`(命令前缀 `/ajay:`)、marketplace `ajay-skill`、环境变量前缀 `UZI_*` → `AJAY_*`、运行时目录 `~/.uzi-skill/` → `~/.ajay-skill/`。上游 issue/PR 链接原样保留。
- 去掉默认的上游 GitHub 更新检查:只有设了 `AJAY_REPO=owner/repo` 才检查(派生版没有上游 release 可"升级")。
- 新增美股补数链 `skills/deep-analysis/scripts/us_backfill.py`(stage1 之后跑,含 `--dry-run`):
  - SEC XBRL:ROE 5 年史、现金+短投(含 MarketableSecuritiesCurrent)、逐季 TTM EPS/BVPS 阶梯 → 精确 PE/PB 5 年分位
  - moomoo OpenD:美股日度资金流向(超大+大单=主力)→ 12_capital_flow
  - yfinance:同业对标表 → 4_peers
  - FMP(可选 `FMP_APIKEY`):目标价共识/评级分布 → 6_research
  - czsc 1.0 缠论:日线+周线 笔/中枢/未完成笔 + 按 108 课定义标注的买卖点候选 → 2_kline.chan(`chan_signals.py`)
- 新增 `merge_panel.py`:把 role-play agent 的评委判断合并回 panel.json 并按 v2.15.5 公式重算共识/流派分(此前每次分析都要手写)。
- `commands/analyze-stock.md` 流程加入美股补数与指纹重跑链(补 raw → stage1_modeling → agent → agent_analysis 带新 hash → stage2)。
- 已知:pandas 3.0 下 DatetimeIndex 单位可能是秒,与 `to_datetime` 的微秒比较会全错——`us_backfill.py` 统一 `as_unit("s")`。
