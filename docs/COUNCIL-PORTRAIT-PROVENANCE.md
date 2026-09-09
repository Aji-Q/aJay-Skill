# aJay Council portrait · generation provenance

- 日期：2026-09-09
- 用途：aJay 研究报告的模拟投委会 / 投资方法论人物肖像。
- 本批范围：新增 Benjamin Graham、Charlie Munger、Peter Lynch、George Soros、Ray Dalio、Jesse Livermore 六张独立肖像。
- 工具：Codex 内置 `image_gen.imagegen`（built-in tool mode）。共六次独立生成，分两批并行各三次；没有使用 CLI/API fallback。
- 参考图：没有向生成工具输入参考图片；通过统一 prompt 规格匹配已有 Buffett/Simons 的视觉语言。
- 编辑：没有后期编辑、裁剪或重试；原始输出保留在工具默认目录，项目文件为逐字节复制。
- 模型标识：工具响应只返回 `image_url` 和 `output_hint`，没有返回可独立核实的模型版本；本记录不声明 Image 2.5 或其他具体模型版本。
- 版权 / 背书：这些是 AI 生成的公众人物艺术化肖像，不是历史照片、实拍会面、采访证据或人物背书。页面使用时统一标注：**AI 生成肖像 · 方法论模拟 · 不代表本人观点或背书**。

## 项目资产与校验

| 人物 | 项目文件 | 原始输出文件 | 尺寸 / 格式 | 文件大小 | SHA-256 |
|---|---|---|---|---:|---|
| Benjamin Graham | `skills/deep-analysis/assets/ajay-council/graham-portrait.png` | `[local generation artifact not distributed]` | 1024 × 1536 / RGB PNG | 2,146,826 bytes | `28247d7cf8e855fdf0b530a4bd1edc4aee4dee1803dc13a97cd756242b7e851f` |
| Charlie Munger | `skills/deep-analysis/assets/ajay-council/munger-portrait.png` | `[local generation artifact not distributed]` | 1024 × 1536 / RGB PNG | 2,282,840 bytes | `33b20b6592d6aeda5e948c00524339b5cfd33cf11f5a220024c3d8e4ed1fa66a` |
| Peter Lynch | `skills/deep-analysis/assets/ajay-council/lynch-portrait.png` | `[local generation artifact not distributed]` | 1024 × 1536 / RGB PNG | 2,250,768 bytes | `834e60cc3d76b4968e07b94def6e071a28c5c9fb0223f4b409dafb3bcc8b597d` |
| George Soros | `skills/deep-analysis/assets/ajay-council/soros-portrait.png` | `[local generation artifact not distributed]` | 1024 × 1536 / RGB PNG | 2,312,275 bytes | `dd8c3129fbbfc09456cfc6afb7414ad4a1cd1965f96726f9ea34ce3894383eeb` |
| Ray Dalio | `skills/deep-analysis/assets/ajay-council/dalio-portrait.png` | `[local generation artifact not distributed]` | 1024 × 1536 / RGB PNG | 2,295,337 bytes | `d0c08aca33cd6d73e9ea06ec5c74d2bdc9439972d7db0ee6546399d97db6d2ad` |
| Jesse Livermore | `skills/deep-analysis/assets/ajay-council/livermore-portrait.png` | `[local generation artifact not distributed]` | 1024 × 1536 / RGB PNG | 2,186,192 bytes | `687ac08d679022f99fd435c6c856107cf2e1d42db31e785756817b2cdba88424` |

### Copy verification

项目六张 PNG 均从上述工具默认原始路径复制到 `skills/deep-analysis/assets/ajay-council/`，生成后使用 `file` 和 SHA-256 校验。六张图均为 2:3、1024 × 1536、8-bit RGB、非隔行 PNG；没有覆盖 `skills/deep-analysis/assets/ajay-brand/buffett-portrait.png` 或 `simons-portrait.png`，也没有改动现有 `ajay-council` 目录中的其他资产。

## 视觉验收

六张项目副本均已目视检查：

- 一人一图，完整头部和肩部留在画面内；没有拼图、第二人物、文字、签名、logo、品牌、watermark、图表、ticker、屏幕或金融产品。
- 深炭黑无物摄影棚背景；黑白银盐方向一致，黑位有层次，银灰中间调与皮肤纹理可见。
- 同一组方向性主灯：约 45° 高位侧光、克制阴影侧填充、自然眼部 catchlight、适度边缘分离。
- 服装无品牌；没有举手、指向、握持材料或演讲式背书动作。
- 姿势有细微区分但仍像同一投委会肖像委托：Graham 三分之四坐姿；Munger 头部轻转；Lynch 轻微前倾；Soros 视线越过镜头并带分割光；Dalio 正面对称坐姿；Livermore 三分之四角度与早期二十世纪三件套服装。
- Livermore 使用黑白银盐而非棕褐色怀旧滤镜；历史服装只用于时间线索，不加入交易大厅、行情纸或可读文字。

## 实际完整 Prompt

以下为六次独立调用实际提交给 `image_gen.imagegen` 的完整 prompt，未根据结果补写或缩短。

### Benjamin Graham · graham-portrait.png

```text
Use case: photorealistic-natural.
Asset type: one vertical 2:3 AI-generated interpretive editorial portrait for a simulated investment-methodology interface, not a documentary photograph and not an endorsement.
Primary request: a single exceptionally high-quality, photorealistic black-and-white portrait of Benjamin Graham in later life, the public historical figure associated with security analysis and value investing. He has a recognizable elderly face, receding silver hair, round understated eyeglasses, a calm analytical expression, and a conservative dark suit with a white shirt and unbranded restrained tie.
Scene/backdrop: deep charcoal-black seamless photography studio, no objects.
Composition/framing: vertical 2:3, seated upper-body three-quarter portrait, complete head and shoulders comfortably inside the frame, natural posture, eyes as the focal point, hands below frame with no gesture, one person only.
Lighting/mood: one large directional studio key light from 45 degrees above camera left, gentle shadow-side fill, controlled catchlight in the eyes, sculpted facial depth, quiet authority and analytical reserve.
Style/medium: sophisticated silver-gelatin black-and-white editorial portrait photography, rich dimensional blacks, differentiated silver midtones, authentic skin pores, age lines and suit fabric, delicate film grain, natural anatomy, no plastic retouching or over-sharpening. Match the restrained commissioned portrait quality of an elite investment committee archive.
Constraints: no text, letters, captions, quotes, signatures, logos, brands, watermarks, charts, tickers, screens, financial instruments, papers with writing, second person, collage, border or frame, product interaction, endorsement pose or testimonial scene.
```

### Charlie Munger · munger-portrait.png

```text
Use case: photorealistic-natural.
Asset type: one vertical 2:3 AI-generated interpretive editorial portrait for a simulated investment-methodology interface, not a documentary photograph and not an endorsement.
Primary request: a single exceptionally high-quality, photorealistic black-and-white portrait of Charlie Munger in later life, the public historical figure associated with quality investing and mental models. He has a recognizable elderly face, swept-back white hair, understated eyeglasses, a firm thoughtful expression with a hint of dry warmth, and a plain dark jacket over a white shirt.
Scene/backdrop: deep charcoal-black seamless photography studio, no objects.
Composition/framing: vertical 2:3, chest-up three-quarter portrait with the head turned slightly toward camera, complete head and shoulders comfortably inside the frame, hands out of frame, relaxed natural posture, one person only.
Lighting/mood: one large directional studio key light from 45 degrees above camera left, soft minimal fill on the shadow side, controlled eye catchlight, detailed cheek and brow texture, direct and intellectually serious mood.
Style/medium: sophisticated silver-gelatin black-and-white editorial portrait photography, dimensional blacks, nuanced silver-gray midtones, realistic skin pores, wrinkles, individual hair strands and woven jacket texture, delicate film grain, no plastic retouching or over-sharpening. Match a consistent commissioned portrait series with Buffett and Simons.
Constraints: no text, letters, captions, quotes, signatures, logos, brands, watermarks, charts, tickers, screens, financial instruments, books with writing, second person, collage, border or frame, product interaction, pointing, raised hands, endorsement pose or testimonial scene.
```

### Peter Lynch · lynch-portrait.png

```text
Use case: photorealistic-natural.
Asset type: one vertical 2:3 AI-generated interpretive editorial portrait for a simulated investment-methodology interface, not a documentary photograph and not an endorsement.
Primary request: a single exceptionally high-quality, photorealistic black-and-white portrait of Peter Lynch in later life, the public historical figure associated with practical growth investing. He has a recognizable mature face, softly graying hair, alert observant eyes, a natural approachable expression without a sales smile, and a simple dark jacket with an unbranded shirt.
Scene/backdrop: deep charcoal-black seamless photography studio, no objects.
Composition/framing: vertical 2:3, seated upper-body three-quarter portrait, complete head and shoulders comfortably inside the frame, subtle lean forward suggesting attentive observation, hands below frame with no gesture, one person only.
Lighting/mood: one large directional studio key light from 45 degrees above camera left, restrained fill, realistic eye catchlight, gentle falloff into charcoal, quiet curiosity and practical intelligence.
Style/medium: sophisticated silver-gelatin black-and-white editorial portrait photography, rich dimensional blacks, fine silver midtones, authentic skin texture, hair and fabric detail, delicate film grain, natural anatomy, no beauty retouching or over-sharpening. Match the same high-end investment-committee portrait commission as Buffett and Simons.
Constraints: no text, letters, captions, quotes, signatures, logos, brands, watermarks, charts, tickers, screens, financial instruments, retail props, papers with writing, second person, collage, border or frame, product interaction, sales gesture, endorsement pose or testimonial scene.
```

### George Soros · soros-portrait.png

```text
Use case: photorealistic-natural.
Asset type: one vertical 2:3 AI-generated interpretive editorial portrait for a simulated investment-methodology interface, not a documentary photograph and not an endorsement.
Primary request: a single exceptionally high-quality, photorealistic black-and-white portrait of George Soros in later life, the public historical figure associated with global macro investing and reflexivity. He has a recognizable elderly face, neatly brushed silver hair, an observant reserved expression, and understated eyeglasses with a dark unbranded suit and white shirt.
Scene/backdrop: deep charcoal-black seamless photography studio, no objects.
Composition/framing: vertical 2:3, chest-up three-quarter portrait turned slightly away from camera, eyes looking just past the lens as if considering a complex question, complete head and shoulders comfortably inside the frame, hands out of frame, one person only.
Lighting/mood: one large directional studio key light from 45 degrees above camera left with a controlled split-light edge, gentle shadow-side fill that preserves facial detail, realistic eye catchlight, quiet tension and contemplative macro perspective.
Style/medium: sophisticated silver-gelatin black-and-white editorial portrait photography, dimensional blacks, nuanced silver-gray midtones, authentic skin pores, age lines, hair and wool-suit texture, delicate film grain, natural anatomy, no plastic retouching or over-sharpening. Match a consistent elite investment-committee portrait commission with the existing Buffett and Simons images.
Constraints: no text, letters, captions, quotes, signatures, logos, brands, watermarks, charts, tickers, screens, financial instruments, maps, papers with writing, second person, collage, border or frame, product interaction, pointing, raised hands, endorsement pose or testimonial scene.
```

### Ray Dalio · dalio-portrait.png

```text
Use case: photorealistic-natural.
Asset type: one vertical 2:3 AI-generated interpretive editorial portrait for a simulated investment-methodology interface, not a documentary photograph and not an endorsement.
Primary request: a single exceptionally high-quality, photorealistic black-and-white portrait of Ray Dalio in later life, the public historical figure associated with macro allocation and systematic risk balancing. He has a recognizable mature face, a bald crown with short silver hair at the sides, calm attentive eyes, and a restrained dark jacket over an unbranded open-collar white shirt.
Scene/backdrop: deep charcoal-black seamless photography studio, no objects.
Composition/framing: vertical 2:3, symmetrical seated upper-body portrait with shoulders square to camera, relaxed hands resting below the frame and no gesture, complete head and shoulders comfortably inside the frame, one person only. The geometry should feel balanced but human, not a corporate headshot.
Lighting/mood: one large directional studio key light from 45 degrees above camera left, soft low-level fill, measured catchlight, gentle edge separation on the hair and jacket, composed and methodical mood.
Style/medium: sophisticated silver-gelatin black-and-white editorial portrait photography, rich dimensional blacks, precise silver midtones, authentic skin texture, fine hair and fabric detail, delicate film grain, natural anatomy, no plastic skin or over-sharpening. Match the same restrained commissioned portrait quality as Buffett and Simons.
Constraints: no text, letters, captions, quotes, signatures, logos, brands, watermarks, charts, tickers, screens, financial instruments, dashboards, papers with writing, second person, collage, border or frame, product interaction, pointing, raised hands, endorsement pose or testimonial scene.
```

### Jesse Livermore · livermore-portrait.png

```text
Use case: photorealistic-natural.
Asset type: one vertical 2:3 AI-generated interpretive editorial portrait for a simulated investment-methodology interface, not a documentary photograph and not an endorsement.
Primary request: a single exceptionally high-quality, photorealistic black-and-white portrait of Jesse Livermore, the early twentieth-century public historical figure associated with tape reading and speculative trading. Depict him as a mature man with a recognizable neatly parted hairstyle, a discreet period mustache, a composed penetrating expression, and an authentic dark three-piece suit with a white shirt and narrow unbranded tie.
Scene/backdrop: deep charcoal-black seamless photography studio, no objects, no period set dressing.
Composition/framing: vertical 2:3, upper-body three-quarter portrait with the torso angled slightly while the face returns toward camera, complete head and shoulders comfortably inside the frame, hands below frame with no gesture, one person only. Keep the full hair silhouette inside the frame.
Lighting/mood: one large directional studio key light from 45 degrees above camera left, restrained shadow-side fill, controlled eye catchlight, subtle rim on hair and lapel, quiet historical gravity rather than theatrical drama.
Style/medium: sophisticated silver-gelatin black-and-white editorial portrait photography, rich dimensional blacks, nuanced silver midtones, authentic skin, mustache, hair, shirt and period wool texture, delicate film grain, natural anatomy, no sepia, no illustration, no plastic retouching or over-sharpening. Match a consistent commissioned portrait archive with Buffett and Simons.
Constraints: no text, letters, captions, quotes, signatures, logos, brands, watermarks, charts, tickers, screens, financial instruments, ticker tape, trading floor, papers with writing, second person, collage, border or frame, product interaction, pointing, raised hands, endorsement pose or testimonial scene.
```

## 使用说明

- 新增资产只放在 `skills/deep-analysis/assets/ajay-council/`；Buffett/Simons 继续使用 `skills/deep-analysis/assets/ajay-brand/` 的既有文件。
- 页面应把这些图当作方法论角色卡，而不是实时人物、采访或推荐信；与每张图并列显示统一非背书标签。
- 不将生成肖像与具体证券、公司 logo、实时行情、人物引语或“本人推荐”按钮拼接在一起。
