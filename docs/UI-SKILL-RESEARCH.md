# aJay 报告 UI 重构：可复用 Skill 调研

核查日期：2026-09-09。范围：公开 GitHub 原始文件、README、许可及关键依赖的只读检查；未安装候选、未运行外部脚本。这里的“可用”表示源文件和使用路径已核实，不代表已完成候选的运行时安全审计或视觉验收。

## 结论与采用方式

本项目采用 **Design DNA 的结构化设计提取方法 + Open Design web-clone 的证据与多视口验收方法**，沿用 aJay 现有报告生成链路，不引入完整克隆平台或 Studio 编辑器。

**后续用户调整优先**：用户明确要求金融科技语境，采用黑曜石、深海军蓝、金属银和真实感金融城市夜景，拒绝自然景观与柔和色调。因此 Vantara 保留为信息层次、导航与章节节奏参考，不再直接采用其奶油色、森林绿或自然意象。新图像与未采用概念稿见 `IMAGE-PROVENANCE.md`。

- 主参考：[zanwei/design-dna 的 SKILL.md](https://github.com/zanwei/design-dna/blob/593e39bc9e3652734653bd75544a333d7d43615e/SKILL.md)。将参考页面拆成 `design_system`、`design_style`、`visual_effects`，再把 aJay 的分析内容映射到版式，而不是复制参考品牌。
- 质量补充：[Open Design web-clone 的 SKILL.md](https://github.com/nexu-io/open-design/blob/main/skills/web-clone/SKILL.md)。先观测实际页面，再记录设计规则、响应式布局和交互；对照真实浏览器输出，不凭代码推断“已经还原”。
- 当前执行方式是读取并应用方法论，不是声称新 Skill 已被安装或加载。报告仍由项目原有 Python 组装器与单文件 HTML 模板生成。
- 保留 aJay 的标题、分析逻辑、数据来源、警示、报告交互及品牌；Vantara 仅为版式、视觉层次和滚动叙事的参照。参考网站的品牌、文案、照片、字体授权和上游 Skill 的许可彼此独立。

## 候选比较

### 1. design-dna — 推荐作为轻量主方法

来源：[仓库与 README](https://github.com/zanwei/design-dna)、[SKILL.md](https://github.com/zanwei/design-dna/blob/main/SKILL.md)、[LICENSE](https://github.com/zanwei/design-dna/blob/main/LICENSE)、[脚本依赖](https://github.com/zanwei/design-dna/blob/main/scripts/package.json)。已核实提交：`593e39bc9e3652734653bd75544a333d7d43615e`。

能力：URL、截图或图片 → 结构化设计 JSON → 应用自己的内容生成 UI。覆盖布局、字阶、色彩、间距、组件和动效，默认输出可独立使用的 HTML/CSS/JS，适配本项目的单文件报告。

依赖：方法与 schema 可直接阅读；可选测色/验证工具需要 Node.js ≥ 18.17 和 `sharp ^0.33.5`，无需 API key。许可为 MIT。

限制：色差和颜色覆盖率检查不等于版式、可读性或交互验收。URL/截图中的未观测信息应标为推断，不把填满 schema 变成编造值。本次不执行它建议的依赖安装；若后续复制代码或文档实质部分，应保留其 MIT 通知。

### 2. Open Design web-clone — 推荐作为证据与验收补充

来源：[SKILL.md](https://github.com/nexu-io/open-design/blob/main/skills/web-clone/SKILL.md)、[Design DNA 说明](https://github.com/nexu-io/open-design/blob/main/skills/web-clone/references/design-dna.md)、[LICENSE](https://github.com/nexu-io/open-design/blob/main/LICENSE)。实时文件版本为 1.6.1，仓库为 Apache-2.0；其 DNA 说明另注明改编自 MIT 的 design-dna。

能力：URL 侦察、响应式截图、真实计算样式、组件/动效线索、视觉差异、报告与品牌清理。可迁移的规则：1440/768/390 三档观测；事实与推断分级；先建视觉基线再重构；最终检查浏览器错误与交互；做自己的品牌时保留设计语言、替换品牌内容。

依赖：当前 `playwright-loader.mjs` 优先复用已有 Playwright；否则使用内置 CDP 适配器和系统 Chrome/Edge/Chromium。旧搜索摘要中“必须安装 Playwright”已与当前代码不符。

限制：完整流程包含资产下载、路由爬取、网络捕获和镜像，不是本次报告重排所必需。仅选择设计观测与 QA 步骤；不自动执行镜像、登录态复用、资产下载或原站源码搬运。所读脚本范围不是全仓库安全审计。

### 3. UI Image to Code Studio — 可用，但本次较重

来源：[SKILL.md](https://github.com/zwq-top/ui-image-to-code-studio/blob/main/skill/SKILL.md)、[README](https://github.com/zwq-top/ui-image-to-code-studio/blob/main/README_EN.md)、[安装要求](https://github.com/zwq-top/ui-image-to-code-studio/blob/main/docs/INSTALL_AND_RUN.md)、[MIT LICENSE](https://github.com/zwq-top/ui-image-to-code-studio/blob/main/LICENSE)。

能力：截图或可见 URL 状态 → 原子证据 → UI 规格 → 前端源码 → 浏览器对照；另提供可视化编辑、稳定元素 ID、修订与回滚。明确避免把截图直接当成页面，并要求观察范围内的交互证据。

依赖：Python ≥ 3.10、Node.js ≥ 18，以及浏览器验证工具；Studio/项目菜单扫描还引入本地编辑桥接和 Playwright 工作流。

限制：适合需要长期拖拽微调的 UI 项目；对已有 Python 单文件报告增加编辑器、同步协议及大量交付产物，投入与本次目标不匹配。README 的案例与通过声明为作者提供的证据，本次未独立重跑。

### 4. website-to-design-md — 方法参考，不纳入代码

来源：[SKILL.md](https://github.com/Paidax01/web-to-design-md/blob/main/SKILL.md)、[README](https://github.com/Paidax01/web-to-design-md/blob/main/README.md)。

能力：用 `agent-browser eval` 提取 DOM、computed styles、CSS variables、文本及交互状态，输出 `DESIGN.md` 与 HTML 设计板。定位是设计文档提取，不是直接完成网站复制。

依赖：明确绑定 `agent-browser`，不同浏览器工作流需额外适配。

限制：实时 GitHub repository API 的 `license` 为 `null`，根目录未见 LICENSE；README 的 Publishing Notes 仍提示公开发布前选择许可。因此不把该仓库的脚本/模板复制进 aJay，也不将其标为 MIT。可参考其事实与推断分离、计算样式优先的通用方法。

## 排除的失效结果

搜索目录仍收录 `Yeachan-Heo/oh-my-codex/skills/web-clone`，但本次打开对应 SKILL.md 返回 404，实时 `skills/` 目录也没有该路径。因此不使用目录站的一键安装建议，不把旧索引当作当前可用性证据。

## Vantara 参考证据与 aJay 转译

参考页：[Vantara 英文首页](https://vantara.in/en)。下表来自本次主任务使用 CUA 对真实页面的截图和 computed styles 观测，不是候选 Skill 自动生成的结果。

| 观测项 | 参考值/特征 | aJay 的应用原则 |
|---|---|---|
| 导航 | 胶囊容器，圆角 40px，内边距 20px 28px | 保持报告章节导航和键盘可达性 |
| 标题 | `fontGTUltra`，观察到 56/32/24px 层级 | 保留鲜明字阶与编辑式层次；字体文件另核许可 |
| 正文 | `Schibsted Grotesk`，16px | 中文长报告另配清晰可读的中文回退字体 |
| 底色 | cream `#fbf8f2` | 仅保留观测记录；最新方案改用黑曜石/深海军蓝 |
| 文字 | warm ink `#1e1916` | 仅保留观测记录；最新方案采用适配深底的金属银/高对比浅色 |
| 深色区块 | forest `#013a2b`、deep `#0b2b22` | 沿用章节转场层次，最终替换为金融科技冷色，不吞没风险提示 |
| 次级色 | taupe `#908271` | 仅保留观测记录；最终冷灰次级文字仍须检查对比度 |
| 章节节奏 | 观察到 80px section padding | 宽屏叙事留白；窄屏收缩，避免过长空屏 |

观测值应作为参考起点，不是全站所有断点的通用常数。品牌照片、商标、原站文案和自定义字体没有因布局参考而获得额外使用权。本项目不宣称与 Vantara 有官方关系。

## 本次重构的验收边界

1. **真实数据契约优先**：保留原有报告占位符、模块渲染接口、风险提示及数据缺失状态。
2. **布局先于装饰**：核对首屏、章节比例、长表格、长文本和窄屏滚动，之后检查颜色与动效。
3. **两套内容验证**：完整数据与缺失/降级数据均可阅读；用本地 fixture 验证，不触发新的金融数据采集。
4. **功能不缩水**：目录跳转、折叠、筛选、主题/布局开关、导出与分享等已有交互按实际模板范围回归。
5. **无伪造精度**：不把 heuristic score、评委人数或配色差异当成统计置信度；视觉相似度没有实测时不写百分比。
6. **归属清晰**：aJay 是当前产品身份；有实际复制的上游代码/素材则保留必要许可和来源，避免把第三方原创资产归为 aJay 原创。
7. **浏览器交付证据**：记录测试视口、实际截图、console 错误、交互结果与仍未验证的部分。

## 现有模板兼容契约（重构前检查）

已检查 `report-template.html`、`assemble_report.py`、分享图渲染器及现有模板测试。基于重构前 Git HEAD，模板包含 **58 个唯一 `{{...}}` 占位符与 21 个 `INJECT_*` 注入标记**。布局变化不应使组装器静默丢失数据。

### 元素与行为

| 契约 | 保留内容 |
|---|---|
| 主题 | `#theme-toggle`、根元素 `data-theme`、`ajay-theme` 存储键、系统主题偏好；暗色所有核心表面/文字变量 |
| 目录 | `#toc-rail`、`.toc-item`、`#toc-toggle`、`.collapsed`、`aria-expanded`、`ajay-toc-collapsed`；点击跳转、滚动章节高亮 |
| 八章节 | `section-core`、`section-clash`、`section-jury`、`section-chat`、`section-scan`、`section-modeling`、`section-risks`、`section-zones` |
| 评委与群聊 | `.seat[data-target]` 指向对应消息；`.chat-tab[data-group]` 筛选 `.chat-msg[data-group]`；点击席位清除筛选、展开消息并定位 |
| 群聊工具 | `#expand-all`、`#collapse-all`、`#scroll-bull`、`#scroll-bear`；消息 `<details>` 与 `.bullish`/`.bearish` |
| 风险 | 数据不足、基金类型说明、低置信度、pipeline fallback、school lock 的注入及可读区别，不因改为品牌绿色而消失 |
| 术语 | `.jargon[data-tip]` 与安全 DOM 构造；PE/PB/ROE/DCF/IRR/WACC/PEG 等词条仍可用 |
| 分享 | `#share-overlay`、`#report-qr-canvas`、`#report-qr-url`；本地文件与可分享地址状态清楚区分 |
| 图片导出 | `#share-card` 为 1080×1920，`#war-report` 为 1920×1080；Python 导出脚本按 ID 截图，仅移除屏外定位，故不能直接改成 `display:none` |
| 安全 | 保持 `escape_text`/`escape_payload` 边界、URL allow-list、头像 ID 清理；交互代码不把数据写入 `innerHTML` |

### 21 个注入标记

`INJECT_CHAT_MESSAGES`、`INJECT_DATA_GAP_BANNER`、`INJECT_DEBATE_ROUNDS`、`INJECT_DIM_COMPANY`、`INJECT_DIM_ENV`、`INJECT_DIM_FINANCIAL`、`INJECT_DIM_INDUSTRY`、`INJECT_DIM_MARKET`、`INJECT_DIM_SAFETY`、`INJECT_FRIENDLY_LAYER`、`INJECT_FUND_MANAGERS`、`INJECT_INSTITUTIONAL_MODELING`、`INJECT_JURY_SEATS`、`INJECT_PANEL_INSIGHTS`、`INJECT_RISKS`、`INJECT_SCHOOL_SCORES`、`INJECT_SEGMENTAL`、`INJECT_STYLE_CHIP`、`INJECT_TOP3_BEARS`、`INJECT_TOP3_BULLS`、`INJECT_VOTE_BARS`。

### 不应盲目继承的旧行为

- 旧二维码函数对任意 HTTP(S) 页面自动将完整 `location.href` 发给外部二维码服务；这不是必须保留的分享功能契约。应优先本地生成或明确触发，避免页面打开即传输报告 URL。
- 旧模板有两套分数动画共同作用于 `.score-giant`；其契约是最终数值准确和遵守低动效偏好，不是保留重复动画。
- 旧测试把侧边 TOC 在 1280px 以下隐藏、特定 CSS 颜色字面值和字符位置当成实现契约。若采用新的胶囊导航，应以不遮挡内容、可键盘操作、对比度充分的行为测试替代失效的布局假设，而不是为通过旧断言保留旧版式。

### 定向回归测试

- `test_v3_9_1_toc_collapse.py`
- `test_v3_6_0_phase_a_visual.py`
- `test_v3_4_4_banner_ux.py`
- `test_html_escape_boundary.py`
- `test_pr93_template_rendering.py`

研究阶段曾尝试运行上述测试，但系统 Python 报 `No module named pytest`，该次尝试未执行任何测试；未因此安装依赖。最终测试结果应以主任务选定的可用环境与重构后实际运行记录为准。
