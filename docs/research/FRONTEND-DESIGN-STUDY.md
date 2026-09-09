# aJay 连续金融报告：前端设计学习笔记

核查日期：2026-09-09。研究对象：MotionSites、React Bits、Uiverse、Anime.js、Aceternity UI。目标不是堆叠组件或照搬视觉效果，而是把成熟的布局、动效和交互方法转译为 aJay 的金融汇报系统。

## 总结

1. **动效必须解释信息**：只服务于章节进度、证据展开、模型切换、风险状态和图片叙事；不做无意义粒子、霓虹、光标尾迹和连续漂浮。
2. **报告是任务界面，不是作品集**：首要顺序为“结论 → 证据 → 模型 → 风险 → 操作”；城市摄影只负责建立金融中心的空间氛围，不成为独立照片画廊。
3. **高级感来自约束**：稳定网格、强字阶、真实摄影、精细状态反馈、留白和节奏，比效果数量更重要。
4. **不为组件库重写架构**：React Bits 与 Aceternity UI 主要作为交互结构参考；当前 Python + 单文件 HTML/CSS/JS 继续保留。若引入动效库，只保留一个主引擎，避免与现有 GSAP/原生动画重复。
5. **动效要可关闭、可中断、可回收**：遵守 `prefers-reduced-motion`，不劫持滚动，不用动画伪造财务数字变化。

## 逐站学习与 aJay 转译

### 1. MotionSites

来源：
- https://motionsites.org/
- https://motionsites.org/prompts/data-storytelling-platform
- https://motionsites.org/prompts/spatial-mapping-platform

学到的重点：
- 先定义页面方向、首屏任务与完整 page map，再决定视觉效果；避免生成器随意堆出 Hero、卡片和装饰区。
- Data Storytelling 方向强调 full-bleed、深色基调、数据界面和“production-minded spacing”。
- MotionSites 的完整提示词含免费与单用户授权内容；本项目只吸收公开设计逻辑，不复制受限提示词。

用于 aJay：
- 把首页改成“投资结论控制台”，首屏必须同时出现研究对象、核心判断、置信度、更新时间和下一步入口。
- 金融中心照片使用全宽或贯穿式构图，但与当前章节内容绑定；切换城市不得改变分析内容。
- 每一大章先写任务句，再放界面：例如“估值是否有安全边际？”后接估值带、敏感性和证据。

### 2. React Bits

来源：
- https://www.reactbits.dev/get-started/index
- https://pro.reactbits.dev/docs/blocks/hero-section
- https://pro.reactbits.dev/docs/blocks/features
- https://pro.reactbits.dev/license

学到的重点：
- 将效果按 Text Animations、Animations、Components、Backgrounds 分层，适合建立“文字/结构/背景”三档动效预算。
- Scroll Reveal、Scroll Stack、Animated Content、Accordion Gallery、Staggered Menu 等模式可拆解复用，不必整体迁移 React。
- Hero 与 Feature 的高质量版本依赖清晰字阶、索引式模块和编辑式网格，不依赖炫技背景。
- Pro 组件受许可约束；只学习交互模式，未获得许可的代码不进入项目。

用于 aJay：
- 章节标题做一次性、低幅度 reveal；正文和表格不逐字飞入。
- 模型区采用索引式工作台：左侧模型目录，右侧假设、结果、敏感性与证据联动。
- 评委观点使用可展开结构，默认显示结论和关键数字，深层推理按需展开。

### 3. Uiverse

来源：
- https://uiverse.io/

学到的重点：
- Uiverse 的价值在微交互与完整控件状态，而不是整页视觉方向。
- 同一类控件可快速比较 hover、focus、loading、success、disabled 等细节。
- 站内 UI 元素注明 MIT 许可，但实际采用时仍需记录作者、来源和改造范围。

用于 aJay：
- 统一按钮、标签、筛选器、搜索框、证据入口的状态语言。
- 导出、复制链接、加载证据等操作必须明确显示进行中、成功或失败，避免用户猜测。
- 拒绝把玻璃、霓虹、3D 按钮和发光描边当成金融高级感。

### 4. Anime.js

来源：
- https://animejs.com/documentation/
- https://animejs.com/documentation/timeline/
- https://animejs.com/documentation/getting-started/module-imports/

学到的重点：
- Timeline 适合协调多个有因果关系的状态变化；Scope 适合组件化清理与响应式行为；WAAPI 适合轻量 opacity/transform 动画。
- 模块化导入可减少无关代码，不需要为一个淡入加载整套能力。
- 动画引擎应暂停隐藏标签页中的非必要动画，并尊重媒体查询。

用于 aJay：
- 只为“章节进入 → 关键结论 → 证据标记”建立短 timeline。
- 上海纵向塔楼、纽约街谷、伦敦金融区、香港维港分别使用不同的滚动关系，避免统一 parallax 模板。
- 数值最终态必须由真实数据直接渲染；动画只改变呈现，不改变含义。

### 5. Aceternity UI

来源：
- https://ui.aceternity.com/components
- https://ui.aceternity.com/components/sticky-scroll-reveal
- https://ui.aceternity.com/components/stateful-button

学到的重点：
- Sticky Scroll Reveal 把滚动中的文本步骤与固定视觉区绑定，适合解释连续研究逻辑。
- Stateful Button 把 loading → success 明确做成同一控件的状态机。
- Expandable Card、Animated Modal、Tabs、Timeline、Compare 等结构适合报告功能；Aurora、Meteors、Sparkles、Infinite Moving Cards、3D wobble 等更适合营销展示。

用于 aJay：
- 上海章节使用“垂直城市构图 + 滚动研究注释”，其他城市按自身构图设计，不复制同一动画。
- 证据详情使用可访问的 modal/drawer；估值假设用 compare；导出和分享使用 stateful button。
- Sticky 结构必须有自然退出点，窄屏改为普通文档流，避免滚动被困。

## 下一轮实施约束

### 建议采用

- 城市影像：构图驱动的滚动叙事，而非城市标签照片墙。
- 页面骨架：编辑式大标题 + 研究任务句 + 高密度工作台 + 渐进披露。
- 模型区：固定索引、主动状态、证据抽屉、比较视图。
- 微交互：120–240ms 为主，优先 `opacity`、`transform`、遮罩和细线进度。
- 可访问性：键盘焦点、语义按钮、减少动效模式、对比度、无 scroll hijack。

### 明确舍弃

- Emoji 充当功能图标。
- 全站套同一套滚动动画。
- 光标追踪、磁吸按钮、无限跑马灯、星空粒子、霓虹玻璃卡片堆叠。
- 为了使用 React 组件而重写当前报告渲染链。
- 同时加载 GSAP、Motion 和 Anime.js 处理同类效果。

## 拟应用到当前报告的五处

1. **首屏**：结论、置信度、时间戳和阅读路径同屏，城市影像退为有叙事作用的环境层。
2. **城市背景**：纽约做街谷纵深，上海做垂直揭示，伦敦做横向建筑节奏，香港做水岸层次与灯光远近；城市切换只更换氛围。
3. **投资委员会**：人物作为汇报者而不是头像列表；当前发言者、观点冲突和证据出处形成一个工作流。
4. **模型工作台**：DCF/LBO/情景/敏感性不再平铺，改为索引导航和渐进披露。
5. **证据与操作**：证据抽屉、搜索、筛选、导出、复制链接拥有完整状态反馈。

## 第二轮学习与 V5 转译（2026-09-09）

本轮针对“动效不足、数据表过于普通、模型中段突然变白”重新检查了 MotionSites 的 data-storytelling page map、Anime.js 的 `onScroll`、Aceternity 的 Sticky Scroll Reveal / Stateful Button / Canvas Reveal，以及 React Bits 的 Spotlight Card 模式。落地仍使用项目已有 GSAP + 原生 `IntersectionObserver`，不再并行引入第二套动画运行时。

实际采用：

- 首屏以短时间轴依次呈现研究对象、结论边界、证据和阅读路径；不做数字从 0 递增。
- 图表进入视口时只绘制折线与柱形视觉标记，文本数字从一开始就是最终值，避免动画制造假行情。
- 表格自动升级为机构工作台表面：粘性表头、等宽数字、列内强度条、正负号状态和行聚焦；保留原表文字与 DOM 语义。
- 卡片、证据记录与模型补充采用一次性层级 reveal；细粒度鼠标只增加低透明度聚光，触屏不运行。
- 模型章节改为午夜蓝—石墨的连续背景，起点承接上海章节，终点接入香港章节；只有整站切换浅色主题时才变为浅色模型区。
- 所有新增动效都服从 `prefers-reduced-motion`，窄屏直接呈现主要内容，不依赖动画理解报告。

明确未采用：Canvas 粒子、无限循环、磁吸跟随、数字滚动、自动切城、把整页迁移为 React 组件库。
