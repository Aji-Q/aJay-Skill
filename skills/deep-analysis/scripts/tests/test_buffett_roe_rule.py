"""Boundary tests for Buffett's strict five-period ROE criterion."""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _features(roe_history):
    from lib.stock_features import extract_features

    raw = {
        "ticker": "SYNTH.ROE",
        "name": "ROE boundary fixture",
        "market": "A",
        "dimensions": {
            "0_basic": {"data": {
                "code": "SYNTH.ROE",
                "name": "ROE boundary fixture",
                "market": "A",
                "industry": "演示软件",
            }},
            "1_financials": {"data": {"roe_history": roe_history}},
        },
    }
    return extract_features(raw, raw["dimensions"])


def _buffett_roe_result(roe_history):
    from lib.investor_evaluator import evaluate

    return evaluate("buffett", _features(roe_history))


def _roe_rule(result):
    for item in result["pass_rules"] + result["fail_rules"]:
        if item["rule_id"] == "roe_5y_15":
            return item
    raise AssertionError("Buffett ROE rule was skipped unexpectedly")


def test_buffett_fixture_with_one_14_2_fails_strict_five_year_rule():
    result = _buffett_roe_result([14.2, 16.1, 17.3, 18.0, 19.2])
    rule = _roe_rule(result)

    assert rule in result["fail_rules"]
    assert "4/5" in rule["msg"]
    assert "连续 5 年 > 15%" not in rule["msg"]


def test_buffett_roe_boundaries_are_strict_with_five_observations():
    cases = [
        ([15.0, 16.0, 17.0, 18.0, 19.0], False),  # equality is not > 15
        ([16.0, 17.0, 18.0, 19.0, 20.0], True),    # all five strictly pass
        ([0.0, 0.0, 0.0, 0.0, 0.0], False),       # zero is a real failing observation
    ]

    for history, expected_pass in cases:
        result = _buffett_roe_result(history)
        rule = _roe_rule(result)
        assert (rule in result["pass_rules"]) is expected_pass, history


def test_buffett_incomplete_roe_history_is_unknown_not_a_failure():
    for history in ([], [16.0, 17.0, 18.0, 19.0]):
        result = _buffett_roe_result(history)
        matching = [
            item for item in result["pass_rules"] + result["fail_rules"]
            if item["rule_id"] == "roe_5y_15"
        ]
        assert matching == []
        assert "0/5" not in result["rationale"]
