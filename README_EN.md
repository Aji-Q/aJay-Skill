# aJay

**A US-focused equity research workspace, maintained by aJay (Aji-Q).**

**Version 1.1.0 · Canonical repository: [Aji-Q/aJay-Skill](https://github.com/Aji-Q/aJay-Skill)**

[中文](README.md) · [Workflow](AGENTS.md) · [Release notes](RELEASE-NOTES.md) · [Contributors](CONTRIBUTORS.md) · [Ownership](docs/OWNERSHIP.md) · [License](LICENSE)

## What it does

- Collects public-market evidence and separates observed data, rule-based scores, AI interpretation and simulated investment-method perspectives.
- Prioritizes US equity research, with SEC XBRL backfill, peer information, optional FMP consensus and moomoo OpenD fund flows. Availability depends on access, configuration and the security being researched.
- Organizes reports around a research summary, evidence quality, drivers, valuation assumptions, risks and detailed data.
- Retains inherited A-share/Hong Kong workflows for compatibility; coverage is not equally complete across markets.

Investor personas are simulations, not actual votes, independent expert opinions or endorsements. Scores and confidence indicators are not return probabilities or calibrated predictions.

## Install

Use Git and Python 3.10+:

```bash
git clone https://github.com/Aji-Q/aJay-Skill.git
cd aJay-Skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py AAPL --depth medium --no-browser
```

Use your own GitHub credentials if repository access requires authentication. Never add secrets to code, reports or issue descriptions.

Platform guides: [Codex](.codex/INSTALL.md), [OpenCode](.opencode/INSTALL.md), [Gemini](GEMINI.md), [Hermes](INSTALL-HERMES.md). For Hermes, review its guide before running this repository's `install-hermes.sh`.

Reports stay local by default. The CLI prints the generated HTML path. `--remote` explicitly publishes access to a report; inspect its contents before choosing that option.

## Research workflow

`lite` and `medium` are automated scans. Deep research requires the review loop in [AGENTS.md](AGENTS.md) and [analyze-stock](commands/analyze-stock.md): collect evidence, backfill US data when appropriate, recompute modeling and the input fingerprint, perform evidence-backed review, then render and inspect the report.

See [.env.example](.env.example) for optional data-provider configuration. Missing sources must remain visible as gaps rather than implied certainty.

## Update and test

```bash
git remote get-url origin
# Expected: https://github.com/Aji-Q/aJay-Skill.git (or its GitHub SSH equivalent)
git pull --ff-only
python -m pip install -r requirements.txt
cd skills/deep-analysis/scripts
python -m pytest tests/ -q
```

Release checks are opt-in through `AJAY_REPO=Aji-Q/aJay-Skill`; `AJAY_NO_UPDATE_CHECK=1` disables them. No release or a failed request does not establish that your checkout is current.

## Ownership and provenance

**aJay owns and maintains the aJay project identity and its own modifications.** The codebase is derived from MIT-licensed stock-deep-analyzer 3.9.4, not wholly original aJay code. Original copyright and contributor records remain intact.

See [NOTICE](NOTICE), [current contribution attribution](CONTRIBUTORS.md), [ownership rules](docs/OWNERSHIP.md), [upstream release history](docs/UPSTREAM-RELEASE-NOTES.md) and [upstream contributors](docs/UPSTREAM-CONTRIBUTORS.md). The current release records aJay's direction and authorship share at 75%+ and Codex's implementation/compilation assistance at up to 25%. Report problems to the [aJay issue tracker](https://github.com/Aji-Q/aJay-Skill/issues).

Old README files and screenshots are retained as historical evidence, not current installation or promotion material. The report's editorial layout is informed by Vantara; its logos, photographs and copy are not used, and no affiliation is implied.

Research support only; not investment advice. Independently verify data and assumptions before making decisions.

## Continuous research report preview

The default single-security report is a continuous, six-chapter research website: brief, business quality, valuation, market disagreement, decision conditions, and evidence. Four financial photographs define distinct chapter compositions rather than interchangeable backgrounds. Shanghai's tower unfolds vertically across the business-quality chapter. Eight simulated method perspectives are connected to evidence; generated portraits are not endorsements.

```bash
cd skills/deep-analysis/scripts
python preview_editorial.py
```

The fixture is synthetic, not a security recommendation. The default build produces identical, self-contained `full-report.html` and `full-report-standalone.html`. All 19 research dimensions, available valuation models, model assumptions, perspective search/filtering, evidence inspection and exports remain in the main report. Missing products have explicit empty states. See [analysis audit](docs/ANALYSIS-AUDIT.md), [functional application audit](docs/FUNCTIONAL-AUDIT.md), [UI delivery notes](docs/UI-REFACTOR.md), and [design specification](docs/brand-spec.md).

Original photography and image-tool edits are tracked in `docs/PHOTOGRAPHY-PROVENANCE.md`; no celebrity endorsement or calibrated return probability is claimed. Explicit `council` and `editorial` layouts remain for compatibility, not as the default experience.
