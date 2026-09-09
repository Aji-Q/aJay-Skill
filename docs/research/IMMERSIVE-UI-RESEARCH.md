# aJay 沉浸式金融报告 UI 调研与可实施方案

**调研日期：** 2026-09-09
**对象：** `AJAY.DEMO_20260909/full-report-standalone.html` 的下一版信息架构与交互方向
**范围：** 公开官网的只读浏览、官方产品/年报页面、Awwwards 线索页及本地已有 UI 研究；未操作 root 的预览标签，未复制外部源码、品牌、文案或素材，未修改报告模板。

> 这份文档是给实现者的结构方案，不是 moodboard。每个案例区分“浏览观察”和“转译推断”。外部页面只作为交互与信息组织的观察样本，不构成代码、图片、字体或商标的授权。

## 1. 先给结论：把报告做成一场可主持的私人投委会

推荐的核心隐喻是 **Decision Room / 私人投委会**：用户进入一间位于全球金融中心的研究室，先看一个待裁决的问题，再听一位主讲人的判断，同时看到最强反证，最后一键打开证据底稿。城市负责空间、光线和章节转场；人物负责方法论视角；数据和证据始终是裁决依据。

这不是：

- 圆桌加一圈会发光的头像；
- 66 张人物卡、emoji、投票动画或“专家排行榜”；
- 3D 地球、粒子、股价跑马灯替代表格；
- 把现有长页换成更大的夜景后继续罗列。

**第一版最重要的改变是版式而非特效：** 每个视口只保留一个视觉舞台、一个待回答的问题、一个主讲人、一个明确反证入口和一组可核对的数据。人物可以增加到 4–6 位跨流派角色，但初始场景只展示与当前问题有关的 1 位主讲人和 1 位反对者，其余进入可检索的观点档案，不制造噪声。

## 2. 研究方法与证据等级

- **观察：** 在 2026-09-09 以只读方式打开当前官网/报告页面，记录可见的导航、层次、媒体、滚动和数据呈现；Awwwards 只用于发现候选，再打开实际官网。
- **推断：** 从上述结构提炼可迁移的规则；推断不是外部站点的设计意图，也不表示 aJay 应复制其视觉。
- **采用：** 针对 aJay 的页面、数据契约和移动端约束给出的落地建议。

现有本地文档仍是品牌与数据边界的权威：[`docs/UI-SKILL-RESEARCH.md`](../UI-SKILL-RESEARCH.md)、[`docs/brand-spec.md`](../brand-spec.md)、[`docs/OWNERSHIP.md`](../OWNERSHIP.md)。本方案沿用黑曜石、深海军蓝、金属银和金融城市夜景，不重新引入普通 SaaS 卡片网格或暖色自然主题。

## 3. 五个主要案例

### 3.1 Globalance World：一个空间舞台承载多种数据视图

**来源：** [Globalance World 官方平台](https://fe.globalanceworld.com/)、[About Globalance World](https://fe.globalanceworld.com/about)、[European Design Awards 案例](https://awards.europeandesign.org/winner/242650)。

**浏览观察**

- 官方平台把 `PORTFOLIO / CREATE / COMPARE / SEARCH` 放在同一主导航，下面再切换 `World Impact View / Assets City View / Assets Map View`。
- 主题轨道把 `Climate / Footprint / Megatrends / Net Return` 作为同一数据集合的观察角度；中心舞台显示世界、城市化资产图或地图，而不是把每个指标拆成卡片。
- City View 下面仍有资产列表、组合权重、升温潜势、数据来源和“只可视化组合的一部分”等说明。空间图不是表格的替代品，表格是可核对的第二层。
- Awards 页面把其概念称为面向投资者的 “Google Earth”，并记录 3D globe、Pebble shape 及把复杂数据转为可行动界面的做法。

**转译推断**

aJay 可以借用“一个舞台、多个视图、同一数据契约”的关系，而不是借用地球或 3D 视觉。地点切换可对应 `Room / City / Evidence` 三种阅读状态：背景和构图变，标的、数值、日期和证据 ID 不变。每个空间数据点必须能打开下方语义表或证据抽屉；页面始终显示 `Data source / As of / DEMO or data gap`。

**采用**

- 右侧 rail：`Brief / Evidence / Assumption / Gap`；中心只放当前主张需要的图表或模型。
- 用 2D SVG/HTML 图形做主读图，必要的“空间感”由摄影、遮挡和层次完成，而不是把 3D 当作金融含义。
- 把 `Compare` 改成同一议题的 `For / Against` 对照，避免虚假的专家投票。

### 3.2 Norges Bank Investment Management：沉浸感也必须能像年报一样阅读

**来源：** [NBIM Annual Report 2024 web report](https://www.nbim.no/en/news-and-insights/reports/2024/annual-report-2024/web-report-annual-report-2024/)。

**浏览观察**

- 页面有清晰的报告标题、面包屑、全局搜索和菜单；`Results`、`Investments` 等大章节下面还有嵌套层级。
- `Key figures` 之后是大幅视觉/留白与长段落，随后进入表格、图表和注释链接；叙事与核对资料在同一连续页面，不把数据锁在画布里。
- 章节导航可以展开，读者可定位到深层内容；报告仍然像一份可回看、可引用的正式文档。

**转译推断**

沉浸式页面不应该牺牲连续阅读。aJay 需要保留真正的 `View as Document`，让用户可以跳过场景动效，按章节、表格、公式和披露阅读；舞台只是对连续文档的空间化入口，而不是唯一入口。

**采用**

- 顶部固定简栏：aJay、标的、报告日期、数据快照、`Document view`、搜索。
- 左侧议程只保留 5 个停靠点；每个停靠点可展开其底层模块和现有 section ID。
- 大图转场之后立即出现具体标题、数值单位、数据时期和来源，不让摄影占据一整个“无信息”屏幕。

### 3.3 J.P. Morgan Guide to the Markets：人物是叙述层，不是数据的替身

**来源：** [Guide to the Markets 官方数字阅读器](https://am.jpmorgan.com/us/en/asset-management/institutional/insights/market-insights/guide-to-the-markets/)、[J.P. Morgan 官方 AR 新闻稿（历史案例）](https://am.jpmorgan.com/us/en/asset-management/institutional/about-us/media/press-releases/jp-morgan-asset-management-launches-new-guide-to-the-markets-mobile-based-augmented-reality-ar-experience/)。

**浏览观察**

- 当前阅读器提供按标题/slide number 搜索，按 `Introduction / Equities / Economy / Fixed Income / International / Alternatives / Investing Principles / Disclosures` 分组，并支持 `Single slide / Section / Fullscreen`。
- 有 `Create custom guide`、收藏、前后页、下载/分享、`Slide sources and disclaimers` 等显式动作；这使“沉浸式阅读”仍然可以被检索和引用。
- 2021 年官方新闻稿曾描述基于浏览器的移动 AR、Dr. David Kelly 的全息讲解、3D 可视化和数据表。它是**历史上的官方产品案例**，不表示今天的页面仍提供同样 AR 功能。

**转译推断**

人物可以像一个受控的播报层：在章节开头用大幅肖像和一句方法论提示建立在场感，进入数字阅读后缩为边缘肖像、文字 transcript 和“打开证据”。不要让头像点击改变分数，不要让模拟角色看起来像真实背书。

**采用**

- 人物卡改成 `speaker / transcript / evidence` 三联关系：姓名、模拟角色标签、具体论点、来源/依据在同一上下文。
- `For / Against`、`Next issue`、`Open evidence` 是明确按钮；不使用自动轮播或“共识环”。
- 深度阅读提供 `Single scene / Section / Full document` 三种模式；所有引用可回到原议题位置。

### 3.4 Apple Vision Pro：每个章节只有一个主场景

**来源：** [Apple Vision Pro 官方产品页](https://www.apple.com/apple-vision-pro/)。

**浏览观察**

- 页面用全幅媒体和很少的文字建立 section：hero、设计、娱乐、生产力、照片/视频、连接、apps、visionOS、技术和价值；本地导航在长页面中保持可见。
- “Take a closer look” 等段落通过前后切换的媒体 gallery 展开细节；滚动时一个媒体场景占据主要视口，文本在其附近有清楚的进入/离开节奏。
- 媒体加载/播放状态会影响交互；观察到的某些媒体控件在当前浏览器自动化状态下不可播放，因此这里只采用结构观察，不把视频可用性当作保证。

**转译推断**

aJay 每个议题只需要一个主场景：例如上海清晨、纽约夜间、模型桌面、辩论档案、风险地平线。滚动只推进该场景的少量状态，不能同时让背景、人物、数字、图表和标题各自独立飞舞。

**采用**

- 桌面：固定舞台约占 55–65% 宽度，右侧 30–35% 为阅读 rail；媒体有静态首帧。
- 场景切换用 opacity/translate/crossfade 和局部 SVG 绘制，不用全屏滚轮劫持。
- 断网、低性能或媒体失败时，标题、人物 alt、图表和数据表仍完整可用。

### 3.5 NASA Exoplanet Travel Bureau：地点是可选择的旅程，而非随机背景

**来源：** [NASA Exoplanet Travel Bureau 官方沉浸式页面](https://science.nasa.gov/exoplanets/immersive/exoplanet-travel-bureau/)。

**浏览观察**

- 页面以 “Take a trip outside our solar system” 开场，用 `6000+ confirmed exoplanets`、`8 destinations` 建立尺度，然后进入 `Tour the Galaxy`。
- 每个目的地有海报式封面、`Take a Guided Tour`、语言选择、`Explore the Surface`、下载海报等路径；往下滚动时，左侧叙述、右侧大图/媒体形成导览节奏。
- 页面明确支持读者阅读或打开声音，文本和导览并存；地点选择先于细节探索。

**转译推断**

这适合 aJay 的“全球金融中心”作为章节选择器：先选上海/纽约，再进入同一份研究的某个议题。地点改变空间语境，不改变研究事实。导览要可暂停、可跳过、可用文字完成；不能把滚动变成必须观看的电影。

**采用**

- 首屏是 `Enter committee`，随后 `Shanghai / New York` 两个可见入口；London/Hong Kong 仅在有相应资产和内容时加入。
- 目的地页使用 1 张大场景 + 2–3 个阅读 beats + `Deep dive`，不用四城四张相同 skyline 卡片。
- 旁白若加入，默认静音、用户主动播放、同步 transcript 和字幕；不把声音作为数值或风险说明的唯一渠道。

## 4. 补充线索：Awwwards 只作发现入口

**Pacific Partners** 是一个可供观察长页节奏的实际官网，而非 aJay 的数据交互模板。

- 发现线索：[Awwwards — Pacific Partners](https://www.awwwards.com/sites/pacific-partners)，页面记录了 `Scrolling / Single page / Transitions / 3D / UI design / next.js` 等标签，并提供 homepage、horizontal stats、mouse interaction、transition 等片段入口。
- 实际官网：[Pacific Partners](https://pacificpartners.com/)。其主张是 “Innovation meets discipline”，用 `Access / Experience / Network` 和五类基金方向推进纵向叙事，而不是堆满产品卡片。

**可取的是**“一个观点接一个观点”的纵向节奏、强 statement 和有序的基金类别；**不采用的是**把 Awwwards 标签当成成熟金融数据交互的证明，也不下载/复制其 Next.js、3D、动画或视觉资产。任何实现依赖都要单独做版本与许可证核查。

## 5. aJay 的目标 IA：五个房间、八个现有 section 的兼容映射

### 5.1 五个顶层停靠点

| 停靠点 | 用户要回答的问题 | 主舞台 | 必须同屏可见 |
|---|---|---|---|
| 01 Arrival / Chair’s Brief | 这份研究现在要裁决什么？ | 城市空间 + 主讲人近身肖像 + 一句 thesis | 标的、快照时间、研究状态、3 个关键数、`Open evidence` |
| 02 Evidence Room | 这句话由什么事实支持？ | 关键图表/指标/价格与财务证据 | 支持依据、最强反证、来源/日期/数据缺口 |
| 03 Model Floor | 假设变动会怎样？ | DCF/机构模型/情景范围 | 当前假设、单位、方法、可回到原值的控件 |
| 04 Debate Archive | 哪些方法论会反对它？ | 1 位主讲人 + 1 位反对者 + transcript | `For / Against`、角色为模拟视角、对应证据入口 |
| 05 Risk Horizon | 在什么条件下判断失效？ | 风险区间、情景/触发条件、zones timeline | 风险条件、缺失项、更新时间、最终披露与来源 |

### 5.2 与现有模板的兼容关系

不要求组装器立即重写数据。先把已有 8 个 section 放进 5 个“场景容器”，保留可定位的语义 ID、注入点和回退状态：

- `section-core` → `Arrival / Chair’s Brief`；
- `section-scan` → `Evidence Room`；
- `section-modeling` → `Model Floor`；
- `section-clash`、`section-jury`、`section-chat` → `Debate Archive` 的不同阅读 beats；
- `section-risks`、`section-zones` → `Risk Horizon`。

`INJECT_*` 数据注入、缺失/不适用状态、`AJAY.DEMO`、分数状态、术语解释、分享/导出 ID 应继续工作。改变的是外层阅读顺序和呈现，不是把数据重新编造成动画文案。

### 5.3 桌面主视图

```text
┌──────────────────────────────────────────────────────────────┐
│ aJay · 标的 · 2026-09-09 · DEMO · Document · Search          │  固定简栏
├───────┬──────────────────────────────────────┬───────────────┤
│ 议程  │                                      │               │
│ 01    │   城市/室内空间（静态首帧或轻转场）    │  阅读 rail    │
│ 02    │                                      │  What it says │
│ 03    │ 主讲人肖像  →  当前待裁决问题          │  3 numbers    │
│ 04    │ 反对者小幅肖像 + 最强异议              │  Evidence     │
│ 05    │      图表/模型/关键依据                │  Source/As of │
│       │      Open evidence                    │  Gap/Method   │
└───────┴──────────────────────────────────────┴───────────────┘
```

- 肖像不要放入圆环或虚拟桌面；人物的身体方向、边缘裁切和城市前景共同建立空间关系。
- 主讲人可以比反对者大，但反证入口不能藏在下一层。分数只作为状态/结果之一，不用巨大圆环或自动计数抢过问题。
- 右侧 rail 每次只显示一件事：解释当前图表、列出来源，或打开一段方法。长文本自然滚动，舞台不遮住数据。

### 5.4 人物与数据共存

1. 首屏：Buffett/Simons 或新增角色之一作为**模拟方法论主讲人**，显示角色标签与具体论点，不使用泛化名言。
2. 同一议题：另一个角色作为最强反对者，直接露出一条可核对的反证摘要。
3. 点击人物：打开 60–70% 宽的 transcript/evidence drawer，包含原始数据、日期、计算路径、缺口和“不是本人观点或背书”的声明。
4. 点击证据：反向高亮人物当前论点，但不改变 score、不制造独立投票。
5. 其余角色：进入按方法论/议题检索的 `Debate Archive`；无意见或不适用明确显示，不以 0 分填位。

## 6. 地点、章节和导航

### 地点切换

首版使用已有 `Shanghai` 和 `New York` 资产；London/Hong Kong 只有在对应空间素材和章节内容准备好后再加入。地点按钮采用明确的 segmented control 或菜单，不绑定滚轮，也不声称切换了实时交易时段。切换地点只改变背景、光线、少量章节标签与空间声学；**不改变当前议题、人物选择、数字、数据时期和证据 ID**。

### 导航

- 顶栏：aJay、标的、报告日期、`AJAY.DEMO`/数据状态、`Document view`、搜索/分享。
- 左侧 itinerary：5 个停靠点，当前项有 `aria-current`；可键盘 Tab 到达，点击直达；不把所有旧小节挤成一排。
- rail 内：`Open evidence`、`Open full table`、`Method`、`Disclosure`；关闭抽屉后恢复原议题、人物和焦点。
- 提供 `Copy link to issue` 或本地锚点，深链应回到议题而非总是回到首屏。
- 手机将 itinerary 改成底部 5 项导航或横向可滚动文字条；不能只靠 hover 或图标猜含义。

## 7. 逐层阅读：Brief → Evidence → Method → Disclosure

默认层级让非专业读者先抓住结论，专业读者不必来回找底稿：

1. **Brief：** 一句话判断、支持/反对各一条、最多 3 个关键数字；每个数字带单位与时期。
2. **Evidence：** 图表、语义表或原始指标；显示数据源、`As of`、选择范围、缺失项；允许打开完整表格。
3. **Method：** 公式、假设、敏感性、模型输入；数值控件只在用户主动操作时更新。
4. **Disclosure：** 合成数据、模拟人物、启发式 score、非投资建议、版本和已知缺口。

每层都用真实 `details`/button/anchor，避免把重要内容放在仅有动画的 canvas 中。所有关键论点从 `Open evidence` 到来源最多一次操作；来源页能回指议题。

## 8. 动效与可复用实现依赖

### 8.1 分阶段依赖选择

| 能力 | 推荐实现 | 使用边界 | 官方资料 |
|---|---|---|---|
| 场景 pin/scrub/轻微 snap | GSAP + ScrollTrigger（可选） | 只控制场景状态和少量 SVG 路径；不用滚轮劫持；先核对版本/许可证 | [ScrollTrigger Docs](https://gsap.com/docs/v3/Plugins/ScrollTrigger/) · [官方安装/下载页](https://gsap.com/docs/v3/Installation/) · [官方标准许可](https://gsap.com/standard-license/) |
| 原生滚动驱动 | CSS `animation-timeline` / `view-timeline` | 作为渐进增强；必须有普通流式布局和 feature-detect fallback | [MDN Scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations)、[W3C Scroll Animations](https://www.w3.org/TR/scroll-animations-1/) |
| 关联图表/刷选 | D3 + SVG `brush` | 2D marks、直接标签、键盘/表格回退；不把 3D 轴当作主数据解释 | [D3 brush](https://d3js.org/d3-brush) |
| 分段进入 | 原生 `IntersectionObserver` + CSS opacity/transform | 只揭示下一段，避免全页粒子与数字跳动 | [MDN IntersectionObserver](https://developer.mozilla.org/en-US/docs/Web/API/IntersectionObserver) |
| 低动效 | `prefers-reduced-motion` + 静态首帧 | 关闭 pin、scrub、自动转场；恢复正常文档流 | [MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion) |

**建议优先级：** Phase 1 不引入新库，用现有 HTML/CSS、inline SVG、IntersectionObserver 完成五场景版式；Phase 2 只有在浏览器验收证明需要时再加 GSAP 或 D3。单文件离线报告不依赖 CDN；若加库，锁定版本、检查许可证并打包本地。

**GSAP 具体落地与许可证核查：** 官方安装页列出 `npm install gsap`、script/zip 下载，以及 `minified/`、`UMD/`、`ESM/`、`src/` 目录；同页说明插件应显式 `registerPlugin`，旧版本从 [GreenSock/GSAP Releases](https://github.com/greensock/GSAP/releases) 下载。当前官方 [Standard “No Charge” GSAP License](https://gsap.com/standard-license/)（页面重定向至 `/community/standard-license/`）的有效日期和限制应在锁版本时重新核对：它允许网站、web app 和数字界面使用，商业使用 FAQ 也明确为免费，但禁止未经书面同意将其用于与 Webflow 可视化动画构建能力竞争的无代码视觉动画工具，且不能移除专有声明。aJay 是本地报告，不是动画构建器；仍应把许可正文随依赖记录在 `NOTICE`/依赖清单中，不把“免费”当作不需归档。原始获取入口：[`gsap.com/docs/v3/Installation/`](https://gsap.com/docs/v3/Installation/)、[`npmjs.com/package/gsap`](https://www.npmjs.com/package/gsap)、[`github.com/greensock/GSAP`](https://github.com/greensock/GSAP)。

### 8.2 动效规则

- 每个场景滚动长度约 1–1.5 个视口，舞台固定时 rail 仍自然滚动；不锁住全页。
- 一次只动一个主变量：背景 crossfade、人物进入、图表高亮三者不能在同一拍全部飞入。
- 数值不做自动从 0 数到目标；只有用户改变模型假设时才更新，并保留原值/新值标识。
- 风险红/绿只表达语义状态，不用发光、闪烁或市场 ticker 伪造紧迫感。
- 不默认播放环境音；旁白需用户主动播放、字幕和 transcript 同步，声音关闭也能完成阅读。

## 9. 手机降级不是缩小桌面

以 390×844 为一等目标：

- 每个视口只有一张静态或轻量背景图；不固定 boardroom，不保留多列舞台。
- 顺序为：主讲人 4:5 裁切 → 待裁决问题 → 反对者摘要 → 关键数/图表 → `Open evidence` → 下一议题。
- 右 rail 改成全宽底部 sheet 或原生 `details`；关闭后回到触发点，Esc/返回键可用。
- 人物头像不能依赖 hover；至少 44px 点击区，并显示姓名、角色、当前议题。
- 表格允许横向滚动且首列 sticky；旁边提供可读文本摘要；图表轴、单位、注释不因缩放消失。
- 顶部 5 项 itinerary 变成底部导航或有文字的横向条；始终提供 `View as Document`。
- `prefers-reduced-motion` 默认给静态阅读流，避免移动设备耗电和跳动。

## 10. 金融理解、真实性和可访问性验收

### 内容验收

- 首屏十秒内能回答：标的是什么、当前待裁决问题是什么、最强支持/反对各是什么。
- 每个场景同屏有 `What this means`、`Source`、`As of`、`Data gap/DEMO`；合成数据和角色模拟不借肖像权威感隐去。
- 每条人物观点可以一键打开对应证据、原值、日期、计算和缺口；不允许所有按钮都通向一个通用资料区。
- 事实、假设、模拟观点、启发式 score、缺失/不适用必须有不同的文字和状态，不用 0 代替未知。
- 保留当前模板的目录、聊天/角色筛选、术语提示、风险状态、分享/导出 ID 和注入契约；视觉重排不能静默丢数据。

### 视觉与交互验收

- 1440×900：第一屏有标题、议题、地点、主讲人、真实反证和证据入口，不是空夜景或免责声明墙。
- 1024×768：rail 可收折但不隐藏关键数字；人物和图表不互相遮挡。
- 390×844：无横向整页溢出；肖像、反证、图表/表格与 `Open evidence` 在自然纵向流中可读。
- 键盘：议程、人物、证据、折叠和关闭按钮可 Tab；焦点可见；Esc 关闭 drawer；`aria-current`/标题层级正确。
- 低动效：不 pin、不 scrub、不自动轮播；静态首帧和完整文档仍可用。
- 性能：首屏只加载一张主背景和必要肖像；下方媒体 lazy-load；图片失败时仍有姓名、论点、表格和 alt。

## 11. 实现顺序（给 root 的直接工作单）

### Phase 1：重排根本布局

1. 将 8 个现有 section 映射到 5 个场景容器，保留所有 data/inject ID。
2. 新建固定顶栏、5 项 itinerary、`View as Document` 和 evidence drawer；先不用 3D 和新动画库。
3. 首屏改为“主讲人 + 问题 + 同屏反证 + 3 个数 + evidence link”，移除 emoji、重复分数动效、紫色兜底条和普通卡片墙。
4. 用现有 Manhattan/Shanghai 背景与 Buffett/Simons 肖像验证构图；先验证人物/数据语义，再补充人物和城市素材。
5. 在 1440/1024/390 三档做浏览器截图、键盘和 console 回归；桌面/手机都保留完整文档路径。

### Phase 2：只为理解增加动效

1. 用 IntersectionObserver 或 CSS scroll-driven 做章节淡入和背景切换。
2. 若固定舞台的节奏确实需要，再加入本地打包的 GSAP ScrollTrigger；若需要关联高亮，再加入 D3/SVG brush。
3. 为每个动效准备 reduced-motion 和媒体加载失败路径；重新核对表格、单位、数据时期和来源。
4. 最终再决定是否扩展 London/Hong Kong 以及 4–6 位人物；不先用资产数量掩盖版式问题。

## 12. 来源与使用边界

### 主要案例

- [Globalance World](https://fe.globalanceworld.com/) · [About](https://fe.globalanceworld.com/about) · [European Design Awards case](https://awards.europeandesign.org/winner/242650)
- [NBIM Annual Report 2024 web report](https://www.nbim.no/en/news-and-insights/reports/2024/annual-report-2024/web-report-annual-report-2024/)
- [J.P. Morgan Guide to the Markets](https://am.jpmorgan.com/us/en/asset-management/institutional/insights/market-insights/guide-to-the-markets/) · [2021 AR press release](https://am.jpmorgan.com/us/en/asset-management/institutional/about-us/media/press-releases/jp-morgan-asset-management-launches-new-guide-to-the-markets-mobile-based-augmented-reality-ar-experience/)
- [Apple Vision Pro](https://www.apple.com/apple-vision-pro/)
- [NASA Exoplanet Travel Bureau](https://science.nasa.gov/exoplanets/immersive/exoplanet-travel-bureau/)

### 补充案例与实现资料

- [Awwwards — Pacific Partners](https://www.awwwards.com/sites/pacific-partners) · [Pacific Partners official site](https://pacificpartners.com/)
- [GSAP ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/) · [官方安装/下载](https://gsap.com/docs/v3/Installation/) · [官方标准许可](https://gsap.com/standard-license/) · [npm 包](https://www.npmjs.com/package/gsap) · [官方 GitHub](https://github.com/greensock/GSAP) · [版本发布](https://github.com/greensock/GSAP/releases)
- [MDN Scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations) · [W3C Scroll Animations](https://www.w3.org/TR/scroll-animations-1/)
- [D3 brush](https://d3js.org/d3-brush) · [MDN IntersectionObserver](https://developer.mozilla.org/en-US/docs/Web/API/IntersectionObserver) · [MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- 本地方法与边界：[UI-SKILL-RESEARCH.md](../UI-SKILL-RESEARCH.md) · [brand-spec.md](../brand-spec.md) · [OWNERSHIP.md](../OWNERSHIP.md)

以上页面和案例仅用于观察信息架构、空间叙事、导航、媒体降级和动效线索。不要把官网截图、人物图、字体、原始代码或第三方 Awwwards 视觉误认为 aJay 可直接复用的素材；实际依赖在进入项目后仍需单独确认版本、许可证、离线打包方式和浏览器支持。
