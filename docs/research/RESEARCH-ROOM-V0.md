# J Trader · Research room v0

日期：2026-09-10。阶段：按确认方向实施 P0 与首屏、估值工作区初版；等待这一轮视觉反馈后，再扩展其它章节的精修。未提交或推送。

## 设计落点

以下为前轮参考研究的落点，不复制网站源码、文案、品牌或素材。

| 参考 | 用在 J Trader 的设计原则 |
|---|---|
| [Aman](https://www.aman.com/) | 建筑摄影提供空间，而不是独立图片展 |
| [Patek Philippe](https://www.patek.com/) | 单一主操作与精简入场层级 |
| [Citadel](https://www.citadel.com/) | 金融机构的冷静尺度与权威感 |
| [Echo Street](https://echostreet.com/) | 投资叙事与环境摄影共同构成连续阅读 |
| [BlackRock Investment Institute](https://www.blackrock.com/corporate/insights/blackrock-investment-institute) | 研究问题、图表、假设相邻 |
| [Monocle](https://monocle.com/) | 编辑式标题、细分隔线与正文密度 |
| [KKR](https://www.kkr.com/) | 以任务组织长篇机构信息 |
| [McKinsey Pixels of Progress](https://www.mckinsey.com/featured-insights/mckinsey-digital/pixels-of-progress) | 逐层阅读，先概览后追问 |
| [Our World in Data](https://ourworldindata.org/) | 图表 / 数据表 / 来源视图共享数据 |
| [The Pudding](https://pudding.cool/) | 滚动服务解释，不以动效遮挡结论 |

## 本轮实现

- 首屏保留纽约建筑环境；公司、质量门控结论、支持与缺口、价格、主入口组成单一信息序列。底部快捷路径保持完整，不贴底截断。
- 估值开场压缩为短段与伦敦局部横幅。左侧价格地图，右侧关键假设，再出现格雷厄姆、西蒙斯方法论汇报。原有 DCF、Comps、LBO 与补充模型继续在下方。
- 价格地图不新造估值：直接读取市场价、DCF 基础案例和同行中位 PE 隐含价；共享币种、时间戳与刻度。缺失不画柱；保留零与负值。手机改用原生文字，避免将桌面 SVG 标签整体缩小。
- 连续式报告不再加载旧模板的 CSS 或执行脚本，保留兼容输出供比对。服务器生成的旧内容块经过显式样式映射，原始数据不改写。
- 动效仅保留进入、章节与导航反馈。停止动态开关、系统减少动态响应、键盘切换视图、来源弹窗焦点恢复与搜索继续可用。
- P0：PE/Comps 缺失分位不默认 50；财务健康进度图与原始值标签分离；顶层市场传递至 K 线，美股绿涨红跌；SVG 对非有限数值守卫。

## 真实预览与边界

- [AAPL 本地预览](http://127.0.0.1:8787/AAPL_20260910/full-report-standalone.html?v=research-room-v0)
- 输入采集时间：`2026-09-09T20:33:51+00:00`。本轮只重新生成 UI，没有更新行情、补齐证据或完成当前输入审阅。
- UI 预览明确显示开发状态、证据缺口和非实时属性；这不是新完成的金融分析。原规则草稿中的默认特征与方法结论仍需独立算法审计。
- 保留 6 章、19 个基础维度卡、8 个方法人物、11 个模型补充块。当前 AAPL 为 42 条角色笔记、24 条原始维度记录；人数不写死为 66。
- 单文件约 36.5 MB，仍是高清内联资产与离线阅读的取舍；本轮未宣称完成公网性能优化。

## 实际检查

- 桌面 1280×720 与手机 390×844 目视检查；手机整页 `scrollWidth = clientWidth = 390`。
- 修复手机固定导航被父级模糊背景约束的问题。模型目录定位避让双层导航；图中文字在手机保持原生字号。
- 价格表展示 315.34 / 210.54 / 345.68，与图形一致；箭头键切到来源，来源按钮打开 dim 20 记录。Esc 关闭后焦点回到原按钮。
- 停用动态后 `data-motion=off`。桌面浅色/深色主题保持统一；测试结束恢复深色与动态开关。
- 搜索“巴菲特”显示 1/42；叠加技术派显示 0/42；清空并选全部恢复 42/42。证据索引保留全部 24 条、来源、时期、采集时间和原始记录入口。
- 默认入口产出 AAPL 与 JTRADER.DEMO；无失效内部锚点。独立美学复核提出的首图过低、首屏路径截断、图中文字过小，已据实修正。
- 本轮最终工程回归为 **1032 passed，5 条现有依赖警告**；JavaScript 语法与 diff 空白检查通过。
- 未进行完整 PDF 逐页检查、屏幕阅读器验收、全部设备与主题组合验收、所有金融算法校准或线上行情稳定性测试。

## 后续编辑入口

- 布局：`skills/deep-analysis/assets/report-continuous.html`
- 视觉：`skills/deep-analysis/assets/report-continuous.css`
- 交互：`skills/deep-analysis/assets/report-continuous.js`
- 编排：`skills/deep-analysis/scripts/lib/report/continuous_renderer.py`
- 快照价格图：`skills/deep-analysis/scripts/lib/report/valuation_brief.py`

修改生成器后重生成报告，不直接编辑 reports 目录中的临时产物。
