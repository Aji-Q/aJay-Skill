# aJay 主报告 UI 重构说明

更新日期：2026-09-09。**最终运行验收结果待主任务实测填写。**

## 范围与最终决策

重构个股主报告的封面、导航、章节、证据区、摄影转场、方法论人物区、阅读交互和本地分享。保留 `assemble_report.py` 与 `lib/report/*` 的数据接口，不更换分析 pipeline。

组合报告 `portfolio_runner.py` 和对比报告 `versus_runner.py` 本次仅做 aJay 品牌调整，不宣称它们已完成同款版式改造。

最终视觉是黑曜石 / 深海军蓝 / 金属银、曼哈顿与上海夜景、黑白人物肖像。Vantara 只提供宏观布局、胶囊导航和章节节奏参考，不复制其源码、商标、字体文件或内容。森林、奶油、暖色庭院、金色日落方案已撤下。详见 `brand-spec.md`、`design-dna.json`、`UI-SKILL-RESEARCH.md`。

## 页面阅读顺序

1. 金融夜景封面：公司身份、价格、采集时间、aJay 导航与 AI 封面说明。
2. 证据区：字段抽检、规则可执行比例、当前输入 AI 审阅状态、采集快照；DEMO/开发闸门状态就地披露。
3. 核心结论：有效研究分、结论状态、历史输入图表、趋势/价格/量能/筹码、新闻/风险/催化和条件计划。
4. 深度数据：财务、行情、行业、公司、环境、安全六类折叠区，保留来源与原始数据。
5. 机构模型：已有 renderer 与有数据时出现的分业务模型。
6. 上海夜景转场：长期研究主题；图像不承担数据证据功能。
7. 分歧与反证：模拟多空立场、辩论与流派汇总。
8. 方法论与角色：生成肖像及非背书说明、动态角色数、信号分布与模拟一致度。
9. 研究笔记与公开持仓：筛选、展开、定位；公开持仓不与模拟意见混淆。
10. 风险与条件区间：输入不足时未评估，不把旧价格倍数称作 DCF 或历史分位。
11. 本地分享与页脚：原生 dialog、打印、aJay 署名和来源声明。

保留 `section-core/clash/jury/chat/scan/modeling/risks/zones` 稳定锚点，另有 `section-evidence`。旧逻辑编号用于兼容，不要求页面按旧编号排序。

## 实现层

```text
raw_data + dimensions + panel + synthesis + fresh agent review
    ↓ 证据校验 / 缺失状态 / 输出转义
assemble_report.py
    ├─ report-template.html：结构、锚点、交互
    ├─ report-editorial.css：后置内联样式与响应式
    ├─ lib/report/evidence.py：证据区、有限数值、输入图表
    └─ lib/report/*：维度、角色、机构模型等既有模块
    ↓
full-report.html + avatars/ + one-liner.txt
    ↓ inline_assets.py
full-report-standalone.html：单文件分享候选
```

模板仍保留旧组件 CSS，后置 editorial 层控制新视觉；维护时按最终 computed style 检查，不从旧注释推断现行方向。四张 PNG 在主组装阶段内联，小型 SVG 头像由单文件打包步骤内联。

## 数值与证据契约

| 位置 | 取值与约束 |
|---|---|
| 综合分 | `synthesis.overall_score`；完整性及 `dimensions.fundamental_score_valid` 通过后使用有限数值，否则 `—` 并同步降级强结论 |
| 维度分 | `dimensions.dimensions[dim].score` + `score_status`；缺失/不适用/过期/heuristic/未知旧状态不冒充测量分 |
| 角色分 | 角色 `score`，不使用旧 `confidence`；缺值保持未知，不补默认 0 |
| 规则比例 | `rule_coverage_pct`；角色记录不完整时未记录，不对已知子集平均后伪装成完整覆盖 |
| 一致度 | `panel_consensus` 为共享输入的模拟一致度，不是成功概率或独立专家置信区间 |
| 历史曲线 | `2_kline.data.close_60d`，所有输入有限且为正；少于两条或有无效值时空状态 |
| 条件区间 | 当前有效 AI 审阅中 `narrative_override.buy_zones`；固定现价倍数不冒充验证后的估值方法 |

这些是展示契约，不意味着所有历史模型、缓存和定性规则已成为统计模型。真实 0 与未知分开；来源、假设、缺失和过期状态同时可见。分析审计另见 `ANALYSIS-AUDIT.md`。

## 交互与安全

- 默认深色；主题和目录状态使用本地存储，容忍存储不可用；目录默认折叠以免遮挡。
- 导航保留跳转与滚动高亮；A–I 流派筛选采用按钮和 `aria-pressed`。
- 角色席位支持 Enter/Space、清除筛选并定位笔记；六类数据与角色详情保留 `<details>`。
- 分数不播放递增动画，低动效模式关闭非必要过渡。
- 分享采用原生 `<dialog>`，打印和键盘路径独立验收。不请求远程二维码，不自动上传/发布。
- 输出转义、URL 白名单、头像 ID 清理与 DOM 文本节点提示保持原安全边界。

## 合成预览与单文件交付

在 `skills/deep-analysis/scripts` 工作目录运行：

```bash
python preview_editorial.py
python inline_assets.py AJAY.DEMO
```

**AJAY.DEMO / Aster Systems** 的价格、财务、事件与走势均为合成 fixture，仅检查布局和渲染。预览不请求市场数据；显式 `is_demo`，组装时跳过质量闸门并在页面披露，随后恢复环境变量。不得作为真实证券结论发布。

标准 `full-report.html` 需相邻 `avatars/`。对外分享选择 `full-report-standalone.html`，并单独移动、断网打开检查。打包器遇到缺失头像会保留原引用，不能凭文件存在宣称完整单文件。

历史图片导出仍绑定 `#share-card` / `#war-report`，CSS 目标为 1080×1920 / 1920×1080；最终像素由 scale 决定。文件大小不是清晰度验收；未生成的 PNG 不列为已交付。

## 待主任务实测的验收表

| 检查 | 状态 | 所需记录 |
|---|---|---|
| 定向与全量 Python 回归 | 待实测 | 环境、命令、结果、失败原因 |
| 深浅主题桌面 | 待实测 | 视口、截图、对比度、长表格 |
| 移动端 | 待实测 | 视口、横向溢出、导航和卡片重排 |
| 键盘与 dialog | 待实测 | Tab、Enter/Space、Esc、焦点返回 |
| 折叠/筛选/席位定位 | 待实测 | 操作与实际 DOM 状态 |
| 有效/缺失数据 | 待实测 | 分数、结论、默认值、空图表 |
| standalone 离线 | 待实测 | 独立 HTML、断网、无残留资产依赖 |
| console / 网络 | 待实测 | 错误、自动请求、图片加载 |
| 打印 / PNG | 待实测 | 按实际执行范围记录 |

未预写通过结论；未测视觉相似度，不给“95% 还原”等数字。实际结果、截图和未覆盖项由主任务补充。
