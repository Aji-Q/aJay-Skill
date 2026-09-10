<div align="center">

# J Trader

### Give every stock on your watchlist its own research analyst.

Hand J Trader a US ticker.<br>
It checks the business, models valuation, challenges the thesis, and returns a research website you can keep.

**Open-source AI equity research assistant**

[Research your first stock](#first-stock) · [See the report](#report) · [Install](#install) · [Explore workflows](#workflows)

[中文](README.md)

</div>

![J Trader equity research report](docs/readme/ajay-report-hero.jpg)

## Your watchlist grew. Your research queue grew faster.

You find an interesting company and save the ticker.

Doing the real work means opening filings, collecting financials, comparing peers, building a valuation, and looking for what could prove you wrong. Soon the browser is full of tabs—and the original question is still unanswered: **what does this business earn, and what am I paying for it?**

J Trader takes on that preparation. Give it a ticker and it organizes public data, operating evidence, valuation assumptions, disagreement, and risks into one browser-based research report.

Start with the stock you have been meaning to understand.

<a id="first-stock"></a>

## Research your first stock

After [installation](#install), ask your agent to read `AGENTS.md` in the project directory, then send:

```text
Use J Trader to research AAPL.
Explain how the company makes money, whether the current price is demanding,
and the strongest bear case. Generate an HTML report and mark every data gap.
```

For a basic local report, run:

```bash
python run.py AAPL --depth medium --no-browser
```

The terminal prints the report path. A deep-research run also requires agent review; one standalone CLI run is not the complete deep workflow.

> **J Trader is the product. aJay is the maintainer.** To protect existing installations, the repository name, plugin ID, command prefix, and `AJAY_*` environment variables continue to use `aJay-Skill` / `ajay` as compatibility identifiers.

## See how the business actually works

What drives revenue? Did cash flow follow earnings? Is leverage helping the business—or narrowing its choices?

J Trader reads operating performance, cash generation, and capital efficiency together. Missing evidence and unanswered questions remain visible instead of being filled with convenient assumptions.

![Business quality and financial analysis](docs/readme/ajay-business-quality.jpg)

## Put the valuation assumptions on the table

A single price target can hide a great deal of optimism.

J Trader places discounted cash flow, comparable-company analysis, and sensitivity analysis in the same workspace. Change the discount rate or long-term growth assumption and see how the estimated value moves—then decide whether you agree with the inputs.

![Valuation model and sensitivity workspace](docs/readme/ajay-valuation-workspace.jpg)

## You have the bull case. Now hear the opposition.

You may like the growth while another method rejects the price. You may trust the industry trend while another lens focuses on cash conversion or macro risk.

For US-equity reports, J Trader can organize **42 simulated investment-method perspectives** across value, growth, macro, trend, and quantitative schools. Filter by school or search the debate for the question you care about.

<sub>These perspectives are algorithmic / AI simulations—not participation, statements, or endorsement by real investors, and not 42 independent evidence sources.</sub>

<a id="report"></a>

## Finish with a report you can keep

Open the report in a browser and follow one continuous path: company, business, valuation, disagreement, risk, and the underlying evidence record. Or jump directly to the chapter you need.

Open an evidence record to check a number. Save the self-contained HTML and research inputs to continue later. Compare a future run with the original thesis rather than starting from memory.

Reports support search, school filters, mobile reading, and offline use. They stay local by default.

<p align="center">
  <img src="docs/readme/ajay-report-mobile.png" width="340" alt="J Trader mobile research report" />
</p>

## Use only the depth the question deserves

| The question in front of you | Workflow |
|---|---|
| Is this stock worth a deeper look? | `/ajay:quick-scan AAPL` |
| Where did this valuation come from? | `/ajay:dcf MSFT` |
| Why is it expensive relative to peers? | `/ajay:comps AMD` |
| What changed after earnings? | `/ajay:earnings AAPL` |
| Research it properly and leave a complete record. | `/ajay:analyze-stock AAPL` |

These slash commands are for Claude Code. Other supported agent environments can use natural language. Tickers are examples, not recommendations.

<a id="install"></a>

## Install

Requires Git and Python 3.10+. The full deep-research workflow also needs an agent that can read project files, run the scripts, and review the evidence.

### Claude Code

```text
/plugin marketplace add Aji-Q/aJay-Skill
/plugin install ajay@ajay-skill
/ajay:analyze-stock AAPL
```

### Codex

Ask Codex to follow this installation guide, then read the repository's `AGENTS.md`:

```text
https://raw.githubusercontent.com/Aji-Q/aJay-Skill/main/.codex/INSTALL.md
```

See [.codex/INSTALL.md](.codex/INSTALL.md) for details.

### Python / CLI

```bash
git clone https://github.com/Aji-Q/aJay-Skill.git
cd aJay-Skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py AAPL --depth medium --no-browser
```

Open `full-report-standalone.html` from the output directory printed by the CLI.

<details>
<summary><strong>Gemini CLI, OpenCode, Hermes, and other environments</strong></summary>

### Gemini CLI

```bash
gemini extensions install https://github.com/Aji-Q/aJay-Skill
```

### OpenCode

Follow [.opencode/INSTALL.md](.opencode/INSTALL.md).

### Hermes

From the cloned repository:

```bash
bash install-hermes.sh "$PWD"
```

See [INSTALL-HERMES.md](INSTALL-HERMES.md). Other agent entry points are documented in [AGENTS.md](AGENTS.md).

</details>

<details>
<summary><strong>Preview the product locally</strong></summary>

```bash
cd skills/deep-analysis/scripts
python preview_editorial.py
```

Aster Systems / `JTRADER.DEMO` is a synthetic UI fixture—not a real security or performance record.

</details>

<a id="workflows"></a>

## Explore all 20 workflows

<details>
<summary><strong>Open the complete workflow list</strong></summary>

| Command | Purpose |
|---|---|
| `/ajay:analyze-stock AAPL` | Full single-name research and final report |
| `/ajay:quick-scan NVDA` | Fast core-data and risk scan |
| `/ajay:dcf MSFT` | DCF, WACC, terminal value, and sensitivity |
| `/ajay:comps AMD` | Peer valuation, historical percentile, and implied price |
| `/ajay:lbo DELL` | LBO feasibility and IRR testing |
| `/ajay:segmental-model AMZN` | Segment revenue and three-scenario forecast |
| `/ajay:initiate META` | Initiating-coverage report |
| `/ajay:ic-memo GOOGL` | Investment-committee memo and scenario returns |
| `/ajay:earnings AAPL` | Earnings review and thesis impact |
| `/ajay:earnings-preview NVDA` | Consensus, scenarios, and implied move before earnings |
| `/ajay:model-update MSFT` | Model update after earnings or guidance |
| `/ajay:catalysts TSLA` | Completed events and future catalysts |
| `/ajay:thesis AMZN` | Thesis review and tracking |
| `/ajay:dd COST` | Due-diligence workflow and checklist |
| `/ajay:screen AAPL` | Value, growth, quality, GARP, and short screens |
| `/ajay:ai-readiness ORCL` | AI exposure, industry position, and key factors |
| `/ajay:panel-only AAPL` | Market-compatible method review only |
| `/ajay:scan-trap TICKER` | Promotion, flow, and trading-risk checks |
| `/ajay:returns` | Portfolio return and sector contribution attribution |
| `/ajay:rebalance` | Position drift, trade list, and turnover-cost analysis |

Available output depends on the market, providers, configuration, and input. Portfolio workflows require your data; a “trade list” is analytical output, not automated order execution.

</details>

<details>
<summary><strong>Research depth and advanced CLI options</strong></summary>

| Depth | Best for |
|---|---|
| `lite` | A fast read of core data and major risks |
| `medium` | Everyday research; the default |
| `deep` | Pre-position or post-earnings work with agent review |

```bash
python run.py AAPL --depth lite --no-browser
python run.py AAPL --depth medium --no-browser
python run.py AAPL --depth deep --no-browser
python run.py AAPL --school A --no-browser
python run.py --versus AAPL MSFT GOOGL
python run.py --portfolio holdings.csv
python run.py AAPL --from-modeling --no-browser
python run.py AAPL --output-dir ./output --no-browser
```

`deep` completes Stage 1, asks an agent to review the captured inputs, then assembles the report using the matching input fingerprint. See [AGENTS.md](AGENTS.md). Runtime depends on the model, network, and data coverage.

</details>

## What “AI research” means here

- Material conclusions should be traceable to a source, date, model input, or explicit assumption.
- Missing fields remain missing; no data is not the same as zero.
- Scores describe rule coverage, not the probability that a stock will rise.
- Simulated investor methods are analysis lenses, not real statements, votes, or endorsements.
- Research reports support decisions; they do not replace independent verification or constitute investment advice.

Read the [analysis architecture audit](docs/ANALYSIS-AUDIT.md), [functional audit](docs/FUNCTIONAL-AUDIT.md), [ownership policy](docs/OWNERSHIP.md), and [NOTICE](NOTICE) for the detailed boundaries.

## Open source, with attribution preserved

J Trader is maintained by **aJay (Aji-Q)**. The project derives from the MIT-licensed stock-deep-analyzer 3.9.4 and preserves upstream copyright and contribution records. Photography, image transformations, and third-party runtime assets retain their own provenance and licenses.

<div align="center">

**A stock idea is easy to save. A defensible judgment takes a system.**

[Start with one ticker](#first-stock) · [Release notes](RELEASE-NOTES.md) · [Open an issue](https://github.com/Aji-Q/aJay-Skill/issues)

<sub>Research support only. Independently verify data and assumptions.</sub>

</div>
