"""Council UI boundary, real-photo provenance and production entrypoint contracts."""
import hashlib
import json
import re
from pathlib import Path
import pytest
from lib.report.council_renderer import ASSETS, json_safe, render_council


def payload(html):
    return json.loads(re.search(r'<script id="council-data" type="application/json">(.*?)</script>',html,re.S)[1])

@pytest.fixture(scope='module')
def empty_html():
    return render_council({'ticker':'EMPTY','dimensions':{},'is_demo':True})


def test_default_empty_report_is_truthful(empty_html):
    data=payload(empty_html)
    assert data['council']['is_demo'] is True
    assert len(data['council']['profiles'])==8
    assert len(data['council']['topics'])==3
    assert all(len(t['voices'])==8 for t in data['council']['topics'])
    assert '<noscript>' in empty_html
    assert '未评估' in data['council']['topics'][0]['voices'][0]['claim']


def test_council_assets_are_self_contained(empty_html):
    data=payload(empty_html)
    assert len(data['cities'])==4
    assert len(data['portraits'])==8
    assert all(p.startswith('data:image/png;base64,') for p in data['portraits'].values())
    assert not re.search(r'<(?:img|script|link)[^>]+(?:src|href)="https?://',empty_html)
    assert 'INJECT_COUNCIL' not in empty_html
    assert 'INJECT_GSAP' not in empty_html
    assert 'fetch(' not in (ASSETS/'report-council.js').read_text()


def test_raw_text_stays_data_not_markup():
    attack='</script><script>alert("x")</script>&<img src=x onerror=alert(1)>'
    raw={'ticker':attack,'dimensions':{'0_basic':{'data':{'name':attack,'price':0}},'22_custom':{'data':{'nested':attack}}}}
    html=render_council(raw)
    assert payload(html)['raw']==raw
    assert attack not in html
    assert '\\u003c/script\\u003e' in html


def test_nonfinite_boundary_and_valid_zero():
    assert json_safe({'zero':0,'missing':None,'bad':[float('nan'),float('inf'),-float('inf')]})=={'zero':0,'missing':None,'bad':[None,None,None]}
    data=payload(render_council({'ticker':'ZERO','dimensions':{'0_basic':{'data':{'price':0,'pe':float('nan')}}}}))
    assert data['raw']['dimensions']['0_basic']['data']=={'price':0,'pe':None}


def test_all_input_dimensions_and_analysis_are_retained():
    raw={'ticker':'ALL','dimensions':{f'{i}_test':{'source':'fixture','data':{'value':i}} for i in range(23)}}
    analysis={'dimensions':{'dimensions':{'1_test':{'score':0,'score_status':'data_backed'}}},'review_skipped':True}
    data=payload(render_council(raw,analysis))
    assert data['raw']==raw and data['analysis']==analysis


def test_real_financial_photos_have_distinct_sources():
    entries=json.loads((ASSETS/'ajay-council/photography.json').read_text())
    assert len({e['original_url'] for e in entries})==4
    assert len({e['composition'] for e in entries})==4
    for item in entries:
        assert '2024-09-09'<=item['date']<='2026-09-09'
        assert item['date_kind'] in ('captured','published')
        assert item['source_url'].startswith('https://')
        assert item['license_url'].startswith('https://')
        assert item['author'] and 'image' in item['credit']
        assert hashlib.sha256((ASSETS/'ajay-council'/item['asset']).read_bytes()).hexdigest()==item['edited_sha256']
        assert item['model_version']=='not returned by tool'
        assert '-room.png' not in item['asset']
    shanghai=next(e for e in entries if e['id']=='shanghai')
    assert shanghai['license']=='CC BY 4.0' and shanghai['date_kind']=='captured'


def test_animation_and_accessibility_contracts():
    js=(ASSETS/'report-council.js').read_text();css=(ASSETS/'report-council.css').read_text()
    assert 'speechTimeline.kill()' in js
    assert 'scene-back' in js and "removeAttribute('src')" in js
    assert 'prefers-reduced-motion' in css and 'prefers-reduced-motion' in js
    assert 'lastFocus.focus({preventScroll:true})' in js
    assert 'textContent = ' in js
    assert js.count('.innerHTML=')==1  # Only local trusted Lucide SVG markup.
    assert 'scene-license' in js and 'license_url' in js
    assert 'writing-mode:horizontal-tb' in css


def test_production_assemble_uses_council_and_keeps_audit_appendix(monkeypatch,tmp_path):
    import assemble_report as report
    inputs={'raw_data':{'ticker':'EMPTY','market':'U','dimensions':{},'is_demo':True},'panel':{'investors':[]},'dimensions':{'fundamental_score_valid':False},'synthesis':{'ticker':'EMPTY','name':'Empty','overall_score':56,'verdict_label':'UNSUPPORTED BUY','dashboard':{}}}
    monkeypatch.setattr(report,'read_task_output',lambda ticker,key:inputs.get(key))
    monkeypatch.setattr(report,'market_status',lambda market:{'label':'TEST','is_open':False})
    monkeypatch.setenv('AJAY_SKIP_REVIEW','1');monkeypatch.chdir(tmp_path)
    path=report.assemble('EMPTY');html=path.read_text();data=payload(html)
    assert 'UNSUPPORTED BUY' not in html
    assert data['analysis']['review_skipped'] is True
    assert data['analysis']['critical_missing'] is True
    assert path.with_name('research-appendix.html').is_file()
    assert path.with_name('full-report-standalone.html').read_text()==html
