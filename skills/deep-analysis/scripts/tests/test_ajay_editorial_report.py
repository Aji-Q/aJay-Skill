"""aJay report contracts: truthful evidence, original assets and offline rendering."""
from pathlib import Path
import re
import pytest
from lib.report.evidence import display_score, render_evidence, render_hero_chart
from assemble_report import render_dim_card
ASSETS = Path(__file__).resolve().parents[2] / 'assets'
TEMPLATE = (ASSETS / 'report-template.html').read_text()
CSS = (ASSETS / 'report-editorial.css').read_text()

@pytest.mark.parametrize('value', [None, float('nan'), float('inf'), True, 'unknown'])
def test_nonfinite_or_absent_score_is_not_zero(value):
    assert display_score(value) == '—'

def test_zero_is_a_valid_score():
    assert display_score(0) == '0'

@pytest.mark.parametrize('status', ['missing', 'not_applicable', 'stale', 'heuristic', None])
def test_no_default_measurement_for_unscored_dimensions(status):
    card = render_dim_card('18_trap', {'score': 9, 'score_status': status, 'label': 'SAFE'},
                           {'data': {'_note': 'placeholder'}, 'source': 'skip'})
    assert '>9<' not in card and 'SAFE' not in card

def test_source_is_not_laundered_as_official():
    card = render_dim_card('7_industry', {'score': 7, 'score_status': 'data_backed'},
                           {'data': {'growth': '8%'}, 'source': 'web_search'})
    assert 'web_search' in card and '官方接口' not in card

def test_missing_chart_has_no_fictional_line():
    html = render_hero_chart({'dimensions': {}})
    assert '<svg' not in html and '待补充' in html

def test_real_chart_is_escaped_and_finite():
    html = render_hero_chart({'dimensions': {'2_kline': {'data': {'close_60d': [1, 2, 3]}, 'source': '<script>alert(1)</script>'}}})
    assert 'HIGH 3' in html and '<script>' not in html
    bad = render_hero_chart({'dimensions': {'2_kline': {'data': {'close_60d': [1, float('nan'), 3]}}}})
    assert '<svg' not in bad

def test_old_confidence_not_presented_as_current_coverage(tmp_path):
    html = render_evidence({'dimensions': {}}, {'investors': [{'confidence': 99, 'signal': 'bullish'}]}, tmp_path)
    assert '未记录' in html and '99%' not in html
    assert '未完成当前输入审阅' in html and '默认特征' in html

def test_core_photography_and_ownership():
    for name in ['manhattan-night.png', 'shanghai-night.png', 'buffett-portrait.png', 'simons-portrait.png']:
        assert (ASSETS / 'ajay-brand' / name).is_file()
    assert 'aJay Research' in TEMPLATE
    assert 'AI-GENERATED PORTRAITS' in TEMPLATE
    assert 'FloatFu-true' not in TEMPLATE and 'wbh604' not in TEMPLATE

def test_report_never_calls_remote_qr_or_fonts():
    assert 'qrserver' not in TEMPLATE
    assert 'fonts.googleapis.com' not in TEMPLATE
    assert 'fetch(' not in TEMPLATE
    assert not re.search(r'<(?:img|script)[^>]+src="https?://', TEMPLATE)

def test_accessible_dialog_and_category_accordions():
    assert '<dialog id="share-overlay"' in TEMPLATE
    assert 'showModal()' in TEMPLATE and 'method="dialog"' in TEMPLATE
    assert TEMPLATE.count('<details class="research-category"') == 6
    assert 'aria-pressed' in TEMPLATE and 's.tabIndex=0' in TEMPLATE
    assert 'prefers-reduced-motion' in CSS

def test_export_surfaces_keep_original_dimensions():
    assert 'id="share-card"' in TEMPLATE and 'id="war-report"' in TEMPLATE
    assert '1080px' in TEMPLATE and '1920px' in TEMPLATE

def test_full_assembly_downgrades_invalid_verdict(monkeypatch, tmp_path):
    import assemble_report as report
    inputs = {'raw_data': {'ticker': 'EMPTY', 'market': 'U', 'dimensions': {}},
              'panel': {'investors': []}, 'dimensions': {'fundamental_score_valid': False},
              'synthesis': {'ticker': 'EMPTY', 'name': 'Empty fixture', 'overall_score': 56, 'verdict_label': '值得重仓',
                            'verdict_detail': 'BUY NOW', 'dashboard': {'core_conclusion': 'FAKE_CORE_56', 'battle_plan': {'entry': 'FAKE_ENTRY_92'}},
                            'buy_zones': {'value': {'price': 85, 'rationale': '历史 PE 25 分位'}}}}
    monkeypatch.setattr(report, 'read_task_output', lambda ticker, key: inputs.get(key))
    monkeypatch.setattr(report, 'market_status', lambda market: {'label': 'TEST', 'is_open': False})
    monkeypatch.setenv('AJAY_SKIP_REVIEW', '1')
    monkeypatch.chdir(tmp_path)
    html = report.assemble('EMPTY', layout='editorial').read_text()
    for unsupported in ['值得重仓', 'BUY NOW', '历史 PE 25 分位', 'FAKE_CORE_56', 'FAKE_ENTRY_92']:
        assert unsupported not in html
    assert '证据不足 · 未形成综合判断' in html
    assert '情景测算尚无明确假设' in html
    assert not re.search(r'\{\{[A-Z_]+\}\}', html)
    assert '<!-- INJECT_' not in html
    assert html.count('data:image/png;base64,') == 4


def test_unknown_persona_score_is_not_zero():
    from lib.report.panel_cards import render_jury_seat, render_chat_message, render_top3_bulls
    assert 'seat-score">—<' in render_jury_seat({})
    assert 'msg-score-badge">—分' in render_chat_message({})
    assert 'score-num' not in render_top3_bulls([{'signal': 'bullish', 'score': None}])
    assert '规则覆盖 未记录' in render_chat_message({'rule_coverage_pct': float('nan')})


def test_no_active_school_is_unscored():
    from lib.report.special_cards import render_school_scores
    html = render_school_scores({'school_scores': {'F': {'label': '游资', 'n_active': 0, 'consensus': 0, 'verdict': '回避'}}}, {})
    assert '无适用角色' in html and '回避' not in html
    assert '投票共识 0%' not in html


def test_inapplicable_persona_score_is_not_measured_zero():
    from lib.report.panel_cards import render_jury_seat, render_chat_message
    inv = {'signal': 'skip', 'score': 0}
    assert 'seat-score">—<' in render_jury_seat(inv)
    assert 'msg-score-badge">—分' in render_chat_message(inv)

def test_summary_uses_actual_role_count():
    from lib.report.special_cards import render_panel_insights
    html = render_panel_insights({}, {'investors': [{}, {}]})
    assert '2 个模拟角色' in html and '51 位' not in html
    assert '模拟一致度 <strong>—%</strong>' in html
    assert '模拟一致度 <strong>0%</strong>' not in html
