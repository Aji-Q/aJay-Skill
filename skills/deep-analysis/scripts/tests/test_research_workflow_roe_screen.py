"""Regression tests for the quality screen's five-period ROE wording."""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _screen_roe(history):
    from lib.research_workflow import run_idea_screen
    from lib.stock_features import extract_features

    raw = {
        "ticker": "SYNTH.SCREEN",
        "dimensions": {
            "0_basic": {"data": {
                "code": "SYNTH.SCREEN",
                "name": "ROE screen fixture",
                "market": "A",
                "industry": "演示软件",
            }},
            "1_financials": {"data": {"roe_history": history}},
        },
    }
    features = extract_features(raw, raw["dimensions"])
    quality = run_idea_screen(features, "quality")
    return next(
        item for item in quality["checks"]
        if item["criterion"] == "ROE 连续 5 年 > 15%"
    )


def test_quality_screen_rejects_four_of_five():
    check = _screen_roe([14.2, 16.1, 17.3, 18.0, 19.2])
    assert check["pass"] is False


def test_quality_screen_accepts_five_finite_strictly_above_fifteen():
    check = _screen_roe([15.01, 16.1, 17.3, 18.0, 19.2])
    assert check["pass"] is True


def test_quality_screen_rejects_missing_period_instead_of_auto_passing():
    check = _screen_roe([16.0, None, 17.3, 18.0, 19.2])
    assert check["pass"] is False
