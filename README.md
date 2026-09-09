<div align="center">

# aJay

### 把全球金融中心，装进你的本地投资研究室。

**输入一个股票代码。得到一套能追溯、能质疑、能拿去做决策的深度研究网站。**

[![Version](https://img.shields.io/badge/version-1.1.0-C7A46A?style=for-the-badge)](RELEASE-NOTES.md)
[![Focus](https://img.shields.io/badge/focus-US%20Equities-0B1118?style=for-the-badge)](#这不是一张更花哨的评分卡)
[![Report](https://img.shields.io/badge/output-Self--contained%20HTML-17324D?style=for-the-badge)](#一条命令开始研究)
[![Tests](https://img.shields.io/badge/release%20gate-1004%20tests%20passed-2E7D65?style=for-the-badge)](docs/FUNCTIONAL-AUDIT.md)
[![License](https://img.shields.io/badge/license-MIT-E7E4DC?style=for-the-badge&labelColor=4B5563)](LICENSE)

[English](README_EN.md) · [立即开始](#一条命令开始研究) · [查看产品](#这不是一张更花哨的评分卡) · [分析审计](docs/ANALYSIS-AUDIT.md) · [功能审计](docs/FUNCTIONAL-AUDIT.md) · [提交问题](https://github.com/Aji-Q/aJay-Skill/issues)

</div>

![aJay private research report — Wall Street investment brief](docs/readme/ajay-report-hero.jpg)

> **你缺的不是第 17 个行情网站。** 你缺的是一个敢把数据缺口、估值假设、反方证据和决策条件同时摆上桌面的研究系统。
>
> **aJay 不是“AI 给个分”的股票玩具。** 它更像一间随时待命的私人投资委员会：先核验证据，再拆生意、算价格、组织分歧，最后告诉你什么条件值得行动，什么信息仍然未知。

## 这不是一张更花哨的评分卡

aJay 把一次个股研究组织成一座连续、可交互的金融研究网站。你从纽约的投资简报出发，穿过上海的经营质量、伦敦的估值模型与香港的市场分歧，最终抵达可执行的决策条件和完整研究底册。

| 传统股票工具 | aJay |
|---|---|
| 给你一个分数 | 给你**结论、证据、反证与缺口** |
| 图表很多，但不知道先看什么 | 按买方决策顺序组织为**六章研究叙事** |
| DCF 只展示目标价 | 展示**输入、假设、结果与敏感性矩阵** |
| AI 语气很确定 | 缺失数据保持未知，不用 `0` 或默认值制造确定感 |
| “大师观点”只是金句 | 42 位美股适配的模拟方法视角进入同一场可检索讨论 |
| 报告依赖在线页面 | 生成可离线保存、转发和审阅的**单文件 HTML** |

## 一个代码，六间研究室

```text
TICKER
  └─ 公开数据与来源校验
       └─ 19 个研究维度
            └─ 生意质量与资本效率
                 └─ DCF / 相对估值 / LBO / 敏感性
                      └─ 42 个市场适配视角的分歧审理
                           └─ 买入条件 / 证伪条件 / 风险边界
                                └─ 可追溯、可导出的独立研究网站
```

### 01 / 先给投资结论，再给结论边界

研究摘要把支持核验、关键缺口、价格与核心判断放在第一屏。读者不必翻完几十张图，才能知道这份研究到底在说什么。

### 02 / 让财务质量随着建筑一起展开

收入、利润、ROE、分红、负债和现金流不再挤在仪表盘卡片里。数据叙事与摄影构图共同推进，让“经营质量”成为一段连续阅读，而不是表格堆积。

![aJay business-quality chapter — Shanghai financial district](docs/readme/ajay-business-quality.jpg)

### 03 / 估值不是答案，是一组可以被攻击的假设

当前估值、历史分位、行业比较、DCF 内在价值和敏感性矩阵进入同一工作台。你看到的不只是一个目标价，还能看到这个价格依赖什么。

![aJay valuation workspace — DCF and sensitivity analysis](docs/readme/ajay-valuation-workspace.jpg)

### 04 / 把“不同意”变成研究资产

价值、质量、成长、量化、宏观与交易视角在同一公司上形成分歧。每个判断都可以继续检索、筛选并回到证据入口——不是人物背书，而是可复核的方法模拟。

![aJay market disagreement chapter — Hong Kong financial district](docs/readme/ajay-market-disagreement.jpg)

## 你的私人投资委员会，不替你假装确定

美股报告会按市场适配性组织当前 42 个模拟视角，包括 Buffett、Munger、Graham、Lynch、Dalio、Soros、Simons、Livermore 等方法原型；不参与美股研究的 A 股专属短线角色会被自动排除。

这里没有真实人物投票，也没有名人背书。真正有价值的是：

- 同一份证据如何被不同投资体系解释；
- 哪些观点彼此冲突，冲突来自事实还是假设；
- 哪条反证足以推翻当前判断；
- 哪些数据尚未获得，因此暂时不应下结论。

## 为决策而生，而不是为展示而生

- **证据可追溯**：关键判断连接数据提供方、日期与原始记录。
- **缺口可见**：缺失、代理指标、降级来源与失败补数不会被包装成完整数据。
- **模型可检查**：估值输入、假设、结果、区间和敏感性在同一阅读路径中。
- **分歧可检索**：按人物、流派和关键词搜索观点，而不是滚动寻找答案。
- **研究可带走**：导出研究输入与自包含 HTML；默认只保存在本机。
- **桌面与移动端一致**：同一份研究可以在大屏深读，也能在手机上完成关键判断。

<p align="center">
  <img src="docs/readme/ajay-report-mobile.png" width="360" alt="aJay mobile equity research report" />
</p>

## 一条命令开始研究

需要 Git 与 Python 3.10+：

```bash
git clone https://github.com/Aji-Q/aJay-Skill.git
cd aJay-Skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py AAPL --depth medium --no-browser
```

完成后，终端会给出报告路径。打开 `full-report-standalone.html`，即可离线阅读、保存或分享。

| 模式 | 适合场景 | 你会得到什么 |
|---|---|---|
| `lite` | 盘前扫描、快速排雷 | 核心数据、规则扫描与初步风险 |
| `medium` | 日常个股研究 | 更完整的数据、建模与报告 |
| 深度研究工作流 | 建仓前、财报后、投资备忘录 | 数据补全、方法评审、输入指纹与人工质量闸门 |

要完成真正的深度研究，请让 agent 按 [AGENTS.md](AGENTS.md) 与 [analyze-stock](commands/analyze-stock.md) 执行证据采集、补数、复算、方法评审和最终检查。一次 CLI 自动扫描不等于独立分析师复核。

### 想先看效果，不想等待数据？

```bash
cd skills/deep-analysis/scripts
python preview_editorial.py
```

预览中的 Aster Systems / `AJAY.DEMO` 是合成样本，不是实际证券或推荐。

## 数据与能力边界

美股是当前重点市场：支持 SEC XBRL 财务补数、yfinance 行情与同行信息，并可选接入 FMP 共识数据和 moomoo OpenD 资金流。实际覆盖取决于数据可达性、凭据和标的；A 股、港股及龙虎榜工作流作为兼容能力保留，但不代表覆盖完全一致。

可选配置见 [.env.example](.env.example)。报告默认留在本机；只有显式使用 `--remote` 才会主动公开访问。公开前请检查报告是否包含私人信息。

## 不是口号：发布前真的跑过

v1.1 发布闸门在真实 AAPL 流程上验证了报告生成、42 位美股适配讨论阵容、搜索与流派筛选、证据弹窗、主题切换、研究输入导出、移动端布局和浏览器控制台；自动化测试结果为 **1004 passed**。

[阅读分析架构审计](docs/ANALYSIS-AUDIT.md) · [阅读功能与应用审核](docs/FUNCTIONAL-AUDIT.md) · [阅读 UI 交付记录](docs/UI-REFACTOR.md) · [查看图像来源](docs/IMAGE-PROVENANCE.md)

## 在你的 agent 工作流里使用

| 环境 | 入口 |
|---|---|
| Codex | [.codex/INSTALL.md](.codex/INSTALL.md) |
| Claude Code / Cursor | [AGENTS.md](AGENTS.md) 与仓库插件 manifest |
| Gemini CLI | [GEMINI.md](GEMINI.md) |
| OpenCode | [.opencode/INSTALL.md](.opencode/INSTALL.md) |
| Hermes | [INSTALL-HERMES.md](INSTALL-HERMES.md) |

## aJay 出品

**aJay（Aji-Q）拥有并维护 aJay 项目的品牌、产品方向与本项目修改。** 完整的贡献归属、维护边界与软件来源见 [CONTRIBUTORS.md](CONTRIBUTORS.md)、[OWNERSHIP.md](docs/OWNERSHIP.md) 与 [NOTICE](NOTICE)。

本项目派生自 MIT 许可的 stock-deep-analyzer 3.9.4，并完整保留上游版权和贡献记录。摄影与 AI 重构素材均有来源记录；模拟投资方法不构成真实人物发言、投票或背书。

<div align="center">

**研究的终点不是一个分数，而是一个你敢为之负责的判断。**

[开始使用](#一条命令开始研究) · [查看版本记录](RELEASE-NOTES.md) · [提交问题](https://github.com/Aji-Q/aJay-Skill/issues)

<sub>研究辅助工具，不构成投资建议。请独立核验数据与假设，并自行承担决策风险。</sub>

</div>
