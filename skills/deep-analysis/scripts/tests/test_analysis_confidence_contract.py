"""Offline aJay audit: coverage is not a calibrated prediction probability."""
from __future__ import annotations

import pytest


def _stub_evaluator(monkeypatch):
    import lib.investor_evaluator as evaluator
    from lib.investor_criteria import Rule

    monkeypatch.setattr(evaluator, "get_locked_school", lambda: None)
    monkeypatch.setattr(evaluator, "reality_check", lambda *_args: {
        "should_evaluate": True, "skip_reason": None,
        "affinity_adjust": 0, "holding_match": None, "override_signal": None,
    })
    monkeypatch.setattr(evaluator, "_is_youzi_out_of_range", lambda *_args: (False, ""))
    monkeypatch.setitem(evaluator.INVESTOR_RULES, "audit_fixture", [
        Rule("a", "A", 3, lambda f: f["a"] > 0),
        Rule("b", "B", 1, lambda f: f["b"] > 0),
    ])
    return evaluator


def test_all_skipped_rules_have_zero_coverage(monkeypatch):
    evaluator = _stub_evaluator(monkeypatch)
    result = evaluator.evaluate("audit_fixture", {"a": None, "b": None})
    assert result["weight_total"] == 0
    assert result["confidence"] == 0
    assert result["rule_coverage_pct"] == 0
    assert result["confidence_kind"] == "rule_coverage"


def test_coverage_uses_observed_rule_weights_not_score_extremeness(monkeypatch):
    evaluator = _stub_evaluator(monkeypatch)
    partial = evaluator.evaluate("audit_fixture", {"a": 1, "b": None})
    complete = evaluator.evaluate("audit_fixture", {"a": 1, "b": -1})
    assert partial["score"] == 100
    assert partial["confidence"] == 75
    assert partial["rule_weight_evaluated"] == 3
    assert partial["rule_weight_possible"] == 4
    assert complete["confidence"] == 100


def test_known_holding_does_not_manufacture_rule_coverage(monkeypatch):
    evaluator = _stub_evaluator(monkeypatch)
    monkeypatch.setattr(evaluator, "reality_check", lambda *_args: {
        "should_evaluate": True, "skip_reason": None,
        "affinity_adjust": 0, "holding_match": ("held", "static fixture"),
        "override_signal": "bullish",
    })
    result = evaluator.evaluate("audit_fixture", {"a": None, "b": None})
    assert result["weight_total"] == 6
    assert result["rule_coverage_pct"] == 0


def test_neutral_default_score_does_not_hide_hollow_panel(monkeypatch):
    import lib.pipeline.score_fns as scorer

    monkeypatch.setattr(scorer, "INVESTORS", [{"id": "audit_fixture", "name": "Fixture", "group": "A"}])
    monkeypatch.setattr(scorer, "extract_features", lambda *_args: {})
    monkeypatch.setattr(scorer, "_persona_comment", lambda *_args: "fixture")
    monkeypatch.setattr(scorer, "_evaluate_investor", lambda *_args: {
        "signal": "neutral", "score": 50, "confidence": 0,
        "rule_coverage_pct": 0, "confidence_kind": "rule_coverage",
        "rule_weight_evaluated": 0, "rule_weight_possible": 4,
        "headline": "数据不足", "rationale": "", "pass_rules": [], "fail_rules": [],
        "weight_pass": 0, "weight_total": 0,
    })
    panel = scorer.generate_panel({}, {"ticker": "TEST", "dimensions": {}})
    assert panel["consensus_valid"] is False
    assert panel["hollow_pct"] == 100
    assert panel["rule_coverage_pct"] == 0
    assert panel["independent_evidence"] is False


def test_no_active_long_personas_is_not_valid_consensus(monkeypatch):
    import lib.pipeline.score_fns as scorer
    monkeypatch.setattr(scorer, "INVESTORS", [])
    panel = scorer.generate_panel({}, {"ticker": "TEST", "dimensions": {}})
    assert panel["consensus_valid"] is False


@pytest.mark.parametrize("value", [float("nan"), float("inf"), [None, "—"], {"nested": [None]}])
def test_integrity_rejects_nonfinite_or_recursively_empty_fields(value):
    from lib.data_integrity import _is_missing
    assert _is_missing(value)


@pytest.mark.parametrize("value", [0, "0", 0.0, "0.0", False, {"growth": 0}])
def test_integrity_preserves_observed_zero(value):
    from lib.data_integrity import _is_missing
    assert not _is_missing(value)


def test_zero_roe_year_is_preserved_in_average_and_minimum():
    from lib.stock_features import _avg, _min
    assert _avg([0, 10, 20]) == 10
    assert _min([0, 10, 20]) == 0
    assert _avg([None, "—", float("nan"), 0, 10]) == 5


def test_style_reweighting_preserves_short_book_exclusion():
    from lib.stock_style import apply_style_weights
    long_book = [{"investor_id": "fixture_long", "group": "A", "signal": "bullish"}]
    short_book = [{"investor_id": "fixture_short", "group": "C", "signal": "bearish", "mandate": "short"}]
    assert apply_style_weights(long_book, {}, "balanced")["panel_consensus"] == 100
    assert apply_style_weights(long_book + short_book, {}, "balanced")["panel_consensus"] == 100


def test_modeling_refresh_preserves_deep_review_requirement(tmp_path, monkeypatch):
    import json
    from lib.agent_review import write_review_context, requires_agent_review
    monkeypatch.delenv("AJAY_DEPTH", raising=False)
    (tmp_path / "_agent_review_context.json").write_text(json.dumps({"depth": "deep"}))
    context = write_review_context(tmp_path, {"ticker": "TEST"})
    assert context["depth"] == "deep"
    assert requires_agent_review(tmp_path)
    monkeypatch.setenv("AJAY_DEPTH", "medium")
    assert write_review_context(tmp_path, {"ticker": "TEST"})["depth"] == "medium"


def test_us_backfill_persistence_revalidates_unrelated_gaps(tmp_path):
    """Execute only the persistence tail; importing the CLI would run live fetches."""
    import ast
    import json
    from pathlib import Path

    source = Path(__file__).resolve().parents[1] / "us_backfill.py"
    module = ast.parse(source.read_text())
    start = next(i for i, node in enumerate(module.body)
                 if isinstance(node, ast.ImportFrom) and node.module == "lib.data_integrity")
    # The final print is not part of the persistence contract.
    persistence = ast.Module(body=module.body[start:-1], type_ignores=[])
    raw = {"ticker": "TEST", "dimensions": {"1_financials": {"data": {"roe_history": [10]}}}}
    raw_path = tmp_path / "raw_data.json"
    (tmp_path / "_data_gaps.json").write_text(json.dumps({"critical_missing": False, "tasks": []}))
    exec(compile(persistence, str(source), "exec"), {
        "raw": raw, "TICKER": "TEST", "CACHE": tmp_path,
        "raw_path": raw_path, "json": json,
    })
    gaps = json.loads((tmp_path / "_data_gaps.json").read_text())
    assert gaps["critical_missing"] is True
    assert any(task["dim"] == "0_basic" and task["field"] == "price" for task in gaps["tasks"])
    assert json.loads(raw_path.read_text())["_integrity"]["critical_missing"] is True


def test_empty_snapshot_numeric_compatibility_is_explicitly_invalid():
    from lib.pipeline.score_fns import score_dimensions
    scored = score_dimensions({"ticker": "TEST", "dimensions": {}})
    assert isinstance(scored["fundamental_score"], float)
    assert scored["fundamental_score_valid"] is False
    assert scored["fundamental_score_status"] == "insufficient_evidence"
    assert all(item["score_status"] == "missing" for item in scored["dimensions"].values())


def test_score_status_separates_na_stale_and_heuristic():
    from lib.pipeline.score_fns import score_dimensions
    raw = {"ticker": "TEST", "dimensions": {
        "16_lhb": {"source": "skip", "data": {"_note": "lhb only A-share"}},
        "2_kline": {"stale": True, "data": {"stage": "Stage 2"}},
        "7_industry": {"data": {"growth": 10}},
        "10_valuation": {"data": {"pe": 20}},
    }}
    dims = score_dimensions(raw)["dimensions"]
    assert dims["16_lhb"]["score_status"] == "not_applicable"
    assert dims["2_kline"]["score_status"] == "stale"
    assert dims["7_industry"]["score_status"] == "heuristic"
    assert dims["10_valuation"]["score_status"] == "missing"  # PE alone is not a historical quantile
