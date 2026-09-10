import math
import pytest
from lib.report.valuation_brief import render_valuation_brief
from lib.report.continuous_renderer import normalize_presentation


def test_price_map_uses_recorded_values_not_an_invented_target_range():
    raw={'market':'U','fetched_at':'2026-09-09','dimensions':{
        '0_basic':{'data':{'price':315.34}},
        '20_valuation_models':{'source':'compute:test','data':{
            'dcf':{'intrinsic_per_share':210.54,'wacc_breakdown':{'wacc':.0696},'assumptions':{'terminal_g':.025}},
            'comps':{'implied_price':{'via_median_pe':345.68}}}}}}
    stage, assumptions=render_valuation_brief(raw)
    for value in ('315.34','210.54','345.68','USD','2026-09-09','compute:test'):
        assert value in stage
    assert '6.96%' in assumptions
    assert '2.50%' in assumptions
    assert '不是价格上下限' in stage


@pytest.mark.parametrize('value',[None,math.nan,math.inf,-math.inf,'100',True])
def test_missing_or_non_finite_prices_are_not_drawn(value):
    stage, _=render_valuation_brief({'dimensions':{'0_basic':{'data':{'price':value}}}})
    assert '输入缺失 / 未绘制' in stage
    assert 'class="price-bar' not in stage
    assert not any(text in stage for text in ('>nan<','>inf<','width="nan','x="nan'))


def test_zero_and_negative_observations_keep_their_meaning():
    for price in (0,-12):
        stage,_=render_valuation_brief({'dimensions':{'0_basic':{'data':{'price':price}}}})
        assert f'>{price:,.2f}<' in stage
        assert 'class="price-bar price-market"' in stage


def test_mobile_chart_keeps_native_labels_and_the_same_recorded_values():
    stage, _ = render_valuation_brief({'market': 'U', 'dimensions': {
        '0_basic': {'data': {'price': 315.34}},
        '20_valuation_models': {'data': {
            'dcf': {'intrinsic_per_share': 210.54},
            'comps': {'implied_price': {'via_median_pe': 345.68}},
        }},
    }})
    assert 'class="price-desktop"' in stage
    assert 'class="price-mobile"' in stage
    assert stage.count('class="mobile-price-row"') == 3
    for number in ('315.34', '210.54', '345.68'):
        assert f'<strong>{number}</strong>' in stage


def test_presentation_adapter_preserves_content_and_positive_negative_colors():
    markup='<p style="color:#111;background:#fff;box-shadow:0 1px 4px #000">#111 raw label</p><td style="background:#065f46;color:#fff">42</td>'
    result=normalize_presentation(markup)
    assert '#111 raw label' in result
    assert 'var(--text-bright,#111)' in result
    assert 'var(--bg-card,#fff)' in result
    assert 'var(--heat-positive,#065f46)' in result
    assert 'box-shadow' not in result
