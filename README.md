# aJay

**aJay 的美股研究工作台。** 从公开数据到可追溯判断，再到清晰、可阅读的研究报告。

**维护者：aJay（Aji-Q） · 版本：1.1.0 · 唯一项目入口：[Aji-Q/aJay-Skill](https://github.com/Aji-Q/aJay-Skill)**

[English](README_EN.md) · [使用流程](AGENTS.md) · [版本记录](RELEASE-NOTES.md) · [贡献归属](CONTRIBUTORS.md) · [品牌与归属](docs/OWNERSHIP.md) · [MIT 许可](LICENSE)

## 研究范围

- **美股优先**：已有 SEC XBRL 财务补数、yfinance 同行信息、可选 FMP 共识与 moomoo OpenD 资金流接口；实际覆盖取决于数据可达性、凭据与标的。
- **证据分层**：区分原始数据、规则评分、AI 推理和模拟投资方法评审；缺失数据、代理指标与降级路径应在报告中明示。
- **决策阅读顺序**：研究摘要 → 证据质量 → 关键驱动 → 估值假设 → 风险与验证条件 → 数据明细。
- **兼容保留**：A 股、港股及龙虎榜等上游工作流继续可用，但不代表各市场具有同等数据覆盖。

投资方法面板是算法 / AI 模拟，不是真实投资者投票、独立专家意见或人物背书。评分和“置信度”不是收益概率；未经回测校准的评分应作为研究线索。

## 安装与运行

需要 Git 和 Python 3.10+。先从 aJay 的仓库克隆，在独立环境安装依赖：

```bash
git clone https://github.com/Aji-Q/aJay-Skill.git
cd aJay-Skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py AAPL --depth medium --no-browser
```

若 GitHub 提示认证，使用你自己的仓库访问凭据。不要在脚本、报告或 issue 中粘贴密钥。

报告生成后，终端会显示 HTML 的实际路径。默认报告保留在本机；`--remote` 是主动公开报告的选项，使用前先检查报告是否包含私人信息。

| 使用方式 | 入口 |
|---|---|
| Codex | [.codex/INSTALL.md](.codex/INSTALL.md) |
| Claude Code / Cursor | 本仓库插件 manifest 与 [AGENTS.md](AGENTS.md) |
| Gemini CLI | [GEMINI.md](GEMINI.md) |
| OpenCode | [.opencode/INSTALL.md](.opencode/INSTALL.md) |
| Hermes | 先阅读 [INSTALL-HERMES.md](INSTALL-HERMES.md)，再运行本仓库的 `install-hermes.sh` |

## 深度研究

`lite` / `medium` 可用于快速规则扫描。需要完整深度分析时，请让 agent 按 [AGENTS.md](AGENTS.md) 和 [analyze-stock](commands/analyze-stock.md) 完成：

1. 采集数据并检查来源、日期与缺口。
2. 美股按需运行 `us_backfill.py`，再重新计算建模与分析指纹。
3. 基于真实输入完成方法评审，记录推理与 `analysis_input_hash`。
4. 生成报告并复核数字、假设、证据质量及风险提示。

直接执行一次 CLI 不等于已完成独立的分析师复核。

可选配置见 [.env.example](.env.example)：SEC 联系方式 `AJAY_SEC_UA`、`FMP_APIKEY`、moomoo OpenD 及其他数据源按实际需要启用。

## 更新与验证

更新前确认远端属于此项目：

```bash
git remote get-url origin
# 预期：https://github.com/Aji-Q/aJay-Skill.git
# GitHub SSH 等价地址也可。
git pull --ff-only
python -m pip install -r requirements.txt
cd skills/deep-analysis/scripts
python -m pytest tests/ -q
```

更新通知默认关闭。显式设置 `AJAY_REPO=Aji-Q/aJay-Skill` 后可检查本项目 GitHub release；`AJAY_NO_UPDATE_CHECK=1` 关闭检查。未发布 release 或网络失败不代表当前代码已是最新。

## 新版报告与审计

连续六章的研究网站：简报 → 生意质量 → 价格模型 → 市场分歧 → 决策条件 → 研究底册。四个金融空间分别按摄影构图组织章节，不再用城市标签切换同一背景；上海超高层跨多屏纵向展开。八位模拟方法视角各自连接具体判断、反证和证据入口。

19 个研究维度、估值模型及假设、完整流派笔记搜索与筛选、风险条件、原始记录和导出均保留在主报告。缺失产品展示真实空状态。摄影来自近两年公开作品，经 image 工具轻微重构；人物为 AI 肖像，非本人发言或背书。

```bash
# 从项目根目录开始；以下只生成合成演示数据
cd skills/deep-analysis/scripts
python preview_editorial.py
# 打开输出的 full-report-standalone.html，可独立保存与分享
```

预览中的 Aster Systems / AJAY.DEMO 不是实际证券。默认一次构建同时输出内容相同、资源内联的 full-report.html 与 full-report-standalone.html。生产报告仍要求完整数据与质量闸门；council / editorial 布局仅作显式兼容入口。

[分析架构审计](docs/ANALYSIS-AUDIT.md) · [功能与应用审核](docs/FUNCTIONAL-AUDIT.md) · [UI 交付与验证](docs/UI-REFACTOR.md) · [品牌规范](docs/brand-spec.md) · [UI skill 检索](docs/UI-SKILL-RESEARCH.md) · [图像来源](docs/IMAGE-PROVENANCE.md)

## 品牌、来源与反馈

**aJay 是本派生项目的品牌与维护者。** 项目基于 MIT 许可的 stock-deep-analyzer 3.9.4，并非所有代码都由 aJay 原创；保留上游版权和贡献记录。

- [NOTICE](NOTICE)：软件来源、版权及非关联说明。
- [贡献归属](CONTRIBUTORS.md)：本次 aJay 主导工作 75%+；Codex 作为实现与编译协助不超过 25%。
- [归属说明](docs/OWNERSHIP.md)：当前维护边界、品牌规范与检查规则。
- [上游发布历史](docs/UPSTREAM-RELEASE-NOTES.md) / [贡献记录](docs/UPSTREAM-CONTRIBUTORS.md)：仅供追溯。
- [本项目问题反馈](https://github.com/Aji-Q/aJay-Skill/issues)：项目维护入口，不引导至上游社群、二维码或联系人。

旧 README 与截图保留在 `docs/archive/` 和 `docs/screenshots/` 作为历史资料，旧安装命令与宣传内容不作为当前说明。报告视觉借鉴 Vantara 的编辑式章节与留白布局，不使用其标志、照片、文案，也不表示双方有关联。

本工具提供研究辅助，不构成投资建议；使用者应自行核实信息与承担决策风险。
