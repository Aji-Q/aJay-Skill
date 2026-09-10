# J Trader · 让 AI Agent 自动交付价格结构图

**给股票代码，不再手工补图。** 标准分析流程已内置缠论与价格行为计算；只想研究价格时，也可直接生成一份单文件交互图，离线打开、逐笔解释、追溯日期和价位。

## 1. 两种入口

以下命令均在仓库根目录运行；`python` 使用已安装本项目依赖的 Python 3.10+ 环境。本机验证环境为 `/opt/anaconda3/bin/python`。

```bash
# 只从已有 AAPL 分析缓存重绘：不刷新行情，不修改审核状态
python skills/deep-analysis/scripts/chart_stock.py AAPL \
  --input skills/deep-analysis/scripts/.cache/AAPL/raw_data.json \
  --output skills/deep-analysis/scripts/reports/AAPL-chart

# 独立分析另一个股票，显式联网获取行情
python skills/deep-analysis/scripts/chart_stock.py MSFT --refresh \
  --output skills/deep-analysis/scripts/reports/MSFT-chart

# 完全离线：自己的 OHLCV / fetch_kline / chan.v1 / raw_data JSON
python skills/deep-analysis/scripts/chart_stock.py 600519.SH \
  --input /absolute/path/ohlcv.json \
  --output /absolute/path/research-chart.html
```

默认不联网；不传 `--input` 时读取 `.cache/<TICKER>/raw_data.json`。`--refresh` 与 `--input` 互斥。输出已有文件需显式加 `--force`；程序始终保护源文件及 `raw_data.json`、`panel.json`、`agent_analysis.json` 等审核文件。

每次输出两个文件：
- `chart.html`：嵌入行情、结构、样式、交互和 GSAP，无 CDN、无外部运行服务。
- `chart.json`：`jtrader.chart.v1` 结构，AI Agent 可读取后解释/复核，也可再次作为 `--input` 重绘。

标准 `python run.py <TICKER>` 的 K 线采集器也自动执行同一价格行为函数，不需要先跑独立命令。本入口仅交付价格研究图，不替代深度基本面分析所需的独立审核。

## 2. AI Agent 的交付流程

1. 确认股票代码与市场，选已有缓存、用户提供数据或显式刷新。
2. 运行 `chart_stock.py`；程序输出实际绝对路径、各周期根数和叠加结构数。
3. 读取 `chart.json` 中来源、复权、截止时间、质量与缺口。数据不足保留普通 K 线，不伪装成完整信号。
4. 围绕 `id`、`dt`、`price`、`evidence` 与 `invalid_if` 写讲解。每句话都对应图中可找到的日期与价位；不要另造买卖点或概率。
5. 打开 HTML，核对日/周切换、缩放、结构选择、点位表；再把 HTML 与 JSON 一起交给用户。

用户可直接对 Agent 说：**“用 J Trader 给 MSFT 生成缠论和价格行为图，解释最近中枢、已确认支撑阻力、突破与失效条件，并交付离线图。”**

## 3. 两层计算，各司其职

### 缠论层：`chan.v1`

复用项目现有 `chan_signals.py` 与已固定的 **CZSC 1.0.1**。保留分型、完成/未完成笔、笔级中枢、三买/三卖候选、一买/一卖力度代理候选。这里没有新增线段、二买二卖或严格 MACD 背驰；也不把官方全部信号库的数量宣传成已接入功能。[CZSC 官方实现说明](https://github.com/waditu/czsc)

美股默认单一命中源最多六年日线，日线图截取最近两年，周线同源聚合。其它市场使用该市场供应链实际返回的日线窗口；可用区间以 JSON 实际日期为准，不承诺每个市场都有六年。复用已有 `chan.v1` 时保留原周线历史，不把较短的日线截取重新冒充六年周线。

### 价格行为层：`price_action.v1`

独立的**确定性启发式观察**，不是严格缠论，也不是概率预测：

| 结构 | 实际计算与时间约束 |
|---|---|
| MA20 / MA60 | 收盘价简单均线；未满周期为 `null`，不补造均线 |
| ATR14 | `max(H−L, |H−前收|, |L−前收|)`；首14个有前收的 TR 均值起算，后续 Wilder 递推；用于区域宽度，不是目标价。公式对照 [TA-Lib ATR 源码](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_ATR.c) |
| 成交量 / 量比 | 当前成交量 ÷ **此前**20根成交量均值；当前根不进入自身基准，缺失时不推定放量 |
| 支撑 / 阻力 | 两侧各3根的严格局部高/低点，右侧确认完成后才启用；平台相同高低点不强选一个拐点 |
| 观察区域 | 确认日 ATR14 × 0.25 作为价位两侧宽度；ATR不足时为精确水平价，不虚设区间 |
| 突破 / 跌破 | 只在区域确认之后，比较相邻收盘是否穿越区域；记录当日收盘、前收、原区域和量比 |
| 回踩 / 失效 | 只在突破之后观察；回踩触区且收在突破侧；之后继续扫描，后续反向收盘穿越区域则标失效并截止水平线 |

末根日/周 K 线收盘状态未核验时仍画出行情，但不参与新的摆动、突破或回踩确认。`summary.confirmed_through` 与 `last_bar_complete` 明确区分观察日期和确认截止日。整个页面解释的是当前输入快照，**不回放过去的信息集，不提供胜率或收益回测**。

## 4. 机器契约

```text
2_kline.data.chan.levels.D|W
  bars / fractals / bis / unfinished_bi / centers / signals / invalidations / steps
  price_action                           # 同日期、同原始 bars 索引
    schema_version: price_action.v1
    indicators: ma20[], ma60[], atr14[], volume_sma20[], relative_volume[]
    moving_averages: [{id, label, period, points:[{index, price}]}]
    volume: [{index, volume}]
    swings: [{id, kind, anchor_index, confirmed_index, dt, confirmed_at, price}]
    levels: [{id, kind, label, anchor_index, start_index, end_index,
              confirmed_at, price, zone_low, zone_high, status, status_as_of,
              reason, evidence, invalid_if, invalidated_at?}]
    events: [{id, level_id, kind, index, anchor_index, dt, price,
              status, reason, evidence, invalid_if, relative_volume}]
    summary / provenance / parameters / quality / warnings
2_kline.data.price_action                 # 同一数据的直接读取入口
```

结构 ID 稳定绑定周期、摆动日期与事件日期。画线起点从确认时刻开始，原摆动日期通过 `anchor_index` 保留用于解释。默认最多显示最近24个确认区域，只保留能解析到这些区域的事件；这不是全历史信号数据库。已有第三方 `chan.v1` 日期/索引不一致时停用叠加层并写缺口，不静默把线画到别的蜡烛上。

## 5. 本地验证

2026-09-10 新进程验证：
- AAPL 实际已采集缓存：日线502根 / 周线314根；价格行为区域各24个，事件31 / 34个。未重新覆盖财务与评审缓存。
- 独立固定样本 `JTRADER.FIXTURE`：日线523根 / 周线137根；明确标记为非市场数据，验证程序不依赖 AAPL 固定数值。
- 专项覆盖：指标预热、量比不含当根、确认时间与无前置事件、先回踩后失效、空/异常数值、平台极值、同源坐标、无外链单文件、输入不可覆盖及 JSON 转义。

```bash
cd skills/deep-analysis/scripts
python -m pytest tests/test_price_action.py tests/test_chart_stock.py -q
```
