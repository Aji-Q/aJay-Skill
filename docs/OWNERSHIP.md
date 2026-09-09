# aJay 品牌与项目归属

## 当前身份

| 字段 | 规范值 |
|---|---|
| 产品品牌 | **aJay** |
| 维护者 | **aJay（Aji-Q）** |
| 官方仓库 | `https://github.com/Aji-Q/aJay-Skill` |
| 插件命令空间 | `ajay` / `/ajay:` |
| Marketplace 名称 | `ajay-skill` |
| 配置前缀 / 本地状态目录 | `AJAY_` / `~/.ajay-skill/` |
| 当前版本 | `1.1.0` |
| 产品定位 | aJay 的美股研究工作台；保留 A 股 / 港股兼容路径 |

## 当前版本贡献分配

- **aJay（Aji-Q）：75% 以上**。负责产品归属、金融研究需求、信息架构、视觉方向、验收判断与最终编辑控制。
- **OpenAI Codex：不超过 25%**。作为实现和编译协助，负责代码组装、重构、测试执行与构建核验。

该比例描述当前 aJay 主导版本的工作分配，不等同于 GitHub commit 数量，也不改写上游贡献历史或版权。Codex 不是项目所有者、维护者、金融分析师或发布者。完整说明见 [`CONTRIBUTORS.md`](../CONTRIBUTORS.md)。

“归属于 aJay”指当前品牌、维护、分发与 aJay 自己的新增修改，不表示上游 MIT 代码变成独占资产，也不代表其他投资者、供应商或设计参考方为项目背书。

## 版权与来源边界

- 上游基础：stock-deep-analyzer 3.9.4，来自 `wbh604/UZI-Skill`，MIT 许可。
- `LICENSE` 保留 **Copyright (c) 2026 Float Future**，并增加 aJay 新增修改的版权行。
- `NOTICE` 是当前分发的来源声明；`docs/UPSTREAM-CONTRIBUTORS.md`、`docs/UPSTREAM-RELEASE-NOTES.md` 保留贡献与历史证据。
- README 安装入口、更新建议、插件作者、报告署名统一为 aJay；上游作者信息留在来源说明，不伪称全部内容由 aJay 原创。
- 报告 UI 借鉴 Vantara 的宏观布局、章节节奏和留白，不复制其标志、图片或文案。不要把他人素材重新署名为 aJay。
- 历史截图及 `docs/archive/` 的旧 README 不是当前品牌素材库。尤其旧二维码、社群入口、旧报告署名不得被当作 aJay 联系入口重新发布。
- 投资者人物资料、数据源与依赖的权利归各自权利人；MIT 许可不自动覆盖来源不明的第三方素材。发布时仍需按素材来源逐项确认。

## 1.1.0 检查及修复范围

1. 根技能与 4 个子技能的作者、版本，Claude/Cursor/Gemini/npm manifest。
2. 中文、英文 README，Codex/OpenCode/Gemini/Hermes 安装说明。
3. 安装脚本默认远端与已存在仓库的身份检查；防止误将上游 checkout 当作 aJay 更新。
4. 更新模块的默认目标、用户提示与 Hermes 更新命令；网络检查仍为显式启用。
5. 会话 hook、CLI 品牌、组合 / 对比报告署名、免责声明。
6. `LICENSE` / `NOTICE`、历史资料隔离与新增回归测试。

主报告与证据质量的修改记录见根目录 `RELEASE-NOTES.md`。回归测试检查身份入口与分发边界，不对所有第三方图片或每一条历史贡献做法律确权；未覆盖资产不得被解释为已获独占权。

## 维护规则

- 新增安装 / 支持链接默认使用本项目仓库，不默认跳转至上游维护者。
- 版本通过 `.version-bump.json` 列出的当前分发文件同步；历史版本、schema 版本、研究来源版本保持原值。
- 更新器只提示版本，不执行远程安装或替用户改写 `origin`。
- 安装到已有目录时应先检查仓库来源；显式 `AJAY_REPO_URL` 可选择用户自己的镜像，默认仍为 aJay。
- 加入新报告入口时检查页面 title、导航 logo、页脚、分享卡、二维码目标及导出文件署名。
- 测试入口：`python -m pytest tests/test_ajay_ownership.py -q`（在 `skills/deep-analysis/scripts/` 运行）。
