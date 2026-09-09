# aJay 变更记录

上游 stock-deep-analyzer 的历史见 [docs/UPSTREAM-RELEASE-NOTES.md](docs/UPSTREAM-RELEASE-NOTES.md)。

## v1.0.1 · 2026-09-09

- 安装脚本 `setup.sh` / `install-hermes.sh` / `INSTALL-HERMES.md` 不再默认克隆上游 UZI-Skill:源码目录内直跑,否则需 `AJAY_REPO_URL`。
- 修复上游 `hooks/session-start` 在 macOS 上因 GNU-only sed 输出非法 JSON、banner 被静默丢弃的 bug(改用 python 编码)。
- 安装快照不再带测试夹具缓存。

## v1.0.0 · 2026-09-09

派生自 stock-deep-analyzer 3.9.4(wbh604/UZI-Skill,MIT)。

- 改名:插件 `ajay`(命令前缀 `/ajay:`)、marketplace `ajay-skill`、环境变量前缀 `UZI_*` → `AJAY_*`、运行时目录 `~/.uzi-skill/` → `~/.ajay-skill/`。上游 issue/PR 链接原样保留。
- 去掉默认的上游 GitHub 更新检查:只有设了 `AJAY_REPO=owner/repo` 才检查(派生版没有上游 release 可"升级")。
- 新增美股补数链 `skills/deep-analysis/scripts/us_backfill.py`(stage1 之后跑,含 `--dry-run`):
  - SEC XBRL:ROE 5 年史、现金+短投(含 MarketableSecuritiesCurrent)、逐季 TTM EPS/BVPS 阶梯 → 精确 PE/PB 5 年分位
  - moomoo OpenD:美股日度资金流向(超大+大单=主力)→ 12_capital_flow
  - yfinance:同业对标表 → 4_peers
  - FMP(可选 `FMP_APIKEY`):目标价共识/评级分布 → 6_research
  - czsc 1.0 缠论:日线+周线 笔/中枢/未完成笔 + 按 108 课定义标注的买卖点候选 → 2_kline.chan(`chan_signals.py`)
- 新增 `merge_panel.py`:把 role-play agent 的评委判断合并回 panel.json 并按 v2.15.5 公式重算共识/流派分(此前每次分析都要手写)。
- `commands/analyze-stock.md` 流程加入美股补数与指纹重跑链(补 raw → stage1_modeling → agent → agent_analysis 带新 hash → stage2)。
- 已知:pandas 3.0 下 DatetimeIndex 单位可能是秒,与 `to_datetime` 的微秒比较会全错——`us_backfill.py` 统一 `as_unit("s")`。
