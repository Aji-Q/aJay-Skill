"""Offline tests for evidence-bound, plain-text private council scripts."""
from __future__ import annotations

from copy import deepcopy
import json

import pytest

from lib.report.council import build_council


IDS = ["buffett", "graham", "munger", "lynch", "soros", "dalio", "livermore", "simons"]


def _raw(**dimensions):
    return {"fetched_at": "2099-12-31T23:59:59+00:00", "dimensions": {
        key: {"data": value, "source": "fixture:raw-observations"}
        for key, value in dimensions.items()
    }}


def _voice(result, topic, investor):
    return next(voice for item in result["topics"] if item["id"] == topic
                for voice in item["voices"] if voice["id"] == investor)


def _fact(result, key):
    return next(fact for record in result["evidence"].values()
                for fact in record["facts"] if fact["id"].endswith("." + key))


def _scripts(result):
    return "\n".join(v[field] for t in result["topics"] for v in t["voices"]
                     for field in ("claim", "rebuttal"))


def test_empty_shape_has_three_questions_and_eight_distinct_method_lenses_each():
    result = build_council({})
    assert [p["id"] for p in result["profiles"]] == IDS
    assert [t["id"] for t in result["topics"]] == ["quality", "price", "risk"]
    assert all(p["name_zh"] and p["name_en"] and p["era"] and p["method"] for p in result["profiles"])
    for topic in result["topics"]:
        assert topic["question"].endswith("？")
        assert [v["id"] for v in topic["voices"]] == IDS
        assert len({v["claim"] for v in topic["voices"]}) == 8
        assert len({v["rebuttal"] for v in topic["voices"]}) == 8
        for voice in topic["voices"]:
            assert voice["claim"] != voice["rebuttal"]
            assert voice["name"] and voice["role"] and voice["supporting_facts"]
            assert set(voice["evidence_ids"]) <= result["evidence"].keys()
            assert "非真实发言" in voice["disclosure"]
    assert "非本人发言、背书或独立投票" in result["disclosure"]
    assert "肖像仅作视觉方位提示" in result["disclosure"]
    assert all(r["status"] == "missing" for r in result["evidence"].values())
    assert all(f["value"] is None for r in result["evidence"].values() for f in r["facts"])
    assert json.loads(json.dumps(result, allow_nan=False)) == result


@pytest.mark.parametrize("raw", [None, [], {"dimensions": None}, {"dimensions": {"1_financials": []}}])
def test_malformed_top_level_and_dimension_are_explicitly_missing(raw):
    result = build_council(raw)
    assert _fact(result, "roe_latest")["value"] is None
    json.dumps(result, allow_nan=False)


def test_known_roe_example_does_not_repeat_false_five_year_claim():
    result = build_council(_raw(**{"1_financials": {
        "roe": "19.2%", "roe_history": [14.2, 16.1, 17.3, 18, 19.2],
        "financial_years": ["Y-4", "Y-3", "Y-2", "Y-1", "Y0"],
    }}))
    assert _fact(result, "roe_latest")["value"] == 19.2
    assert _fact(result, "roe_min")["value"] == 14.2
    claim = _voice(result, "quality", "buffett")["claim"]
    assert "5 期" in claim and "最低 14.2%" in claim
    assert "未获这些记录支持" in claim
    assert "连续 5 年" not in _scripts(result)
    assert _fact(result, "roe_history")["date"] == "未记录"


def test_roe_precision_is_preserved_in_facts_and_claims():
    result = build_council(_raw(**{"1_financials": {"roe_history": [14.2345, 19.2876]}}))
    assert "14.2345%" in _voice(result, "quality", "buffett")["claim"]
    assert "14.2345%" in _fact(result, "roe_min")["text"]
    assert "19.2876%" in _voice(result, "quality", "soros")["claim"]


def test_history_latest_missing_does_not_become_last_nonmissing_or_summary_roe():
    result = build_council(_raw(**{"1_financials": {"roe_history": [14.2, float("nan")], "roe": 80}}))
    assert _fact(result, "roe_latest")["value"] is None
    assert _fact(result, "roe_min")["value"] == 14.2
    assert "末期 ROE 未记录" in _voice(result, "quality", "soros")["claim"]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf"), "NaN", "inf", True, "not a number"])
def test_nonfinite_or_nonnumeric_values_never_become_zero_or_non_json_numbers(bad):
    result = build_council(_raw(**{
        "0_basic": {"price": bad, "pe_ttm": bad},
        "1_financials": {"roe_history": [bad], "net_margin": bad,
                         "revenue_growth": bad, "financial_health": {"debt_ratio": bad}},
        "2_kline": {"close_60d": [100, bad]},
        "10_valuation": {"pe_quantile": bad, "industry_pe": bad},
    }))
    for key in ["price", "pe", "roe_latest", "roe_min", "net_margin", "revenue_growth", "debt_ratio", "pe_quantile", "industry_pe", "window_change"]:
        assert _fact(result, key)["value"] is None
    json.dumps(result, allow_nan=False)


def test_actual_zero_and_negative_financial_values_survive_without_positive_spin():
    result = build_council(_raw(**{
        "0_basic": {"price": 0, "pe_ttm": 0},
        "1_financials": {"roe_history": [-4, 0], "net_margin": 0, "revenue_growth": 0,
                         "ocf_to_net_income_ratio": 0, "financial_health": {"debt_ratio": 0}},
        "10_valuation": {"pe": 20, "industry_pe": 25, "pe_quantile": 0},
    }))
    for key in ["price", "pe", "roe_latest", "net_margin", "revenue_growth", "debt_ratio", "ocf_profit_ratio", "pe_quantile"]:
        assert _fact(result, key)["value"] == 0
        assert _fact(result, key)["status"] == "available"
    assert _fact(result, "roe_min")["value"] == -4
    assert _fact(result, "pe_relative")["value"] is None
    assert "比较未评估" in _voice(result, "price", "graham")["claim"]


@pytest.mark.parametrize("pe,industry", [(None, 25), (20, None), (0, 25), (20, 0), (-2, 25), (20, -5)])
def test_pe_comparison_requires_both_explicit_positive_inputs(pe, industry):
    result = build_council(_raw(**{"0_basic": {"pe_ttm": pe}, "10_valuation": {"industry_pe": industry}}))
    assert _fact(result, "pe_relative")["value"] is None
    assert "未同时具备" in _voice(result, "price", "graham")["claim"]


def test_pe_comparison_uses_only_real_inputs_and_records_derivation_dependencies():
    result = build_council(_raw(**{"0_basic": {"pe_ttm": 28.4}, "10_valuation": {"industry_pe": 25}}))
    comparison = _fact(result, "pe_relative")
    assert comparison["value"] == pytest.approx(13.6)
    assert comparison["status"] == "derived"
    assert comparison["inputs"] == ["0_basic.pe", "10_valuation.industry_pe"]
    assert "高约 13.6%" in _voice(result, "price", "graham")["claim"]


@pytest.mark.parametrize("governance", [{}, {"pledge": [], "insider_trades_1y": []}, {"status": "clean", "risk": "安全", "score": 10}])
def test_missing_or_empty_governance_never_becomes_a_clean_bill(governance):
    result = build_council(_raw(**{"11_governance": governance}))
    assert result["evidence"]["11_governance"]["status"] == "missing"
    assert "治理状况未评估" in _voice(result, "quality", "munger")["claim"]
    assert "治理状况未评估" in _voice(result, "risk", "munger")["claim"]
    assert "治理干净" not in _scripts(result)
    assert "零风险" not in _voice(result, "risk", "munger")["claim"]
    assert _fact(result, "pledges")["value"] is None
    assert _fact(result, "insiders")["value"] is None


def test_one_governance_channel_does_not_fill_the_missing_channel_with_zero():
    result = build_council(_raw(**{"11_governance": {"pledge": [{"ratio": 0}], "insider_trades_1y": []}}))
    assert _fact(result, "pledges")["value"] == 1
    assert _fact(result, "insiders")["value"] is None
    claim = _voice(result, "risk", "munger")["claim"]
    assert "质押材料 1 条" in claim and "内部交易材料未记录" in claim
    assert "0 条" not in claim


@pytest.mark.parametrize("metadata,status", [
    ({"fallback": True}, "missing"), ({"error": "failed"}, "missing"),
    ({"_pipeline": {"fallback": True}}, "missing"),
    ({"quality": "missing"}, "missing"), ({"_pipeline": {"quality": "error"}}, "missing"),
    ({"stale": True}, "stale"), ({"_pipeline": {"stale": True}}, "stale"),
    ({"_pipeline": {"quality": "stale"}}, "stale"),
    ({"source": "skip"}, "not_applicable"), ({"applicable": False}, "not_applicable"),
])
def test_unusable_dimension_does_not_speak_from_optimistic_cached_numbers(metadata, status):
    raw = _raw(**{"1_financials": {"roe_history": [99, 100]}})
    raw["dimensions"]["1_financials"].update(metadata)
    result = build_council(raw)
    assert result["evidence"]["1_financials"]["status"] == status
    assert _fact(result, "roe_latest")["value"] is None
    assert _fact(result, "roe_latest")["status"] == status
    assert "99%" not in _scripts(result) and "100%" not in _scripts(result)


def test_sixty_prices_are_historical_observations_not_a_backtest_or_prediction():
    result = build_council(_raw(**{"2_kline": {"close_60d": list(range(100, 160))}}))
    assert _fact(result, "close_count")["value"] == 60
    assert _fact(result, "window_change")["value"] == pytest.approx(59)
    assert _fact(result, "window_change")["date"] == "未记录"
    assert "历史描述" in _voice(result, "price", "livermore")["claim"]
    assert "没有估计收益概率或开展预测回测" in _voice(result, "price", "simons")["claim"]
    assert "不生成入场价、止损价或目标价" in _voice(result, "price", "livermore")["rebuttal"]


def test_reported_financial_staleness_warning_is_not_discarded():
    result = build_council(_raw(**{"1_financials": {"roe_history": [14.2, 19.2],
        "financial_staleness_warning": "stale financials: prior period"}}))
    assert result["evidence"]["1_financials"]["status"] == "stale"
    assert _fact(result, "roe_latest")["value"] is None


def test_derivation_references_resolve_to_primary_facts():
    result = build_council(_raw(**{"0_basic": {"pe_ttm": 25}, "10_valuation": {"industry_pe": 20},
                                  "2_kline": {"close_60d": [100, 105]}, "1_financials": {"roe_history": [14, 19]}}))
    facts = [f for record in result["evidence"].values() for f in record["facts"]]
    fact_ids = {f["id"] for f in facts}
    assert all(set(f["inputs"]) <= fact_ids for f in facts)


def test_extreme_numeric_inputs_keep_output_json_finite():
    result = build_council(_raw(**{"0_basic": {"price": 10 ** 1000, "pe_ttm": 1e308},
                                  "10_valuation": {"industry_pe": 1e-308},
                                  "2_kline": {"close_60d": [1e-308, 1e308]}}))
    assert _fact(result, "price")["value"] is None
    assert _fact(result, "pe_relative")["value"] is None
    assert _fact(result, "window_change")["value"] is None
    json.dumps(result, allow_nan=False)


def test_real_aligned_candle_dates_remain_separate_from_collection_time():
    raw = _raw(**{"2_kline": {"close_60d": [100, 105], "candles_60d": [
        {"date": "2026-09-03", "close": 100}, {"date": "2026-09-04", "close": 105},
    ]}})
    result = build_council(raw)
    fact = _fact(result, "window_change")
    assert fact["date"] == "2026-09-03 — 2026-09-04"
    assert fact["collected_at"] == "2099-12-31T23:59:59+00:00"
    raw["dimensions"]["2_kline"]["data"]["candles_60d"][1]["close"] = 999
    assert _fact(build_council(raw), "window_change")["date"] == "未记录"


def test_roe_does_not_borrow_revenue_years_or_latest_report_date_for_its_history():
    raw = _raw(**{"1_financials": {"roe_history": [14.2, 19.2],
                                   "financial_years": ["2024", "2025"], "financial_period": "2026-06-30"}})
    result = build_council(raw)
    assert result["evidence"]["1_financials"]["date"] == "2026-06-30"
    for key in ["roe_history", "roe_min", "roe_latest"]:
        assert _fact(result, key)["date"] == "未记录"
    raw["dimensions"]["1_financials"]["data"]["roe_periods"] = ["2024", "2025"]
    result = build_council(raw)
    assert _fact(result, "roe_history")["date"] == "2024 — 2025"
    assert _fact(result, "roe_latest")["date"] == "2025"


def test_fact_specific_source_and_date_are_retained_without_claiming_official_provenance():
    result = build_council(_raw(**{"1_financials": {"revenue_growth_yoy": 0,
        "revenue_growth_source": "derived:revenue_history", "revenue_growth_period": "2025-12-31",
        "roe_history": [14.2], "_roe_source": "mx_api"}}))
    assert _fact(result, "revenue_growth")["source"] == "derived:revenue_history"
    assert _fact(result, "revenue_growth")["date"] == "2025-12-31"
    assert _fact(result, "roe_history")["source"] == "mx_api"
    assert "官方" not in _scripts(result)


def test_sources_remain_plain_json_data_for_the_root_renderer_to_escape():
    # HTML escaping belongs to safe_json_script / textContent at the UI boundary,
    # not this data builder; it must never manufacture an HTML field/template.
    attack = '</script><img src=x onerror="alert(1)">\u2028'
    raw = _raw(**{"1_financials": {"roe_history": [14.2]}, "3_macro": {"rate_cycle": attack}})
    raw["dimensions"]["1_financials"]["source"] = attack
    result = build_council(raw)
    assert _fact(result, "roe_history")["source"] == attack.strip()
    assert _fact(result, "rate_cycle")["value"] == attack
    assert attack not in _scripts(result)
    restored = json.loads(json.dumps(result, ensure_ascii=False, allow_nan=False))
    assert restored == result
    def check_keys(value):
        if isinstance(value, dict):
            assert not {"html", "innerHTML", "unsafe_html", "confidence", "win_rate", "score"} & value.keys()
            for child in value.values():
                check_keys(child)
        elif isinstance(value, list):
            for child in value:
                check_keys(child)
    check_keys(result)


def test_builder_is_deterministic_and_does_not_mutate_raw_or_use_legacy_persona_text():
    raw = _raw(**{"1_financials": {"roe_history": [14.2, 19.2]},
                  "0_basic": {"pe_ttm": 28.4}, "10_valuation": {"industry_pe": 25}})
    raw.update({"is_demo": True, "confidence": 0.99,
                "panel": [{"id": "buffett", "reason": "连续 5 年 ROE >15%，治理干净", "score": 100}]})
    before = deepcopy(raw)
    result = build_council(raw)
    assert result == build_council(raw)
    assert raw == before
    assert result["is_demo"] is True
    assert "治理干净" not in _scripts(result)
    assert "连续 5 年" not in _scripts(result)
    assert all({"value", "source", "date", "status"} <= f.keys()
               for t in result["topics"] for v in t["voices"] for f in v["supporting_facts"])
