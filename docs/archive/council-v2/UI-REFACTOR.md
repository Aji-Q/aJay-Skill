# aJay Investment Council · 重构与验收

更新：2026-09-09。默认主报告已切换为研究会议，不再是 V1 的长页卡片罗列。

## 信息架构

- 会议主屏：研究议题 → 当前方法视角 → 原始输入支持的判断 → 同屏反证 → 一键证据。
- 八个模拟方法视角：巴菲特、格雷厄姆、芒格、林奇、索罗斯、达利欧、利弗莫尔、西蒙斯。三议题 × 八视角，观点由原始记录确定生成，不使用旧 persona 的随机台词。不是本人发言、投资建议或背书。
- 城市只改变环境，不重置议题、人物或金融数据。主屏不显示伪精确胜率。
- 研究底稿：全部输入维度、来源/时间/状态、缺口、完整原始记录、估值模型、分维度规则状态。只显示 data_backed 的规则分；启发式/缺失分不作测量值。
- 历史完整版保留为 research-appendix.html 供审计与兼容，不是默认界面。组合/对比报告本轮仅同步品牌，未完成同款布局。

## 实现边界

- lib/report/council.py：无网络、无 HTML 的确定性证据与观点模型。
- lib/report/council_renderer.py：安全 JSON 注入、非有限数清理、全部数据保留、本地资产内联。
- assets/report-council.html/.css/.js：场景层、方法视角、原生底稿 dialog、摄影展开页。
- assemble_report.py 默认 layout=council，同时输出 full-report.html 与完整内联的 full-report-standalone.html；layout=editorial 仅用于兼容审计。
- 保留自查质量门槛。AJAY.DEMO 明确为合成证券示例，跳过审阅门槛会披露；真实运行不默认跳过。
- GSAP 3.15.0 本地内联：人物出入场、文字次序和城市淡换；快速切换取消旧时间线，切换完成清除旧场景。无自动轮播、滚轮劫持、数字递增或动画假行情。
- Lucide SVG 取代 emoji/像素头像。原始数据只用 textContent；innerHTML 仅用于本地固定 Lucide SVG。
- reduced-motion 使用静态切换；noscript 保留可读原始输入。字体使用系统栈，无外部字体、运行时 CDN 或自动数据上传。

## 摄影策略与合法来源

放弃“同一室内构图换城市”的纯生成组图。先筛近两年公开作品，验证摄影师、日期类型、许可，实际目检并淘汰普通游客街拍；再将原图直接交给 image 工具做轻微重构。

入选：华尔街街牌与石材近景 / 金丝雀码头办公立面 / 陆家嘴上海中心竖幅 / 中环金融建筑与维港横幅。金融语义优先于旅游景点识别。

详情与逐图来源见 [真实摄影记录](PHOTOGRAPHY-PROVENANCE.md)。Unsplash 三张只有公开日期，未冒称拍摄日；上海拍摄日可核实。图像工具没有返回精确模型版本，不宣称 image-2.5。

## 验收

- 全量 Python 回归：**964 passed，5 warnings**；包含缺失/零值/NaN/Inf、覆盖度、版权与身份、安全注入、新默认主报告、24个确定性视角。现有依赖警告不是测试失败。
- 浏览器：1280×720 主屏、390×844 手机首屏已实际查看。手机 DOM 宽度390、scrollWidth390；证据入口约501px、反证入口约645px。
- Astra Low 独立静态审美终审：桌面与真实390×844手机截图通过；建议进一步减弱上海天空竖向光柱，已纳入场景层压光。
- 前次 Astra Low 实际交互验收：证据展开、Esc关闭/焦点恢复、人物切换通过。根代理继续检验最终版本，不把静态审图冒称交互测试。
- 报告数据为合成输入，不代表模型已回测或置信度已校准；剩余分析风险见 [分析审计](ANALYSIS-AUDIT.md)。

## 本地重建

在 skills/deep-analysis/scripts 下运行：

```sh
python preview_editorial.py  # 名称沿用，现已通过正式assemble输出新主报告
python preview_photography.py  # 原图与编辑版并列对照
python -m pytest tests/ -q
python -m http.server 8787 --directory reports
```

默认报告与对照页分别为 reports/AJAY.DEMO_YYYYMMDD/full-report-standalone.html、photography-review.html。对照页原图按需加载；主报告自身无外部资产依赖。
