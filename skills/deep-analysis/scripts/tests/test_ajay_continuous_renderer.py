"""Continuous reporting contracts: preserve functionality, not interchangeable scenes."""
import json
import re
from pathlib import Path
import pytest
from lib.report.continuous_renderer import (
    ReportIndex,
    clean,
    committee_record,
    panel_record,
    render_continuous,
)
from lib.report.council_renderer import ASSETS


def test_span_index_keeps_nested_svg_and_html_escaping():
    source='<main><section class="a"><div>A &amp; B<br><svg><path d="M0 1"/><text>x&lt;y</text></svg></div></section></main>'
    index=ReportIndex(source)
    assert index.first(cls='a')=='<section class="a"><div>A &amp; B<br><svg><path d="M0 1"/><text>x&lt;y</text></svg></div></section>'
    section=index.select(cls='a')[0]
    assert len(index.select(tag='svg',within=section))==1
    assert index.html(index.select(tag='text')[0],inner=True)=='x&lt;y'


def test_remove_legacy_ornaments_but_keep_math_and_zero():
    result=clean('<img src="avatars/a.svg">📈 ⭐ ★ score 0 · x > 15% &amp; y ≤ 4')
    assert result=='   score 0 · x > 15% &amp; y ≤ 4'


def test_committee_record_removes_game_vocabulary():
    source='''
      <div class="tag">THE GREAT DIVIDE</div>
      <h2>最看多 VS 最看空</h2>
      <div class="corner">▶ BULL</div><div class="corner">BEAR ◀</div>
      <div class="round-label">ROUND 1</div><div class="round-vs">VS</div>
      <div class="conf-label">SCORE</div>
    '''
    result=committee_record(source)
    for legacy_term in ['THE GREAT DIVIDE','最看多 VS 最看空','ROUND 1','SCORE']:
        assert legacy_term not in result
    for record_term in ['THE INVESTMENT COMMITTEE RECORD','支持、挑战与待核验','01 / 核心论点','规则分']:
        assert record_term in result


def test_panel_record_distinguishes_score_from_simulated_agreement():
    source='<div class="stat-tile total"><div class="num">55%</div><div class="label">Agreement · 模拟一致度</div></div>'
    result=panel_record(source)
    assert '55 / 100' in result
    assert 'Panel score · 原始聚合分' in result
    assert '模拟一致度' not in result


@pytest.fixture(scope='module')
def assembled(tmp_path_factory):
    import assemble_report as report
    from lib.report.demo_fixture import augment_demo
    raw=augment_demo({'ticker':'JTRADER.DEMO','is_demo':True,'market':'U','dimensions':{'0_basic':{'data':{'name':'Demo','price':100}}}})
    inputs={'raw_data':raw,'panel':{'investors':[]},'dimensions':{'fundamental_score_valid':False},'synthesis':{'ticker':'JTRADER.DEMO','name':'Demo','overall_score':56,'verdict_label':'UNSUPPORTED BUY','dashboard':{}}}
    with pytest.MonkeyPatch.context() as m:
        m.setattr(report,'read_task_output',lambda ticker,key:inputs.get(key))
        m.setattr(report,'market_status',lambda market:{'label':'TEST','is_open':False})
        m.setenv('AJAY_SKIP_REVIEW','1');m.chdir(tmp_path_factory.mktemp('continuous'))
        path=report.assemble('JTRADER.DEMO')
        path=path.resolve();html=path.read_text()
    return path,html


def test_default_production_is_continuous_and_offline(assembled):
    path,html=assembled
    assert 'class="continuous-report"' in html
    assert 'UNSUPPORTED BUY' not in html
    assert not re.search(r'<(?:img|script|link)[^>]+(?:src|href)="https?://',html)
    assert path.with_name('full-report-standalone.html').read_text()==html
    assert path.with_name('research-appendix.html').is_file()
    assert not re.search(r'\[\[[A-Z_]+\]\]',html)
    assert 'data-group="F"' not in html
    assert 'YOUZI 游资派' not in html


def test_all_original_reporting_blocks_live_in_main_document(assembled):
    html=assembled[1];index=ReportIndex(html)
    main=index.select(tag='main')[0]
    assert len(index.select(cls='dim-card',within=main))==19
    for cls in ['dcf-block','comps-block','lbo-block','initiating-block','ic-memo-block','catalyst-block','competitive-block','divide-section','panel-section','chat-container','risk-box','zones-grid','fund-mgr-section','evidence-strip']:
        assert index.select(cls=cls,within=main),cls
    assert len(index.select(cls='method-voice',within=main))==8
    assert len(index.select(cls='supplement-product',within=main))==11
    for id in ['model-valuation','model-dcf','model-comps','model-lbo','model-research','market-evidence']:
        assert len(index.select(id=id))==1,id
    for id in ['section-core','section-scan','section-modeling','section-clash','section-jury','section-chat','section-risks','section-zones','section-library','section-evidence']:
        assert len(index.select(id=id))==1,id
    for id in ['share-overlay','share-card','war-report','download-inputs','perspective-search','print-report']:
        assert index.select(id=id),id
    assert '<iframe' not in html


def test_photography_is_chapter_space_not_switchable_tab(assembled):
    index=ReportIndex(assembled[1]);nav=index.select(cls='chapter-nav')[0]
    assert not re.search('NEW YORK|LONDON|SHANGHAI|HONG KONG',index.html(nav))
    for cls in ['ny-arrival','shanghai-tower','london-frieze','hk-horizon']:
        assert len(index.select(cls=cls))==1
    css=(ASSETS/'report-continuous.css').read_text()
    assert 'aspect-ratio:835/1884' in css
    assert 'min-height:1559px' in css
    assert 'scroll-snap-type' not in css
    assert 'wheel' not in (ASSETS/'report-continuous.js').read_text()


def test_raw_payload_injection_is_data_not_executable():
    attack='</script><script>alert(1)</script>&<img src=x onerror=alert(1)>'
    raw={'ticker':attack,'dimensions':{'0_basic':{'data':{'name':attack,'price':0}}}}
    html=render_continuous(raw,{},'<main></main>')
    data=json.loads(re.search(r'<script id="council-data" type="application/json">(.*?)</script>',html,re.S)[1])
    assert data['raw']==raw
    assert attack not in html
    assert '\\u003c/script\\u003e' in html
    assert 'innerHTML' not in (ASSETS/'report-continuous.js').read_text()


def test_functional_interaction_and_print_contracts():
    js=(ASSETS/'report-continuous.js').read_text()
    for s in ['applyNoteFilter','perspective-count','beforeprint','afterprint','revokeObjectURL','showModal','evidenceFocus?.focus','prefers-reduced-motion','upgradeTables','prepareDataMotion','prepareChartMotion','preparePointerDepth']:
        assert s in js
    assert 'fetch(' not in js
    assert "['https:','http:']" in js


def test_midnight_model_and_fancy_data_surface_contracts():
    css=(ASSETS/'report-continuous.css').read_text()
    for token in ['V5 — midnight data continuum','.table-frame','.ajay-data-table','data-cell-level','.model-chapter svg text','prefers-reduced-motion:reduce']:
        assert token in css
    assert css.rfind('linear-gradient(180deg,#091522 0%') > css.find('background:#dfe5e9')


def test_nested_kpis_do_not_leak_python_dict_representation():
    from assemble_report import _extract_kpi_value
    text=_extract_kpi_value({'events':[{'date':'2026-09-09','event':'DEMO event','expectation':'0 surprises'}]},'events')
    assert text=='2026-09-09 · DEMO event · 0 surprises'
    assert _extract_kpi_value({'zero':0},'zero')=='0'


def test_entry_uses_quality_gated_conclusion_not_generic_cover_copy():
    legacy='<div class="hero-copy"><p class="one-liner">GENERIC SLOGAN</p><div class="price-row">0</div></div><div class="core-conclusion"><div class="text">Evidence &amp; limitations</div></div>'
    html=render_continuous({'ticker':'JTRADER.DEMO'}, {}, legacy)
    hero=ReportIndex(html).first(cls='hero-copy')
    assert 'GENERIC SLOGAN' not in hero
    assert 'Evidence &amp; limitations' in hero
    assert '反证 / 缺口' in hero
    assert '治理记录缺失' in hero


def test_missing_governance_cannot_render_as_clean_in_visible_chat():
    legacy='<main><div class="chat-container"><p>治理干净</p><div>符合标准： • [权4] 治理干净 • [权3] 其他规则</div></div></main>'
    html=render_continuous({'ticker':'JTRADER.DEMO'}, {}, legacy)
    chat=ReportIndex(html).first(cls='chat-container')
    assert '治理材料缺失 · 待核验' in chat
    assert '治理干净' not in chat
    assert '[权4]' not in chat
    assert '[权3] 其他规则' in chat


def test_mobile_photo_keeps_research_tasks_and_segment_state():
    html=render_continuous({}, {}, '<div class="segmental-section">real segment model</div>')
    assert '已接入 · 由独立分业务 renderer 展示' in html
    index=ReportIndex(html)
    notes=index.select(cls='tower-notes')[0]
    assert len(index.select(cls='evidence-link',within=notes))==3
    assert index.select(cls='market-actions')
    assert index.select(cls='model-directory')
