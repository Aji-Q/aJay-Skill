# J Trader functional and application audit

Audit date: 2026-09-09. Target: the default continuous single-security report
and the `python run.py <ticker>` workflow.

## Release gates

| Area | Result | Evidence |
|---|---|---|
| Actual analysis run | Pass | `python run.py AAPL --depth lite --no-browser` completed and rebuilt the standalone report. |
| Market-specific panel | Pass | US reports evaluate 42 market-applicable roles and exclude 24 A-share-only short-term traders before scoring. |
| Missing-data truthfulness | Pass | Missing debt ratio, five-year ROE history, PE percentile and failed macro fallback no longer appear as observed zero/default facts in panel conclusions. |
| Financial visualization | Pass | Missing/non-finite history points are removed with year alignment preserved; renderer internals are not exposed to readers. |
| Provider provenance | Pass | US quote/history records identify the US provider or fallback chain rather than an A-share source label. |
| Search and school filters | Pass | Perspective search returned 1/42 for Buffett; the value-school filter returned 6/42. |
| Evidence workflow | Pass | Evidence buttons open a modal with status, provider, period, collected time, facts and raw input. Focus returns on close. |
| Export workflow | Pass | Export dialog opens; research-input download produced `J-Trader-AAPL-inputs.json`; print/share remains available. |
| Reading controls | Pass | Light/dark reading theme toggles and persists; chapter navigation and progress remain functional. |
| Responsive use | Pass | 390×844 mobile review preserves the brief, findings, price, primary actions and chapter bar without replacing the report with a photo gallery. |
| Browser console | Pass | Reloaded standalone report produced no page-script or missing-favicon error. |
| Automated regression | Pass | Full pytest, JavaScript syntax and diff-whitespace checks are required immediately before release. |

## Product behavior retained

- The report remains a functional research website: brief, evidence quality,
  company quality, valuation models, disagreement, decision conditions and raw
  records are present in one continuous document.
- City photography establishes financial context but does not change or hide
  security data.
- A missing or unreviewed input reduces/withholds decision certainty rather
  than being silently converted into a favorable fact.
- Investor identities are method simulations, not actual participation or
  endorsement.

## Environment-dependent extras

The HTML report, JSON export and browser interactions do not require a browser
binary during generation. Optional pre-rendered share/war-report PNG capture
requires a compatible local Playwright Chromium installation; generation
continues with an explicit warning when it is absent.
