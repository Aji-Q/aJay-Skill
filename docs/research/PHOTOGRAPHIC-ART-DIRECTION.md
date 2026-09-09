# aJay 摄影艺术指导：全球金融中心的真实在场感

**研究快照：** 2026-09-09
**用途：** 为 aJay 研究报告页面提供真实建筑摄影方向、城市场景 prompt、人物肖像扩展与可追溯素材来源。
**范围：** 只做视觉研究和生成提示词，不下载图片、不改前端代码。

---

## 0. 先给结论

当前宽幅 skyline 的问题不是“城市不够壮观”，而是**把金融中心拍成一张脱离身体尺度的城市海报**：没有可站立的地面、没有遮挡或前景、没有真实曝光取舍，窗格和反射过于整齐，容易出现 AI 城市图的油腻感。

### 最推荐的架构：`Observed Capital Cities / 被观察的资本城市`

1. **主 Hero：Manhattan 低机位街景，不再使用水面全景。** 以湿石路、历史建筑立面和远处 One World Trade Center 的玻璃体量组成前—中—后景；建筑占画面约 55%，前景保留足够可呼吸的暗部，标题由网页叠加。
2. **四城不是四张相同全景，而是四种“进入建筑的方式”：**
   - Manhattan：街道尺度、湿地面、低机位仰视。
   - London：站在覆盖式步行拱廊/入口内，透过湿玻璃看 City；古老街道与现代金融办公空间重叠。
   - Shanghai：从陆家嘴塔楼的中庭/裙房向上看双层幕墙和多层空间；用仰拍的结构，而不是黄浦江全景。
   - Hong Kong：站在 Central 的高架步行系统或室内前厅，透过雨痕玻璃、栏杆和幕墙看 Two IFC；用压缩的层次表达密度。
3. **统一摄影语言：** 全画幅三脚架/稳定支撑、35/50/85mm 为主、建筑垂直线校正、蓝调时刻或真实夜间长曝、受控高光、轻微真实瑕疵；保留三个深度平面和人类尺度。避免超广角、统一点亮窗格、HDR 光晕、霓虹赛博朋克、漂浮图表和完美 CGI。
4. **人物扩展：** 以 Buffett 与 Simons 现有的纵向 2:3 黑白银盐质感为母版，增加 8 位跨时代、跨流派投资人物。每张统一为“AI 生成肖像 · 方法论模拟 · 不代表本人观点或背书”，不能让人物像是在为 aJay、某只股票或某个产品作证。

### 不可误读的素材声明

`docs/IMAGE-PROVENANCE.md` 已明确：当前 Manhattan/Shanghai 夜景与庭院图均为 AI 生成的摄影质感素材，不是实地拍摄、不是具体建筑的事实证据。`docs/BUFFETT-PORTRAIT-PROVENANCE.md` 和 `docs/SIMONS-PORTRAIT-PROVENANCE.md` 也明确两张人像是 AI 生成艺术化肖像，不是历史照片或人物背书。本文件的真实摄影术语是**给 image_gen 的物理约束和美学目标**，不是把生成图伪装成实拍。

---

## 1. 已有图像审阅：保留什么、修正什么

### 1.1 Buffett / Simons 的有效母版

已目视审阅：

- `skills/deep-analysis/assets/ajay-brand/buffett-portrait.png`
- `skills/deep-analysis/assets/ajay-brand/simons-portrait.png`

两张图的可复用优点：

- 纵向 **2:3**，胸像或上半身，不靠夸张环境讲故事。
- 深炭黑摄影棚背景，背景没有物件、标题、logo、图表。
- 黑白银盐方向：黑位深但不糊，银灰中间调丰富，皮肤纹理、皱纹、胡须/头发细节可见。
- 单一方向性 key light，眼睛有克制的 catchlight，阴影侧有少量填充。
- 服装简洁，面部和眼神是焦点；没有“演讲台”“基金牌子”“股票图”等背书暗示。

### 1.2 需要与城市图保持的同一性

- **黑位：** 用炭黑/午夜蓝承接肖像背景，但城市图不应全部压成黑色；主体建筑要保留可读的立面纹理。
- **银色：** 让金属边缘、玻璃窗格和城市湿反射承担银色，而不是叠加金属渐变。
- **光线：** 肖像是一盏方向性主灯；城市图则以可解释的现实光源（路灯、室内灯、幕墙反射、车灯）形成主次关系。
- **克制：** 保留自然噪点和局部不完美，但每张图最多加入 3–4 个瑕疵线索，不能用脏乱来“证明真实”。

---

## 2. 研究结论：真实建筑摄影为何有空间在场感

### 2.1 垂直线不是装饰，而是摄影机位置的证据

Nikon 对 PC（Perspective Control）镜头的说明强调：建筑摄影可通过 tilt/shift 保持平行线，摄影机应保持与建筑面垂直；shift 也能在不移动机位时重新构图、排除前景干扰或拍摄多张拼接。这是本项目拒绝“向上仰拍后再强行拉直”的关键依据。参考：[Nikon USA — The PC Lens Advantage](https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/the-pc-lens-advantage-what-you-see-is-what-you-get)。

**落地规则：**

- 城市外景：优先 35mm 或 50mm；画面越高，越需要 tilt-shift/透视校正。
- 室内高层：保持相机水平，先找结构线，再用 shift 取景；不把天花板拉成扇形。
- 如果生成 prompt 中写“tilt-shift”，同时写“camera level / parallel verticals / no keystone distortion”，否则模型可能只生成一个风格词。
- 允许轻微真实的镜头边缘暗角，但不允许边缘建筑被拉伸或重复。

### 2.2 夜景的可信度来自曝光取舍

Nikon 的夜景指南建议三脚架支撑长曝，夜景可以使用 1、10、30 秒等曝光配合小光圈获得灯轨和细节；使用三脚架时关闭镜头 VR。参考：[Nikon USA — Taking Pictures at Dusk and at Night](https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/taking-pictures-at-dusk-and-at-night)。

**落地规则：**

- 不把所有窗格都提升到同一亮度；高层办公室允许黑窗、半亮窗和少量过曝灯具并存。
- 不把夜空打成纯黑渐变；保留深蓝、薄雾和城市光污染的层次。
- 让路灯或 LED 招牌出现受控高光，但不允许白色光源形成 HDR 晕圈。
- 生成图可写“single exposure look, highlight-preserving exposure, restrained bloom”，比“cinematic HDR”更可信。
- 反射必须有来源：湿地面反射街灯，玻璃反射相机视线方向的光，河面反射建筑下部灯光；不要出现没有光源的发光水面。

### 2.3 建筑不应被拍成脱离城市的产品渲染

Iwan Baan 的官方介绍将其方法概括为：关注建筑中的生活和互动，让建筑回到周围的环境与使用者；其作品并非只拍孤立、静止的建筑，而是把地点、人物和意外时刻纳入叙事。参考：[Iwan Baan — About](https://iwan.com/about/) 与 [Iwan Baan — Projects](https://iwan.com/portfolio)。

由 Vitra Design Museum 对其展览的介绍可进一步看到：Baan 以不同视角和细节组接建筑，接受真实天气和现场“意外”进入画面，不把理想天气当成唯一答案。参考：[Vitra Design Museum — Iwan Baan: Moments in Architecture](https://www.vitra.com/en-gb/campus/news/details/iwan-baan-moments-in-architecture)。

**转译为 aJay：**

- 每个城市图至少保留一个可识别的近景平面：地面、窗框、栏杆、拱廊柱、门厅边缘或雨滴。
- 人物只做尺度参照：一两个经过的背影/移动鬼影即可，不生成可识别客户或名人。
- 天气不必“完美”：薄雨、潮湿路面、雾化玻璃和不一致的室内灯光比整齐的蓝色天幕更有可信度。
- 不使用单一“英雄地标”填满画面；地标应是空间关系中的一个节点。

### 2.4 室内外应当像一次真实拍摄任务的不同帧

Hufton+Crow 官方定位是拍摄当代建筑的室内与外部，并强调让建筑处在其建成环境中；项目索引同时包含纽约 World Trade Center、伦敦 Paddington Square、纽约 56 Leonard Street 等。参考：[Hufton+Crow — About](https://www.huftonandcrow.com/about/) 与 [Hufton+Crow — Projects](https://www.huftonandcrow.com/projects/)。

**落地规则：**

- 同一城市至少配一张“进入建筑”的帧和一张“退到街道”的帧；不要只做四张天际线横幅。
- 室内外切换时保留共同材质或色温，例如湿玻璃→室内银色灯带、湿石路→黑色花岗岩大厅。
- 建筑细节、真实使用痕迹和人流方向要比光效更重要。

---

## 3. 建筑锚点：用官方资料校准，不复制官方图片

这些资料用于校准建筑比例、材料、位置与空间关系；生成图仍要标为 aJay AI 生成素材，不宣称为官方照片，也不复用页面图片。

| 城市 | 官方事实锚点 | 视觉转译 |
|---|---|---|
| Manhattan | One World Trade Center 官方资料指出其玻璃外立面会反射天际线并随天气变化，切角边缘形成独特的八边形上升体量。[官方页面](https://wtc.com/work-place/1wtc/) | 用玻璃反射与切角体量做远景结构；不要把整座塔楼变成过亮的银色广告牌。 |
| London | Foster + Partners 的 Bloomberg 项目页描述了 City 核心区、砂岩结构框架、青铜鳍片、步行拱廊与内部 Vortex 双层高空间。[官方项目页](https://www.fosterandpartners.com/projects/bloomberg/) | 用“砂岩/青铜/湿拱廊/双层高空腔”构成可进入的空间，不必生成 Bloomberg 文字或 logo。 |
| Shanghai | Shanghai Tower 官方项目介绍将其置于陆家嘴金融区，说明 632m、127 层及多层功能；官方设计资料提到双层幕墙、多层中庭，以及与金茂大厦、上海环球金融中心相邻。[项目介绍](https://en.shanghaitower.com/ProjectIntroduction.html) · [设计/工程资料](https://en.shanghaitower.com/news_2/1.html) | 用中庭向上仰视双层幕墙和中庭空腔，邻近塔楼只做透过玻璃的层次，不重复滨江全景。 |
| Hong Kong | IFC 官方资料将 One/Two IFC 置于 Central Waterfront，说明其为金融机构办公空间，Two IFC 的塔冠在夜间会成为城市灯塔。[官方 About](https://ifc.com.hk/en/about-us/) | 用高架步行系统、雨痕玻璃和受控塔冠光构成垂直密度；删除商场品牌与可读招牌。 |

---

## 4. 统一摄影语言（给 image_gen 的物理约束）

### 4.1 镜头、机位和输出比例

- **相机：** full-frame professional camera on tripod；相机水平，建筑线平行；不要 drone-like fantasy view。
- **焦段：** 24mm PC 只用于受控室内结构；城市街景优先 35mm；中距离建筑关系优先 50mm；雨玻璃后的塔楼层次用 70–85mm 压缩。
- **景深：** 建筑主题以 f/5.6–f/11 的真实中深景深为主；不要把整个城市渲染成同一无限锐利平面。
- **比例：** 生成时优先 3:2 或 4:3 横幅，再在网页中裁成 16:9；肖像保持 2:3。这样可保留真实拍摄的边缘信息，也避免每张图都像同一个全景模板。
- **构图：** 前景（材质/栏杆/雨地）—中景（街道/拱廊/中庭）—后景（塔楼/灯光）至少三层；留白必须是空间留白，而不是空洞的 AI 天幕。
- **天气：** 雨只作为局部、可解释的现场条件：一块玻璃、一个湿地面或一段雾化边缘即可；不要把雨丝、镜头水珠或霓虹反射做成全屏电影特效。Shanghai 场景默认干燥夜间，以清洁痕迹和不齐窗光提供现实感。

### 4.2 曝光起点（不是硬性 EXIF）

这些值是给生成模型的“物理语义”，实际摄影或后期仍需按光线调整：

| 场景 | 焦段/光圈 | ISO | 快门起点 | 曝光意图 |
|---|---|---:|---:|---|
| 蓝调时刻外景 | 35–50mm，f/8 | 64–100 | 1/2–4s | 留住深蓝天空与室内灯，地面略有移动柔化。 |
| 深夜街景 | 35–50mm，f/8–11 | 64–200 | 2–10s | 固定建筑，车辆或行人产生少量自然鬼影；高光不爆。 |
| 室内/拱廊 | 35–50mm，f/4–5.6 | 200–800 | 1/4–1s | 保留窗外冷色和室内暖色，不做无来源补光。 |
| 中庭仰拍 | 24mm PC，f/8 | 100–200 | 1/2–2s | 结构线清晰，玻璃反射可解释，避免超广角扇形变形。 |
| 人物肖像 | 85mm，f/4–5.6 | 100–400 | 1/125–1/250s | 单向 key light、眼神和皮肤纹理清楚；黑位有细节。 |

### 4.3 真实瑕疵清单

每张城市图从下列项目中选择 3–4 项，不全部堆上：

- 雨滴/擦拭痕在一块玻璃上而非全画面均匀贴图。
- 湿石路反射被脚印、接缝或排水口打断。
- 少量窗口未点亮，办公楼层之间亮度不齐。
- 一辆车或一个背影形成轻微移动拖影，脸不可识别。
- 镜头边缘轻微冷色 flare，但不能覆盖建筑线。
- 空气中有一层真实薄雾，远景对比度略低，近景纹理更清楚。
- 金属/石材有细微使用痕迹，不是均匀噪点或塑料纹理。
- 室内玻璃反射出摄影机视线内的灯带/窗格，但不反射不存在的楼体。

### 4.4 明确禁用词与验收底线

**禁用：** `HDR halo`, `ultra-wide distortion`, `perfectly repeated windows`, `all windows illuminated`, `neon cyberpunk`, `holographic charts`, `floating tickers`, `stock graph`, `numbers`, `logos`, `watermarks`, `text`, `CGI render`, `illustration`, `golden sunset wash`, `generic futuristic skyline`。

**验收 8 项：**

1. 垂直线和水平线能追溯到同一机位；没有一栋楼同时向不同方向倾斜。
2. 前景、中景、后景均有真实尺度；没有“城市贴在平面背景上”。
3. 窗格亮度、路灯、玻璃反射存在可解释的光源。
4. 所有地标轮廓完整且不被模型拼接成新建筑。
5. 细节不靠过度锐化；近景材质有颗粒和微小缺陷，远景自然衰减。
6. 不出现可读文字、商标、股票代码、图表或人物背书。
7. 裁成浅 16:9 后仍保留一个前景平面和一个中景结构。
8. 画面情绪来自空间、材质和曝光，不来自滤镜、渐变或霓虹。

---

## 5. 四城场景方案与可直接交给 image_gen 的 Prompt

### 5.1 Manhattan：湿街低机位 / `The Street Before the Bell`

**叙事：** 不是隔着水看“金融区海报”，而是站在金融区的人行道上。历史石材和现代玻璃同时出现，One WTC 是远方的几何锚点；前景湿地面把城市灯光压低、拉长。

**机位与曝光：** 眼高约 1.45m，三脚架，35mm PC 或 40mm；相机保持水平、建筑线近似平行；蓝调时刻后 1–4 秒、f/8、ISO 64–100，做高光保留的单次曝光观感；可有一辆车轻微拖影。

**网页构图：** 16:9 hero 可裁图；建筑在右侧约 55%，左侧和下方为深色可读留白；不要水岸全景、不要直升机视角。

#### Prompt（完整复制版）

```text
Use case: photorealistic-natural.
Asset type: premium editorial architectural photograph for a financial research website hero, generated as an original interpretive image rather than a documentary photograph.
Primary request: stand at human eye level on a wet Lower Manhattan financial-district sidewalk just after blue hour, looking through a real street corridor toward the glass geometry of One World Trade Center in the distance. The image must feel physically entered and photographed from the street, not like a skyline poster.
Composition: horizontal 3:2 source intended for a shallow 16:9 crop. Use a three-layer structure: foreground dark wet stone paving with seams and a restrained broken reflection; middle ground historic limestone and granite façades, a curb, one understated streetlight and a few anonymous passing silhouettes; background One World Trade Center rising in the right half, recognizable through its chamfered glass form but not oversized. Leave calm deep navy negative space in the lower-left for webpage title overlay. Keep the camera close to level and preserve believable building proportions.
Camera and exposure: full-frame camera on a stable tripod, 35mm perspective-control lens, camera kept level and parallel verticals, f/8, ISO 64–100, 1–4 second blue-hour exposure, highlight-preserving single-exposure look, restrained motion blur on one vehicle or passerby only. Natural architectural sharpness with gradual distance falloff; no ultra-wide distortion.
Light: deep blue ambient sky, cool reflected light from glass, practical street lamps with modest warm pools on the wet pavement, a few uneven office windows, no uniform illumination. Keep glass reflections and pavement reflections consistent with the visible light sources. Rich blacks retain stone texture and curb detail.
Realism cues: one small patch of moisture on a nearby glass door or window, irregular paving joints, a slightly dirty curb, a faint lens flare at the edge, varied window brightness, subtle atmospheric haze between buildings. Use no more than four imperfections; the street remains elegant and clean.
Style: high-end architectural magazine photography, sober global-capital mood, real materials, controlled exposure, corrected perspective, tactile stone and glass, no glossy CGI finish.
Do not show: water panorama, harbor skyline, drone view, generic futuristic towers, giant fabricated buildings, trees or gardens, neon cyberpunk color, magenta light, holograms, floating charts, stock tickers, numbers, text, logos, watermarks, readable signs, identifiable people, HDR halos, illustration, 3D render, border or frame.
```

### 5.2 London：湿玻璃拱廊 / `City, Layered`

**叙事：** 把 London 拍成历史与现代办公空间的重叠，不直接复制 skyline。参考 Bloomberg European Headquarters 官方资料中的砂岩结构框架、青铜鳍片、步行拱廊和双层高 Vortex；这些是材质/空间线索，不是 logo 或官方图片复刻。

**机位与曝光：** 站在覆盖式步行拱廊或公共入口内，1.55m 眼高，50mm，三脚架；f/5.6、ISO 200–400、1/4–1 秒；室内暖色池光和窗外冷雨光同时存在，但都不过曝。

**网页构图：** 4:3 或 3:2 图片卡，裁切时保留拱廊顶部和湿玻璃边缘；不要让塔楼横向铺满。

#### Prompt（完整复制版）

```text
Use case: photorealistic-natural.
Asset type: high-end editorial photograph of a global financial city, an original interpretive image with the spatial character of London's historic City district.
Primary request: photograph from inside a covered pedestrian arcade at blue hour in the City of London, looking diagonally through rain-streaked glass and a bronze-toned façade rhythm toward a narrow glimpse of St Paul's Cathedral and nearby contemporary office volumes. The architectural reference is a restrained sandstone frame, vertical bronze fins, a public passage and a double-height lobby void; do not reproduce a corporate logo or signage.
Composition: horizontal 4:3 source. Camera at standing eye level, foreground a dark stone threshold, one mullion and a section of wet glass; middle ground a covered colonnade with believable sandstone texture and bronze fins; background a cool rainy street and a small, proportionate view of St Paul's dome between buildings. Use a strong diagonal leading line into the lobby/arcade and leave one quiet dark side for copy. Do not make a skyline panorama.
Camera and exposure: full-frame camera on tripod, 50mm lens, camera level with corrected verticals, f/5.6, ISO 200–400, 1/4 to 1 second exposure, natural mixed-light interior/exterior balance, moderate depth of field with the mullion and architectural edges sharp and the far traffic softly separated. No extreme perspective.
Light: overcast London blue hour, cool rain outside, warm tungsten or soft LED pools inside the arcade, small specular highlights on wet stone and bronze. The light should reveal the material grain and architectural joints. Allow one distant passerby to become a small natural motion blur; no faces or staged business meeting.
Realism cues: uneven rain beads on only part of the glass, a faint wiped area, slight condensation near the lower edge, small differences in office window brightness, a tiny flare from one practical lamp, subtle ambient haze. Reflections must mirror the actual arcade and light sources, never an invented city.
Style: refined architectural magazine photography, calm and expensive without glamour-filter polish, a sense of standing under shelter while the city continues outside, realistic exposure and color separation.
Do not show: full panoramic skyline, golden sunset, perfectly clean CGI surfaces, neon cyberpunk, magenta or rainbow lighting, floating financial charts, screens, tickers, numbers, readable text, logos, watermarks, brand names, recognizable corporate employees, tourist crowd, illustration, 3D render, border or frame.
```

### 5.3 Shanghai：塔楼中庭仰拍 / `Vertical Capital`

**叙事：** Shanghai 不再重复已生成的黄浦江陆家嘴全景。把金融中心变成一座可进入的垂直城市：人在低处，双层幕墙、多层中庭和结构缝隙向上延伸；邻近塔楼只从玻璃中被看见。

**机位与曝光：** 塔楼裙房或中庭一层，24mm PC，镜头向上但相机保持水平并 shift 取景；f/8、ISO 100–200、1/2–2 秒；结构线清楚，玻璃反射有真实来源。

**网页构图：** 4:3 竖向感强的横图或 3:2 卡片；裁剪后保留中庭底部/栏杆作为身体尺度，不做完整 skyline。

#### Prompt（完整复制版）

```text
Use case: photorealistic-natural.
Asset type: premium architectural interior photograph for a global investment-research interface, an original interpretive image set in Shanghai's Lujiazui financial district.
Primary request: stand at ground level inside a real-scale high-rise financial tower atrium and look upward through a layered double-skin glass façade and multi-story void. The visual anchor is Shanghai Tower's twisting translucent envelope and vertical atrium logic, with restrained glimpses of Jin Mao Tower and Shanghai World Financial Center through distant glass. The image is about vertical structure and human presence, not a riverfront skyline panorama.
Composition: horizontal 4:3 source with a strong upward diagonal. Foreground includes a dark stone floor seam, a brushed-metal handrail and one small anonymous silhouette for scale; middle ground contains a multi-story atrium, lift core edges and believable mullions; background rises into overlapping glass skins and a cool night sky. Keep the adjacent towers small and physically distant. Preserve aligned structural lines and a calm area of darker glass for text overlay.
Camera and exposure: full-frame camera on a tripod, 24mm perspective-control lens, camera body kept level, verticals corrected with controlled upward shift, f/8, ISO 100–200, 1/2–2 second exposure, highlight-preserving single-exposure look. Deep focus on the architectural frame with natural distance falloff; no fisheye or barrel distortion.
Light: midnight blue ambient light outside, restrained cool white and steel-blue façade lighting, soft warm office floors appearing only in scattered windows, subtle reflected light on metal and stone. No saturated colored LEDs. Every reflection must correspond to a visible mullion, lamp or interior volume.
Realism cues: slight fingerprints or cleaning streaks on one glass panel, a few unlit office levels, small differences in curtain-wall reflectance, a gentle exposure gradient through the atrium, one faint moving silhouette. Keep imperfections selective and believable.
Style: high-end architectural photography, precise perspective, tactile stone, glass, metal and concrete, sophisticated global-finance atmosphere, physically plausible scale and engineering rather than a concept render.
Do not show: Huangpu River panorama, Bund view, four identical landmark towers in a row, giant glowing Shanghai Tower, neon cyberpunk, rainbow or magenta light, holograms, charts, stock tickers, numbers, text, logos, watermarks, advertisements, readable signs, staged executives, impossible reflections, CGI sheen, illustration, border or frame.
```

### 5.4 Hong Kong：雨痕玻璃与高架步行层 / `Density, Seen Through Glass`

**叙事：** 用 Central 的高架连接、室内前厅和雨天幕墙表达金融流动的密度。Two IFC/One IFC 是受控远景锚点；栏杆、玻璃、MTR/街灯反射作为近景层，不将商业品牌带入画面。

**机位与曝光：** 站在 Central 高架步行系统或室内前厅边缘，70–85mm 压缩层次，f/5.6、ISO 200–400、1/2–2 秒；让一两个行人变成轻微移动影子。

**网页构图：** 3:2 或 4:3；将塔楼置于右上/中远景，把栏杆和玻璃边缘保留在前景，禁止横向填满。

#### Prompt（完整复制版）

```text
Use case: photorealistic-natural.
Asset type: sophisticated editorial architecture photograph for a premium financial intelligence website, an original interpretive image set in Hong Kong's Central business district.
Primary request: photograph from a sheltered elevated pedestrian walkway or quiet office-lobby edge on a rainy night, looking obliquely through rain-marked glass toward the vertical forms of One and Two IFC across layered streets and harbour haze. The scene should feel dense, close and navigable, as if the viewer is physically standing inside the circulation system of the district, not looking at a postcard panorama.
Composition: horizontal 3:2 source intended for a 16:9 crop. Foreground: one dark handrail, a glass mullion and wet floor edge; middle ground: overlapping walkway structures, a few anonymous silhouettes and muted traffic light traces; background: Two IFC's proportionate finial and One IFC separated by real atmospheric depth. Use a 70–85mm lens perspective to compress layers without flattening them. Leave a dark, uncluttered side for copy and keep no single tower larger than the frame can support.
Camera and exposure: full-frame camera on a stable tripod or braced architectural support, 70–85mm lens, level camera with restrained perspective correction, f/5.6, ISO 200–400, 1/2–2 second exposure, controlled mixed-light balance. Hold highlights in the wet glass and tower lights; allow only one or two moving silhouettes to soften naturally.
Light: cool humid night air, subdued steel-blue façade reflections, warm sodium or interior lobby pools, tiny restrained red or green traffic accents only when physically sourced. Rain should absorb and scatter light locally, not create a neon wash. Reflections must repeat the actual mullion, handrail and visible lamps.
Realism cues: irregular rain tracks on one pane, a wiped section at eye height, a slightly fogged lower corner, uneven office occupancy, mild atmospheric haze toward the harbour, one small lens flare from a practical lamp. Keep the architecture clean but not sterile.
Style: high-end architectural magazine photography, sober and tactile, careful exposure, coherent perspective, lived urban circulation, no fantasy skyline and no advertising aesthetic.
Do not show: full Victoria Harbour panorama, cruise ships dominating the scene, giant glowing signs, readable retail branding, logos, watermarks, text, numbers, stock graphs, holograms, cyberpunk neon, rainbow light, perfectly repeated windows, all windows lit, impossible glass reflections, CGI render, illustration, border or frame.
```

---

## 6. 可商用或明确许可的真实城市照片来源（仅作备选，不直接下载）

这些是**来源入口**而不是已经选定的图片。任何进入生产的真实照片仍须保存具体文件页、作者、许可证、访问日期和裁剪记录；不得只凭搜索缩略图使用。平台条款可能更新，交付前应重新打开许可证页。

| 来源 | 可用范围与边界 | 适合检索 / 记录方式 |
|---|---|---|
| [Unsplash License](https://unsplash.com/license) | 官方许可证允许免费下载、复制、修改、分发和商业使用，通常无需署名；不得原样售卖，也不得把照片中的人物/品牌理解为 aJay 背书。单张图仍应检查商标、隐私、地标或其他第三方权利。 | 搜索 `New York Financial District night architecture`、`London City rain architecture`、`Shanghai Lujiazui night`、`Hong Kong Central rain glass`；记录作者和原图页。 |
| [Pexels License](https://www.pexels.com/legal-pages/license/) | 官方条款允许网站、产品、广告等商业使用且通常无需署名；不允许原样售卖或把画面人物/品牌暗示为产品背书；画面中的商标、logo、人物与建筑权利仍需单独评估。 | 先在 Pexels 内筛选横向、高分辨率、无明显 logo 的真实照片；记录具体摄影师、原图页、许可证页和是否裁剪。 |
| [Wikimedia Commons — Reusing content](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/licenses) | 每个文件页会给出公共领域或 CC BY/CC BY-SA 等许可证；CC BY/CC BY-SA 通常可商业使用但需要署名，CC BY-SA 还要求相同方式共享衍生作品。Commons 特别提醒仍可能存在商标、人格权、地标或当地法律限制。 | 按城市和建筑名搜文件页；只使用许可证清楚、作者/来源/修改记录齐全的文件；把署名文本和许可证链接一起保存。 |
| [Openverse — About](https://openverse.org/kin/about) | Openverse 聚合 CC 授权和公共领域素材，提供发现和归因入口，但官方明确不逐项核验许可或归因准确性；必须回到原始来源确认。 | 用作跨站检索，不把 Openverse 结果页当作许可证；保存原始仓库 URL、文件页、作者、许可证全文链接和访问日期。 |

### 6.1 真实照片进入 aJay 前的记录模板

```text
Asset ID: CITY_SCENE_YYYYMMDD_NN
City / building:
Original file page URL:
Author / creator:
Repository / platform:
License name and full-text URL:
Commercial use allowed: yes / no / verify
Attribution text required:
Model / property / trademark concerns:
Changes made: crop / color / retouch / none
Access date: 2026-09-09
Where used in aJay:
```

**推荐策略：** 真实授权照片只作为局部纹理、资料对照或备用；主页面的统一场景仍用“AI 生成、摄影物理约束明确、来源可追溯”的项目素材，避免四城照片来自不同摄影师而出现色彩和空间语言断裂。

---

## 7. 补充投资人物：8 位跨时代、跨流派肖像

不再扩大科技 CEO 阵容。以下 8 位和 Buffett、Simons 组合后，能覆盖价值、质量成长、全球逆向、宏观、信用/周期与长期成本纪律；页面展示的是方法论标签，不是本人对 aJay 或任何证券的真实意见。

| 人物 | 方法论标签（用于卡片，不写成引语） | 黑白构图与姿态 |
|---|---|---|
| Benjamin Graham | 安全边际、证券分析、价值底线 | 2:3 半身三分之四侧坐，保守深色西装，眼神略离镜头；硬一些的 key light 让额头和纸张般的皮肤纹理可见，但画面不出现纸上文字。 |
| Charlie Munger | 质量、逆向思考、跨学科心智模型 | 胸像、轻微侧身、下颌收紧，眼镜有一处克制反光；阴影侧保留细节，气质直接而不戏剧化。 |
| Peter Lynch | GARP、实地观察、可理解的生意 | 轻松三分之四坐姿，深色外套或针织层，表情带一点自然亲和力；背景仍是深炭黑，不加入股票图或商店 logo。 |
| Philip Fisher | 质量成长、管理层研究、scuttlebutt | 较紧的侧面胸像，眼神看向画外，头肩轮廓被边缘光分开；强调观察感而非“演讲者”姿态。 |
| John Templeton | 全球逆向、危机中的纪律 | 正面或轻微三分之二正面，旅行后仍克制的深色西装，光线从侧上方切入；不放地图、国旗或市场行情。 |
| George Soros | 宏观、反身性、风险与叙事 | 分割光的三分之四肖像，一半面部进入银灰、一半沉入可读阴影；眼神略偏离镜头，避免生成“宣布观点”的戏剧场面。 |
| Ray Dalio | 宏观配置、相关性、平衡框架 | 对称坐姿、双手自然相叠但不指向图表，柔和方向性 key light；服装简洁，背景无“全天候”文字。 |
| Howard Marks | 信用、周期、风险控制 | 坐姿侧光胸像，桌边可有一本合上的无字笔记本但不必出现；压低高光，保留纸张和西装纹理，传达安静审慎。 |

### 7.1 统一黑白肖像 Prompt

可以将下列共用段落放在每位人物的个性段落前，再替换 `ROLE_A` 与姿态描述：

```text
Use case: photorealistic-natural.
Asset type: one vertical 2:3 AI-generated interpretive editorial portrait for a simulated investment-methodology interface, not a documentary photograph and not an endorsement.
Subject: ROLE_A, depicted as a public historical or public figure for methodology discussion only; one person, recognizable but not staged as a spokesperson for any product, company or security.
Composition: chest-up or seated upper-body portrait, full head and shoulders comfortably inside the frame, natural anatomy, restrained posture, eyes as the focal point, no collage and no second person.
Studio and light: deep charcoal-black seamless studio background; one large directional studio key light from 45 degrees above camera left, gentle shadow-side fill, controlled catchlight, subtle edge separation on hair, realistic falloff into black.
Style: sophisticated silver-gelatin black-and-white editorial portrait photography, rich dimensional blacks, differentiated silver midtones, authentic skin pores, wrinkles, hair and fabric texture, delicate film grain, no plastic retouching or over-sharpening.
Wardrobe: plain dark jacket or suit with an unbranded shirt; no visible corporate marks, tie logos, pins or slogans. If a notebook or paper is present, it is closed or blank and contains no readable marks.
Constraints: no text, letters, captions, quotes, signatures, logos, watermarks, charts, tickers, screens, financial instruments, campaign imagery, product interaction, endorsement gesture or testimonial pose. Keep the result quiet, human and photographic.
```

### 7.2 肖像卡片的非背书规则

- 标签统一写：**“AI 生成肖像 · 方法论模拟 · 不代表本人观点或背书”**；英文可写 **“AI-generated portrait · simulated methodology · no endorsement implied.”**
- 不使用引号包围模型生成的投资判断，不写“X 说 aJay 应该买……”；使用“模拟评审视角：关注安全边际/周期/质量”等方法论标签。
- 人像旁边不要放公司的 logo、产品截图、实时股价或“本人推荐”按钮；人物只对应流派/分析维度。
- 不把 AI 生成肖像与真实采访、历史照片、基金持仓截图拼成一张图；若需要历史证据，单独引用真实来源并标注来源。
- 现有 Buffett/Simons 记录已经把“不是实拍、不是背书”写清楚；新增人物沿用同一句声明和同一份来源记录格式。

---

## 8. 交付与验收顺序（给页面实现者）

1. **先换架构，不先堆图：** Hero 采用 Manhattan 湿街低机位；London、Shanghai、Hong Kong 各用不同的室内/街道进入方式。
2. **先做一张代表性测试帧：** 用 Manhattan Prompt 检查垂直线、湿地面反射、标题裁切和现实瑕疵；通过后再生成另外三城。
3. **四城统一调色但不统一景别：** 黑位、银色高光、冷蓝环境一致；机位、焦段、前景材质和城市色温各自不同。
4. **每次生成保留来源：** 记录 prompt、日期、输出路径、是否重试、裁剪/压缩版本和最终使用位置；继续遵守 `docs/IMAGE-PROVENANCE.md` 的“原始 PNG 保留、项目副本逐字节记录”原则。
5. **真实照片仅在许可通过后进入：** 走第 6 节记录模板，不从搜索结果缩略图或不明搬运账号下载。
6. **人物扩展最后做：** 先锁定城市摄影语言，再用同一组肖像灯光生成 Graham/Munger/Lynch/Fisher/Templeton/Soros/Dalio/Marks；每张图都带统一非背书标签。
7. **最终人工检查：** 在真实网页裁切尺寸中检查高光、阴影、垂直线、雨滴、窗口重复、文字/商标残留和人物面部是否被误读为真实合影。

---

## 9. 来源索引（研究使用）

- [Nikon USA — The PC Lens Advantage: What You See Is What You'll Get](https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/the-pc-lens-advantage-what-you-see-is-what-you-get)
- [Nikon USA — Taking Pictures at Dusk and at Night](https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/taking-pictures-at-dusk-and-at-night)
- [Iwan Baan — About](https://iwan.com/about/)
- [Iwan Baan — Projects](https://iwan.com/portfolio)
- [Vitra Design Museum — Iwan Baan: Moments in Architecture](https://www.vitra.com/en-gb/campus/news/details/iwan-baan-moments-in-architecture)
- [Hufton+Crow — About](https://www.huftonandcrow.com/about/)
- [Hufton+Crow — Projects](https://www.huftonandcrow.com/projects/)
- [Foster + Partners — Bloomberg](https://www.fosterandpartners.com/projects/bloomberg/)
- [One World Trade Center — official workplace page](https://wtc.com/work-place/1wtc/)
- [Shanghai Tower — official project brief](https://en.shanghaitower.com/ProjectIntroduction.html)
- [Shanghai Tower — official design/engineering page](https://en.shanghaitower.com/news_2/1.html)
- [International Finance Centre Hong Kong — official About](https://ifc.com.hk/en/about-us/)
- [Unsplash — License](https://unsplash.com/license)
- [Pexels — License](https://www.pexels.com/legal-pages/license/)
- [Wikimedia Commons — Reusing content outside Wikimedia](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/licenses)
- [Openverse — About](https://openverse.org/kin/about)
