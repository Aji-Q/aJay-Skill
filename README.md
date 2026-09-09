<div align="center">

# aJay

### 让 42 套投资方法在你买入之前，先把一家公司吵明白。

**巴菲特会等，西蒙斯会算，索罗斯会追问宏观，查诺斯会先找破绽。**<br>
**aJay 把这些方法原型放进同一间私人研究室，但只允许它们对证据说话。**

[![Version](https://img.shields.io/badge/aJay-1.1.0-C7A46A?style=for-the-badge&labelColor=0B1118)](RELEASE-NOTES.md)
[![Market](https://img.shields.io/badge/FOCUS-US%20EQUITIES-17324D?style=for-the-badge)](#这是啥)
[![Dimensions](https://img.shields.io/badge/RESEARCH-19%20DIMENSIONS-2C4157?style=for-the-badge)](#一次研究会得到什么)
[![Perspectives](https://img.shields.io/badge/COMMITTEE-42%20PERSPECTIVES-7A6238?style=for-the-badge)](#42-位美股适配评审团)
[![Commands](https://img.shields.io/badge/WORKFLOWS-20%20COMMANDS-324A46?style=for-the-badge)](#20-条专项工作流)
[![Tests](https://img.shields.io/badge/RELEASE%20GATE-1004%20PASSED-2E7D65?style=for-the-badge)](docs/FUNCTIONAL-AUDIT.md)

**美股优先 · 19 维研究 × 42 位市场适配视角 × 20 条专项工作流 × 六章沉浸式报告**

[30 秒上手](#30-秒上手) · [这是啥](#这是啥) · [报告长什么样](#报告长什么样) · [评审团](#42-位美股适配评审团) · [专项命令](#20-条专项工作流) · [三档深度](#三档研究深度) · [FAQ](#faq) · [English](README_EN.md)

</div>

![aJay private research report — Wall Street investment brief](docs/readme/ajay-report-hero.jpg)

> **不是行情终端，不是三段式 GPT 总结，也不是换了皮的股票评分卡。**
>
> 输入一个代码，aJay 会完成数据采集、证据质量检查、经营拆解、估值建模、42 种方法审理与风险证伪，最后生成一座可以离线保存的金融研究网站。

---

## 30 秒上手

任何支持 agent / skill 的环境里，直接把安装和研究要求说清楚。装好后，你只需要一句：

> **用 aJay 深度研究 AAPL。先检查数据质量，再给我估值、反方意见和可证伪的决策条件。**

| 你使用的环境 | 直接执行或交给 agent |
|---|---|
| **Claude Code** | `/plugin marketplace add Aji-Q/aJay-Skill`，然后 `/plugin install ajay@ajay-skill` |
| **Codex** | `按 https://raw.githubusercontent.com/Aji-Q/aJay-Skill/main/.codex/INSTALL.md 安装 aJay，然后深度研究 AAPL` |
| **Cursor** | `/add-plugin ajay`，然后说“用 aJay 深度研究 AAPL” |
| **Gemini CLI** | `gemini extensions install https://github.com/Aji-Q/aJay-Skill` |
| **OpenCode** | `按 https://raw.githubusercontent.com/Aji-Q/aJay-Skill/main/.opencode/INSTALL.md 安装 aJay，然后研究 AAPL` |
| **Hermes** | 按 [INSTALL-HERMES.md](INSTALL-HERMES.md) 安装，再用自然语言触发 aJay |
| **纯 CLI** | `git clone https://github.com/Aji-Q/aJay-Skill.git && cd aJay-Skill && pip install -r requirements.txt && python run.py AAPL` |

Claude Code 中最常用的四句话：

```text
/ajay:analyze-stock AAPL     ← 完整个股研究与编辑式 HTML 报告
/ajay:quick-scan NVDA        ← 快速排雷与核心结论
/ajay:dcf MSFT               ← DCF、WACC 与敏感性矩阵
/ajay:ic-memo META           ← 投委会备忘录与三情景回报
```

Codex、Gemini、Hermes、OpenCode 等环境直接说自然语言即可；agent 会按 [AGENTS.md](AGENTS.md) 选择对应工作流。

> **当前稳定版 v1.1.0**
> - 美股报告从 66 人总池中自动筛选 **42 位市场适配视角**，不再让 24 位 A 股游资刷屏说“不参与”；
> - 报告升级为纽约、上海、伦敦、香港贯穿的 **六章连续研究网站**，不是照片轮播，也不是卡片堆砌；
> - 未知 ROE、负债率、估值分位与宏观输入保持未知，**不再用默认 `0` 制造完整感**；
> - 搜索、流派筛选、证据弹窗、主题、导出、移动端与浏览器控制台已完成真实流程验收；
> - v1.1 自动化发布闸门：**1004 passed**。

---

## 这是啥

一句话：**输入一家公司，让 agent 像买方研究团队一样核验公开事实、拆解生意、计算价格、组织分歧，然后交付一份能追到原始证据的研究网站。**

```text
一个股票代码
   ↓
公开数据 + 来源日期 + 缺口检查
   ↓
19 个研究维度 + 经营质量 + 资本效率
   ↓
DCF / Comps / LBO / Segmental Model
   ↓
42 种美股适配投资方法交叉审理
   ↓
支持证据 + 反方证据 + 失效条件
   ↓
可检索、可导出、可离线保存的 HTML 研究网站
```

### 一次研究会得到什么

- **一份连续六章的 HTML 研究网站**：简报 → 生意质量 → 价格模型 → 市场分歧 → 决策条件 → 研究底册；
- **一个可攻击的估值工作台**：DCF、历史分位、同行比较、LBO 与敏感性，而不只是孤零零的目标价；
- **一场可搜索的投资委员会讨论**：按人物、流派和关键词查看全部判断与反证；
- **一套证据质量记录**：数据源、日期、代理指标、降级路径和真正的未知值；
- **一组决策边界**：什么条件支持建仓、什么变化触发复核、什么证据足以推翻当前判断；
- **一份可以带走的研究资产**：单文件 HTML 与研究输入导出，默认只保存在本机。

## 为什么做 aJay

过去研究一只美股，常见流程是：

```text
SEC / 财报找数字
→ 行情网站看估值
→ Excel 搭 DCF
→ 搜同行与共识
→ 刷新闻和观点
→ 自己拼一份备忘录
→ 最后忘了哪些是事实，哪些只是当时的假设
```

市场从来不缺信息，真正稀缺的是**判断的生产线**：

1. 事实和推理必须分开；
2. 支持理由和反方证据必须同时出现；
3. 估值必须暴露假设，而不是只报一个数字；
4. 缺失数据必须保持未知，不能偷偷变成 `0`；
5. 报告必须告诉你下一步核验什么，而不是用“建议关注”结束。

所以有了 aJay：

> **公开事实 × 证据质量 × 估值模型 × 方法分歧 × 决策条件**<br>
> **而不是：抓一堆数据 × 让 AI 自信地写三段话。**

---

## 报告长什么样

### 01 / 纽约：投资简报

第一屏先回答“这家公司现在值不值得继续研究”，并同时展示支持核验、重大缺口、当前价格和判断边界。

### 02 / 上海：生意质量

收入、利润、ROE、分红、负债和现金流随着陆家嘴纵向构图逐步展开。城市不是壁纸，而是研究节奏的一部分。

![aJay business-quality chapter — Shanghai financial district](docs/readme/ajay-business-quality.jpg)

### 03 / 伦敦：价格模型

当前估值、历史分位、行业比较、DCF 内在价值与敏感性矩阵进入同一工作台。每个结果都能追问：“它依赖了什么假设？”

![aJay valuation workspace — DCF and sensitivity analysis](docs/readme/ajay-valuation-workspace.jpg)

### 04 / 香港：市场分歧

同一家公司，不同的市场解释。价值、成长、宏观、趋势、量化与科技产业方法在这里正面碰撞。

![aJay market disagreement chapter — Hong Kong financial district](docs/readme/ajay-market-disagreement.jpg)

### 05–06 / 决策条件与研究底册

最后两章不是重复结论，而是把催化剂、风险、失效条件、原始记录和证据入口集中交给读者。桌面端适合深读，移动端保留完整决策路径。

<p align="center">
  <img src="docs/readme/ajay-report-mobile.png" width="360" alt="aJay mobile equity research report" />
</p>

---

## 42 位美股适配评审团

不是 42 段人物口吻，也不是名人金句生成器。每个角色代表一套投资方法，判断必须落回当前公司的真实输入。

| 组别 | 方法方向 | 人数 | 代表方法原型 |
|---|---:|---:|---|
| A | 经典价值 | 6 | Buffett · Graham · Munger · Fisher · Templeton · Klarman |
| B | 成长与科技投资 | 9 | Lynch · O'Neil · Thiel · Wood · Andreessen · Gurley · Naval |
| C | 宏观与对冲 | 7 | Soros · Dalio · Howard Marks · Druckenmiller · Burry · Chanos |
| D | 趋势与交易系统 | 4 | Livermore · Minervini · Darvas · Gann |
| E | 中国价值投资方法 | 7 | 段永平 · 张磊 · 冯柳 · 朱少醒 · 邓晓峰 |
| G | 量化与统计套利 | 4 | Simons · Thorp · D. E. Shaw · Asness |
| H | 科技产业领袖视角 | 4 | Jensen Huang · Musk · Sam Altman · Saylor |
| I | AI 卡位与瓶颈审视 | 1 | Serenity |

**为什么不是 66 位？** 因为 aJay 的核心服务对象是美股研究。24 位依赖 A 股涨停板、龙虎榜与席位生态的短线角色不会参与美股报告，避免用“不适用”消息填满讨论区。A 股兼容工作流仍会在对应市场启用它们。

> 上述角色均为算法 / AI 对投资方法的模拟，不是真实人物投票、发言、独立意见或背书。

---

## 20 条专项工作流

不必每次都跑完整报告。直接选择你此刻真正要解决的问题：

| 命令 | 用来做什么 |
|---|---|
| `/ajay:analyze-stock AAPL` | 完整个股深度研究与最终报告 |
| `/ajay:quick-scan NVDA` | 快速扫描核心数据与风险 |
| `/ajay:dcf MSFT` | DCF、WACC、终值与 5×5 敏感性 |
| `/ajay:comps AMD` | 同行估值、历史分位与隐含价格 |
| `/ajay:lbo DELL` | 杠杆收购可行性与 IRR 快速测试 |
| `/ajay:segmental-model AMZN` | 分业务收入、三情景与三年预测 |
| `/ajay:initiate META` | 机构风格首次覆盖报告 |
| `/ajay:ic-memo GOOGL` | 投委会备忘录与三情景回报 |
| `/ajay:earnings AAPL` | 财报结果、超预期检测与逻辑影响 |
| `/ajay:earnings-preview NVDA` | 财报前共识、情景与隐含波动 |
| `/ajay:model-update MSFT` | 新财报 / 指引后的模型增量更新 |
| `/ajay:catalysts TSLA` | 已发生事件与未来 60 天催化剂 |
| `/ajay:thesis AMZN` | 五条核心投资逻辑的持续追踪 |
| `/ajay:dd COST` | 五类工作流、21 项尽调清单 |
| `/ajay:screen AAPL` | Value / Growth / Quality / GARP / Short 筛选 |
| `/ajay:ai-readiness ORCL` | AI 暴露、卡位评级与关键杠杆点 |
| `/ajay:panel-only AAPL` | 只运行市场适配评审团 |
| `/ajay:scan-trap TICKER` | 异常宣传、资金与交易风险排查 |
| `/ajay:returns` | 组合收益与行业贡献归因 |
| `/ajay:rebalance` | 持仓漂移、交易清单与换手成本 |

> Claude Code 使用 `/ajay:<command>`；其他 agent 可以直接说自然语言。命令能力和可用数据仍取决于当前市场、数据源与配置。

### CLI 进阶

```bash
python run.py AAPL --depth lite --no-browser              # 快速扫描
python run.py AAPL --depth medium --no-browser            # 日常研究
python run.py AAPL --depth deep --no-browser              # 深度工作流 Stage 1
python run.py AAPL --school A --no-browser                # 只看经典价值方法
python run.py --versus AAPL MSFT GOOGL                    # 2–4 只股票横向比较
python run.py --portfolio holdings.csv                    # 组合排名与健康度
python run.py AAPL --from-modeling --no-browser           # 从缓存恢复建模
python run.py AAPL --output-dir ./output --no-browser     # 集成到指定目录
python run.py AAPL --remote                               # 显式生成远程访问入口
```

---

## 三档研究深度

| 档位 | 适合场景 | 目标耗时 | 研究方式 |
|---|---|---:|---|
| `lite` | 盘前扫描、快速排雷 | 1–2 分钟 | 核心数据、代表性视角、关键风险 |
| `medium` | 日常个股研究 | 5–8 分钟 | 完整数据采集、建模与报告；默认档 |
| `deep` | 建仓前、财报后、投委会 | 15–20 分钟以上 | 强化补数、Bull/Bear 辩论、分部建模与人工复核 gate |

实际耗时受网络、数据源和 agent 推理过程影响。`deep` 会先完成 Stage 1；agent 还必须读取当前输入、完成带 `analysis_input_hash` 的复核，才能进入最终组装。旧股票的角色判断不会直接复用到新数据上。

---

## 数据与可信度

美股是当前主线：SEC XBRL 财务补数、yfinance 行情与同行信息可直接参与工作流；FMP 共识数据和 moomoo OpenD 资金流为可选增强。A 股、港股与龙虎榜能力作为兼容路径保留，但不同市场不会伪装成同等覆盖。

| aJay 的处理原则 | 报告里的表现 |
|---|---|
| 观察值与推理分开 | 原始数据、规则评分、AI 解释分别标记 |
| 缺失就是缺失 | 不把未知 ROE、负债率或估值分位写成 `0` |
| 降级必须可见 | 记录来源链、代理指标与 fallback |
| 分数不是概率 | 未经校准的置信度只作为研究线索 |
| 反方必须上桌 | 风险、证伪条件与支持理由同等可见 |

v1.1 发布前已真实运行 AAPL 流程，验证报告生成、42 位美股适配阵容、搜索、流派筛选、证据弹窗、主题切换、研究输入导出、移动端布局与浏览器控制台；自动化测试结果为 **1004 passed**。

[分析架构审计](docs/ANALYSIS-AUDIT.md) · [功能与应用审核](docs/FUNCTIONAL-AUDIT.md) · [UI 交付记录](docs/UI-REFACTOR.md) · [图像来源](docs/IMAGE-PROVENANCE.md)

---

## 安装

### Python / CLI

需要 Git 与 Python 3.10+：

```bash
git clone https://github.com/Aji-Q/aJay-Skill.git
cd aJay-Skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py AAPL --depth medium --no-browser
```

完成后终端会输出报告实际路径。打开 `full-report-standalone.html` 即可离线阅读。

### Claude Code

```text
/plugin marketplace add Aji-Q/aJay-Skill
/plugin install ajay@ajay-skill
/ajay:analyze-stock AAPL
```

### Codex

直接把这句话交给 Codex：

> 按 https://raw.githubusercontent.com/Aji-Q/aJay-Skill/main/.codex/INSTALL.md 安装 aJay，读取 AGENTS.md，然后深度研究 AAPL。

### Gemini CLI

```bash
gemini extensions install https://github.com/Aji-Q/aJay-Skill
```

OpenCode、Hermes 和其他环境见 [.opencode/INSTALL.md](.opencode/INSTALL.md)、[INSTALL-HERMES.md](INSTALL-HERMES.md) 与 [AGENTS.md](AGENTS.md)。

### 只想看产品演示

```bash
cd skills/deep-analysis/scripts
python preview_editorial.py
```

Aster Systems / `AJAY.DEMO` 是合成样本，不是实际证券或推荐。默认报告留在本机；`--remote` 会主动建立外部访问入口，公开前请检查报告内容。

---

## FAQ

<details>
<summary><strong>这些投资者真的参与了分析吗？</strong></summary>

没有。评审团是对公开投资方法的算法 / AI 模拟，用于制造方法分歧与反证，不代表任何真实人物的实时观点、投票或背书。
</details>

<details>
<summary><strong>42 位是不是越多越准？</strong></summary>

不是。人数不是准确率。42 位的价值是覆盖不同的决策框架；最终仍应看证据质量、模型假设、分歧来源和失效条件。
</details>

<details>
<summary><strong>为什么美股报告删掉了 A 股游资？</strong></summary>

因为涨停板、龙虎榜、席位溢价等方法不适用于美股。aJay 会按市场过滤角色，而不是用大量“不讨论”制造虚假繁荣。
</details>

<details>
<summary><strong>一定需要付费 API 吗？</strong></summary>

核心路径可以使用公开数据运行；FMP、moomoo OpenD 等属于可选增强。具体覆盖受网络、数据源、标的和凭据影响，缺失项会在报告中保留为空缺。
</details>

<details>
<summary><strong>报告能发到手机吗？</strong></summary>

可以。单文件 HTML 可直接保存与发送；也可显式使用 `--remote` 创建临时外部访问入口。远程模式会公开报告访问面，使用前应检查私人信息。
</details>

<details>
<summary><strong>这能替我决定买卖吗？</strong></summary>

aJay 的任务是提高研究质量，不是替你承担决策。评分不是收益概率，模型依赖假设，所有结论都应结合最新公开信息独立核验。
</details>

---

## aJay 出品

**aJay（Aji-Q）拥有并维护 aJay 项目的品牌、产品方向与本项目修改。** 贡献归属、维护边界、上游版权与软件来源见 [CONTRIBUTORS.md](CONTRIBUTORS.md)、[OWNERSHIP.md](docs/OWNERSHIP.md) 与 [NOTICE](NOTICE)。

本项目派生自 MIT 许可的 stock-deep-analyzer 3.9.4，并保留上游版权和贡献记录。摄影与图像工具重构素材均有来源记录；报告对真实投资者不构成关联声明。

<div align="center">

### 研究的终点不是一个分数，而是一个你敢为之负责的判断。

[开始使用](#30-秒上手) · [查看版本记录](RELEASE-NOTES.md) · [提交问题](https://github.com/Aji-Q/aJay-Skill/issues) · [MIT License](LICENSE)

<sub>研究辅助工具，不构成投资建议。请独立核验数据与假设，并自行承担决策风险。</sub>

</div>
