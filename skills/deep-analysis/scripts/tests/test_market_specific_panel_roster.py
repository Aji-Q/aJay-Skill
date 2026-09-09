"""Panel discussions contain only personas that can evaluate the target market."""
from __future__ import annotations


def test_us_roster_removes_all_a_share_youzi_skip_messages():
    from lib.pipeline.score_fns import _panel_roster

    included, excluded, market = _panel_roster({"ticker": "AAPL", "market": "U"}, {"market": "US"})

    assert market == "US"
    assert len(included) + len(excluded) == 66
    assert len(excluded) == 24
    assert not any(item["group"] == "F" for item in included)
    assert {item["group"] for item in excluded} == {"F"}


def test_a_share_roster_keeps_youzi_but_removes_us_only_mandates():
    from lib.pipeline.score_fns import _panel_roster

    included, excluded, market = _panel_roster({"ticker": "600000.SH", "market": "A"}, {"market": "A"})

    assert market == "A"
    assert any(item["group"] == "F" for item in included)
    assert any(item["id"] == "thorp" for item in excluded)
