# J Trader 品牌与项目归属

## 当前身份

| 字段 | 规范值 |
|---|---|
| 产品品牌 | **J Trader** |
| 维护者 | **aJay（Aji-Q）** |
| 官方仓库 | `https://github.com/Aji-Q/aJay-Skill` |
| 插件技术 ID / 命令空间 | `ajay` / `/ajay:` |
| Marketplace 技术名称 | `ajay-skill` |
| 配置前缀 / 本地状态目录 | `AJAY_` / `~/.ajay-skill/` |
| 当前版本 | `1.2.0` |
| 产品定位 | J Trader 开源 AI 美股研究助手；保留 A 股 / 港股兼容路径 |

**J Trader 是产品名，aJay 是维护者。** 仓库名、插件 ID、命令前缀、环境变量和部分资产路径继续保留 `aJay-Skill` / `ajay`，用于兼容现有安装，不再作为产品品牌展示。

“归属于 aJay”指 J Trader 的当前产品方向、维护、分发及 aJay 自己的新增修改；不表示上游 MIT 代码变成独占资产，也不代表投资者、供应商、摄影作者或设计参考方为项目背书。

## 版权与来源边界

- 上游基础：stock-deep-analyzer 3.9.4，来自 `wbh604/UZI-Skill`，MIT 许可。
- `LICENSE` 保留 **Copyright (c) 2026 Float Future**，并增加 aJay 新增修改的版权行。
- `NOTICE` 是当前分发的来源声明；`docs/UPSTREAM-CONTRIBUTORS.md`、`docs/UPSTREAM-RELEASE-NOTES.md` 保留贡献与历史证据。
- README、CLI、会话提示、报告 UI 和导出文件使用 J Trader；维护与创作者署名使用 aJay（Aji-Q）。
- 报告 UI 借鉴 Vantara 的宏观布局、章节节奏和留白，不复制其标志、图片或文案，也不把第三方素材重新署名为 J Trader 或 aJay。
- `docs/archive/` 与旧截图是历史证据，不是当前品牌入口；旧二维码、社群入口和旧产品名不得作为当前联系或安装入口重新发布。
- 投资者人物资料、数据源与依赖的权利归各自权利人；MIT 许可不自动覆盖来源不明的第三方素材。

## 1.2.0 品牌迁移范围

1. 中文 / 英文 README 与产品叙事统一为 J Trader，保留现有安装命令。
2. 根技能、子技能、Claude/Cursor/Gemini/npm manifest 同步至 1.2.0；技术 ID 继续为 `ajay`。
3. CLI、会话 hook、主报告、投委会、组合 / 对比报告、导出文件和免责声明统一展示 J Trader。
4. 合成 UI fixture 改为 `JTRADER.DEMO`，明确与真实证券研究隔离。
5. 新增回归断言：产品品牌、维护者署名、兼容 ID、版本和来源边界必须同时成立。

## 维护规则

- 新增用户可见入口默认展示 J Trader；作者、维护者或版权语境使用 aJay（Aji-Q）。
- 不主动改名仓库、插件 ID、`/ajay:` 命令、`AJAY_*` 环境变量或既有资产目录；这些变更需单独迁移方案。
- 版本通过 `.version-bump.json` 列出的当前分发文件同步；历史版本、schema 版本与研究来源版本保持原值。
- 更新器只提示版本，不执行远程安装或替用户改写 `origin`。
- 加入新报告入口时检查页面 title、导航 logo、页脚、分享卡与导出文件署名。
- 测试入口：在 `skills/deep-analysis/scripts/` 运行 `python -m pytest tests/test_ajay_ownership.py -q`。
