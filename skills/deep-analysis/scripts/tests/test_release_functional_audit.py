from __future__ import annotations

from pathlib import Path


def test_financial_chart_drops_missing_points_without_reader_facing_error():
    from lib.report.dim_viz import _viz_financials

    html = _viz_financials({
        "revenue_history": [None, 100.0, 120.0],
        "net_profit_history": [None, 10.0, 15.0],
        "financial_years": ["2021", "2022", "2023"],
    })

    assert "viz error" not in html
    assert "2021" not in html
    assert "2022" in html and "2023" in html


def test_financial_score_does_not_present_missing_debt_as_zero():
    from lib.pipeline.score_fns import score_dimensions

    raw = {"ticker": "AAPL", "dimensions": {
        "1_financials": {"data": {
            "roe": "148.8%",
            "net_margin": "27.6%",
            "revenue_history": [None, 100.0, 106.4],
            "revenue_growth_yoy": 16.4,
            "financial_health": {"total_debt": 98.0, "cash": 35.0},
        }},
    }}

    financial = score_dimensions(raw)["dimensions"]["1_financials"]
    assert "营收增速 +16.4%" in financial["label"]
    assert "负债率" not in financial["label"]
    assert not any("资产负债率" in reason for reason in financial["reasons_pass"])


def test_panel_rules_skip_unknown_financial_and_macro_inputs():
    from lib.investor_evaluator import evaluate
    from lib.stock_features import extract_features

    raw = {"ticker": "AAPL", "market": "U", "dimensions": {
        "0_basic": {"data": {"code": "AAPL", "name": "Apple Inc.", "price": 100, "pe_ttm": 20}},
        "1_financials": {"data": {"roe": "148.8%", "financial_health": {"cash": 35}}},
        "3_macro": {"fallback": True, "data": {
            "rate_cycle": "中性（自动兜底）",
            "_autofill_failed": {"reason": "no evidence"},
        }},
        "10_valuation": {"data": {}},
    }}
    features = extract_features(raw, {})

    assert features["debt_ratio"] is None
    assert features["pe_quantile_5y"] is None
    assert features["macro_rate_easing"] is None
    assert features["roe_observation_count"] == 0

    buffett = evaluate("buffett", features)
    rendered_rules = " ".join(
        rule["msg"] for key in ("pass_rules", "fail_rules") for rule in buffett[key]
    )
    assert "负债率 0%" not in rendered_rules
    assert "0/5 期" not in rendered_rules
    assert "5 年 50 分位" not in rendered_rules

    dalio = evaluate("dalio", features)
    assert all(rule["rule_id"] != "rate_cycle_pos" for rule in dalio["fail_rules"])


def test_us_fetcher_provenance_names_us_providers(monkeypatch):
    import fetch_basic
    import fetch_kline

    monkeypatch.setattr(fetch_basic.ds, "fetch_basic", lambda _ticker: {"price": 100})
    monkeypatch.setattr(fetch_kline.ds, "fetch_kline", lambda _ticker: [
        {"Date": f"2026-01-{day:02d}", "Open": day, "Close": day + 1,
         "High": day + 2, "Low": day - 1, "Volume": 1000}
        for day in range(1, 29)
    ])

    assert fetch_basic.main("AAPL")["source"] == "yfinance:Ticker.info"
    history_source = fetch_kline.main("AAPL")["source"]
    assert "US history" in history_source
    assert "stock_zh_a_hist" not in history_source


def test_continuous_report_embeds_favicon():
    template = (Path(__file__).resolve().parents[2] / "assets" / "report-continuous.html").read_text()
    assert 'rel="icon"' in template
    assert "data:image/svg+xml" in template
