from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import pytest
from chart_stock import main, prepare_chart, render_chart_html
from test_price_action import event_rows


def test_list_input_reusable_structures_offline_html():
    bundle = prepare_chart('TEST', event_rows(), input_source='fixed test data')
    assert bundle['schema_version'] == 'jtrader.chart.v1'
    assert bundle['data']['chan']['source'] == 'fixed test data'
    assert bundle['data']['chan']['adjusted'] is None
    assert bundle['data']['price_action']['levels']['D']['events']
    html = render_chart_html(bundle)
    assert '<title>TEST' in html and 'id="jtrader-chart-data"' in html
    assert 'data-chan-level-panel="D"' in html
    assert '<script src=' not in html and '<link rel="stylesheet"' not in html


def test_existing_chan_retains_weekly_and_does_not_mutate():
    chan = prepare_chart('TEST', event_rows())['data']['chan']
    original = deepcopy(chan)
    result = prepare_chart('TEST', chan)
    assert result['data']['chan']['levels']['W']['bars'] == original['levels']['W']['bars']
    assert chan == original
    with pytest.raises(ValueError, match='does not match'):
        prepare_chart('DIFFERENT', chan)


def test_cli_new_process_preserves_input_and_protects_names(tmp_path):
    path = tmp_path/'input.json'
    path.write_text(json.dumps(event_rows()))
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    script = Path(__file__).resolve().parents[1]/'chart_stock.py'
    proc = subprocess.run([sys.executable, str(script), 'TEST', '--input', str(path), '--output', str(tmp_path/'out')], text=True, capture_output=True)
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path/'out/chart.html').exists()
    assert json.loads((tmp_path/'out/chart.json').read_text())['ticker'] == 'TEST'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
    for output in (path, tmp_path/'raw_data.json'):
        with pytest.raises(SystemExit) as exc:
            main(['TEST', '--input', str(path), '--output', str(output), '--force'])
        assert exc.value.code == 2
    with pytest.raises(SystemExit):
        main(['TEST', '--input', str(path), '--output', str(tmp_path/'out')])


def test_empty_bad_ticker_and_payload_escaping():
    with pytest.raises(ValueError):
        prepare_chart('TEST', [])
    with pytest.raises(ValueError):
        prepare_chart('../TEST', event_rows())
    bundle = prepare_chart('TEST', {'rows':event_rows(), 'source':'</script><img src=x onerror=alert(1)>'})
    html = render_chart_html(bundle)
    assert '</script><img src=x' not in html
    assert '\\u003c/script>' in html


def test_bad_ohlcv_is_reported_then_strict_json_remains_serializable():
    rows = event_rows()
    rows.append(dict(rows[-1], dt='2026-01-01', close=float('nan')))
    result = prepare_chart('TEST', rows)
    assert result['data']['chan']['quality']['invalid_rows'] == 1
    json.dumps(result, allow_nan=False)
