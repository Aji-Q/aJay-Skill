---
name: ajay
description: J Trader, an open-source AI US-equity research skill (A-share/Hong Kong workflows retained for compatibility) for deep research, quick scans, investor panel review, hot-money/LHB analysis, trap detection, valuation, IC memos, and J Trader editorial HTML reports.
version: 1.2.0
author: aJay
license: MIT
metadata:
  tags: [finance, stocks, a-share, hong-kong, us-stocks, dcf, valuation, investor-panel, youzi, lhb, trap-detection]
  related_skills: [deep-analysis, investor-panel, lhb-analyzer, trap-detector]
---

# J Trader Skill Root · 1.2.0

**J Trader** is maintained by **aJay (Aji-Q)** at `https://github.com/Aji-Q/aJay-Skill`.
The product focus is US equity research; legacy A-share/Hong Kong workflows remain available.
Upstream code and contributor credit are recorded in `NOTICE` and `docs/OWNERSHIP.md`.

This root file is the top-level entry for agents that expect a `SKILL.md` at the repository root.

Use the narrowest matching workflow:

- Full stock research, valuation, IC memo, initiation, catalysts, earnings review, or HTML report:
  read `skills/deep-analysis/SKILL.md`.
- Investor jury, "which investors would buy", panel-only voting, or persona review:
  read `skills/investor-panel/SKILL.md`.
- Hot-money, LHB, seat recognition, or A-share short-term trader analysis:
  read `skills/lhb-analyzer/SKILL.md`.
- Trap detection, pump-and-dump checks, "teacher/group/friend recommended this stock", or safety review:
  read `skills/trap-detector/SKILL.md`.
- Command-specific requests:
  read the matching file under `commands/`.

## Default Execution

From the repository root:

```bash
python3 run.py <ticker> --no-browser
```

For remote/mobile reports:

```bash
python3 run.py <ticker> --remote
```

For a single investor school, such as A-share hot-money:

```bash
python3 run.py <ticker> --school F --no-browser
```

## Agent Rules

1. Treat scripts as data and scoring tools, not as final analyst judgment.
2. Do not invent numbers. Use script outputs, cached JSON, or current public evidence.
3. For serious deep-analysis requests, complete the agent review loop described in `skills/deep-analysis/SKILL.md` before final report assembly.
4. For hot-money analysis, apply LHB seat matching and `is_in_range()` before making a short-term judgment.
5. For trap detection, scan all eight signals and include concrete evidence when risk is non-trivial.
6. For report template or UI changes, update tests, version metadata, and release notes together.
