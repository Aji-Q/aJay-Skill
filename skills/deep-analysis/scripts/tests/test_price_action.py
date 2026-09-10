"""Causal, numeric and same-coordinate contract checks."""
from copy import deepcopy
from datetime import date, timedelta
import json
import math
import pytest
from price_action import build_price_action_level, enrich_chan_price_action


def rows(n=80):
    return [dict(dt=(date(2025, 1, 1)+timedelta(days=i)).isoformat(), open=100+i, close=100+i, high=102+i, low=98+i, volume=100) for i in range(n)]


def event_rows():
    out = rows(45)
    for b in out:
        b.update(open=20, close=20, high=21, low=19)
    out[17].update(high=30)
    out[22].update(open=20, close=32, high=33, low=19, volume=1000)
    out[23].update(open=32, close=32, high=33, low=29)
    for b in out[24:]:
        b.update(open=33, close=33, high=34, low=32)
    return out


def test_indicators_warmups_wilder_atr_and_previous_volume_baseline():
    bars = rows()
    bars[20]['volume'] = 1000
    r = build_price_action_level(bars)
    i = r['indicators']
    assert i['ma20'][:19] == [None]*19
    assert i['ma20'][19] == pytest.approx(109.5)
    assert i['ma60'][:59] == [None]*59
    assert i['atr14'][:14] == [None]*14
    assert i['atr14'][14] == pytest.approx(4)
    assert i['relative_volume'][20] == 10
    assert i['volume_sma20'][20] == 100
    assert len(i['atr14']) == len(bars)
    json.dumps(r, allow_nan=False)


def test_level_confirmation_then_breakout_then_retest():
    result = build_price_action_level(event_rows(), swing_span=2)
    level = next(x for x in result['levels'] if x['anchor_index'] == 17)
    assert level['start_index'] == level['confirmed_index'] == 19
    events = [x for x in result['events'] if x['level_id'] == level['id']]
    assert [x['kind'] for x in events] == ['breakout_up', 'retest_hold']
    assert [x['index'] for x in events] == [22, 23]
    assert all(e['index'] > level['confirmed_index'] for e in events)
    assert '32.00' in events[0]['evidence']
    assert events[0]['dt'] in events[0]['evidence']
    assert events[0]['invalid_if']['below'] == level['zone_low']


def test_no_backfilled_events_and_latest_bar_not_confirmation():
    bars = event_rows()
    early_break = build_price_action_level(bars[:23], swing_span=2)
    assert not any(e['index'] == 22 for e in early_break['events'])
    after_break = build_price_action_level(bars[:24], swing_span=2)
    assert any(e['index'] == 22 for e in after_break['events'])
    later = build_price_action_level(bars, swing_span=2)
    for event in after_break['events']:
        assert event in later['events']
    early = build_price_action_level(bars[:20], swing_span=2)
    assert not any(l['anchor_index'] == 17 for l in early['levels'])
    explicit_close = build_price_action_level(bars[:20], swing_span=2, last_bar_complete=True)
    assert any(l['anchor_index'] == 17 for l in explicit_close['levels'])


def test_failure_and_downward_side_have_actual_condition_prices():
    bars = event_rows()
    bars[23].update(open=25, high=26, low=17, close=18)
    r = build_price_action_level(bars, swing_span=2)
    assert any(e['kind'] == 'retest_failed' and e['index'] == 23 for e in r['events'])
    mirrored = [{**b, 'open':100-b['open'], 'close':100-b['close'], 'high':100-b['low'], 'low':100-b['high']} for b in event_rows()]
    r = build_price_action_level(mirrored, swing_span=2)
    event = next(e for e in r['events'] if e['kind'] == 'breakout_down')
    assert 'above' in event['invalid_if']
    assert any(e['kind'] == 'retest_hold' for e in r['events'])


def test_empty_bad_and_plateau_input_do_not_invent_structures():
    assert build_price_action_level([])['status'] == 'unavailable'
    bars = rows(20)
    for b in bars:
        b.update(open=100, close=100, high=102, low=98, volume=0)
    bars.append(dict(bars[-1], dt='2026-01-01', high=float('nan')))
    r = build_price_action_level(bars)
    assert r['quality']['invalid_rows'] == 1
    assert r['levels'] == [] and r['events'] == []
    assert r['indicators']['relative_volume'] == [None]*20
    json.dumps(r, allow_nan=False)


def test_enrichment_shares_ids_indices_and_preserves_chan():
    bars = event_rows()
    chan = {'ticker':'TEST', 'source':'fixed input', 'adjusted':True, 'levels':{'D':{'bars':bars, 'bis':[{'id':'original-bi'}]}, 'W':{'bars':[]}}}
    before = deepcopy(chan['levels']['D']['bis'])
    pa = enrich_chan_price_action(chan)
    assert pa['schema_version'] == 'price_action.v1'
    assert chan['levels']['D']['price_action'] is pa['levels']['D']
    assert chan['levels']['D']['bis'] == before
    assert len(pa['levels']['D']['volume']) == len(bars)
    assert pa['levels']['W']['status'] == 'unavailable'
    assert pa['levels']['D']['summary']['confirmed_through'] == bars[-2]['dt']
    assert all(e['method'] == 'heuristic' for e in pa['levels']['D']['events'])
    assert 'probability' not in json.dumps(pa)


def test_visible_events_always_resolve_to_parent_and_finite():
    bars = rows(300)
    for i, b in enumerate(bars):
        c = 100+math.sin(i/4)*10+i*.1
        b.update(open=c-.2, close=c, high=c+2, low=c-2)
    r = build_price_action_level(bars, max_levels=7)
    assert len(r['levels']) <= 7
    ids = {l['id'] for l in r['levels']}
    assert all(e['level_id'] in ids for e in r['events'])
    assert all(e['anchor_index'] == e['index'] for e in r['events'])
    json.dumps(r, allow_nan=False)


def test_later_failure_overrides_early_held_retest_and_ends_level():
    bars = event_rows()
    bars[30].update(open=25, close=18, high=26, low=17)
    r = build_price_action_level(bars, swing_span=2)
    level = next(x for x in r['levels'] if x['anchor_index'] == 17)
    linked = [e for e in r['events'] if e['level_id'] == level['id']]
    assert [e['kind'] for e in linked] == ['breakout_up', 'retest_hold', 'retest_failed']
    assert level['status'] == 'invalidated'
    assert level['first_retest_index'] == 23
    assert level['end_index'] == level['invalidated_index'] == 30
    assert bars[30]['dt'] in level['reason']


def test_misaligned_existing_chan_does_not_plot_wrong_coordinates():
    bars = event_rows()
    bars[7], bars[8] = bars[8], bars[7]
    r = enrich_chan_price_action({'levels': {'D': {'bars': bars}}})['levels']['D']
    assert r['status'] == 'unavailable'
    assert r['reason'] == 'unaligned_source_coordinates'
    assert r['levels'] == [] and r['events'] == [] and r['moving_averages'] == []


def test_standard_fetch_kline_automatically_attaches_price_action(monkeypatch):
    import fetch_kline
    from types import SimpleNamespace
    data = [{'Date':b['dt'], 'Open':b['open'], 'High':b['high'], 'Low':b['low'], 'Close':b['close'], 'Volume':b['volume']} for b in event_rows()]
    monkeypatch.setattr(fetch_kline, 'parse_ticker', lambda ticker: SimpleNamespace(full=ticker, market='U'))
    monkeypatch.setattr(fetch_kline, '_fetch_rows_for_analysis', lambda ti: (data, {'source':'fixed', 'adjusted':True, 'adjustment_status':'applied'}))
    monkeypatch.setattr(fetch_kline, 'fetch_chip_distribution', lambda ti: {})
    result = fetch_kline.main('TEST')['data']
    assert result['price_action']['schema_version'] == 'price_action.v1'
    assert result['chan']['levels']['D']['price_action']['events']
    assert result['price_action']['levels']['D']['provenance']['source'] == 'fixed'
