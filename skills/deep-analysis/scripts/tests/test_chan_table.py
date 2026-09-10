from lib.report.chan_table import render_chan_table, row_details, condition_text


def test_seven_column_structure_ledger_includes_supplied_evidence_and_invalidation():
    model={'level':'D','bars':[],'annotations':[{'key':'D-one','raw_id':'D:signal:0','kind':'signal','label':'三买候选','status':'candidate','item':{'at':'2026-09-09','level':120,'rule':'回踩不进入原中枢','invalid_if':{'below':115}}}]}
    out=render_chan_table(model)
    for value in ['结构名称','周期','日期','价位 / 区间','状态','成立依据','失效条件','2026-09-09','120.00','115.00','候选 · 未确认','回踩不进入原中枢']:
        assert value in out
    assert 'data-chan-point="D-one"' in out
    assert 'data-chan-point-row="D-one"' in out
    assert 'D:signal:0' in out


def test_row_uses_explicit_endpoints_and_bar_date_not_extreme_guess():
    model={'level':'W','bars':[{'index':1,'dt':'2026-08-28'},{'index':9,'dt':'2026-09-04'}]}
    ann={'kind':'bi','item':{'start_index':1,'end_index':9,'start_price':0,'end_price':42,'high':100,'low':5}}
    date,price,_,_=row_details(ann,model)
    assert date=='2026-08-28 → 2026-09-04'
    assert price=='0.00 → 42.00'
    ann['item'].pop('start_price')
    assert row_details(ann,model)[1]=='— → 42.00'


def test_missing_invalid_data_never_becomes_zero_or_invented_stop():
    assert condition_text({'below':float('nan')})=='未记录具体失效价位'
    assert condition_text({'above':0})=='价格突破 0.00'
    assert condition_text(None)=='未记录具体失效价位'


def test_point_table_escapes_provider_text_and_identifiers():
    model={'level':'D','annotations':[{'key':'\" onclick=\"x','label':'<script>bad</script>','kind':'signal','item':{'rule':'<img src=x onerror=x>'}}]}
    out=render_chan_table(model)
    assert '<script>' not in out and '<img' not in out
    assert '&lt;script&gt;' in out and '&quot;' in out
