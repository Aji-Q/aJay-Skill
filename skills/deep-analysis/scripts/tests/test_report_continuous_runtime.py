from pathlib import Path


JS = (Path(__file__).parents[2] / "assets" / "report-continuous.js").read_text()


def test_runtime_has_dynamic_motion_preference_and_manual_stop_contract():
    assert "prefers-reduced-motion: reduce" in JS
    assert "motion-toggle" in JS
    assert "data-motion" in JS
    assert "addEventListener('change'" in JS
    assert "cancelAnimationFrame" in JS
    assert "function stopMotion()" in JS
    assert "motionIsOff() ? 'auto' : 'smooth'" in JS


def test_runtime_removes_generic_chart_drawing_and_pointer_spotlight():
    for token in (
        "getTotalLength",
        "strokeDasharray",
        "strokeDashoffset",
        "pointermove",
        "--spot-x",
        "--spot-y",
        "interactive-surface",
    ):
        assert token not in JS


def test_model_view_switcher_is_scoped_and_keyboard_accessible():
    assert ".valuation-stage[data-viz-switcher]" in JS
    assert "[data-model-view]" in JS
    assert "[data-model-panel]" in JS
    assert "const allowedViews = ['chart', 'table', 'source']" in JS
    assert "setAttribute('role', 'tab')" in JS
    assert "setAttribute('role', 'tabpanel')" in JS
    assert "aria-controls" in JS
    assert "aria-selected" in JS
    assert "ArrowRight" in JS and "ArrowLeft" in JS
    assert "ArrowDown" in JS and "ArrowUp" in JS
    assert "event.key === 'Home'" in JS and "event.key === 'End'" in JS
    assert "candidate.hidden = !selected" in JS


def test_report_body_is_not_gated_by_runtime_motion_classes():
    assert "motion-ready" not in JS
    assert "opacity:0" not in JS
    assert ".model-directory a[href^=\"#\"]" in JS
    assert "setAttribute('aria-current', 'location')" in JS


def test_evidence_index_keeps_raw_dimensions_and_record_metadata_visible():
    assert "Object.keys(data?.raw?.dimensions || {})" in JS
    assert "Object.keys(evidence).forEach" in JS
    assert "function dimensionPeriod" in JS
    assert "data?.raw?.fetched_at" in JS
    assert "状态：${statusLabel(status)}" in JS
    assert "来源：${sourceText}" in JS
    assert "时期：${period} · 采集：${collected}" in JS
    assert "核对原始记录 ↗" in JS
