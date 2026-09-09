"""Focused tests for the omitted institutional-model supplement."""
from __future__ import annotations

from lib.report.model_supplement import render_model_supplement


def _raw_with_omitted_products() -> dict:
    return {
        "ticker": "TEST",
        "dimensions": {
            "20_valuation_models": {
                "source": "compute:fin_models",
                "fallback": False,
                "data": {
                    "three_statement": {
                        "method": "project_three_stmt",
                        "years": ["Y1", "Y2"],
                        "income_statement": {"revenue": [0, 12.5], "net_income": [1, float("nan")]},
                        "cash_flow": {"fcf": [3.25, float("inf")]},
                        "balance_sheet": {"equity_rollforward": [4, 5]},
                        "assumptions": {"growth": "<b>2%</b>", "wacc": 0},
                        "growth_path": ["base", "stress"],
                        "methodology_log": ["source row 1"],
                    }
                },
            },
            "21_research_workflow": {
                "source": 'provider"><script>alert(1)</script>',
                "fallback": True,
                "data": {
                    "earnings_analysis": {
                        "method": "build_earnings_analysis",
                        "headline": "<img src=x onerror=alert(1)>",
                        "latest": {
                            "revenue_yi": 0,
                            "net_profit_yi": 8.1,
                            "revenue_yoy_pct": 10.2,
                            "net_profit_yoy_pct": -1.5,
                        },
                        "consensus": {"rev": 0, "ni": 8},
                        "beat_miss": {
                            "revenue_vs_consensus_pct": 0,
                            "revenue_tag": "inline",
                            "net_profit_vs_consensus_pct": -2,
                            "net_profit_tag": "miss",
                        },
                        "thesis_impact": "主线 unchanged",
                    },
                    "thesis_tracker": {
                        "direction": "up",
                        "pillars_passed": 1,
                        "pillars_total": 2,
                        "thesis_intact_pct": 50,
                        "conviction": "Medium",
                        "recommended_action": "watch",
                        "pillars": [{
                            "pillar": "<thesis>",
                            "original_target": 0,
                            "current_status": "on track",
                            "trend": "flat",
                            "verdict": "<b>hold</b>",
                        }],
                    },
                    "morning_note": {
                        "date": "2026-09-09",
                        "top_call": "保持观察",
                        "recommendation": "hold",
                        "bullets": ["一点", "<script>bad</script>"],
                    },
                    "idea_screens": {
                        "value": {
                            "passed": 1,
                            "total": 2,
                            "pass_rate_pct": 50,
                            "fits_screen": False,
                            "verdict": "not yet",
                            "checks": [{"criterion": "PE", "pass": 0}],
                        }
                    },
                    "sector_overview": {
                        "industry": "Software",
                        "peer_count": 0,
                        "market_size": {"tam": 100, "growth": 0, "lifecycle": "mature"},
                        "value_chain": {"upstream": ["chips"], "company": "target", "downstream": "clients"},
                        "competitive_map": [{"name": "Peer", "ticker": "P", "market_share_pct": 0}],
                    },
                },
            },
            "22_deep_methods": {
                "source": "compute:deep_analysis_methods",
                "data": {
                    "unit_economics": {
                        "method": "build_unit_economics",
                        "business_type": "recurring",
                        "metrics": {"arpu_yi": 0, "gross_margin_pct": 70, "ltv_cac_ratio": float("nan")},
                        "healthy": True,
                        "verdict": "healthy",
                    },
                    "value_creation_plan": {
                        "current_ebitda_yi": 10,
                        "current_margin_pct": 20,
                        "total_uplift_yi": 0,
                        "target_ebitda_yi": 10,
                        "target_margin_pct": 20,
                        "levers": [{
                            "category": "pricing",
                            "lever": "mix",
                            "current_state": "now",
                            "target_state": "next",
                            "ebitda_impact_yi": 0,
                            "timeline": "12m",
                            "confidence": "low",
                        }],
                        "hundred_day_priorities": ["first"],
                    },
                    "dd_checklist": {
                        "total_items": 2,
                        "items_auto_verified": 1,
                        "completion_pct": 50,
                        "manual_review_required": 1,
                        "workstreams": [{
                            "workstream": "financial",
                            "items": [{"item": "cash", "status": "open"}],
                        }],
                    },
                    "portfolio_rebalance": {
                        "portfolio_total_yuan": 10000,
                        "needs_rebalance": False,
                        "drift_rows": [{
                            "asset_class": "equity",
                            "target_pct": 50,
                            "current_pct": 50,
                            "drift_pct": 0,
                            "dollar_drift_yuan": 0,
                            "action": "none",
                        }],
                        "rebalance_trades": [],
                    },
                },
            },
        },
    }


def test_render_omitted_products_and_preserve_zero() -> None:
    html = render_model_supplement(_raw_with_omitted_products())

    for product in (
        "three_statement", "earnings_analysis", "thesis_tracker", "morning_note",
        "idea_screens", "sector_overview", "unit_economics", "value_creation_plan",
        "dd_checklist", "portfolio_rebalance", "segmental",
    ):
        assert f'data-product="{product}"' in html
    for title in ("三表投影", "业绩分析", "投资主线跟踪", "晨会简报", "行业概览", "单位经济模型", "尽调清单"):
        assert title in html
    assert ">0<" in html  # zero is data, not a missing sentinel
    assert "未记录" in html  # NaN/Inf are rendered as missing
    assert "备用输入 · 模型已有" in html
    assert 'class="model-supplement"' in html
    assert html.count('class="supplement-product"') == 11
    assert html.count('class="supplement-table"') >= 10


def test_escape_all_provider_text_and_do_not_dump_json() -> None:
    html = render_model_supplement(_raw_with_omitted_products())

    assert "<script>" not in html
    assert "<img src=x" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert '"dimensions"' not in html
    assert "float" not in html


def test_missing_products_are_explicit_and_segment_state_is_not_fabricated() -> None:
    html = render_model_supplement({"dimensions": {}})

    assert html.startswith('<section class="model-supplement"')
    assert html.count("输入缺失 · 尚未生成") == 10
    assert "segmental_model.json（未发现）" in html
    assert "尚未建立 · 不显示预测结果" in html
    assert "分部收入或情景结果" in html
    assert "forecast" not in html.lower()

    connected = render_model_supplement(None, segment_present=True)
    assert "已接入 · 由独立分业务 renderer 展示" in connected
    assert "segmental_model.json / segmental_validation.json" in connected


def test_malformed_input_is_a_safe_pure_render() -> None:
    first = render_model_supplement(["not", "a", "mapping"])
    second = render_model_supplement(["not", "a", "mapping"])
    assert first == second
    assert "model-supplement" in first
    assert "nan" not in first.lower()
