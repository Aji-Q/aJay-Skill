<div align="center">

# aJay

### Put the world's financial centers inside your local research room.

**Enter a ticker. Get an evidence-linked, challengeable, decision-ready equity research website.**

[![Version](https://img.shields.io/badge/version-1.1.0-C7A46A?style=for-the-badge)](RELEASE-NOTES.md)
[![Focus](https://img.shields.io/badge/focus-US%20Equities-0B1118?style=for-the-badge)](#not-another-stock-scorecard)
[![Report](https://img.shields.io/badge/output-Self--contained%20HTML-17324D?style=for-the-badge)](#one-command-to-start)
[![Tests](https://img.shields.io/badge/release%20gate-1004%20tests%20passed-2E7D65?style=for-the-badge)](docs/FUNCTIONAL-AUDIT.md)
[![License](https://img.shields.io/badge/license-MIT-E7E4DC?style=for-the-badge&labelColor=4B5563)](LICENSE)

[中文](README.md) · [Quick start](#one-command-to-start) · [See the product](#not-another-stock-scorecard) · [Analysis audit](docs/ANALYSIS-AUDIT.md) · [Functional audit](docs/FUNCTIONAL-AUDIT.md) · [Issues](https://github.com/Aji-Q/aJay-Skill/issues)

</div>

![aJay private research report — Wall Street investment brief](docs/readme/ajay-report-hero.jpg)

> **You do not need a seventeenth market-data dashboard.** You need a research system willing to put evidence gaps, valuation assumptions, the bear case, and decision conditions on the same page.
>
> **aJay is not an “AI gives a stock a score” toy.** It behaves more like an always-on private investment committee: verify the evidence, understand the business, model the price, organize disagreement, and define what would justify action—or invalidate the thesis.

## Not another stock scorecard

aJay turns single-name research into a continuous, interactive financial website. Start with a New York investment brief, move through Shanghai business quality, a London valuation desk and Hong Kong market disagreement, then finish with explicit decision conditions and the complete evidence ledger.

| Typical stock tool | aJay |
|---|---|
| Produces a score | Produces a **claim, evidence, counter-evidence and known gaps** |
| Shows charts without a reading order | Organizes research into a **six-chapter buy-side narrative** |
| Shows a DCF target | Shows **inputs, assumptions, outputs and sensitivity** |
| Sounds certain when data is missing | Preserves unknowns instead of inventing zeroes or defaults |
| Reduces investors to quotations | Places 42 US-market-compatible simulated methods in one searchable debate |
| Depends on a hosted dashboard | Generates a portable, offline **single-file HTML report** |

## One ticker. Six research rooms.

```text
TICKER
  └─ Public data and source validation
       └─ 19 research dimensions
            └─ Business quality and capital efficiency
                 └─ DCF / relative value / LBO / sensitivity
                      └─ 42 market-compatible perspectives in disagreement
                           └─ Buy conditions / invalidation / risk boundaries
                                └─ Traceable, exportable research website
```

### Investment brief first

The first screen shows the claim, supporting evidence, material gaps, price and the boundary of the conclusion. Readers know what the report is arguing before they enter the detail.

### Business quality as a continuous story

Revenue, earnings, ROE, dividends, leverage and cash flow unfold as a narrative rather than a pile of dashboard cards.

![aJay business-quality chapter — Shanghai financial district](docs/readme/ajay-business-quality.jpg)

### Valuation as an attackable set of assumptions

Current multiples, historical percentiles, peer context, DCF value and a sensitivity matrix live in one workspace. The output matters; what the output depends on matters more.

![aJay valuation workspace — DCF and sensitivity analysis](docs/readme/ajay-valuation-workspace.jpg)

### Disagreement becomes a research asset

Value, quality, growth, quantitative, macro and trading methods interpret the same company differently. Search by name, school or keyword, then jump back to the underlying evidence.

![aJay market disagreement chapter — Hong Kong financial district](docs/readme/ajay-market-disagreement.jpg)

## A private investment committee that does not fake certainty

The current US report assembles 42 market-compatible simulated perspectives, including method archetypes associated with Buffett, Munger, Graham, Lynch, Dalio, Soros, Simons and Livermore. A-share-only short-term roles are automatically excluded from US reports.

These are simulations—not real votes, endorsements or independent expert opinions. Their purpose is to expose:

- how different investment systems read the same evidence;
- whether disagreement comes from facts or assumptions;
- which counter-evidence could invalidate the thesis;
- what is still unknown and therefore should not support a conclusion.

## Built for decisions, not decoration

- **Traceable evidence:** material claims link to providers, dates and raw records.
- **Visible gaps:** missing inputs, proxies and degraded sources stay visible.
- **Inspectable models:** valuation inputs, assumptions, outputs, ranges and sensitivity share one path.
- **Searchable disagreement:** search the full perspective record by method and keyword.
- **Portable research:** export the research inputs and a self-contained HTML report; local by default.
- **Desktop and mobile:** preserve the decision flow across large screens and phones.

<p align="center">
  <img src="docs/readme/ajay-report-mobile.png" width="360" alt="aJay mobile equity research report" />
</p>

## One command to start

Requires Git and Python 3.10+:

```bash
git clone https://github.com/Aji-Q/aJay-Skill.git
cd aJay-Skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py AAPL --depth medium --no-browser
```

The CLI prints the report path when complete. Open `full-report-standalone.html` to read, archive or share it offline.

| Mode | Best for | Output |
|---|---|---|
| `lite` | Fast screening | Core data, rule scan and initial risks |
| `medium` | Everyday single-name research | Broader data, modeling and report generation |
| Deep research workflow | Pre-position, post-earnings, investment memo | Data backfill, method review, input fingerprint and human quality gates |

For genuine deep research, have an agent follow [AGENTS.md](AGENTS.md) and [analyze-stock](commands/analyze-stock.md) through evidence collection, backfill, recomputation, method review and final inspection. One automated CLI run is not an independent analyst review.

### Want the experience before waiting for live data?

```bash
cd skills/deep-analysis/scripts
python preview_editorial.py
```

Aster Systems / `AJAY.DEMO` is a synthetic fixture, not a security or recommendation.

## Data and boundaries

US equities are the current focus: SEC XBRL financial backfill, yfinance market and peer data, plus optional FMP consensus and moomoo OpenD fund-flow inputs. Availability depends on access, configuration and the security. Inherited A-share, Hong Kong and Dragon-Tiger workflows remain available, but coverage is not identical across markets.

See [.env.example](.env.example) for optional providers. Reports stay local by default; `--remote` is an explicit publishing choice. Inspect the report for private information before using it.

## Proven in the release gate

The v1.1 release was exercised through a real AAPL report flow: generation, the 42-member US-compatible roster, search and school filters, evidence modal, theme switch, research-input export, mobile layout and browser console. The automated suite completed with **1004 passed**.

[Analysis architecture audit](docs/ANALYSIS-AUDIT.md) · [Functional application audit](docs/FUNCTIONAL-AUDIT.md) · [UI delivery record](docs/UI-REFACTOR.md) · [Image provenance](docs/IMAGE-PROVENANCE.md)

## Use it with your agent stack

| Environment | Entry point |
|---|---|
| Codex | [.codex/INSTALL.md](.codex/INSTALL.md) |
| Claude Code / Cursor | [AGENTS.md](AGENTS.md) and the repository plugin manifest |
| Gemini CLI | [GEMINI.md](GEMINI.md) |
| OpenCode | [.opencode/INSTALL.md](.opencode/INSTALL.md) |
| Hermes | [INSTALL-HERMES.md](INSTALL-HERMES.md) |

## Built by aJay

**aJay (Aji-Q) owns and maintains the aJay identity, product direction and project modifications.** See [OWNERSHIP.md](docs/OWNERSHIP.md) and [NOTICE](NOTICE) for maintenance boundaries and software provenance.

The project derives from MIT-licensed stock-deep-analyzer 3.9.4 and preserves upstream copyright and contributor records. Photography and image-tool transformations have provenance records. Simulated investment methods are not statements, votes or endorsements by real people.

<div align="center">

**Research should not end with a score. It should end with a judgment you can defend.**

[Get started](#one-command-to-start) · [Release notes](RELEASE-NOTES.md) · [Open an issue](https://github.com/Aji-Q/aJay-Skill/issues)

<sub>Research support only; not investment advice. Independently verify data and assumptions.</sub>

</div>
