# aJay 金融摄影来源与编辑记录

审核日期：2026-09-09。金融/投资语义优先；不以城市旅游感替代研究场所。

## 当前采用的四张作品

| 场景 | 原作与作者 | 日期依据 | 许可 | 空间语言 |
|---|---|---|---|---|
| 纽约 | [Wall street sign on a building facade](https://unsplash.com/photos/wall-street-sign-on-a-building-facade-2Dv0-S9KNVI) — Mick Waanders | 作品页公开 2025-11-10 | [Unsplash License](https://unsplash.com/license) | 华尔街近景：前景虚化、石材斜线与街牌焦点 |
| 伦敦 | [Canary Wharf skyline in September 2025](https://commons.wikimedia.org/wiki/File:Canary_Wharf_skyline_in_September_2025.png) — Azurevanilla ash | 拍摄 2025-09-22 | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | 格陵兰码头横向全景：水岸前景、One Canada Square 楼冠与完整金融区天际线 |
| 上海 | [Shanghai Tower 20251126](https://commons.wikimedia.org/wiki/File:Shanghai_Tower_20251126.jpg) — Supanut Arunoprayote | 拍摄 2025-11-26 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 陆家嘴超高层：168mm长焦、完整扭转轮廓、极窄竖幅 |
| 香港 | [Nighttime skyline of hong kong lit up](https://unsplash.com/photos/nighttime-skyline-of-hong-kong-lit-up-cZ2PwQJ8Fpw) — Raymond Yeung | 作品页公开 2025-06-23 | [Unsplash License](https://unsplash.com/license) | 中环金融建筑与维港：前景渡轮、横幅水域、远近多层 |

纽约、香港只有可核实的作品页公开日期，未将其当作拍摄日期。伦敦原作页面标注拍摄 2025-09-22；上海作品页和 EXIF 标注拍摄 2025-11-26。所有原作日期依据均落在用户要求的近两年窗口内；公开日期本身不能证明拍摄时点。

## 选择与淘汰

- 纽约：Mick Waanders 的华尔街街牌、前景虚化与真实石材斜线，直接指向机构资本；不采用已经试改的热狗摊/游客街口。
- 伦敦：Azurevanilla ash 从 Greenland Dock 拍摄的金丝雀码头完整天际线，用 One Canada Square 金字塔楼冠和 Citi 塔建立城市识别；旧办公立面因缺少可辨识地标退出主页面。
- 上海：Supanut Arunoprayote 的168mm长焦上海中心完整竖幅，不将其机械裁成横幅城市背景。建筑：Shanghai Tower，Gensler设计团队，Jun Xia领衔。
- 香港：Raymond Yeung 的中环金融建筑、IFC与中国银行大厦、前景渡轮与维港水面；避免手机水印街拍。
- 首轮四张同构纯生成室内城市图退出当前assets，保留于docs/archive/visual-concepts用于历史对比。

## 编辑方式与真实边界

每张图先下载并view_image核验原作，再通过image_gen.imagegen的referenced_image_paths输入真实原图。不同构图分别制定曝光/局部对比/色偏指令；不是同一文字提示词替换城市名。

编辑输出改变了部分曝光、局部细节和色调，因此只称“AI轻微重构摄影”，不称未经编辑纪实原片。工具未返回可核实精确模型版本，不宣称image-2.5。城市只作为视觉环境，不用于证明金融事实、公司地点或名人活动。

## 逐图追溯

### 纽约 / Mick Waanders
- 原图存储：不随仓库分发；预览脚本按原作 URL 下载，并用下列 SHA256 校验。
- 当前编辑图：`skills/deep-analysis/assets/ajay-council/new-york-photography.png`
- 原作下载：[original](https://images.unsplash.com/photo-1762805080843-ea9bb9a5116e)
- 原作SHA256：`631ae2122abb49898de6ff7eccb70d0a0c866fdb0be115eadf754933ac0ea800`
- 编辑图SHA256：`25479bee7daf64621afba06466cc0e1f384c51daca02f63c96a61212cb2fd0ca`
- 工具与模型：image_gen.imagegen；精确版本未返回。
- 编辑说明：保留摄影视角和主要建筑关系，调整曝光/冷暖/局部层次；UI中包含作者、原作链接、许可链接和改动提示。

```text
Edit THIS real Wall Street photograph by Mick Waanders, not a fresh generated city. Keep the square composition, original shallow depth of field, out-of-focus foreground vertical pole at left, strong dark diagonal limestone architecture and metal pole at right. Preserve the exact green Wall St street sign and its spelling/arrow as the central focal anchor, and keep real weathered texture. This is a financial district editorial scene, not tourist travel photography. Refine rather than redesign: expose the historic limestone a quarter stop brighter to reveal expensive crisp stone texture while retaining the deliberate dark canyon; neutralize slightly green shadows to charcoal, retaining the sign's restrained dark green. Clean only the partial delivery truck and construction scraps at the very bottom edge by a minimal tight crop, not by inventing architecture. Preserve viewpoint, architecture, all sign positions, time of day and sunlight direction. No new windows or room, no futuristic graphics, no glossy surfaces, no HDR, no bloom, no added people or billboards, no panorama. One faithful photo-derived image, square aspect ratio, no frame or titles.
```

### 伦敦 / Azurevanilla ash
- 原图存储：不随仓库分发；预览脚本按原作 URL 下载，并用下列 SHA256 校验。
- 当前编辑图：`skills/deep-analysis/assets/ajay-council/london-photography.png`
- 原作下载：[original](https://commons.wikimedia.org/wiki/Special:Redirect/file/Canary%20Wharf%20skyline%20in%20September%202025.png)
- 原作SHA256：`4a596e606885e2450c7930ff157f637d938571aa631cba15c1a3c5a073c61eed`
- 编辑图SHA256：`d04e7f8aaf4603b3c8e39a9ca0b23b134046ef7aa29bd41f6c034ff342a36071`
- 工具与模型：image_gen.imagegen；精确版本未返回。
- 编辑说明：保留摄影视角和主要建筑关系，调整曝光/冷暖/局部层次；UI中包含作者、原作链接、许可链接和改动提示。

```text
Edit THIS supplied real Canary Wharf skyline photograph dated 22 September 2025; do not generate a different city or rearrange any architecture. Preserve the exact panoramic composition, viewpoint from Greenland Dock, waterline, trees at both edges, low brick warehouses, all existing buildings and their silhouettes, including One Canada Square with its pyramidal roof, the Citi tower, and the distinctive Newfoundland residential tower. The purpose is a premium institutional financial-research website frieze, not travel imagery. Apply only a restrained professional architectural RAW finishing pass: lower the harsh midday exposure and sky, recover facade highlights, increase local separation among the actual towers, neutralize the pale cyan cast toward graphite and sober steel blue, keep the water natural and slightly darker, and retain optical imperfections. No extra buildings, replaced skyline, neon, HUD, financial charts, duplicated windows, CGI smoothness, typography or border.
```

### 上海 / Supanut Arunoprayote
- 原图存储：不随仓库分发；预览脚本按原作 URL 下载，并用下列 SHA256 校验。
- 当前编辑图：`skills/deep-analysis/assets/ajay-council/shanghai-photography.png`
- 原作下载：[original](https://upload.wikimedia.org/wikipedia/commons/f/f1/Shanghai_Tower_20251126.jpg)
- 原作SHA256：`c7b0983b7dba373b4cbc2ccbd719526785891b8c0538020dc0b435c488e3eb8b`
- 编辑图SHA256：`996de1ee7cf0d37104f36f7440ae1183ca7977837bd4df2c8b4efbe9be899702`
- 工具与模型：image_gen.imagegen；精确版本未返回。
- 编辑说明：保留摄影视角和主要建筑关系，调整曝光/冷暖/局部层次；UI中包含作者、原作链接、许可链接和改动提示。

```text
Make a very restrained architectural-photography finishing edit to THIS supplied real Shanghai Tower photograph by Supanut Arunoprayote, photographed 2025-11-26. Retain this unusual tall 0.44:1 aspect ratio (do not expand to generic skyline), exact 168mm telephoto perspective, centered full height twisted glass facade, slender setback tower behind left side, low foreground buildings and trees, existing early dusk light. Reconstruct no buildings. Improve only tonal exposure: reduce the bright blue sky by about one half stop to a more sober slate blue, retain the physical cool ambient sky/warm interior-light separation, keep every glass-floor pattern sharp but optical and irregular; reduce low-mid haze gently, do not add bloom or sharpen a fake grid. Maintain the same time of day, all architectural shapes, object positions, crop, and camera geometry. The result should read as a careful professional RAW development of the given photograph, a silvery architectural study for a financial research experience. No added city towers, no floating charts, no interior room/window frame, no new signage/text, no glossy render, no cyan neon, no cinematic fog, no symmetrical panorama. One portrait photo; no design labels or border.
```

### 香港 / Raymond Yeung
- 原图存储：不随仓库分发；预览脚本按原作 URL 下载，并用下列 SHA256 校验。
- 当前编辑图：`skills/deep-analysis/assets/ajay-council/hong-kong-photography.png`
- 原作下载：[original](https://images.unsplash.com/photo-1750700206243-52c6e2e87632)
- 原作SHA256：`8c79c806464dfc77b492294d2bebed83ff7416886b22df301b6d7d18e011fe44`
- 编辑图SHA256：`8431247e45c16b170422f0606565575328d0e502e3547ad8cc71523d3b62f238`
- 工具与模型：image_gen.imagegen；精确版本未返回。
- 编辑说明：保留摄影视角和主要建筑关系，调整曝光/冷暖/局部层次；UI中包含作者、原作链接、许可链接和改动提示。

```text
Perform only a subtle high-end photographic finishing edit of the supplied actual Hong Kong Victoria Harbour night photo. Preserve its existing horizontal 1.43:1 framing, camera position, ferry pier and ferry in lower left, small wheel in mid distance, Bank of China on left, tall IFC tower on right, their exact architectural silhouettes, mountain lights, water texture and all real lighting locations. The deliberate visual grammar is horizontal waterfront depth with a dark foreground ferry, not a room or window scene. Slightly reduce the green/cyan cast in the sky and water toward neutral deep blue-black; retain localized colored building lights and warm white window lights. Reduce blown neon halation subtly, keep shadow detail and natural sensor grain, improve separation of the waterfront from dark hills using restrained local contrast only. Do not alter the time, weather, skyline, relative building sizes, viewpoint or object placements. No interior, no glossy water, no new skyscrapers, no pseudo-HDR, no fog, no added graphic lines or text. This is an AI-edited derivative of a real photographic work, not a synthetic replacement. Output one landscape photograph with the same composition.
```

## 许可与产品归属

上海摄影按 CC BY 4.0 保留作者、原作链接、许可链接和改动声明；伦敦原作按 CC0 1.0 使用；纽约与香港按 Unsplash License 使用并自愿署名。图片没有因进入 aJay 代码库而变成 aJay 独占摄影版权。UI 设计与新增实现署名 aJay，照片作者/上游 MIT/第三方依赖各自保留权利边界。

原图与编辑图并列预览：在scripts下运行python preview_photography.py；脚本仅在首次预览时下载原图并核对 SHA256，输出photography-review.html。主报告将四张编辑图和八张肖像内联，运行时不加载远程影像。
